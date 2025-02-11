import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

from gpiozero import Servo

import atexit  # to turn off both motors

motor_address = 0x80  # 128 - motor_roboclaw address
shooter_address = 0x82  # 130 - shooter_roboclaw address

# Initialize Roboclaw
motor_roboclaw = Roboclaw("/dev/ttyS0", 460800)
shooter_roboclaw = Roboclaw("/dev/ttyS0", 460800)

motor_roboclaw.Open()
shooter_roboclaw.Open()

LOWER_DEAD_ZONE = 132
UPPER_DEAD_ZONE = 124

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Motor 1 speed
right_speed = 0  # Motor 2 speed

shooter_active = False  # Tracks if shooter thread is running

# Locate the PS4 controller


def stop_motors():
    print("\nStopping motors...")
    motor_roboclaw.ForwardM1(motor_address, 0)  # Force Stop Right Motor (M1)
    motor_roboclaw.ForwardM2(motor_address, 0)  # Force Stop Left Motor (M2)
    motor_roboclaw.BackwardM1(motor_address, 0)  # Ensure No Reverse Movement
    motor_roboclaw.BackwardM2(motor_address, 0)  # Ensure No Reverse Movement
    motor_roboclaw.SpeedM1(motor_address, 0)  # Final Check
    motor_roboclaw.SpeedM2(motor_address, 0)  # Final Check

    shooter_roboclaw.ForwardM1(shooter_address, 0)  # Stop Shooter Motor 1
    shooter_roboclaw.ForwardM2(shooter_address, 0)  # Stop Shooter Motor 2


# Register the stop_motors function to run on exit
atexit.register(stop_motors)


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to continuously send motor commands


def send_motor_command():
    global left_speed, right_speed
    last_left_speed = -1  # Track last sent speed for Motor 1
    last_right_speed = -1  # Track last sent speed for Motor 2

    while True:
        try:
            with lock:
                speed_L = left_speed
                speed_R = right_speed

            # Motor 1 - Left Joystick Control (M2 is Left)
            if LOWER_DEAD_ZONE <= speed_L <= UPPER_DEAD_ZONE:  # Dead zone
                motor_roboclaw.FordwardM1(motor_address, 0)  # Reverse Stop
                if last_left_speed != 0:
                    print("Sent Stop Command to Motor 1")
                    last_left_speed = 0
            elif speed_L < 128:  # Forward (Now Backward)
                motor_roboclaw.ForwardM1(
                    motor_address, 127 - speed_L)  # Reverse Forward
                if last_left_speed != speed_L:
                    print(f"Sent Reverse Speed to Motor 1: {127 - speed_L}")
                    last_left_speed = speed_L
            else:  # Reverse (Now Forward)
                motor_roboclaw.BackwardM1(
                    motor_address, speed_L - 128)  # Reverse Reverse
                if last_left_speed != speed_L:
                    print(f"Sent Forward Speed to Motor 1: {speed_L - 128}")
                    last_left_speed = speed_L

            # Motor 2 - Right Joystick Control
            if LOWER_DEAD_ZONE <= speed_R <= UPPER_DEAD_ZONE:  # Dead zone
                motor_roboclaw.ForwardM2(motor_address, 0)
                if last_right_speed != 0:
                    print("Sent Stop Command to Motor 2")
                    last_right_speed = 0
            elif speed_R < 128:  # Forward
                motor_roboclaw.ForwardM2(motor_address, 127 - speed_R)
                if last_right_speed != speed_R:
                    print(f"Sent Forward Speed to Motor 2: {127 - speed_R}")
                    last_right_speed = speed_R
            else:  # Reverse
                motor_roboclaw.BackwardM2(motor_address, speed_R - 128)
                if last_right_speed != speed_R:
                    print(f"Sent Reverse Speed to Motor 2: {speed_R - 128}")
                    last_right_speed = speed_R

        except Exception as e:
            print(f"Error sending motor command: {e}")

        time.sleep(0.02)  # Reduce delay to 20ms for faster response

# Function to continuously read joystick positions


def poll_joystick(controller):
    global left_speed, right_speed, shooter_active
    while True:
        try:
            event = controller.read_one()
            if event is None:
                time.sleep(0.002)  # Reduced sleep to improve polling speed
                continue

            if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
                value = event.value
                if event.code == ecodes.ABS_Y:  # Left joystick
                    with lock:
                        joystick_positions['LEFT_Y'] = value
                        left_speed = value
                    print(f"Joystick Left Y: {value}")

                elif event.code == ecodes.ABS_RY:  # Right joystick
                    with lock:
                        joystick_positions['RIGHT_Y'] = value
                        right_speed = value
                    print(f"Joystick Right Y: {value}")

            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TR:  # R2 Trigger
                print("Right Trigger Pressed!")
                shooter_active = True  # Activate shooter

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay

# Shooter motor control function


def shooter_motor_control():
    global shooter_active
    shooter_speed = 64  # Half speed (0-127 scale)

    while True:
        if shooter_active:
            shooter_roboclaw.ReverseM1(shooter_address, shooter_speed)
            shooter_roboclaw.ReverseM2(shooter_address, shooter_speed)
            time.sleep(2)  # Simulate ramp-up time
            print("Shooter Motors Up to Speed!")

            servo = Servo(12, min_pulse_width=0.5/1000,
                          max_pulse_width=2.5/1000)

            servo.min()  # Move to 0 degrees
            sleep(1)
            servo.max()  # Move to 180 degrees

            shooter_roboclaw.ForwardM1(shooter_address, 64)
            shooter_roboclaw.ForwardM2(shooter_address, 64)

            shooter_active = False  # Reset after reaching speed
        time.sleep(0.01)  # Prevent CPU overload


# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    # Set default acceleration
    motor_roboclaw.SetM1DefaultAccel(motor_address, 8)
    motor_roboclaw.SetM2DefaultAccel(motor_address, 8)
    shooter_roboclaw.SetM1DefaultAccel(shooter_address, 8)
    shooter_roboclaw.SetM2DefaultAccel(shooter_address, 8)

    shooter_roboclaw.ForwardM1(shooter_address, 64)
    shooter_roboclaw.ForwardM2(shooter_address, 64)

    stop_motors()  # Ensure motors are stopped at startup

    # Start polling threads
    joystick_thread = threading.Thread(
        target=poll_joystick, daemon=True, args=(controller,))
    joystick_thread.start()

    motor_thread = threading.Thread(target=send_motor_command, daemon=True)
    motor_thread.start()

    shooter_thread = threading.Thread(
        target=shooter_motor_control, daemon=True)  # ADDED HERE
    shooter_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_motors()


main()

import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

import atexit  # to turn off both motors

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

address = 0x80  # Roboclaw address

LOWER_DEAD_ZONE = 132
UPPER_DEAD_ZONE = 124


# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Motor 1 speed
right_speed = 0  # Motor 2 speed

# Locate the PS4 controller


def stop_motors():
    print("\nStopping motors...")
    roboclaw.ForwardM1(address, 0)  # Force Stop Right Motor (M1)
    roboclaw.ForwardM2(address, 0)  # Force Stop Left Motor (M2)
    roboclaw.BackwardM1(address, 0)  # Ensure No Reverse Movement
    roboclaw.BackwardM2(address, 0)  # Ensure No Reverse Movement
    roboclaw.SpeedM1(address, 0)  # Final Check
    roboclaw.SpeedM2(address, 0)  # Final Check


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
    # M1 is RIGHT
    # M2 is LEFT
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
                roboclaw.ForwardM1(address, 0)  # ✅ Reverse Stop
                if last_left_speed != 0:
                    print("Sent Stop Command to Motor 1")
                    last_left_speed = 0
            elif speed_L < 128:  # Forward (Now Backward)
                # Reverse Forward
                roboclaw.ForwardM1(address, (127 - speed_L)/2)
                if last_left_speed != speed_L:
                    print(f"Sent Reverse Speed to Motor 1: {127 - speed_L}")
                    last_left_speed = speed_L
            else:  # Reverse (Now Forward)
                # Reverse Reverse
                roboclaw.BackwardM1(address, (speed_L - 128)/2)
                if last_left_speed != speed_L:
                    print(f"Sent Forward Speed to Motor 1: {speed_L - 128}")
                    last_left_speed = speed_L

            # Motor 2 - Right Joystick Control
            if LOWER_DEAD_ZONE <= speed_R <= UPPER_DEAD_ZONE:  # Dead zone
                roboclaw.ForwardM2(address, 0)
                if last_right_speed != 0:
                    print("Sent Stop Command to Motor 2")
                    last_right_speed = 0
            elif speed_R < 128:  # Forward
                roboclaw.BackwardM2(address, (127 - speed_R)/2)
                if last_right_speed != speed_R:
                    print(f"Sent Forward Speed to Motor 2: {127 - speed_R}")
                    last_right_speed = speed_R
            else:  # Reverse
                roboclaw.ForwardM2(address, (speed_R - 128)/2)
                if last_right_speed != speed_R:
                    print(f"Sent Reverse Speed to Motor 2: {speed_R - 128}")
                    last_right_speed = speed_R

        except Exception as e:
            print(f"Error sending motor command: {e}")

        time.sleep(0.02)  # Reduce delay to 20ms for faster response

# Function to continuously read joystick positions


def poll_joystick(controller):
    global left_speed, right_speed
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
                        left_speed = value  # Directly store joystick value
                    print(f"Joystick Left Y: {value}")

                elif event.code == ecodes.ABS_RY:  # Right joystick
                    with lock:
                        joystick_positions['RIGHT_Y'] = value
                        right_speed = value  # Directly store joystick value
                    print(f"Joystick Right Y: {value}")

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay

# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    roboclaw.SetM1DefaultAccel(address, 8)  # Smooth acceleration for M1
    roboclaw.SetM2DefaultAccel(address, 8)  # Smooth acceleration for M2

    # Starting speed Zero
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)
    print("Motors initialized to 0 speed")

    # Start joystick polling thread
    joystick_thread = threading.Thread(
        target=poll_joystick, daemon=True, args=(controller,))
    joystick_thread.start()

 # Start motor command streaming thread
    motor_thread = threading.Thread(target=send_motor_command, daemon=True)
    motor_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_motors()  # Ensure motors stop before exiting


main()

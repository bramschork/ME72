import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw
from math import ceil

# To turn off both motors
import atexit

# Servo control
from gpiozero import Servo

# Initialize Roboclaws
motor_roboclaw = Roboclaw("/dev/ttyS0", 38400)
shooter_roboclaw = Roboclaw("/dev/ttyS0", 38400)

# Open Serial Ports with Roboclaws
motor_roboclaw.Open()
shooter_roboclaw.Open()

motor_address = 0x80  # 128 - motor_motor_roboclaw address
shooter_address = 0x82  # 130 - shooter_motor_roboclaw address

LOWER_DEAD_ZONE = 134
UPPER_DEAD_ZONE = 116

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Motor 1 speed
right_speed = 0  # Motor 2 speed

# Locate the PS4 controller

servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


def stop_motors():
    print("\nStopping motors...")
    motor_roboclaw.ForwardM1(motor_address, 0)
    motor_roboclaw.ForwardM2(motor_address, 0)

    shooter_roboclaw.ForwardM1(motor_address, 0)
    shooter_roboclaw.ForwardM2(motor_address, 0)


def stop_shooter():
    shooter_roboclaw.ForwardM1(shooter_address, 0)
    shooter_roboclaw.ForwardM2(shooter_address, 0)
    servo.min()
    print("Motors stopped")


# Variable to hold the timer instance
stop_timer = None


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
                motor_roboclaw.ForwardM1(motor_address, 0)  # ✅ Reverse Stop
                if last_left_speed != 0:
                    # print("Sent Stop Command to Motor 1")
                    last_left_speed = 0
            elif speed_L < 128:  # Forward (Now Backward)
                # Reverse Forward
                motor_roboclaw.ForwardM1(
                    motor_address, ceil((127 - speed_L)/2))
                if last_left_speed != speed_L:
                    # print(f"Sent Reverse Speed to Motor 1: {127 - speed_L}")
                    last_left_speed = speed_L
            else:  # Reverse (Now Forward)
                # Reverse Reverse
                motor_roboclaw.BackwardM1(
                    motor_address, ceil((speed_L - 128)/2))
                if last_left_speed != speed_L:
                    # print(f"Sent Forward Speed to Motor 1: {speed_L - 128}")
                    last_left_speed = speed_L

            # Motor 2 - Right Joystick Control
            if LOWER_DEAD_ZONE <= speed_R <= UPPER_DEAD_ZONE:  # Dead zone
                motor_roboclaw.ForwardM2(motor_address, 0)
                if last_right_speed != 0:
                    # print("Sent Stop Command to Motor 2")
                    last_right_speed = 0
            elif speed_R < 128:  # Forward
                motor_roboclaw.BackwardM2(
                    motor_address, ceil((127 - speed_R)/2))
                if last_right_speed != speed_R:
                    # print(f"Sent Forward Speed to Motor 2: {127 - speed_R}")
                    last_right_speed = speed_R
            else:  # Reverse
                motor_roboclaw.ForwardM2(
                    motor_address, ceil((speed_R - 128)/2))
                if last_right_speed != speed_R:
                    # print(f"Sent Reverse Speed to Motor 2: {speed_R - 128}")
                    last_right_speed = speed_R

        except Exception as e:
            print(f"Error sending motor command: {e}")

        time.sleep(0.02)  # Reduce delay to 20ms for faster response

# Function to continuously read joystick positions


intake = False
motor_running = False


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
                    # print(f"Joystick Left Y: {value}")

                elif event.code == ecodes.ABS_RY:  # Right joystick
                    with lock:
                        joystick_positions['RIGHT_Y'] = value
                        right_speed = value  # Directly store joystick value
                    # print(f"Joystick Right Y: {value}")

                if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_Z:
                    print('trigger')
                    # Only toggle when the trigger is fully pressed (adjust threshold if needed)
                    if event.value > 200:  # Adjust this threshold as needed
                        # Toggle motor state
                        motor_running = not motor_running

                        # Set motor speed based on state
                        if motor_running:
                            shooter_roboclaw.ForwardM1(shooter_address, 64)
                            shooter_roboclaw.ForwardM2(shooter_address, 64)
                            print("Motors running at speed 64")
                        else:
                            shooter_roboclaw.ForwardM1(shooter_address, 0)
                            shooter_roboclaw.ForwardM2(shooter_address, 0)
                            print("Motors stopped")

                        # Debounce: Wait for trigger release to avoid rapid toggling
                        while event.value > 200:
                            events = controller.read_loop()
                            for e in events:
                                if e.type == ecodes.EV_ABS and e.code == ecodes.ABS_Z:
                                    event = e
                                    shooter_roboclaw.ForwardM2(
                                        shooter_address, 64)
                else:
                    print(event.code)

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay

# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    motor_roboclaw.SetM1DefaultAccel(
        motor_address, 8)  # Smooth acceleration for M1
    motor_roboclaw.SetM2DefaultAccel(
        motor_address, 8)  # Smooth acceleration for M2

    # Starting speed Zero
    motor_roboclaw.ForwardM1(motor_address, 0)
    motor_roboclaw.ForwardM2(motor_address, 0)
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

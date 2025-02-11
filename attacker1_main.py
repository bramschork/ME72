import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

address = 0x80  # Roboclaw address

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Motor 1 speed
right_speed = 0  # Motor 2 speed

# Acceleration - speed increments per seconds
# Ex. 1000 = Takes 1 second to ramp from 0 to 1,000 speed units
# 5000 = Takes ~0.2 seconds to reach max speed
# 65,535 = Instant acceleration (max setting)
acceleration = 500

# Locate the PS4 controller


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
            # Read speeds outside the lock to avoid blocking joystick updates
            with lock:
                speed_L = left_speed
                speed_R = right_speed

            # Always send a command, even if speed hasn't changed
            if 126 <= speed_L <= 130:
                roboclaw.SpeedAccelM1()(address, accel=acceleration, 0)
                if last_left_speed != 0:
                    print("Sent Stop Command to Motor 1")
                    last_left_speed = 0
            else:
                roboclaw.SpeedAccelM1()(address, accel=acceleration, speed_L)
                if last_left_speed != speed_L:
                    print(f"Sent Speed to Motor 1: {speed_L}")
                    last_left_speed = speed_L

            if 126 <= speed_R <= 130:
                roboclaw.SpeedAccelM2()(address, accel=acceleration, 0)
                if last_right_speed != 0:
                    print("Sent Stop Command to Motor 2")
                    last_right_speed = 0
            else:
                roboclaw.SpeedAccelM2()(address, accel=acceleration, speed_R)
                if last_right_speed != speed_R:
                    print(f"Sent Speed to Motor 2: {speed_R}")
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
                        left_speed = 0 if 126 <= value <= 130 else max(
                            0, min(127, 128 - value))
                    print(f"Joystick Left Y: {value}")

                elif event.code == ecodes.ABS_RY:  # Right joystick
                    with lock:
                        joystick_positions['RIGHT_Y'] = value
                        right_speed = 0 if 126 <= value <= 130 else max(
                            0, min(127, 128 - value))
                    print(f"Joystick Right Y: {value}")

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay

# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

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
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)
        print("\nExiting...")


main()

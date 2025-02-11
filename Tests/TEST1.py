import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 115200)
roboclaw.Open()
address = 0x80  # Roboclaw address

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick positions
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()  # Lock for thread safety

# Locate the PS4 controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


# Initialize controller
controller = find_ps4_controller()
controller.grab()  # Ensure exclusive access
print(f"Connected to {controller.name} at {controller.path}")

# Function to continuously read joystick positions

try:
    print("Starting joystick polling thread.")

    while True:
        try:
            # ✅ Extract the event from the generator
            event = next(controller.read())
        except (BlockingIOError, StopIteration):
            continue  # No new events, keep looping

        if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
            if event.code == ecodes.ABS_Y:
                joystick_positions['LEFT_Y'] = event.value
                print(joystick_positions['LEFT_Y'])

                try:
                    speed = max(
                        0, min(127, 128 - joystick_positions['LEFT_Y']))
                    roboclaw.ForwardM1(address, speed)
                    print(f"Sent: {speed}")
                except Exception as e:
                    print(f"Roboclaw Error: {e}")

except KeyboardInterrupt:
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)
    print("\nExiting...")

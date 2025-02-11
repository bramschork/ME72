import evdev
from evdev import InputDevice, ecodes
import time
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

address = 0x80  # Roboclaw address

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variable for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
left_speed = 0  # Motor speed variable

# Locate the PS4 controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Main loop: Read joystick input & send motor commands


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    last_sent_speed = -1  # Track last sent speed

    while True:
        try:
            # Read joystick input (non-blocking)
            event = controller.read_one()

            if event and event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
                value = event.value
                if event.code == ecodes.ABS_Y:
                    joystick_positions['LEFT_Y'] = value
                    left_speed = 0 if 126 <= value <= 130 else max(
                        0, min(127, 128 - value))
                    print(f"Joystick Y: {value}")

            # Always send motor commands, even if joystick is idle
            if left_speed != last_sent_speed:
                roboclaw.ForwardM1(address, left_speed)
                print(f"Sent Speed to Roboclaw: {left_speed}")
                last_sent_speed = left_speed

            # Small delay for efficiency, prevents CPU overload
            time.sleep(0.005)

        except KeyboardInterrupt:
            roboclaw.ForwardM1(address, 0)
            print("\nExiting...")
            break


main()

# pip install evdev

import evdev
from evdev import InputDevice, categorize, ecodes

# Locate the controller


def find_ps4_controller():
    devices = [InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


# Initialize controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Axis codes for left and right joysticks
AXIS_CODES = {
    'LEFT_X': ecodes.ABS_X,
    'LEFT_Y': ecodes.ABS_Y,
    'RIGHT_X': ecodes.ABS_RX,
    'RIGHT_Y': ecodes.ABS_RY,
}

# Initialize joystick positions
joystick_positions = {
    'LEFT_X': 0,
    'LEFT_Y': 0,
    'RIGHT_X': 0,
    'RIGHT_Y': 0,
}

# Read and print joystick positions
try:
    print("Reading joystick positions. Move the joysticks to see the output.")
    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code in AXIS_CODES.values():
                for axis_name, axis_code in AXIS_CODES.items():
                    if event.code == axis_code:
                        joystick_positions[axis_name] = event.value
                        # print(f"{axis_name}: {joystick_positions[axis_name]}")
                        print(
                            f"Left Joystick Y: {joystick_positions['Left _Y']} | Right Joystick Y: {joystick_positions['Right_Y']}")

except KeyboardInterrupt:
    print("\nExiting...")

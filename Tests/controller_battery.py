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

# Get battery level


def get_battery_level(controller):
    try:
        with open(f"/sys/class/power_supply/{controller.uniq}/capacity", "r") as f:
            battery_level = f.read().strip()
            return battery_level
    except FileNotFoundError:
        print("Battery level not available.")
        return "Unknown"


# Initialize controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Get and print battery level
battery_level = get_battery_level(controller)
print(f"Battery Level: {battery_level}%")

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
                        print(
                            f"Left Joystick Y: {joystick_positions['LEFT_Y']} | Right Joystick Y: {joystick_positions['RIGHT_Y']}")

except KeyboardInterrupt:
    print("\nExiting...")

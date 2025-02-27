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

# Button codes for L1, L2, R1, and R2
BUTTON_CODES = {
    'L1': ecodes.BTN_TL,
    'R1': ecodes.BTN_TR,
}

# Trigger codes for L2 and R2 (Analog triggers)
TRIGGER_CODES = {
    'L2': ecodes.ABS_Z,
    'R2': ecodes.ABS_RZ,
}

# Initialize joystick positions and button states
joystick_positions = {
    'LEFT_X': 0,
    'LEFT_Y': 0,
    'RIGHT_X': 0,
    'RIGHT_Y': 0,
}

button_states = {
    'L1': False,
    'R1': False,
    'L2': False,
    'R2': False,
}

# Read and print joystick positions and button presses
try:
    print("Reading joystick positions and button presses...")
    for event in controller.read_loop():
            # Triggers (Analog input)
            if event.code in TRIGGER_CODES.values():
                for trigger_name, trigger_code in TRIGGER_CODES.items():
                    if event.code == trigger_code:
                        pressed = event.value > 0
                        if button_states[trigger_name] != pressed:
                            button_states[trigger_name] = pressed
                            if pressed:
                                print(f"{trigger_name} pressed")
                            else:
                                print(f"{trigger_name} released")

        # Button Presses (Digital input)
        if event.type == ecodes.EV_KEY:
            if event.code in BUTTON_CODES.values():
                for button_name, button_code in BUTTON_CODES.items():
                    if event.code == button_code:
                        pressed = event.value == 1
                        if button_states[button_name] != pressed:
                            button_states[button_name] = pressed
                            if pressed:
                                print(f"{button_name} pressed")
                            else:
                                print(f"{button_name} released")

except KeyboardInterrupt:
    print("\nExiting...")

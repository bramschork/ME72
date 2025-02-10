from roboclaw_3 import Roboclaw
from evdev import InputDevice, list_devices, ecodes

import threading
import time

# Grab axis codes and initial stick positions
from joystick_config import AXIS_CODES, joystick_positions

########## ROBOCLAW INIT  ##########
# Addresses for the two Roboclaws
motor_roboclaw_address = 0x80  # 128 in hex
mechanism_roboclaw_address = 0x82  # 130 in hex

# Initialize both Roboclaws
motor_roboclaw = Roboclaw("/dev/ttyS0", 115200)
mechanism_roboclaw = Roboclaw("/dev/ttyS0", 115200)

# Open serial communication
motor_roboclaw.Open()
mechanism_roboclaw.Open()
#####################################

# Joystick Deadzone threshold
DEADZONE = 5

# Set Initial Lightbar Color
set_lightbar_color(0, 255, 0)

# Find PS4 controller for inputs


def find_ps4_controller():
    """
    Finds and returns the first detected PS4 controller.

    Returns:
        InputDevice: The PS4 controller device.

    Raises:
        RuntimeError: If no PS4 controller is found.

    Notes:
        evdev (Event Device) interacts with the PS4 controller as an input device.
            Listens to joystick movements, button presses, and touchpad inputs.
            Used for reading inputs like analog stick positions and button presses. 
    """

    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:  # Name for PS4 controller
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Hidraw for light bar and rumble control


def find_ps4_hidraw():
    """
    hidraw (Human Interface Device Raw) communicates with the controller at a lower level via raw HID reports.
        Can send commands for light bar color, control rumble, outputs, etc.
    """

    hidraw_devices = glob.glob('/dev/hidraw*')
    for device in hidraw_devices:
        try:
            with open(device, "rb") as f:
                name = os.readlink(
                    f"/sys/class/hidraw/{os.path.basename(device)}/device/driver")
                if "sony" in name.lower():
                    return device
        except Exception:
            pass
    raise RuntimeError(
        "PS4 hidraw device not found! Ensure it's connected via USB.")

# Function to change the light bar color


def set_lightbar_color(r, g, b):
    """Sends a HID report to change the PS4 controller light bar color."""
    hidraw_device = find_ps4_hidraw()
    with open(hidraw_device, "wb") as f:
        command = bytes([0x05, 0xFF, r, g, b, 0x00, 0x00, 0x00, 0x00, 0x00])
        f.write(command)


# Initialize the PS4 controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")


# Normalize joystick values (0–256 to -127 to 127)


def normalize(value):
    # If within deadzone, treat as zero
    # If value is greater than 123 and less than 133, treat as 0
    if 128 - DEADZONE <= value <= 128 + DEADZONE:
        return 0
    # ABOVE SCALE IS 0 to 256. Now convert!
    return value - 128  # New scale is from -128 to 128

# Tank drive mixed mode function


def tank_drive(left_x, left_y, right_x, right_y):
    # Normalize inputs
    left_y = normalize(left_y)  # Forward/Reverse for Motor 1
    right_y = normalize(right_y)  # Forward/Reverse for Motor 2
    left_x = normalize(left_x)  # Turning for Motor 1
    right_x = normalize(right_x)  # Turning for Motor 2

    # Calculate mixed motor speeds
    left_motor_speed = left_y  # Left joystick controls Motor 1
    right_motor_speed = right_y  # Right joystick controls Motor 2

    roboclaw.ForwardBackwardM1(
        motor_roboclaw_address, left_motor_speed)  # Motor 1
    roboclaw.ForwardBackwardM2(
        motor_roboclaw_address, right_motor_speed)  # Motor 2


# Read joystick inputs and control motors
try:
    print("JOYSTICKS HOT")
    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS:

            # Joystick Event
            if event.code in AXIS_CODES.values():
                for axis_name, axis_code in AXIS_CODES.items():
                    if event.code == axis_code:
                        # Update joystick position
                        joystick_positions[axis_name] = event.value

                        # Determine deadzone or actual value
                        if 128 - DEADZONE <= event.value <= 128 + DEADZONE:
                            # print(f"{axis_name}: Deadzone")
                            pass
                        else:
                            # print(f"{axis_name}: {event.value}")
                            pass

                        # Call tank_drive with updated joystick positions
                        tank_drive(
                            joystick_positions['LEFT_X'],
                            joystick_positions['LEFT_Y'],
                            joystick_positions['RIGHT_X'],
                            joystick_positions['RIGHT_Y']
                        )

            # Right Trigger / Mechanism Event
            if event.code == ecodes.ABS_RZ:  # Right Trigger (R2)
                trigger_value = event.value
                if trigger_value > 10 and not blinking:  # R2 is pressed
                    blink_thread = threading.Thread(
                        target=blink_lightbar, args=(255, 0, 0), daemon=True)
                    blink_thread.start()
                elif trigger_value <= 10 and blinking:  # R2 released
                    blinking = False
                    set_lightbar_color(0, 255, 0)  # Restore default green
except KeyboardInterrupt:
    print("\nExiting...")

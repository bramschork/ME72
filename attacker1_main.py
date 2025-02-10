from roboclaw_3 import Roboclaw
from evdev import InputDevice, list_devices, ecodes

import threading
import time
import glob

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

MECHANISM_MOTOR_SPEED = 64  # half-speed, since full speed is 127

# Joystick Deadzone threshold
DEADZONE = 5

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


# Set Initial Lightbar Color
set_lightbar_color(0, 255, 0)

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


def monitor_and_check_motor_speed(target_current=2.0, tolerance=0.5, check_interval=0.1):
    """
    Monitors the motor current until it stabilizes at the target speed.
    Once the motors are up to speed, this function returns.

    Args:
        target_current (float): Expected steady-state current (in Amps).
        tolerance (float): Allowed variation from the target current.
        check_interval (float): Time in seconds between checks.

    Returns:
        bool: True when motors reach target speed.
    """
    while True:
        # Read motor currents (converted from mA to A)
        m1_current = mechanism_roboclaw.ReadCurrents(
            mechanism_roboclaw_address)[1] / 100.0
        m2_current = mechanism_roboclaw.ReadCurrents(
            mechanism_roboclaw_address)[2] / 100.0

        # Check if both motors are within the target range
        if (
            abs(m1_current - target_current) <= tolerance and
            abs(m2_current - target_current) <= tolerance
        ):
            print("Motors are up to speed!")
            return True  # Exit and return once motors stabilize

        time.sleep(check_interval)  # Wait before checking again


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

            # Handle R2 (Right Trigger) press for motor control and monitoring
            if event.code == ecodes.ABS_RZ:
                trigger_value = event.value

                if trigger_value > 10:  # Trigger pulled
                    set_lightbar_color(255, 0, 0)  # Set light bar red

                    # Set mechanism motors: M1 forward, M2 reverse
                    mechanism_roboclaw.ForwardM1(
                        mechanism_roboclaw_address, MECHANISM_MOTOR_SPEED)
                    mechanism_roboclaw.BackwardM2(
                        mechanism_roboclaw_address, MECHANISM_MOTOR_SPEED)

                    def monitor_and_stop_motors():
                        """Runs monitor function and stops motors when it's done."""
                        if monitor_and_check_motor_speed():
                            # Stop mechanism motors after reaching speed
                            mechanism_roboclaw.ForwardM1(
                                mechanism_roboclaw_address, 0)
                            mechanism_roboclaw.BackwardM2(
                                mechanism_roboclaw_address, 0)
                            print("Mechanism motors stopped.")

                    # Start monitoring motor speed in a separate thread
                    motor_monitor_thread = threading.Thread(
                        target=monitor_and_stop_motors,
                        daemon=True
                    )
                    motor_monitor_thread.start()

                else:  # Trigger released
                    set_lightbar_color(0, 255, 0)  # Set light bar green

                    # Stop mechanism motors
                    mechanism_roboclaw.ForwardM1(mechanism_roboclaw_address, 0)
                    mechanism_roboclaw.BackwardM2(
                        mechanism_roboclaw_address, 0)
except KeyboardInterrupt:
    print("\nExiting...")

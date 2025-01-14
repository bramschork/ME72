from roboclaw_3 import Roboclaw
from evdev import InputDevice, list_devices, ecodes

# Initialize RoboClaw (update COM port and baud rate as per your setup)
address = 0x40
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Function to find PS4 controller


def find_ps4_controller():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:  # Name for PS4 controller
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


# Initialize the PS4 controller
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
    'LEFT_X': 128,
    'LEFT_Y': 128,
    'RIGHT_X': 128,
    'RIGHT_Y': 128,
}

# Deadzone threshold
DEADZONE = 5

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
    motor1_speed = left_y  # Left joystick controls Motor 1
    motor2_speed = right_y  # Right joystick controls Motor 2

    roboclaw.ForwardBackwardM1(address, motor1_speed)  # Address 0x40, M1
    roboclaw.ForwardBackwardM2(address, motor2_speed)  # Address 0x40, M2


# Read joystick inputs and control motors
try:
    print("Reading joystick positions. Move the joysticks to control the motors.")
    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code in AXIS_CODES.values():
                for axis_name, axis_code in AXIS_CODES.items():
                    if event.code == axis_code:
                        # Update joystick position
                        joystick_positions[axis_name] = event.value

                        # Determine deadzone or actual value
                        if 128 - DEADZONE <= event.value <= 128 + DEADZONE:
                            print(f"{axis_name}: Deadzone")
                        else:
                            print(f"{axis_name}: {event.value}")

                        # Call tank_drive with updated joystick positions
                        tank_drive(
                            joystick_positions['LEFT_X'],
                            joystick_positions['LEFT_Y'],
                            joystick_positions['RIGHT_X'],
                            joystick_positions['RIGHT_Y']
                        )
except KeyboardInterrupt:
    print("\nExiting...")

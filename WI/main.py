import evdev
from evdev import InputDevice, categorize, ecodes
from roboclaw_3 import Roboclaw
from time import sleep


def find_ps4_controller():
    devices = [InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


# Initialize controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Roboclaw Init
address = 0x80
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

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
                        print(f"{axis_name}: {joystick_positions[axis_name]}")
except KeyboardInterrupt:
    print("\nExiting...")


# Normalize joystick values (0–256 to -127 to 127)
def normalize(value):
    return value - 128

# Tank drive mixed mode function


def tank_drive(left_x, left_y, right_x, right_y):
    # Normalize inputs
    left_y = normalize(left_y)  # Forward/Reverse for Motor 1
    right_y = normalize(right_y)  # Forward/Reverse for Motor 2
    left_x = normalize(left_x)  # Turning for Motor 1
    right_x = normalize(right_x)  # Turning for Motor 2

    # Calculate mixed motor speeds
    motor1_speed = left_y + left_x  # Left joystick controls Motor 1
    motor2_speed = right_y + right_x  # Right joystick controls Motor 2

    # Clamp values to -127 to 127
    motor1_speed = max(min(motor1_speed, 127), -127)
    motor2_speed = max(min(motor2_speed, 127), -127)

    # Send speed commands to motors
    roboclaw.ForwardBackwardM1(0x80, motor1_speed + 127)  # Address 0x80, M1
    roboclaw.ForwardBackwardM2(0x80, motor2_speed + 127)  # Address 0x80, M2


# Example usage
# Replace with actual joystick values
tank_drive(left_x=128, left_y=200, right_x=128, right_y=56)

from roboclaw_3 import Roboclaw
from evdev import InputDevice, categorize, ecodes

# Roboclaw Init
address = 0x80
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Device path for the controller (update as needed)
# Replace 'eventX' with your joystick device path
controller = InputDevice('/dev/input/eventX')

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
    roboclaw.ForwardBackwardM1(address, motor1_speed + 127)
    roboclaw.ForwardBackwardM2(address, motor2_speed + 127)


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
                        print(f"{axis_name}: {joystick_positions[axis_name]}")

                        # Call tank_drive with updated joystick positions
                        tank_drive(
                            joystick_positions['LEFT_X'],
                            joystick_positions['LEFT_Y'],
                            joystick_positions['RIGHT_X'],
                            joystick_positions['RIGHT_Y']
                        )
except KeyboardInterrupt:
    print("\nExiting...")

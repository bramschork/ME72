import evdev
from evdev import ecodes
from roboclaw_3 import Roboclaw
import serial

# Initialize PS4 controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Initialize RoboClaw
roboclaw = Roboclaw(serial.Serial('/dev/ttyS0', 38400))
roboclaw.Open()
address = 0x80  # Default address; adjust if necessary

# Axis codes
AXIS_CODES = {
    'LEFT_Y': ecodes.ABS_Y,
    'RIGHT_Y': ecodes.ABS_RY,
}

# Initialize joystick positions
joystick_positions = {
    'LEFT_Y': 128,
    'RIGHT_Y': 128,
}

def joystick_to_speed(value):
    # Normalize to -127 to 127
    return int((value - 128) * 127 / 128)

try:
    print("Reading joystick positions. Use the left and right joysticks to control motors.")
    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
            for axis_name, axis_code in AXIS_CODES.items():
                if event.code == axis_code:
                    joystick_positions[axis_name] = event.value
                    speed = joystick_to_speed(event.value)
                    if axis_name == 'LEFT_Y':
                        if speed >= 0:
                            roboclaw.ForwardM1(address, speed)
                        else:
                            roboclaw.BackwardM1(address, -speed)
                    elif axis_name == 'RIGHT_Y':
                        if speed >= 0:
                            roboclaw.ForwardM2(address, speed)
                        else:
                            roboclaw.BackwardM2(address, -speed)
except KeyboardInterrupt:
    print("\nExiting...")
    # Stop motors on exit
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)

import evdev
from evdev import InputDevice, ecodes
from roboclaw_3 import Roboclaw
import time

# Function to locate the PS4 controller
def find_ps4_controller():
    devices = [InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to scale joystick input to motor speed
def scale_value(value):
    # PS4 joystick values range from -32768 to 32767
    # RoboClaw speed values range from 0 to 127
    return int((value + 32768) * 127 / 65535)

# Initialize PS4 controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Initialize RoboClaw
address = 0x80  # Replace with your RoboClaw address if different
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

# Read joystick positions and control motors
try:
    print("Reading joystick positions. Use the left joystick for Motor 1 and the right joystick for Motor 2.")
    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
            for axis_name, axis_code in AXIS_CODES.items():
                if event.code == axis_code:
                    joystick_positions[axis_name] = event.value
                    motor_speed = scale_value(event.value)
                    if axis_name == 'LEFT_Y':
                        roboclaw.ForwardM1(address, motor_speed)
                    elif axis_name == 'RIGHT_Y':
                        roboclaw.ForwardM2(address, motor_speed)
                    print(f"{axis_name}: {joystick_positions[axis_name]}, Motor Speed: {motor_speed}")
        time.sleep(0.01)  # Small delay to prevent CPU overload
except KeyboardInterrupt:
    print("\nExiting...")
    # Stop motors on exit
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)

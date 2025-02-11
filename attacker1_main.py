import time
import evdev
from evdev import InputDevice, ecodes
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 115200)
roboclaw.Open()
address = 0x80  # Roboclaw address

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}

# Locate the PS4 controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


# Initialize controller
controller = find_ps4_controller()
print(f"Connected to {controller.name} at {controller.path}")

# Function to set motor speed (0-127 forward only)


def set_motor_speed(motor, speed):
    speed = max(0, min(127, speed))  # Clamp speed between 0 and 127
    if motor == 1:
        roboclaw.ForwardM1(address, speed)
    elif motor == 2:
        roboclaw.ForwardM2(address, speed)


# Poll joysticks every 20ms and send values to motors
try:
    print("Polling joystick every 20ms. Move the joysticks to control the motors.")

    while True:
        # Read all available joystick events
        for event in controller.read():
            if event.type == ecodes.EV_ABS:
                if event.code == AXIS_CODES['LEFT_Y']:
                    joystick_positions['LEFT_Y'] = event.value
                elif event.code == AXIS_CODES['RIGHT_Y']:
                    joystick_positions['RIGHT_Y'] = event.value

        # Convert joystick input to motor speed (Forward only)
        left_speed = (
            joystick_positions['LEFT_Y'] - 128) // 2 if joystick_positions['LEFT_Y'] > 128 else 0
        right_speed = (
            joystick_positions['RIGHT_Y'] - 128) // 2 if joystick_positions['RIGHT_Y'] > 128 else 0

        # Send motor commands
        set_motor_speed(1, left_speed)
        set_motor_speed(2, right_speed)

        # Print values in real-time
        print(
            f"\rLeft Motor: {left_speed} | Right Motor: {right_speed}", end="")

        # Wait 20ms before polling again
        time.sleep(0.1)

except KeyboardInterrupt:
    # Stop motors on exit
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)
    print("\nExiting...")

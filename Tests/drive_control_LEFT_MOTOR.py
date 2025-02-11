import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

address = 0x80  # Roboclaw address

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

# Shared variables for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Motor speed variable

# Locate the PS4 controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to continuously send motor commands


def send_motor_command():
    global left_speed
    last_sent_speed = -1  # Track the last sent speed

    while True:
        try:
            # Read speed outside the lock to avoid blocking joystick updates
            with lock:
                speed_to_send = left_speed

            # Always send a command, even if speed hasn't changed
            if 126 <= speed_to_send <= 130:
                roboclaw.ForwardM1(address, 0)
                if last_sent_speed != 0:
                    print("Sent Stop Command to Roboclaw")
                    last_sent_speed = 0
            else:
                roboclaw.ForwardM1(address, speed_to_send)
                if last_sent_speed != speed_to_send:
                    print(f"Sent Speed to Roboclaw: {speed_to_send}")
                    last_sent_speed = speed_to_send

        except Exception as e:
            print(f"Error sending motor command: {e}")

        time.sleep(0.02)  # Reduce delay to 20ms for faster response

# Function to continuously read joystick positions


def poll_joystick(controller):
    global left_speed
    while True:
        try:
            event = controller.read_one()
            if event is None:
                time.sleep(0.002)  # Reduced sleep to improve polling speed
                continue

            if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
                value = event.value
                if event.code == ecodes.ABS_Y:
                    with lock:
                        joystick_positions['LEFT_Y'] = value
                        left_speed = 0 if 126 <= value <= 130 else max(
                            0, min(127, 128 - value))

                    print(f"Joystick Y: {value}")  # Debugging feedback

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay

# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    # Start joystick polling thread
    joystick_thread = threading.Thread(
        target=poll_joystick, daemon=True, args=(controller,))
    joystick_thread.start()

    # Start motor command streaming thread
    motor_thread = threading.Thread(target=send_motor_command, daemon=True)
    motor_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)
        print("\nExiting...")


main()

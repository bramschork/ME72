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

# Shared variable for joystick position
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0  # Global variable for speed

# Locate the PS4 controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to send motor commands in a side thread


def send_motor_command():
    global left_speed
    last_speed = -1  # Track last sent speed
    last_update_time = time.time()  # Track last update time

    while True:
        acquired = lock.acquire(blocking=False)
        if acquired:
            try:
                if not roboclaw._port:  # Check if serial port is open
                    # print("Error: Serial connection to Roboclaw is not open")
                    roboclaw.Open()  # Attempt to reopen the connection

                speed_to_send = left_speed  # Read speed inside the lock

                # Send command if speed has changed OR if no update for 0.2 seconds
                if speed_to_send != last_speed or (time.time() - last_update_time > 0.2):
                    roboclaw.ForwardM1(address, speed_to_send)
                    # print(f"Sent Speed to Roboclaw: {speed_to_send}")
                    last_speed = speed_to_send  # Update last sent speed
                    last_update_time = time.time()  # Reset update time

            except Exception as e:
                print(e)
                # print(f"Error sending motor command: {e}")
            finally:
                lock.release()  # Release lock to avoid blocking joystick updates

        time.sleep(0.01)  # Ensures frequent updates

# Function to continuously read joystick positions


def poll_joystick(controller):
    global left_speed
    while True:
        try:
            event = controller.read_one()  # Use `read_one()` to avoid `BlockingIOError`
            if event is None:
                # Prevents looping when no input / changes on controller
                time.sleep(0.01)
                continue

            if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
                if event.code == ecodes.ABS_Y:
                    with lock:
                        joystick_positions['LEFT_Y'] = event.value
                        left_speed = max(
                            0, min(127, 128 - joystick_positions['LEFT_Y']))
                        # print(f"Joystick Y: {joystick_positions['LEFT_Y']}")

        except Exception as e:
            print(e)

# Main function


def main():
    controller = find_ps4_controller()
    controller.grab()
    # print(f"Connected to {controller.name} at {controller.path}")

    # Start joystick polling thread
    joystick_thread = threading.Thread(
        target=poll_joystick, daemon=True, args=(controller,))
    joystick_thread.start()

    # Start motor command thread
    motor_thread = threading.Thread(target=send_motor_command, daemon=True)
    motor_thread.start()

    try:
        while True:
            time.sleep(0.1)  # Keeps the main thread running
    except KeyboardInterrupt:
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)
        print("\nExiting...")


main()  # Runs once instead of restarting repeatedly

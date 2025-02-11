import evdev
from evdev import InputDevice, ecodes
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()
address = 0x80  # Roboclaw address

# Locate the PS4 Controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to execute when R2 is pulled


def trigger_pulled():
    print("Right Trigger (R2) Pulled!")

# Function to stop motors when D-pad Down is pressed


def stop_motors():
    print("D-Pad Down Pressed! Stopping motors...")
    roboclaw.ForwardM1(address, 0)  # Stop Motor 1
    roboclaw.ForwardM2(address, 0)  # Stop Motor 2

# Main loop to poll trigger and D-pad


def poll_controller():
    controller = find_ps4_controller()
    print(f"Connected to {controller.name} at {controller.path}")

    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_RZ:  # R2 Trigger
            if event.value > 10:  # Adjust threshold as needed
                trigger_pulled()

        elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_DPAD_DOWN:
            if event.value == 1:  # Button Pressed
                stop_motors()


# Run the script
poll_controller()

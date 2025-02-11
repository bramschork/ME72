from roboclaw_3 import Roboclaw
from gpiozero import Servo
from time import sleep
import evdev
from evdev import InputDevice, ecodes


address = 0x82  # 130 in hex

# controller_address_2 = 0x82  # 128 in hex
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

# Locate the PS4 Controller


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# Function to execute when R2 is pulled


def trigger_pulled():
    # Shooting
    roboclaw.BackwardM1(address, 10)
    roboclaw.BackwardM2(address, 10)
    sleep(1)
    servo.max()
    servo.min()

    # Back to intake
    roboclaw.ForwardM1(address, 10)
    roboclaw.ForwardM2(address, 10)

# Main loop to poll the trigger


def poll_trigger():
    controller = find_ps4_controller()
    print(f"Connected to {controller.name} at {controller.path}")

    for event in controller.read_loop():
        if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_RZ:  # R2 Trigger
            if event.value > 10:  # Adjust threshold as needed
                trigger_pulled()


# Set to intake
roboclaw.ForwardM1(address, 10)
roboclaw.ForwardM2(address, 10)
servo.min()  # Move to 0 degrees


while True:
    try:
        poll_trigger()
    except KeyboardInterrupt:
        print("\nExiting...")
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)

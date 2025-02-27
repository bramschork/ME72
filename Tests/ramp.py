'''import time
from roboclaw_test import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/serial0", 38400)
roboclaw.Open()

address = 0x80  # Roboclaw address


def ramp_motor_speed():
    while True:
        try:
            # Ramp up from 0 to 127
            for speed in range(0, 128):
                roboclaw.ForwardM1(address, speed)
                print(f"Sent Speed to Roboclaw: {speed}")
                time.sleep(0.2)  # 5ms delay

            # Ramp down from 127 to 0
            for speed in range(127, -1, -1):
                roboclaw.ForwardM1(address, speed)
                print(f"Sent Speed to Roboclaw: {speed}")
                time.sleep(0.2)  # 5ms delay

        except KeyboardInterrupt:
            roboclaw.ForwardM1(address, 0)
            print("\nExiting...")
            break


ramp_motor_speed()
'''

import time
from roboclaw import Roboclaw

# Initialize Roboclaw using the new library.
roboclaw = Roboclaw("/dev/serial0", 38400)
if not roboclaw.Open():
    print("Failed to open Roboclaw")
    exit(1)

address = 0x80  # Roboclaw address (the library uses its internal address)


def ramp_motor_speed():
    try:
        while True:
            # Ramp up from 0 to 127
            for speed in range(0, 128):
                if not roboclaw.ForwardM1(address, speed):
                    print(f"Failed to send speed {speed} to Motor 1")
                else:
                    print(f"Sent Speed to Motor 1: {speed}")
                time.sleep(0.2)
            # Ramp down from 127 to 0
            for speed in range(127, -1, -1):
                if not roboclaw.ForwardM1(address, speed):
                    print(f"Failed to send speed {speed} to Motor 1")
                else:
                    print(f"Sent Speed to Motor 1: {speed}")
                time.sleep(0.2)
    except KeyboardInterrupt:
        roboclaw.ForwardM1(address, 0)
        print("\nExiting...")


ramp_motor_speed()

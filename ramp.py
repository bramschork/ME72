import time
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/serial0", 38400)
roboclaw.Open()

address = 0x82  # Roboclaw address


def ramp_motor_speed():
    while True:
        try:
            # Ramp up from 0 to 127
            for speed in range(0, 128):
                roboclaw.ForwardM1(address, speed)
                roboclaw.ForwardM2(address, speed)
                print(f"Sent Speed to Roboclaw: {speed}")
                time.sleep(0.2)  # 5ms delay

            # Ramp down from 127 to 0
            for speed in range(127, -1, -1):
                roboclaw.ForwardM1(address, speed)
                roboclaw.ForwardM2(address, speed)
                print(f"Sent Speed to Roboclaw: {speed}")
                time.sleep(0.2)  # 5ms delay

        except KeyboardInterrupt:
            roboclaw.ForwardM1(address, 0)
            roboclaw.ForwardM2(address, 0)
            print("\nExiting...")
            break


ramp_motor_speed()

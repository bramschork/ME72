import time
from roboclaw_3 import Roboclaw

# Initialize Roboclaw
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

address = 0x80  # Roboclaw address


def ramp_motor_speed():
    response = roboclaw.ReadEeprom(address, 38400)
    print(response)


ramp_motor_speed()

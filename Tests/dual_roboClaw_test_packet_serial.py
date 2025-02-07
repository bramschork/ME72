from roboclaw_3 import Roboclaw
from time import sleep

# Addresses for the two Roboclaws
controller_address_1 = 0x80  # 128 in hex
controller_address_2 = 0x82  # 130 in hex

# Initialize both Roboclaws
roboclaw_1 = Roboclaw("/dev/ttyS0", 115200)
roboclaw_2 = Roboclaw("/dev/ttyS0", 115200)

# Open serial communication
roboclaw_1.Open()
roboclaw_2.Open()

# 5% power (127 * 0.05 ≈ 6)
power = 6

while True:
    # Roboclaw 1 - Motor 1
    roboclaw_1.ForwardM1(controller_address_1, power)
    sleep(2)
    roboclaw_1.ForwardM1(controller_address_1, 0)
    sleep(2)

    # Roboclaw 1 - Motor 2
    roboclaw_1.ForwardM2(controller_address_1, power)
    sleep(2)
    roboclaw_1.ForwardM2(controller_address_1, 0)
    sleep(2)

    # Roboclaw 2 - Motor 1
    roboclaw_2.ForwardM1(controller_address_2, power)
    sleep(2)
    roboclaw_2.ForwardM1(controller_address_2, 0)
    sleep(2)

    # Roboclaw 2 - Motor 2
    roboclaw_2.ForwardM2(controller_address_2, power)
    sleep(2)
    roboclaw_2.ForwardM2(controller_address_2, 0)
    sleep(2)

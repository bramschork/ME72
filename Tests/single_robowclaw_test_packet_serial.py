from roboclaw_3 import Roboclaw
from time import sleep

address = 0x80  # 128 in hex
# controller_address_2 = 0x82  # 128 in hex
roboclaw = Roboclaw("/dev/ttyS0", 115200)
roboclaw.Open()

while True:

    roboclaw.ForwardM1(address, 64)
    sleep(2)
    roboclaw.ForwardM1(address, 0)
    sleep(2)

    roboclaw.ForwardM2(address, 64)
    sleep(2)
    roboclaw.ForwardM2(address, 0)
    sleep(2)

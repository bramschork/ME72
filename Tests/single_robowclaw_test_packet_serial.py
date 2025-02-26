from roboclaw_3 import Roboclaw
from time import sleep
address = 0x82  # 128 in hex
# controller_address_2 = 0x82  # 128 in hex
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

while True:

    print('Start')
    roboclaw.ForwardM1(address, 64)
    sleep(2)
    roboclaw.ForwardM1(address, 0)
    sleep(2)

    roboclaw.ForwardM2(address, 64)
    sleep(2)
    roboclaw.ForwardM2(address, 0)
    sleep(2)

    error_status = roboclaw.ReadError(address)
    print(f"Error Status: {error_status}")

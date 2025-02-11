from roboclaw_3 import Roboclaw
from gpiozero import Servo
from time import sleep
address = 0x82  # 130 in hex

# controller_address_2 = 0x82  # 128 in hex
roboclaw = Roboclaw("/dev/ttyS0", 460800)
roboclaw.Open()

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

while True:
    try:
        servo.min()  # Move to 0 degrees
        roboclaw.ForwardM1(address, 20)
        roboclaw.ForwardM2(address, 20)
        sleep(1)

        servo.max()  # Move to 180 degre
        roboclaw.ForwardM1(address, 20)
        roboclaw.ForwardM2(address, 20)

        sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)

'''from gpiozero import Servo
from time import sleep

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

while True:
    # servo.min()  # Move to 0 degrees
    servo.value = -1
    sleep(1)
    # servo.max()  # Move to 180 degrees
    servo.value = 1
    sleep(1)
'''

from gpiozero import Servo
from time import sleep

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


def set_angle(angle):
    """
    Sets the servo to the specified angle (0-180).
    The conversion maps 0 degrees to -1 and 180 degrees to 1.
    """
    servo.value = (angle - 90) / 90


while True:
    set_angle(0)    # Move to 0 degrees
    sleep(1)
    set_angle(180)  # Move to 180 degrees
    sleep(1)

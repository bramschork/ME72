'''from gpiozero import Servo
from time import sleep

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

while True:
    servo.min()  # Move to 0 degrees
    sleep(1)
    servo.max()  # Move to 180 degrees
    sleep(1)
'''

from gpiozero import Servo
from time import sleep

servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

# Helper function to map angle (0-180) to servo.value (-1 to 1)


def angle_to_value(angle):
    return (angle / 180) * 2 - 1


while True:
    # Sweep from 0 to 180 degrees
    for angle in range(0, 181, 5):  # adjust step size for smoother or faster sweep
        servo.value = angle_to_value(angle)
        sleep(0.02)
    # Sweep back from 180 to 0 degrees
    for angle in range(180, -1, -5):
        servo.value = angle_to_value(angle)
        sleep(0.02)

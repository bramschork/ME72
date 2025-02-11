from gpiozero import Servo
from time import sleep

# Second up from bottom pins facing right
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

while True:
    servo.min()  # Move to 0 degrees
    sleep(1)
    servo.max()  # Move to 180 degrees
    sleep(1)

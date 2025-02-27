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

servo = Servo(25)
val = -1

try:
    while True:
        servo.value = val
        sleep(0.1)
        val = val + 0.1
        if val > 1:
            val = -1
except KeyboardInterrupt:
    print("Program stopped")

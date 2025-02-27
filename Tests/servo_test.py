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

import time
import RPi.GPIO as GPIO
''


# Use the physical pin numbering (BOARD) or BCM depending on your wiring.
# Here we assume BOARD mode since pin 12 refers to physical pin 12.
GPIO.setmode(GPIO.BOARD)

# Set up pin 12 for PWM output
servo_pin = 12
GPIO.setup(servo_pin, GPIO.OUT)

# Set up PWM on servo_pin at 50 Hz (common for servos)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)  # Start PWM with 0% duty cycle


def set_angle(angle):
    """
    Sets the servo to the specified angle.
    The duty cycle is computed to map 0° to ~2% and 180° to ~12%.
    Adjust these values if your servo requires different calibration.
    """
    duty = angle / 18.0 + 2
    pwm.ChangeDutyCycle(duty)
    # Allow time for the servo to move
    time.sleep(0.02)


try:
    while True:
        # Sweep from 0° to 180°
        for angle in range(0, 181, 5):
            set_angle(angle)
        # Sweep back from 180° to 0°
        for angle in range(180, -1, -5):
            set_angle(angle)
except KeyboardInterrupt:
    pass
finally:
    # Cleanup the GPIO settings
    pwm.stop()
    GPIO.cleanup()

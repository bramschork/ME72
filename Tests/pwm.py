import RPi.GPIO as GPIO
import time

# Pin configuration for Raspberry Pi Zero 2 W
MOTOR1_PIN = 12  # S1
MOTOR2_PIN = 13  # S2
PWM_FREQ = 50    # Frequency in Hz (20ms period)

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1_PIN, GPIO.OUT)
GPIO.setup(MOTOR2_PIN, GPIO.OUT)

# Initialize PWM on both pins
pwm_motor1 = GPIO.PWM(MOTOR1_PIN, PWM_FREQ)
pwm_motor2 = GPIO.PWM(MOTOR2_PIN, PWM_FREQ)

# Start PWM with a neutral duty cycle (for example, 7.5% might be neutral)
neutral_dc = 7.5
pwm_motor1.start(neutral_dc)
pwm_motor2.start(neutral_dc)

try:
    while True:
        # Ramp up the speed
        for dc in range(50, 101, 1):  # from 5.0% to 10.0% in 0.1% increments
            duty_cycle = dc / 10.0
            pwm_motor1.ChangeDutyCycle(duty_cycle)
            pwm_motor2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)  # small delay for smooth transition

        # Hold at max speed for a moment
        time.sleep(1)

        # Ramp down the speed
        for dc in range(100, 49, -1):  # from 10.0% back down to 5.0%
            duty_cycle = dc / 10.0
            pwm_motor1.ChangeDutyCycle(duty_cycle)
            pwm_motor2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)

        # Hold at min speed for a moment
        time.sleep(1)

except KeyboardInterrupt:
    # Stop PWM and clean up on CTRL+C
    pass

pwm_motor1.stop()
pwm_motor2.stop()
GPIO.cleanup()

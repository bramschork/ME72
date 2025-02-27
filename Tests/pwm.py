import RPi.GPIO as GPIO
import time

# Define the GPIO pins for RC control signals
# S1 controls Motor 1 and S2 controls Motor 2 in RC mode.
MOTOR1_PIN = 12  # connected to S1
MOTOR2_PIN = 13  # connected to S2
PWM_FREQ = 50    # 50 Hz is standard for servo pulses

# Setup the GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1_PIN, GPIO.OUT)
GPIO.setup(MOTOR2_PIN, GPIO.OUT)

# Initialize PWM channels on both pins
pwm_motor1 = GPIO.PWM(MOTOR1_PIN, PWM_FREQ)
pwm_motor2 = GPIO.PWM(MOTOR2_PIN, PWM_FREQ)

# In RC mode, a pulse width of about 1ms (5% duty cycle at 50Hz) corresponds to full reverse,
# 1.5ms (7.5% duty cycle) is neutral, and 2ms (10% duty cycle) is full forward.
neutral_dc = 7.5
pwm_motor1.start(neutral_dc)
pwm_motor2.start(neutral_dc)

try:
    while True:
        # Ramp from full reverse (5.0%) to full forward (10.0%)
        for dc in range(50, 101, 1):  # 5.0% to 10.0% duty cycle (in tenths)
            duty_cycle = dc / 10.0
            pwm_motor1.ChangeDutyCycle(duty_cycle)
            pwm_motor2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)  # smooth transition delay

        # Hold at full forward for a moment
        time.sleep(1)

        # Ramp back from full forward to full reverse
        for dc in range(100, 49, -1):
            duty_cycle = dc / 10.0
            pwm_motor1.ChangeDutyCycle(duty_cycle)
            pwm_motor2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)

        # Hold at full reverse for a moment
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up on exit
    pass

pwm_motor1.stop()
pwm_motor2.stop()
GPIO.cleanup()

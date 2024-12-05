#  Raspberry Pi Master for Arduino Slave
#  i2c_master_pi.py
#  Connects to Arduino via I2C

#  DroneBot Workshop 2019
#  https://dronebotworkshop.com

from smbus import SMBus
import pygame
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.joystick.init()

addr = 0x8  # bus address
bus = SMBus(1)  # indicates /dev/ic2-1

# Function to calculate joystick direction and magnitude


def get_joystick_direction(x, y):
    magnitude = math.sqrt(x**2 + y**2)
    direction = "Neutral"

    if magnitude > 0.2:  # Deadzone threshold
        if abs(x) > abs(y):
            if x > 0:
                direction = "Right"
            else:
                direction = "Left"
        else:
            if y > 0:
                direction = "Down"
            else:
                direction = "Up"

    return direction, round(magnitude, 2)


# Check for connected joysticks
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to: {joystick.get_name()}")

    # Display left joystick input
    print("Reading left joystick input. Use Ctrl+C to quit.")
    while True:
        pygame.event.pump()

        # Left joystick axes for PS4 controller
        x = joystick.get_axis(0)  # Horizontal axis
        y = joystick.get_axis(1)  # Vertical axis (inverted)

        # Get direction and magnitude
        direction, magnitude = get_joystick_direction(x, y)
        send_magnitude = magnitude*127
        byte = '0x' + str(send_magnitude)

        if direction == 'Up':
            bus.write_byte(addr, byte)  # switch it on

        print(f"Direction: {direction}, Magnitude: {magnitude}")
else:
    print("No joystick connected.")

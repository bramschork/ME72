# Caltech ME72 2024
# Wayne Botzky

from smbus import SMBus
import pygame
import math
from pygame.locals import *
import time
pygame.init()  # Initialize Pygame
pygame.joystick.init()

addr = 0x8  # bus address
bus = SMBus(1)  # indicates /dev/ic2-1

# Function to calculate joystick direction and magnitude


while True:
    left_stick = pygame.joystick.Joystick(0)
    left_stick.init()

    right_stick = pygame.joystick.Joystick(1)
    right_stick.init()

    print(f"Connected to: {left_stick.get_name()}")
    pygame.event.pump()

    # Left joystick axes for PS4 controller
    x = left_stick.get_axis(0)  # Horizontal axis
    left_y = left_stick.get_axis(1)  # Vertical axis (inverted)
    right_y = right_stick.get_axis(1)  # Vertical axis (inverted)

    left_direction = "Neutral"
    if left_y > 0.2:  # Deadzone threshold
        if left_y > 0:
            bus.write_byte(addr, 0x7F)
        else:
            bus.write_byte(addr, 0x7F)
    else:
        bus.write_byte(addr, 0x0)

    right_direction = "Neutral"
    if right_y > 0.2:  # Deadzone threshold
        if right_y > 0:
            bus.write_byte(addr, 0x7F)
        else:
            bus.write_byte(addr, 0x7F)
    else:
        bus.write_byte(addr, 0x0)

    time.sleep(0.1)

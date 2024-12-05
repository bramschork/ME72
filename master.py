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
# print('PS4 Controller Battery: {0}%'.format(
#    pygame.joystick.Joystick.get_power_level))

while True:
    left_stick = pygame.joystick.Joystick(0)
    left_stick.init()

    right_stick = pygame.joystick.Joystick(0)
    right_stick.init()

    # print(f"Connected to: {left_stick.get_name()}")
    pygame.event.pump()

    # Left joystick axes for PS4 controller
    left_y = left_stick.get_axis(1)  # Vertical axis (inverted)
    right_y = right_stick.get_axis(3)  # Vertical axis (inverted)

    # MODIFIER to slow down the motors
    modifier = (round(.5 * 127 * left_y))

    if left_y > 0.2:  # Reverse
        bus.write_byte(addr, modifier+1000)
    elif left_y < 0.2:  # Forward
        bus.write_byte(addr, modifier)

    if right_y > 0.2:  # Reverse
        bus.write_byte(addr, modifier+3000)
    elif right_y < 0.2:  # Forward
        bus.write_byte(addr, modifier+2000)

    time.sleep(0.1)

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

    # right_stick = pygame.joystick.Joystick(1)
    # right_stick.init()

    # print(f"Connected to: {left_stick.get_name()}")
    pygame.event.pump()

    # Left joystick axes for PS4 controller
    left_y = left_stick.get_axis(1)  # Vertical axis (inverted)
    # right_y = right_stick.get_axis(1)  # Vertical axis (inverted)

    # MODIFIER to slow down the motors
    modifier = 1 * 127

    '''if abs(left_y > 0.2):  # Deadzone threshold
        if left_y > 0:  # Reverse
            bus.write_byte(addr, hex(1000+int(left_y)*modifier))
        else:  # Forward
            bus.write_byte(addr, hex(int(left_y)*modifier))
            print(hex(int(left_y)*modifier))'''
    print(type(left_y))
    bus.write_byte(addr, hex(left_y))
    print(hex(left_y))
    # else:
    #    bus.write_byte(addr, 0x0)

    time.sleep(0.1)

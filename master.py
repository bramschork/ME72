# THIS VERSION WORKS
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
    if pygame.joystick.get_count() > 0:
        left_stick = pygame.joystick.Joystick(0)
        left_stick.init()

        right_stick = pygame.joystick.Joystick(0)
        right_stick.init()

        # print(f"Connected to: {left_stick.get_name()}")
        pygame.event.pump()

        # Left joystick axes for PS4 controller
        left_y = -left_stick.get_axis(1)  # Vertical axis (inverted)
        right_y = right_stick.get_axis(3)  # Vertical axis (inverted)

    i = 0
    if i == 0:
        # LEFT MOTOR / MOTOR ONE
        if left_y > 0.2:   # Motor One Forward
            bus.write_byte(addr, 0x1)
            time.sleep(0.1)
            print('ONE FORWARD')
        elif left_y < -0.2:   # Motor One Reverse
            bus.write_byte(addr, 0x2)
            time.sleep(0.1)
            print('ONE REVERSE')
        else:  # Motor One Neutral
            bus.write_byte(addr, 0x0)
            time.sleep(0.1)
            print('ONE ZERO')
        i = 1

    else:
        # RIGHT MOTOR / MOTOR TWO
        if right_y > 0.2:   # Motor One Forward
            bus.write_byte(addr, 0xC)
            time.sleep(0.1)
            print('TWO FORWARD')
        elif right_y < -0.2:   # Motor One Reverse
            bus.write_byte(addr, 0xD)
            time.sleep(0.1)
            print('TWO REVERSE')
        else:  # Motor One Neutral
            bus.write_byte(addr, 0xB)
            time.sleep(0.1)
            print('TWO ZERO')
    i = 0

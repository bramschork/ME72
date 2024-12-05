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

        if left_y < 0.2:
            L_modifier = 0
        elif left_y >= 0.2 and left_y < 0.5:
            L_modifier = 32
        else:
            L_modifier = 64

        if right_y < 0.2:
            R_modifier = 0
        elif right_y >= 0.2 and right_y < 0.5:
            R_modifier = 32
        else:
            R_modifier = 64

        ''' # print(f'Modifier: {modifier} Left_y: {left_y}')
        if left_y > 0.2:   # Forward
            bus.write_byte(addr, L_modifier)
            print(L_modifier)
        else:
            bus.write_byte(addr, 0)
            print('L0')'''

        if right_y > 0.2:   # Forward
            bus.write_byte(addr, 0x14)
            time.sleep(0.2)
            print(R_modifier)
        else:
            bus.write_byte(addr, 0x3E8)
            time.sleep(0.2)
            print('R0')

    else:
        print("No joystick connected.")


import pygame
import math
import time
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.joystick.init()

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

        zero = joystick.get_axis(4)  # Vertical axis (inverted)
        print(zero)
        time.sleep(0.1)

        # Get direction and magnitude
        # direction, magnitude = get_joystick_direction(x, y)

        # print(f"Direction: {direction}, Magnitude: {magnitude}")

else:
    print("No joystick connected.")

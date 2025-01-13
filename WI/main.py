import pygame
import serial
import time
from roboclaw_3 import Roboclaw

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Function to find and initialize the PS4 controller


def initialize_ps4_controller():
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        raise RuntimeError(
            "No joystick detected. Ensure the PS4 controller is connected via Bluetooth.")
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Connected to controller: {controller.get_name()}")
    return controller


# Initialize the PS4 controller
controller = initialize_ps4_controller()

# Initialize RoboClaw
roboclaw = Roboclaw('/dev/ttyS0', 115200)  # Adjust the serial port as needed
roboclaw.Open()
address = 0x80  # Replace with your RoboClaw address

# Function to map joystick input (-1 to 1) to motor speed (0 to 127)


def joystick_to_speed(value):
    return int((value + 1) * 63.5)  # Maps -1 to 1 range to 0 to 127


# Main loop
try:
    print("Press Ctrl+C to exit.")
    while True:
        # Process Pygame events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Read joystick positions
                left_y = controller.get_axis(1)  # Left joystick vertical axis
                # Right joystick vertical axis
                right_y = controller.get_axis(4)

                # Print joystick values
                print(
                    f"Left joystick Y-axis: {left_y:.2f}, Right joystick Y-axis: {right_y:.2f}")

                # Convert joystick positions to motor speeds
                # Invert axis if necessary
                speed_m1 = joystick_to_speed(-left_y)
                # Invert axis if necessary
                speed_m2 = joystick_to_speed(-right_y)

                # Send commands to RoboClaw
                roboclaw.ForwardM1(address, speed_m1)
                roboclaw.ForwardM2(address, speed_m2)

        # Delay to prevent excessive CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    # Stop motors and clean up
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)
    pygame.joystick.quit()
    pygame.quit()

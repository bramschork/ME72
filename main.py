import pygame
import time
from roboclaw import Roboclaw

# Initialize RoboClaw (adjust '/dev/ttyS0' and baud rate as needed)
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Motor addresses (ensure this is an integer)
ADDRESS = 0x80

# Initialize Pygame for the PS4 controller
pygame.init()
pygame.joystick.init()


def map_value(x, in_min, in_max, out_min, out_max):
    """Map joystick values to motor speed range."""
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Main function


def main():
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Connected to controller: {joystick.get_name()}")

        while True:
            pygame.event.pump()

            left_UD_stick_y = -joystick.get_axis(1)

            # Map joystick input (-1 to 1) to motor speed (-127 to 127)
            motor1_speed = map_value(left_UD_stick_y, -1, 1, -127, 127)

            # Send commands to RoboClaw
            roboclaw.SpeedM1(ADDRESS, motor1_speed)

            print(f"Motor1: {motor1_speed}")

            time.sleep(0.1)  # Small delay for smoother control

    except KeyboardInterrupt:
        print("\nExiting program.")
        roboclaw.SpeedM1(ADDRESS, 0)
        roboclaw.SpeedM2(ADDRESS, 0)
        pygame.quit()


if __name__ == "__main__":
    main()

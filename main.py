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

            # Get the Y-axis value of the left joystick
            left_UD_stick_y = -joystick.get_axis(1)

            if left_UD_stick_y > 0.5:  # Joystick is pushed upward
                roboclaw.ForwardM1(ADDRESS, 64)
                print("Joystick up: Sending ForwardM1 with speed 64")
            else:  # Joystick not pushed upward
                roboclaw.ForwardM1(ADDRESS, 0)
                print("Joystick not up: Sending ForwardM1 with speed 0")

            time.sleep(0.1)  # Small delay for smoother control

    except KeyboardInterrupt:
        print("\nExiting program.")
        roboclaw.ForwardM1(ADDRESS, 0)
        roboclaw.ForwardM2(ADDRESS, 0)
        pygame.quit()


if __name__ == "__main__":
    main()

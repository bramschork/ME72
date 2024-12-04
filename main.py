import pygame
import time
from roboclaw import Roboclaw

# Initialize RoboClaw (adjust '/dev/ttyS0' and baud rate as needed)
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Motor address (set this to match the Packet Serial address in RoboClaw)
ADDRESS = 0x80

# Initialize Pygame for the PS4 controller
pygame.init()
pygame.joystick.init()


def initialize_controller():
    """Initialize the PS4 controller."""
    if pygame.joystick.get_count() < 1:
        raise ValueError("No joystick connected")
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to controller: {joystick.get_name()}")
    return joystick


def map_value(x, in_min, in_max, out_min, out_max):
    """Map joystick values to motor speed range."""
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def main():
    try:
        joystick = initialize_controller()

        while True:
            # Poll events to update the controller state
            pygame.event.pump()

            # Get the Y-axis value of the left joystick (-1 is up, 1 is down)
            left_UD_stick_y = -joystick.get_axis(1)

            if left_UD_stick_y > 0.5:  # Joystick is pushed upward
                # Move motor forward at speed 64
                roboclaw.ForwardM1(ADDRESS, 64)
                print("Joystick up: Sending ForwardM1 with speed 64")
            else:  # Joystick is not pushed upward
                roboclaw.ForwardM1(ADDRESS, 0)  # Stop the motor
                print("Joystick not up: Sending ForwardM1 with speed 0")

            # Small delay for smoother control
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting program.")
        # Stop motors when exiting
        roboclaw.ForwardM1(ADDRESS, 0)
        roboclaw.ForwardM2(ADDRESS, 0)
        pygame.quit()
    except ValueError as e:
        print(f"Error: {e}")
        pygame.quit()


if __name__ == "__main__":
    main()

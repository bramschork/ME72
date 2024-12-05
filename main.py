
# this is a comment
#testing change 
import pygame
import time
from roboclaw_3 import Roboclaw

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


def main():
    try:
        joystick = initialize_controller()

        running = True
        while running:
            # Pump events to update the state of the controller
            pygame.event.pump()

            # Check joystick position
            left_UD_stick_y = -joystick.get_axis(1)

            if left_UD_stick_y > 0.5:  # Joystick is pushed upward
                roboclaw.ForwardM1(ADDRESS, 64)  # Move motor forward
                print("Motor Forward")
            else:  # Joystick not pushed upward
                roboclaw.ForwardM1(ADDRESS, 0)  # Stop the motor
                print("Motor Stopped")

            # Wait for 0.1 seconds before checking again
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting program.")
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        # Stop motors when exiting
        roboclaw.ForwardM1(ADDRESS, 0)
        pygame.quit()


if __name__ == "__main__":
    main()

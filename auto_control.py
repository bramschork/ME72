import pygame
import time
from roboclaw_3 import Roboclaw

# Initialize RoboClaw (adjust '/dev/ttyS0' and baud rate as needed)
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Motor address (set this to match the Packet Serial address in RoboClaw)
ADDRESS = 0x80


def main():
    try:

        running = True
        while running:
            # Pump events to update the state of the controller
            pygame.event.pump()

            print('Forward')
            roboclaw.ForwardM1(ADDRESS, 64)  # Move motor forward
            time.sleep(2)
            print('Stop')
            roboclaw.ForwardM1(ADDRESS, 0)  # Stop the motor
            time.sleep(2)

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

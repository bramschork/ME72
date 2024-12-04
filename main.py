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


def map_value(x, in_min, in_max, out_min, out_max):
    """Map joystick values to motor speed range."""
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def main():
    try:
        joystick = initialize_controller()

        running = True  # Use a flag to control the main loop
        while running:
            # Pump events to update the state of the controller
            pygame.event.pump()

            # Check if the joystick axis indicates upward movement
            left_UD_stick_y = -joystick.get_axis(1)

            if left_UD_stick_y > 0.5:  # Joystick is pushed upward
                # Move motor forward at speed 64
                roboclaw.ForwardM1(ADDRESS, 64)
                print("Joystick up: Sending ForwardM1 with speed 64")
            else:  # Joystick is not pushed upward
                roboclaw.ForwardM1(ADDRESS, 0)  # Stop the motor
                print("Joystick not up: Sending ForwardM1 with speed 0")

            # Replace sleep with a very short delay to reduce CPU usage
            time.sleep(0.01)  # 10ms delay for smoother operation

    except KeyboardInterrupt:
        print("\nExiting program.")
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        # Stop motors when exiting
        roboclaw.ForwardM1(ADDRESS, 0)
        roboclaw.ForwardM2(ADDRESS, 0)
        pygame.quit()


if __name__ == "__main__":
    main()

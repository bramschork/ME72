import time
from roboclaw_3 import Roboclaw
from inputs import devices, get_gamepad

# Initialize RoboClaw (adjust '/dev/ttyS0' and baud rate as needed)
roboclaw = Roboclaw("/dev/ttyS0", 38400)
roboclaw.Open()

# Motor address (set this to match the Packet Serial address in RoboClaw)
ADDRESS = 0x80


def get_joystick_input():
    """
    Fetch the latest gamepad inputs and return the Y-axis value of the left joystick.
    """
    left_UD_stick_y = 0  # Default neutral value for joystick

    events = get_gamepad()
    for event in events:
        if event.code == "ABS_Y":  # 'ABS_Y' corresponds to the Y-axis of the left joystick
            left_UD_stick_y = event.state / 32768.0  # Normalize to range [-1, 1]
    
    return -left_UD_stick_y  # Invert Y-axis for natural forward/backward control


def main():
    try:
        print("Searching for connected gamepads...")
        if not devices.gamepads:
            raise ValueError("No gamepad detected. Please connect a PS4 controller.")

        print("Gamepad connected. Starting motor control...")
        while True:
            # Fetch joystick Y-axis position
            left_UD_stick_y = get_joystick_input()

            # Forward movement
            if left_UD_stick_y > 0.5:  # Joystick pushed forward
                roboclaw.ForwardM1(ADDRESS, 64)  # Adjust speed as needed
                print("Motor Forward")
            
            # Reverse movement
            elif left_UD_stick_y < -0.5:  # Joystick pulled backward
                roboclaw.BackwardM1(ADDRESS, 64)  # Adjust speed as needed
                print("Motor Backward")
            
            # Stop motor if joystick is in neutral zone
            else:
                roboclaw.ForwardM1(ADDRESS, 0)
                print("Motor Stopped")

            # Minimize delay for smoother control
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting program.")
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        # Stop the motor on exit
        roboclaw.ForwardM1(ADDRESS, 0)
        print("Motor Stopped.")
        roboclaw.Close()


if __name__ == "__main__":
    main()
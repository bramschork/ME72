import time
from roboclaw import Roboclaw

# Initialize RoboClaw
# Adjust the port and baudrate as needed
roboclaw = Roboclaw("/dev/ttyS0", 38400)


def main():
    address = 0x80  # Default address; adjust if necessary
    roboclaw.Open()

    try:
        while True:
            # Move Motor 1 forward at half speed
            roboclaw.ForwardM1(address, 64)
            time.sleep(2)

            # Stop Motor 1
            roboclaw.ForwardM1(address, 0)
            time.sleep(2)

            # Move Motor 2 forward at half speed
            roboclaw.ForwardM2(address, 64)
            time.sleep(2)

            # Stop Motor 2
            roboclaw.ForwardM2(address, 0)
            time.sleep(2)

    except KeyboardInterrupt:
        # Ensure motors are stopped on exit
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)
        print("Motors stopped. Exiting...")


if __name__ == "__main__":
    main()

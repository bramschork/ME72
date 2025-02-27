import time
from roboclaw import Roboclaw

# Serial Configuration
serial_port = "/dev/serial0"  # Use /dev/serial0 for Raspberry Pi
baudrate = 38400              # Match this with the RoboClaw baud rate
address = 0x80                # Default RoboClaw address

# Initialize RoboClaw Object
roboclaw = Roboclaw(serial_port, baudrate)

# Open Serial Connection
if roboclaw.Open():
    print("Connected to RoboClaw.")
else:
    print("Failed to connect to RoboClaw.")
    exit()


def cycle_motors_and_check_ack():
    print("Cycling Motors to 50% Duty Cycle...")

    # 50% Duty Cycle is 64 for Packet Serial Mode
    duty_cycle = 64

    # Forward M1 and M2 at 50% power
    ack_m1 = roboclaw.ForwardM1(address, duty_cycle)
    ack_m2 = roboclaw.ForwardM2(address, duty_cycle)

    # Check Acknowledgment
    if ack_m1 and ack_m2:
        print("Acknowledgment received for both motors.")
    else:
        print("No acknowledgment received. Checking error status...")

    # Read Error Status
    error_status = roboclaw.ReadError(address)
    print(f"Error Status: {error_status}")

    # Wait for 2 seconds
    time.sleep(2)

    # Stop Motors
    print("Stopping Motors...")
    roboclaw.ForwardM1(address, 0)
    roboclaw.ForwardM2(address, 0)


if __name__ == "__main__":
    cycle_motors_and_check_ack()
    roboclaw._port.close()

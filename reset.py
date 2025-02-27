from serial import Serial
from time import sleep

# RoboClaw Address (default is 0x80)
shooter_address = 0x80

# Serial Configuration
serial_port = "/dev/ttyS0"  # Adjust this to your correct serial port
baudrate = 38400  # Match this with the RoboClaw baud rate

# Initialize Serial Connection
roboclaw = Serial(serial_port, baudrate, timeout=1)


def reset_roboclaw():
    # Construct the reset packet
    packet = [shooter_address, 21]  # 21 = Reset Command
    checksum = shooter_address ^ 21
    packet.append(checksum)

    # Send the packet
    roboclaw.write(bytes(packet))
    print("Reset command sent to RoboClaw.")

    # Allow time for the RoboClaw to reset
    sleep(2)
    print("RoboClaw should be rebooting now.")


if __name__ == "__main__":
    print("Sending reset command to RoboClaw...")
    reset_roboclaw()

    # Close the serial connection
    roboclaw.close()

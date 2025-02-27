import serial
from time import sleep

# Configuration
serial_port = "/dev/serial0"  # Use /dev/serial0 for Raspberry Pi
baudrate = 38400              # Match this with the RoboClaw baud rate
address = 0x80                # Default RoboClaw address

# Initialize Serial Connection
roboclaw = serial.Serial(serial_port, baudrate, timeout=1)

# Function to send a packet and read response


def send_packet(address, command):
    # Construct the packet
    packet = [address, command]
    # Calculate checksum
    checksum = address ^ command
    packet.append(checksum)

    # Send the packet
    roboclaw.write(bytes(packet))
    sleep(0.1)  # Short delay for processing

    # Read response (32 bytes max)
    response = roboclaw.read(32)
    return response

# Function to request firmware version


def get_firmware_version():
    print("Requesting Firmware Version...")
    response = send_packet(address, 21)  # 21 = Get Version Command

    if response:
        # Decode the version string
        version = response.split(b'\r')[0].decode('ascii')
        print(f"Firmware Version: {version}")
    else:
        print("No response. Check wiring and baud rate.")

# Function to read and interpret error status


def get_error_status():
    print("Reading Error Status...")
    response = send_packet(address, 0x90)  # 0x90 = Read Error Status

    if len(response) >= 3:
        # Parse response
        error_status = (response[0] << 8) | response[1]
        received_checksum = response[2]
        calculated_checksum = address ^ 0x90 ^ response[0] ^ response[1]

        # Verify checksum
        if received_checksum == calculated_checksum:
            print(f"Error Status: 0x{error_status:04X}")
            interpret_error_status(error_status)
        else:
            print("Checksum mismatch. Communication error.")
    else:
        print("No response from RoboClaw.")

# Function to interpret and print error codes


def interpret_error_status(error_status):
    # Dictionary of error codes from RoboClaw manual
    error_codes = {
        0x0001: "E-Stop",
        0x0002: "Temperature Error",
        0x0004: "Temperature Warning",
        0x0008: "Main Battery High",
        0x0010: "Main Battery Low",
        0x0020: "Logic Battery High",
        0x0040: "Logic Battery Low",
        0x0080: "M1 Over Current",
        0x0100: "M2 Over Current"
    }

    if error_status == 0:
        print("No errors detected.")
    else:
        for code, description in error_codes.items():
            if error_status & code:
                print(f" - {description}")


# Main function
if __name__ == "__main__":
    print("Communicating with RoboClaw...")

    # Get firmware version
    get_firmware_version()

    # Read and print error status
    get_error_status()

    # Close the serial connection
    roboclaw.close()

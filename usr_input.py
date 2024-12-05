import serial
import time

# Initialize serial connection
ser = serial.Serial(
    port='/dev/ttyS0',  # Replace with the correct serial port for your Raspberry Pi
    baudrate=38400,        # Baudrate set in your motor controller
    timeout=1
)


def send_command(value):
    """
    Sends a single-byte command to the motor controller.
    :param value: Integer (0-255)
    """
    if 0 <= value <= 255:
        ser.write(bytes([value]))
        print(f"Sent command: {value}")
    else:
        print("Invalid value! Enter a number between 0 and 255.")


def main():
    print("Motor Control Program")
    print("Commands:")
    print("0 - Shutdown both motors")
    print("1 - Channel 1 full reverse")
    print("64 - Channel 1 stop")
    print("127 - Channel 1 full forward")
    print("128 - Channel 2 full reverse")
    print("192 - Channel 2 stop")
    print("255 - Channel 2 full forward")
    print("Enter a number between 0 and 255 to control the motors.")

    try:
        while True:
            user_input = input("Enter command: ")
            if user_input.lower() == 'exit':
                print("Exiting program.")
                break
            try:
                command = int(user_input)
                send_command(command)
            except ValueError:
                print("Invalid input! Please enter a number between 0 and 255.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        ser.close()
        print("Serial connection closed.")


if __name__ == "__main__":
    main()

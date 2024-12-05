import serial
import time

# Initialize serial connection
ser = serial.Serial(
    port='/dev/serial0',  # Replace with the correct serial port
    baudrate=9600,        # Ensure the baudrate matches your motor controller
    timeout=1
)


def send_command(value):
    """
    Sends a single-byte command to the motor controller.
    :param value: Integer (0 or 1)
    """
    if value == 0:
        ser.write(bytes([64]))  # 64 = Stop channel 1
        ser.flush()
        print("Motor off.")
    elif value == 1:
        # 73 = ~10% forward for channel 1 (approximation, controller dependent)
        ser.write(bytes([73]))
        ser.flush()
        print("Motor set to 10% power.")
    else:
        print("Invalid command. Enter 0 (off) or 1 (10% power).")


def main():
    print("Motor Control Program")
    print("Commands:")
    print("0 - Turn motor off")
    print("1 - Turn motor on at 10% power")
    print("Type 'exit' to quit.")

    try:
        while True:
            user_input = input("Enter command (0 or 1): ")
            if user_input.lower() == 'exit':
                print("Exiting program.")
                break
            try:
                command = int(user_input)
                send_command(command)
            except ValueError:
                print("Invalid input! Please enter 0 or 1.")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        ser.close()
        print("Serial connection closed.")


if __name__ == "__main__":
    main()

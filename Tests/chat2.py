import serial
import evdev
from evdev import InputDevice, ecodes
import time
import threading
from math import ceil
import atexit


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def writeS2(ser, address, cmd, value, retries=3):
    # This function sends a command with a 16-bit value (using a “writesword” style command)
    for _ in range(retries):
        ser.reset_input_buffer()
        crc = 0
        # Send address
        ser.write(address.to_bytes(1, 'big'))
        crc = crc_update(crc, address)
        # Send command
        ser.write(cmd.to_bytes(1, 'big'))
        crc = crc_update(crc, cmd)
        # Send value as a 2-byte word (big-endian)
        high = (value >> 8) & 0xFF
        low = value & 0xFF
        ser.write(high.to_bytes(1, 'big'))
        crc = crc_update(crc, high)
        ser.write(low.to_bytes(1, 'big'))
        crc = crc_update(crc, low)
        # Send the calculated checksum (2 bytes)
        ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
        ser.write((crc & 0xFF).to_bytes(1, 'big'))
        # Read one acknowledgment byte; nonzero indicates success.
        ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def stop_motors():
    print("\nStopping motors...")
    roboclaw.ForwardM1(address, 0)  # Force Stop Right Motor (M1)
    roboclaw.ForwardM2(address, 0)  # Force Stop Left Motor (M2)
    roboclaw.BackwardM1(address, 0)  # Ensure No Reverse Movement
    roboclaw.BackwardM2(address, 0)  # Ensure No Reverse Movement
    roboclaw.SpeedM1(address, 0)  # Final Check
    roboclaw.SpeedM2(address, 0)  # Final Check


# Register the stop_motors function to run on exit
atexit.register(stop_motors)


def find_ps4_controller():
    for path in evdev.list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


def set_motor_duty(ser, address, motor, duty):
    # For RoboClaw, motor 1 duty command is 32 and motor 2 duty command is 33.
    if motor == 1:
        cmd = 32
    elif motor == 2:
        cmd = 33
    else:
        raise ValueError("Motor must be 1 or 2")
    return writeS2(ser, address, cmd, duty)


def poll_joystick(controller):
    global left_speed, right_speed
    while True:
        try:
            event = controller.read_one()
            if event is None:
                time.sleep(0.002)  # Reduced sleep to improve polling speed
                continue

            if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
                value = event.value
                if event.code == ecodes.ABS_Y:  # Left joystick
                    with lock:
                        joystick_positions['LEFT_Y'] = value
                        left_speed = value  # Directly store joystick value
                    print(f"Joystick Left Y: {value}")

                elif event.code == ecodes.ABS_RY:  # Right joystick
                    with lock:
                        joystick_positions['RIGHT_Y'] = value
                        right_speed = value  # Directly store joystick value
                    print(f"Joystick Right Y: {value}")
                error_status = roboclaw.ReadError(address)
                print(f"Error Status: {error_status}")

        except BlockingIOError:
            time.sleep(0.002)  # Minimize blocking delay


def main():
    port = '/dev/serial0'   # Use /dev/serial0 as requested.
    baudrate = 38400
    address = 0x80          # Default RoboClaw address.

    LOWER_DEAD_ZONE = 136
    UPPER_DEAD_ZONE = 120

    # Joystick axis mappings
    AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

    # Shared variables for joystick position
    joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
    lock = threading.Lock()
    left_speed = 0  # Motor 1 speed
    right_speed = 0  # Motor 2 speed

    # Locate the PS4 controller

    # Function to continuously send motor commands

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return

    # Allow port to settle
    time.sleep(0.1)

    try:
        with lock:
            speed_L = left_speed
            speed_R = right_speed

        print('Speed L:')
        print(speed_L)
        if not set_motor_duty(ser, address, 1, 128-speed_L):
            print("Failed to set Motor 1 duty")

    except Exception as e:
        print(f"Error sending motor command: {e}")

    ser.close()


if __name__ == '__main__':
    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    # roboclaw.SetM1DefaultAccel(address, 8)  # Smooth acceleration for M1
    # roboclaw.SetM2DefaultAccel(address, 8)  # Smooth acceleration for M2

    # Start joystick polling thread
    joystick_thread = threading.Thread(
        target=poll_joystick, daemon=True, args=(controller,))
    joystick_thread.start()

 # Start motor command streaming thread
    motor_thread = threading.Thread(target=send_motor_command, daemon=True)
    motor_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_motors()  # Ensure motors stop before exiting

    main()

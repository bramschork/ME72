import serial
import time
import evdev
from evdev import InputDevice, ecodes, list_devices
import threading
import atexit
from math import ceil

# Global lock for serial port access
serial_lock = threading.Lock()

###############################
# Minimal RoboClaw Protocol Functions
###############################


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def write1(ser, address, cmd, value, retries=3):
    """Send a command with a single byte argument."""
    for _ in range(retries):
        with serial_lock:
            ser.reset_input_buffer()
            crc = 0
            ser.write(address.to_bytes(1, 'big'))
            crc = crc_update(crc, address)
            ser.write(cmd.to_bytes(1, 'big'))
            crc = crc_update(crc, cmd)
            ser.write(value.to_bytes(1, 'big'))
            crc = crc_update(crc, value)
            ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            ser.write((crc & 0xFF).to_bytes(1, 'big'))
            ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def writeS2(ser, address, cmd, value, retries=3):
    """Send a command with a 2-byte (word) argument."""
    for _ in range(retries):
        with serial_lock:
            ser.reset_input_buffer()
            crc = 0
            ser.write(address.to_bytes(1, 'big'))
            crc = crc_update(crc, address)
            ser.write(cmd.to_bytes(1, 'big'))
            crc = crc_update(crc, cmd)
            high = (value >> 8) & 0xFF
            low = value & 0xFF
            ser.write(high.to_bytes(1, 'big'))
            crc = crc_update(crc, high)
            ser.write(low.to_bytes(1, 'big'))
            crc = crc_update(crc, low)
            ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            ser.write((crc & 0xFF).to_bytes(1, 'big'))
            ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def write4(ser, address, cmd, value, retries=3):
    """Send a command with a 4-byte argument."""
    for _ in range(retries):
        with serial_lock:
            ser.reset_input_buffer()
            crc = 0
            ser.write(address.to_bytes(1, 'big'))
            crc = crc_update(crc, address)
            ser.write(cmd.to_bytes(1, 'big'))
            crc = crc_update(crc, cmd)
            b = value.to_bytes(4, 'big', signed=False)
            for byte in b:
                ser.write(byte.to_bytes(1, 'big'))
                crc = crc_update(crc, byte)
            ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            ser.write((crc & 0xFF).to_bytes(1, 'big'))
            ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def read4(ser, address, cmd, retries=3):
    """Send a command (with no extra args) and read a 4-byte signed value."""
    for _ in range(retries):
        with serial_lock:
            ser.reset_input_buffer()
            crc = 0
            ser.write(address.to_bytes(1, 'big'))
            crc = crc_update(crc, address)
            ser.write(cmd.to_bytes(1, 'big'))
            crc = crc_update(crc, cmd)
            data = ser.read(4)
            if len(data) != 4:
                continue
            for byte in data:
                crc = crc_update(crc, byte)
            checksum = ser.read(2)
            if len(checksum) != 2:
                continue
        received_crc = (checksum[0] << 8) | checksum[1]
        if crc == received_crc:
            return int.from_bytes(data, 'big', signed=True)
        time.sleep(0.01)
    return None

# Command functions (using RoboClaw command codes)


def forwardM1(ser, address, value):
    return write1(ser, address, 0, value)


def backwardM1(ser, address, value):
    return write1(ser, address, 1, value)


def forwardM2(ser, address, value):
    return write1(ser, address, 4, value)


def backwardM2(ser, address, value):
    return write1(ser, address, 5, value)


def speedM1(ser, address, value):
    return write1(ser, address, 35, value)


def speedM2(ser, address, value):
    return write1(ser, address, 36, value)


def setM1DefaultAccel(ser, address, accel):
    return write4(ser, address, 68, accel)


def setM2DefaultAccel(ser, address, accel):
    return write4(ser, address, 69, accel)


def readError(ser, address):
    # GETERROR command code is 90
    return read4(ser, address, 90)


def stop_motors(ser, address):
    print("\nStopping motors...")
    forwardM1(ser, address, 0)
    forwardM2(ser, address, 0)
    backwardM1(ser, address, 0)
    backwardM2(ser, address, 0)
    speedM1(ser, address, 0)
    speedM2(ser, address, 0)

###############################
# Joystick and Motor Control Code
###############################


# Dead zone settings (adjust as needed)
LOWER_DEAD_ZONE = 136
UPPER_DEAD_ZONE = 120

# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}
joystick_positions = {'LEFT_Y': 128, 'RIGHT_Y': 128}
lock = threading.Lock()
left_speed = 0   # Global variable for Motor 1 (LEFT_Y)
right_speed = 0  # Global variable for Motor 2 (RIGHT_Y)


def find_ps4_controller():
    for path in list_devices():
        device = InputDevice(path)
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


def poll_joystick(controller, ser, address):
    global left_speed, right_speed
    while True:
        event = controller.read_one()
        if event is None:
            time.sleep(0.002)
            continue
        if event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
            value = event.value
            if event.code == ecodes.ABS_Y:
                with lock:
                    joystick_positions['LEFT_Y'] = value
                    left_speed = value
                print(f"Joystick Left Y: {value}")
            elif event.code == ecodes.ABS_RY:
                with lock:
                    joystick_positions['RIGHT_Y'] = value
                    right_speed = value
                print(f"Joystick Right Y: {value}")
            # Read error status (wrapped with serial_lock inside readError)
            err = readError(ser, address)
            print(f"Error Status: {err}")


def send_motor_command(ser, address):
    global left_speed, right_speed
    last_left_speed = -1
    last_right_speed = -1
    while True:
        try:
            with lock:
                speed_L = left_speed
                speed_R = right_speed

            # Motor 1 control (LEFT joystick)
            if LOWER_DEAD_ZONE <= speed_L <= UPPER_DEAD_ZONE:
                forwardM1(ser, address, 0)
                if last_left_speed != 0:
                    print("Sent Stop Command to Motor 1")
                    last_left_speed = 0
            elif speed_L < 128:
                val = ceil((127 - speed_L) / 2)
                forwardM1(ser, address, val)
                if last_left_speed != speed_L:
                    print(f"Sent Reverse Speed to Motor 1: {val}")
                    last_left_speed = speed_L
            else:
                val = ceil((speed_L - 128) / 2)
                backwardM1(ser, address, val)
                if last_left_speed != speed_L:
                    print(f"Sent Forward Speed to Motor 1: {val}")
                    last_left_speed = speed_L

            # Motor 2 control (RIGHT joystick)
            if LOWER_DEAD_ZONE <= speed_R <= UPPER_DEAD_ZONE:
                forwardM2(ser, address, 0)
                if last_right_speed != 0:
                    print("Sent Stop Command to Motor 2")
                    last_right_speed = 0
            elif speed_R < 128:
                val = ceil((127 - speed_R) / 2)
                backwardM2(ser, address, val)
                if last_right_speed != speed_R:
                    print(f"Sent Forward Speed to Motor 2: {val}")
                    last_right_speed = speed_R
            else:
                val = ceil((speed_R - 128) / 2)
                forwardM2(ser, address, val)
                if last_right_speed != speed_R:
                    print(f"Sent Reverse Speed to Motor 2: {val}")
                    last_right_speed = speed_R

        except Exception as e:
            print(f"Error sending motor command: {e}")
        time.sleep(0.02)

###############################
# Main Function
###############################


def main():
    port = '/dev/serial0'
    baudrate = 38400
    address = 0x80
    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return

    time.sleep(0.1)
    setM1DefaultAccel(ser, address, 8)
    setM2DefaultAccel(ser, address, 8)
    forwardM1(ser, address, 0)
    forwardM2(ser, address, 0)
    print("Motors initialized to 0 speed")

    controller = find_ps4_controller()
    controller.grab()
    print(f"Connected to {controller.name} at {controller.path}")

    # Start threads for joystick polling and motor command sending
    joystick_thread = threading.Thread(
        target=poll_joystick, args=(controller, ser, address), daemon=True)
    joystick_thread.start()

    motor_thread = threading.Thread(
        target=send_motor_command, args=(ser, address), daemon=True)
    motor_thread.start()

    atexit.register(stop_motors, ser, address)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_motors(ser, address)


if __name__ == '__main__':
    main()

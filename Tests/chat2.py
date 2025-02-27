import serial
import time
import evdev
from evdev import InputDevice, ecodes

# --- Motor control functions (RoboClaw) ---


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def writeS2(ser, address, cmd, value, retries=3):
    # Sends a command with a 16-bit value (writesword style).
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


def set_motor_duty(ser, address, motor, duty):
    # For RoboClaw, motor 1 duty command is 32 and motor 2 is 33.
    if motor == 1:
        cmd = 32
    elif motor == 2:
        cmd = 33
    else:
        raise ValueError("Motor must be 1 or 2")
    return writeS2(ser, address, cmd, duty)

# --- PS4 Controller functions ---


def find_ps4_controller():
    devices = [InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:
            return device
    raise RuntimeError("PS4 controller not found! Ensure it's connected.")

# --- Mapping function ---


def map_joystick_to_duty(joy_value):
    """
    Maps a joystick value (0-256) to a motor duty value (0-127).
    Here a joystick value of 128 (neutral) maps to 0 (motor off).
    Only values above neutral produce a forward speed.
    """
    if joy_value <= 128:
        return 0
    # Map [128, 256] linearly to [0, 127]
    duty = int((joy_value - 128) * 127 / 128)
    # Clamp to valid range
    return max(0, min(duty, 127))

# --- Main loop combining controller and motor control ---


def main():
    # Initialize the serial port for the RoboClaw.
    port = '/dev/serial0'
    baudrate = 38400
    address = 0x80  # Default RoboClaw address
    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except Exception as e:
        print("Error opening serial port:", e)
        return
    # Allow port to settle.
    time.sleep(0.1)

    # Initialize the PS4 controller.
    try:
        controller = find_ps4_controller()
    except RuntimeError as err:
        print(err)
        ser.close()
        return
    print(f"Connected to {controller.name} at {controller.path}")

    # Initial joystick positions set to neutral.
    joystick_positions = {
        'LEFT_Y': 128,
        'RIGHT_Y': 128,
    }

    print("Reading joystick positions. Move the joysticks to control motor speeds.")
    try:
        for event in controller.read_loop():
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_Y:  # Left joystick Y-axis
                    joystick_positions['LEFT_Y'] = event.value
                elif event.code == ecodes.ABS_RY:  # Right joystick Y-axis
                    joystick_positions['RIGHT_Y'] = event.value

                # Compute motor duty values from joystick positions.
                left_duty = map_joystick_to_duty(joystick_positions['LEFT_Y'])
                right_duty = map_joystick_to_duty(
                    joystick_positions['RIGHT_Y'])

                # Debug print: show raw values and mapped duty values.
                print(f"Left Joystick: {joystick_positions['LEFT_Y']} -> Duty: {left_duty} | "
                      f"Right Joystick: {joystick_positions['RIGHT_Y']} -> Duty: {right_duty}")

                # Send commands to motors.
                if not set_motor_duty(ser, address, 1, left_duty):
                    print("Failed to update Motor 1 duty")
                if not set_motor_duty(ser, address, 2, right_duty):
                    print("Failed to update Motor 2 duty")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ser.close()


if __name__ == '__main__':
    main()

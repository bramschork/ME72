import serial
import time


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def writeS2(ser, address, cmd, value, retries=3):
    # Sends a command with a 16-bit value (writesword style)
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
    # For RoboClaw, motor 1 duty command is 32 and motor 2 duty command is 33.
    if motor == 1:
        cmd = 32
    elif motor == 2:
        cmd = 33
    else:
        raise ValueError("Motor must be 1 or 2")
    return writeS2(ser, address, cmd, duty)


class Roboclaw:
    "Roboclaw Interface Class"

    def __init__(self, comport, rate, timeout=0.1, address=0x80):
        self.comport = comport
        self.rate = rate
        self.timeout = timeout
        self.address = address
        self.ser = None

    def Open(self):
        try:
            self.ser = serial.Serial(
                self.comport, self.rate, timeout=self.timeout)
        except Exception as e:
            print("Error opening serial port:", e)
            return 0
        time.sleep(0.1)
        return 1

    def Close(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    # These functions mirror the working all-in-one file exactly.
    def ForwardM1(self, addr, val):
        return writeS2(self.ser, self.address, 32, val)

    def ForwardM2(self, addr, val):
        return writeS2(self.ser, self.address, 33, val)

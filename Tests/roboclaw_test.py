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
    # Sends a command with a 16-bit value.
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


class Roboclaw:
    "Roboclaw Interface Class"
    # Command enumeration (we only include the commands needed for this test)
    class Cmd:
        M1FORWARD = 0
        M1BACKWARD = 1
        M2FORWARD = 4
        M2BACKWARD = 5
        M1DUTY = 32
        M2DUTY = 33

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

    # Motor commands (note: the 'address' parameter is kept for compatibility but ignored)
    def ForwardM1(self, address, val):
        return writeS2(self.ser, self.address, self.Cmd.M1FORWARD, val)

    def BackwardM1(self, address, val):
        return writeS2(self.ser, self.address, self.Cmd.M1BACKWARD, val)

    def ForwardM2(self, address, val):
        return writeS2(self.ser, self.address, self.Cmd.M2FORWARD, val)

    def BackwardM2(self, address, val):
        return writeS2(self.ser, self.address, self.Cmd.M2BACKWARD, val)

    def SpeedM1(self, address, val):
        # For RoboClaw, setting motor duty cycle (speed) is done with command 32 for Motor 1.
        return writeS2(self.ser, self.address, self.Cmd.M1DUTY, val)

    def SpeedM2(self, address, val):
        # Command 33 is used for Motor 2.
        return writeS2(self.ser, self.address, self.Cmd.M2DUTY, val)

import serial
import time
import threading

# Global serial lock so that only one thread accesses the serial port at a time.
serial_lock = threading.Lock()


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
        try:
            with serial_lock:
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
        except Exception as e:
            print(f"writeS2 error (cmd {cmd}, value {value}): {e}")
        time.sleep(0.01)
    return False


def write4(ser, address, cmd, value, retries=3):
    # Sends a command with a 4-byte (long) argument.
    for _ in range(retries):
        try:
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
        except Exception as e:
            print(f"write4 error (cmd {cmd}, value {value}): {e}")
        time.sleep(0.01)
    return False


def readN(ser, address, cmd, n, retries=3):
    # Sends a command and reads back n bytes (followed by a 2-byte checksum).
    for _ in range(retries):
        try:
            with serial_lock:
                ser.reset_input_buffer()
                crc = 0
                ser.write(address.to_bytes(1, 'big'))
                crc = crc_update(crc, address)
                ser.write(cmd.to_bytes(1, 'big'))
                crc = crc_update(crc, cmd)
                data = ser.read(n)
                if len(data) != n:
                    continue
                for byte in data:
                    crc = crc_update(crc, byte)
                checksum = ser.read(2)
                if len(checksum) != 2:
                    continue
            received_crc = (checksum[0] << 8) | checksum[1]
            if crc == received_crc:
                return data
        except Exception as e:
            print(f"readN error (cmd {cmd}, expected {n} bytes): {e}")
        time.sleep(0.01)
    return None


class Roboclaw:
    "Roboclaw Interface Class"
    class Cmd:
        # Command enumeration (we include only those used in our test)
        M1FORWARD = 0
        M1BACKWARD = 1
        M2FORWARD = 4
        M2BACKWARD = 5
        GETVERSION = 21
        SETM1DEFAULTACCEL = 68
        SETM2DEFAULTACCEL = 69
        M1DUTY = 32  # Duty command for motor 1
        M2DUTY = 33  # Duty command for motor 2
        GETERROR = 90

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
            print(f"Error opening serial port: {e}")
            return 0
        time.sleep(0.1)
        return 1

    def Close(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    # Motor Commands
    # We map ForwardM1 and ForwardM2 to setting duty via commands 32 and 33 respectively.
    def ForwardM1(self, addr, val):
        return writeS2(self.ser, self.address, self.Cmd.M1DUTY, val)

    def BackwardM1(self, addr, val):
        # You can implement reverse commands if needed.
        return writeS2(self.ser, self.address, self.Cmd.M1BACKWARD, val)

    def ForwardM2(self, addr, val):
        return writeS2(self.ser, self.address, self.Cmd.M2DUTY, val)

    def BackwardM2(self, addr, val):
        return writeS2(self.ser, self.address, self.Cmd.M2BACKWARD, val)

    # You can add additional functions (acceleration, error checking, etc.) as needed.
    def SetM1DefaultAccel(self, addr, accel):
        result = write4(self.ser, self.address,
                        self.Cmd.SETM1DEFAULTACCEL, accel)
        if not result:
            print("Failed to set Motor 1 acceleration.")
        return result

    def SetM2DefaultAccel(self, addr, accel):
        result = write4(self.ser, self.address,
                        self.Cmd.SETM2DEFAULTACCEL, accel)
        if not result:
            print("Failed to set Motor 2 acceleration.")
        return result

    def ReadError(self, addr):
        data = readN(self.ser, self.address, self.Cmd.GETERROR, 4)
        if data:
            return int.from_bytes(data, 'big', signed=True)
        return None

    def ReadVersion(self, addr):
        try:
            with serial_lock:
                self.ser.reset_input_buffer()
                crc = 0
                self.ser.write(self.address.to_bytes(1, 'big'))
                crc = crc_update(crc, self.address)
                self.ser.write(self.Cmd.GETVERSION.to_bytes(1, 'big'))
                crc = crc_update(crc, self.Cmd.GETVERSION)
                version = ""
                for _ in range(48):
                    byte = self.ser.read(1)
                    if len(byte) == 0:
                        break
                    val = byte[0]
                    crc = crc_update(crc, val)
                    if val == 0:
                        break
                    version += chr(val)
                checksum = self.ser.read(2)
            if len(checksum) == 2:
                received_crc = (checksum[0] << 8) | checksum[1]
                if crc == received_crc:
                    return version
        except Exception as e:
            print(f"Error in ReadVersion: {e}")
        return None

import serial
import time


class Roboclaw:
    # Command codes for S2 commands (16-bit parameter)
    M1DUTY = 32
    M2DUTY = 33

    def __init__(self, port, baudrate=38400, address=0x80, timeout=0.1):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.timeout = timeout
        self.ser = None

    def Open(self):
        try:
            self.ser = serial.Serial(
                self.port, self.baudrate, timeout=self.timeout)
            # Allow time for the serial port to settle.
            time.sleep(0.1)
            return True
        except Exception as e:
            print("Error opening serial port:", e)
            return False

    def Close(self):
        if self.ser is not None:
            self.ser.close()

    def crc_update(self, crc, data):
        crc ^= (data << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
        return crc

    def writeS2(self, address, cmd, value, retries=3):
        """
        Sends a packet containing:
          - 1 byte: address
          - 1 byte: command
          - 2 bytes: value (big-endian)
          - 2 bytes: checksum (calculated with CRC-CCITT)
        Expects an acknowledgment byte; nonzero ack indicates success.
        """
        for _ in range(retries):
            self.ser.reset_input_buffer()
            crc = 0
            # Send address
            self.ser.write(address.to_bytes(1, 'big'))
            crc = self.crc_update(crc, address)
            # Send command
            self.ser.write(cmd.to_bytes(1, 'big'))
            crc = self.crc_update(crc, cmd)
            # Send value as 2 bytes (big-endian)
            high = (value >> 8) & 0xFF
            low = value & 0xFF
            self.ser.write(high.to_bytes(1, 'big'))
            crc = self.crc_update(crc, high)
            self.ser.write(low.to_bytes(1, 'big'))
            crc = self.crc_update(crc, low)
            # Send checksum (2 bytes)
            self.ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            self.ser.write((crc & 0xFF).to_bytes(1, 'big'))
            # Read one acknowledgment byte
            ack = self.ser.read(1)
            if len(ack) == 1 and ack[0] != 0:
                return True
            time.sleep(0.01)
        return False

    def set_motor_duty(self, motor, duty):
        """
        Sets the motor duty for the specified motor (1 or 2) using the internal address.
        """
        if motor == 1:
            cmd = self.M1DUTY
        elif motor == 2:
            cmd = self.M2DUTY
        else:
            raise ValueError("Motor must be 1 or 2")
        return self.writeS2(self.address, cmd, duty)

    # API methods matching your test code:
    def ForwardM1(self, address, speed):
        """
        Sends a forward speed command to motor 1.
        The 'address' parameter is provided for compatibility—if it doesn't match
        the internal address, a warning is printed.
        """
        if address != self.address:
            print("Warning: provided address does not match internal address.")
        return self.writeS2(address, self.M1DUTY, speed)

    def ForwardM2(self, address, speed):
        """
        Sends a forward speed command to motor 2.
        """
        if address != self.address:
            print("Warning: provided address does not match internal address.")
        return self.writeS2(address, self.M2DUTY, speed)


# If this module is run directly, demonstrate a simple usage.
if __name__ == '__main__':
    port = '/dev/serial0'  # Adjust as needed.
    roboclaw = Roboclaw(port)
    if not roboclaw.Open():
        print("Failed to open Roboclaw")
        exit(1)

    # Set motor 1 to a duty value of 100
    if roboclaw.ForwardM1(roboclaw.address, 100):
        print("Motor 1 duty set to 100 successfully")
    else:
        print("Failed to set Motor 1 duty")
    time.sleep(1)
    # Stop motor 1
    roboclaw.ForwardM1(roboclaw.address, 0)
    roboclaw.Close()

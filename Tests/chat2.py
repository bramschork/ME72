#!/usr/bin/env python3
import serial
import time
from math import ceil
import threading

# Global serial lock so that only one command is active at a time
serial_lock = threading.Lock()

#################################
# Low‐Level Helper Functions
#################################


def crc_update(crc, data):
    crc ^= (data << 8)
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
    return crc


def write0(ser, address, cmd, retries=3):
    for _ in range(retries):
        with serial_lock:
            ser.reset_input_buffer()
            crc = 0
            ser.write(address.to_bytes(1, 'big'))
            crc = crc_update(crc, address)
            ser.write(cmd.to_bytes(1, 'big'))
            crc = crc_update(crc, cmd)
            ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            ser.write((crc & 0xFF).to_bytes(1, 'big'))
            ack = ser.read(1)
        if len(ack) == 1 and ack[0] != 0:
            return True
        time.sleep(0.01)
    return False


def write1(ser, address, cmd, value, retries=3):
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
    # Sends a command with a 16-bit value.
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
    # Sends a command with a 4-byte (long) argument.
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


def readN(ser, address, cmd, n, retries=3):
    # Sends a command and reads back n bytes of data (followed by a 2-byte checksum)
    for _ in range(retries):
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
        time.sleep(0.01)
    return None

#################################
# Roboclaw Class Definition
#################################


class Roboclaw:
    # Command enumeration (subset of full commands; add more as needed)
    class Cmd:
        M1FORWARD = 0
        M1BACKWARD = 1
        M2FORWARD = 4
        M2BACKWARD = 5
        GETM1ENC = 16
        GETM2ENC = 17
        GETM1SPEED = 18
        GETM2SPEED = 19
        RESETENC = 20
        GETVERSION = 21
        SETM1ENCCOUNT = 22
        SETM2ENCCOUNT = 23
        GETMBATT = 24
        GETLBATT = 25
        SETMINLB = 26
        SETMAXLB = 27
        M1DUTY = 32
        M2DUTY = 33
        MIXEDDUTY = 34
        M1SPEED = 35
        M2SPEED = 36
        MIXEDSPEED = 37
        SETM1DEFAULTACCEL = 68
        SETM2DEFAULTACCEL = 69
        GETERROR = 90
        # Add additional commands as desired

    def __init__(self, port, baudrate, timeout=0.1, address=0x80):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.address = address
        self.ser = None

    def open(self):
        try:
            self.ser = serial.Serial(
                self.port_name, self.baudrate, timeout=self.timeout)
        except Exception as e:
            print("Error opening serial port:", e)
            return False
        time.sleep(0.1)
        return True

    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    # Motor Commands
    def forwardM1(self, value):
        return write1(self.ser, self.address, self.Cmd.M1FORWARD, value)

    def backwardM1(self, value):
        return write1(self.ser, self.address, self.Cmd.M1BACKWARD, value)

    def forwardM2(self, value):
        return write1(self.ser, self.address, self.Cmd.M2FORWARD, value)

    def backwardM2(self, value):
        return write1(self.ser, self.address, self.Cmd.M2BACKWARD, value)

    def setM1Duty(self, duty):
        return writeS2(self.ser, self.address, self.Cmd.M1DUTY, duty)

    def setM2Duty(self, duty):
        return writeS2(self.ser, self.address, self.Cmd.M2DUTY, duty)

    def setMixedDuty(self, duty1, duty2):
        # MIXEDDUTY command sends two 16-bit values in sequence.
        with serial_lock:
            self.ser.reset_input_buffer()
            crc = 0
            self.ser.write(self.address.to_bytes(1, 'big'))
            crc = crc_update(crc, self.address)
            self.ser.write(self.Cmd.MIXEDDUTY.to_bytes(1, 'big'))
            crc = crc_update(crc, self.Cmd.MIXEDDUTY)
            # Write duty for M1
            high1 = (duty1 >> 8) & 0xFF
            low1 = duty1 & 0xFF
            self.ser.write(high1.to_bytes(1, 'big'))
            crc = crc_update(crc, high1)
            self.ser.write(low1.to_bytes(1, 'big'))
            crc = crc_update(crc, low1)
            # Write duty for M2
            high2 = (duty2 >> 8) & 0xFF
            low2 = duty2 & 0xFF
            self.ser.write(high2.to_bytes(1, 'big'))
            crc = crc_update(crc, high2)
            self.ser.write(low2.to_bytes(1, 'big'))
            crc = crc_update(crc, low2)
            self.ser.write(((crc >> 8) & 0xFF).to_bytes(1, 'big'))
            self.ser.write((crc & 0xFF).to_bytes(1, 'big'))
            ack = self.ser.read(1)
        return (len(ack) == 1 and ack[0] != 0)

    # Encoder Commands
    def getM1Encoder(self):
        data = readN(self.ser, self.address, self.Cmd.GETM1ENC, 4)
        if data:
            return int.from_bytes(data, 'big', signed=True)
        return None

    def getM2Encoder(self):
        data = readN(self.ser, self.address, self.Cmd.GETM2ENC, 4)
        if data:
            return int.from_bytes(data, 'big', signed=True)
        return None

    def resetEncoders(self):
        return write0(self.ser, self.address, self.Cmd.RESETENC)

    # Battery Commands
    def getMainBattery(self):
        data = readN(self.ser, self.address, self.Cmd.GETMBATT, 2)
        if data:
            return int.from_bytes(data, 'big')
        return None

    def getLogicBattery(self):
        data = readN(self.ser, self.address, self.Cmd.GETLBATT, 2)
        if data:
            return int.from_bytes(data, 'big')
        return None

    def setMinLogicBattery(self, value):
        return write1(self.ser, self.address, self.Cmd.SETMINLB, value)

    def setMaxLogicBattery(self, value):
        return write1(self.ser, self.address, self.Cmd.SETMAXLB, value)

    # Speed Commands (for example purposes, simple serial commands)
    def setM1Speed(self, speed):
        return write1(self.ser, self.address, self.Cmd.M1SPEED, speed)

    def setM2Speed(self, speed):
        return write1(self.ser, self.address, self.Cmd.M2SPEED, speed)

    # Acceleration Commands
    def setM1DefaultAccel(self, accel):
        return write4(self.ser, self.address, self.Cmd.SETM1DEFAULTACCEL, accel)

    def setM2DefaultAccel(self, accel):
        return write4(self.ser, self.address, self.Cmd.SETM2DEFAULTACCEL, accel)

    # Error and Version
    def getError(self):
        # GETERROR returns a 4-byte value.
        data = readN(self.ser, self.address, self.Cmd.GETERROR, 4)
        if data:
            return int.from_bytes(data, 'big', signed=True)
        return None

    def getVersion(self):
        with serial_lock:
            self.ser.reset_input_buffer()
            crc = 0
            self.ser.write(self.address.to_bytes(1, 'big'))
            crc = crc_update(crc, self.address)
            self.ser.write(self.Cmd.GETVERSION.to_bytes(1, 'big'))
            crc = crc_update(crc, self.Cmd.GETVERSION)
            version = ""
            # Read up to 48 bytes (null-terminated string)
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
        return None

#################################
# Example Usage (Main Function)
#################################


def main():
    # Use /dev/serial0 as requested.
    port = '/dev/serial0'
    baudrate = 38400
    address = 0x80  # Default address

    rc = Roboclaw(port, baudrate, timeout=0.1, address=address)
    if not rc.open():
        print("Failed to open serial port.")
        return

    print("Roboclaw opened successfully.")
    print("Firmware Version:", rc.getVersion())
    print("Main Battery Voltage (raw):", rc.getMainBattery())
    print("Logic Battery Voltage (raw):", rc.getLogicBattery())

    # Set default acceleration for both motors
    if rc.setM1DefaultAccel(8):
        print("Motor 1 acceleration set.")
    else:
        print("Failed to set Motor 1 acceleration.")
    if rc.setM2DefaultAccel(8):
        print("Motor 2 acceleration set.")
    else:
        print("Failed to set Motor 2 acceleration.")

    # Demo: Power cycle motors (on for 1 second, off for 1 second, 10 cycles)
    cycles = 10
    on_duty = 1000  # Example duty value for "on"
    off_duty = 0

    for i in range(cycles):
        print(f"Cycle {i+1}: Turning motors ON")
        if not rc.setM1Duty(on_duty):
            print("Failed to set Motor 1 duty")
        if not rc.setM2Duty(on_duty):
            print("Failed to set Motor 2 duty")
        time.sleep(1)
        print(f"Cycle {i+1}: Turning motors OFF")
        if not rc.setM1Duty(off_duty):
            print("Failed to set Motor 1 duty")
        if not rc.setM2Duty(off_duty):
            print("Failed to set Motor 2 duty")
        time.sleep(1)

    # Read encoder values (if connected and running)
    enc1 = rc.getM1Encoder()
    enc2 = rc.getM2Encoder()
    print("Encoder Motor 1:", enc1)
    print("Encoder Motor 2:", enc2)

    # Read error status
    err = rc.getError()
    print("Error Status:", err)

    rc.close()
    print("Roboclaw closed.")


if __name__ == '__main__':
    main()

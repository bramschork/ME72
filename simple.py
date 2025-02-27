from serial import Serial
from time import sleep

if __name__ == "__main__":
    serial_port = "/dev/ttyS0"
    baudrate = 38400

    roboclaw = Serial(serial_port, baudrate, timeout=1)

    while True:
        # Send bytes instead of strings
        roboclaw.write(bytes([94]))   # chr(94) -> '^'
        sleep(2)
        roboclaw.write(bytes([64]))   # chr(64) -> '@'
        sleep(2)
        roboclaw.write(bytes([32]))   # chr(32) -> ' '
        sleep(2)
        roboclaw.write(bytes([64]))   # chr(64) -> '@'
        sleep(2)

        roboclaw.write(bytes([223]))  # chr(223)
        sleep(2)
        roboclaw.write(bytes([192]))  # chr(192)
        sleep(2)
        roboclaw.write(bytes([160]))  # chr(160)
        sleep(2)
        roboclaw.write(bytes([192]))  # chr(192)
        sleep(2)

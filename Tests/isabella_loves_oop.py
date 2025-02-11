import evdev
from evdev import InputDevice, ecodes
import time
import threading
from roboclaw_3 import Roboclaw

# define useful global variables/dictionaries/etc
# Joystick axis mappings
AXIS_CODES = {'LEFT_Y': ecodes.ABS_Y, 'RIGHT_Y': ecodes.ABS_RY}

class SharedData:
    def __init__(self):
        self.lock = threading.Lock()
        
        # make motor speeds accessible as part of class
        self.left_speed = 0
        self.right_speed = 0
        # replace joystick dictionary w shared object
        self.left_y_joystick = 128
        self.right_y_joystick = 128

# target this function in thread to get joystick data
def joystick(shared_data):
    # first, connect to the PS4 controller
    for path in evdev.list_devices():
        controller = InputDevice(path)
        if not "Wireless Controller" in controller.name:
            raise RuntimeError("PS4 controller not found! Ensure it's connected.")

    # next, get data from controller
    event = controller.read_one()
    if shared_data.lock.acquire():
        if event != None and event.type == ecodes.EV_ABS and event.code in AXIS_CODES.values():
            if event.code == ecodes.ABS_Y:
                try:
                    shared_data.left_y_joystick = event.value
                    shared_data.left_speed = 128 - shared_data.left_y_joystick
                except Exception as e:
                    print(e)
                    print("Motor thread busy, skipping update.")
        elif event == None:
            shared_data.left_speed = 0
            print('None type loser')
        shared_data.lock.release()
    

# target this function in thread to send motor commands
# this includes initializing the Roboclaws
def motor_controller(shared_data):
    # Initialize Roboclaw
    roboclaw = Roboclaw("/dev/ttyS0", 460800)
    roboclaw.Open()
    address = 0x80  # Roboclaw address
    
    # send command to motors
    if shared_data.lock.acquire():
        roboclaw.ForwardM1(address, shared_data.left_speed)
        print(f"Sent Speed: {shared_data.left_speed}")
        shared_data.lock.release()


def main():
    # Daemon - killed when over
    shared_data = SharedData()

    joystick_thread = threading.Thread(
        target=joystick(), daemon=True, args=(shared_data,))
    joystick_thread.start()

    try:
        motor_controller(shared_data)
    except KeyboardInterrupt:
        print("\nExiting...")
    
    joystick_thread.join()

if __name__ == "__main__":
    main()
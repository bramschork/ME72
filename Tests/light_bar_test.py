import hid
import time
import subprocess
from evdev import InputDevice, list_devices

# Replace with your actual PS4 controller's MAC address
PS4_CONTROLLER_MAC = "30:0E:D5:92:26:3E"  # Update with your controller's MAC

# Sony DualShock 4 Vendor & Product ID
DS4_VENDOR_ID = 0x054C
DS4_PRODUCT_ID = 0x05C4
LIGHTBAR_REPORT_ID = 0x11  # Standard HID report for light bar


def connect_ps4_controller():
    """
    Ensures the PS4 controller is connected via Bluetooth before proceeding.
    """
    cmd = f"bluetoothctl info {PS4_CONTROLLER_MAC}"
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if "Connected: yes" not in output.stdout:
        print("Controller is NOT connected. Attempting to connect...")
        cmd_connect = f"bluetoothctl connect {PS4_CONTROLLER_MAC}"
        subprocess.run(cmd_connect, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("Controller is already connected!")


def find_ps4_controller():
    """
    Finds and returns the first detected PS4 controller input device.
    Ensures it's connected via Bluetooth first.

    Returns:
        InputDevice: The PS4 controller device.

    Raises:
        RuntimeError: If no PS4 controller is found.
    """
    connect_ps4_controller()

    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "Wireless Controller" in device.name:
            print(f"Connected to {device.name} at {device.path}")
            return device

    raise RuntimeError("PS4 controller not found! Ensure it's connected.")


def set_lightbar_color(r, g, b):
    """
    Sets the PS4 controller light bar color using HIDAPI.
    """
    try:
        ds4 = hid.device()
        ds4.open(DS4_VENDOR_ID, DS4_PRODUCT_ID)

        command = [LIGHTBAR_REPORT_ID, 0xFF, r, g, b, 0, 0, 0, 0, 0]
        ds4.write(command)

        ds4.close()
        print(f"Light bar set to: R={r}, G={g}, B={b}")

    except Exception as e:
        print(f"Failed to set light bar color: {e}")


def cycle_lightbar_colors():
    """
    Cycles through different colors on the PS4 controller's light bar.
    """
    colors = [
        (255, 0, 0),   # Red
        (0, 255, 0),   # Green
        (0, 0, 255),   # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Purple
        (0, 255, 255),  # Cyan
        (255, 255, 255)  # White
    ]

    for r, g, b in colors:
        set_lightbar_color(r, g, b)
        time.sleep(1)  # Wait 1 second before changing to the next color


if __name__ == "__main__":
    print("Ensuring PS4 controller is connected via Bluetooth...")
    find_ps4_controller()

    print("Cycling light bar colors...")
    cycle_lightbar_colors()
    print("Finished cycling colors.")

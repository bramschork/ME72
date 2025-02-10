import hid
import time

# Replace this with your actual PS4 controller's HID Vendor & Product IDs
DS4_VENDOR_ID = 0x054C  # Sony
DS4_PRODUCT_ID = 0x05C4  # DualShock 4 (CUH-ZCT1)
LIGHTBAR_REPORT_ID = 0x11  # Standard HID report for light bar


def set_lightbar_color(r, g, b):
    """
    Sets the PS4 controller light bar color using HIDAPI.
    Works over both USB and Bluetooth.
    """
    try:
        # Open the HID device (PS4 Controller)
        ds4 = hid.device()
        ds4.open(DS4_VENDOR_ID, DS4_PRODUCT_ID)

        # Send light bar color change command
        command = [LIGHTBAR_REPORT_ID, 0xFF, r, g, b, 0, 0, 0, 0, 0]
        ds4.write(command)

        print(f"Light bar set to: R={r}, G={g}, B={b}")
        ds4.close()
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
    print("Cycling light bar colors...")
    cycle_lightbar_colors()
    print("Finished cycling colors.")

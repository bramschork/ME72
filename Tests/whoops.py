import hid
import time

DS4_VENDOR_ID = 0x054C  # Sony
DS4_PRODUCT_ID = 0x09CC  # Use 0x05C4 for USB mode


def set_lightbar_color(r, g, b):
    """
    Sends a correctly formatted HID report to change the PS4 controller light bar color.
    """
    try:
        ds4 = hid.Device(DS4_VENDOR_ID, DS4_PRODUCT_ID)

        # HID Report for Bluetooth requires a 78-byte payload
        command = bytes([
            0x11, 0x80, 0x00,  # Report ID
            r, g, b,  # RGB values
            0x00, 0x00,  # Rumble (Left, Right)
            0x00, 0x00, 0x00, 0x00,  # Padding
        ] + [0x00] * 64)  # Ensuring 78-byte report length

        ds4.write(command)  # Send HID report
        ds4.close()
        print(f"Light bar set to: R={r}, G={g}, B={b}")

    except Exception as e:
        print(f"Failed to set light bar color: {e}")


# Set light bar to green
set_lightbar_color(0, 255, 0)

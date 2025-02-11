import hid

# Use 0x09CC if 0x05C4 does not work
DS4_VENDOR_ID = 0x054C  # Sony
DS4_PRODUCT_ID = 0x05c4  # DualShock 4 Bluetooth Mode


def set_lightbar_color(r, g, b):
    """
    Sends a properly formatted HID report to change the PS4 light bar color.
    """
    try:
        ds4 = hid.Device(DS4_VENDOR_ID, DS4_PRODUCT_ID)

        # HID Report Format (USB requires a 32-byte report, Bluetooth requires 78 bytes)
        command = bytes([
            0x11, 0x80, 0x00,  # HID Report ID
            r, g, b,  # RGB values
            0x00, 0x00, 0x00, 0x00,  # Padding
        ] + [0x00] * 56)  # Ensure report is 64 bytes long

        ds4.write(command)  # Send the HID report

        ds4.close()
        print(f"Light bar set to: R={r}, G={g}, B={b}")

    except Exception as e:
        print(f"Failed to set light bar color: {e}")


# Try setting light bar to green
set_lightbar_color(0, 255, 0)

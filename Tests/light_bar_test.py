import hid

# Use 0x09CC if 0x05C4 does not work
DS4_VENDOR_ID = 0x054C  # Sony
DS4_PRODUCT_ID = 0x09CC  # DualShock 4 Bluetooth Mode


def set_lightbar_color(r, g, b):
    """
    Sets the PS4 controller light bar color using HIDAPI.
    """
    try:
        ds4 = hid.Device(DS4_VENDOR_ID, DS4_PRODUCT_ID)

        # HID Report Format (Bluetooth requires a longer 78-byte report)
        command = bytearray([
            0x11, 0x80, 0x00,  # HID Report ID
            r, g, b,  # RGB values
            0x00, 0x00, 0x00, 0x00,  # Padding
        ] + [0x00] * 56)  # Ensuring 64-byte length

        ds4.write(command)
        ds4.close()
        print(f"Light bar set to: R={r}, G={g}, B={b}")

    except Exception as e:
        print(f"Failed to set light bar color: {e}")


# Try setting light bar to green
set_lightbar_color(0, 255, 0)

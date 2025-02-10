import hid

PS4_CONTROLLER_MAC = "30:0E:D5:92:26:3E".lower()  # Ensure lowercase MAC


def find_ps4_controller():
    """
    Finds the PS4 controller's HID path by matching the MAC address.
    Returns the device path (e.g., '/dev/hidraw0') if found, else None.
    """
    devices = hid.enumerate()
    for device in devices:
        if 'serial_number' in device and device['serial_number'].lower() == PS4_CONTROLLER_MAC:
            return device['path']  # Return the HID device path

    return None  # Controller not found


def set_lightbar_color(r, g, b):
    """
    Sets the PS4 controller light bar color using HIDAPI.
    """
    controller_path = find_ps4_controller()
    if controller_path is None:
        print("PS4 controller not found! Ensure it's connected via Bluetooth or USB.")
        return

    try:
        # Open the controller using its path
        ds4 = hid.Device(path=controller_path)

        # HID Report Format (USB requires 32 bytes, Bluetooth requires 78 bytes)
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


# Example usage: Set light bar to green
set_lightbar_color(0, 255, 0)

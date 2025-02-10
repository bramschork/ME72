import subprocess
import time

# Replace this with your actual PS4 controller's MAC address
PS4_CONTROLLER_MAC = "30:0E:D5:92:26:3E"  # Update with your actual MAC


def connect_ps4_controller():
    """
    Ensures the PS4 controller is connected via Bluetooth before sending commands.
    """
    cmd = f"echo -e 'connect {PS4_CONTROLLER_MAC}\ntrust {PS4_CONTROLLER_MAC}\nquit' | bluetoothctl"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def set_lightbar_color(r, g, b):
    """
    Uses `ds4drv` to change the light bar color on a Bluetooth-connected PS4 controller.
    """
    cmd = f"ds4drv --led {r},{g},{b}"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    print(f"Setting light bar color to: R={r}, G={g}, B={b}")


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
    connect_ps4_controller()

    print("Starting `ds4drv` for Bluetooth LED control...")
    subprocess.Popen("ds4drv --hidraw", shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("Cycling light bar colors...")
    cycle_lightbar_colors()

    print("Finished cycling colors.")

# WiFi

WiFi Router Management IP: 192.168.8.1
SSID: The Net
Password: michaelmello

# Raspberry Pi's

## Login:

RPI 1
RPI USER: ME72
SSH IP: me72@192.168.8.135
Pass: mello

RPI 1
RPI USER: ME72
SSH IP: me72@192.168.8.162
Pass: mello

## Setup

Use the Raspberry Pi imager to flash the SD card using the first recommended full installation of Raspbian for the Raspberry Pi Zero W. **Follow the prompts to install custom settings**. Here, when flashing the SD card, you can populate the SSID and password of the network so that the Pi automatically joins on startup. The IP address of the Pi can be found using the instructions below.
![[Pasted image 20250206112721.png]]

## Login Help

The IP address of the Pi's can be found on the router using a tool such as Angry IP Scanner (free Mac/Windows). This tool cans the local network and will locate the IP of the Raspberry pi as long as it is connected to the network.
![[Pasted image 20250206123146.png]]

## Bluetooth Commands

List connected devices: `bluetoothctl devices`
Info on specific device: `bluetoothctl info [DEVICE_MAC_ADDRESS]`

If the above hangs try starting bluetooth: `systemctl start bluetooth`
If there are any errors: `systemctl status bluetooth`

**Set up Autoconnection**
Edit the Bluetooth configuration file to ensure the controller connects automatically:
sudo nano /etc/bluetooth/main.conf

AutoEnable=true
Save and exit (Ctrl+O, Enter, Ctrl+X).

sudo systemctl restart bluetooth

# Programming

### Venv

Create and activate virtual environment:

```
python -m venv venv
source venv/bin/activate
```

### controller_test.py

Prints the value of the left and right joysticks in both the x and y directions.

# Controllers

## Controller Lists

Pi 1, Controller 1 (MAC: 30:0E:D5:92:26:3E)
Pi 2, Controller 2 (MAC: 28:C1:3C:59:86:C9)

## Useful Commands

`bluetooth ctl info MAC`: See the status (ex. paired, trusted, connected)
**Note:** only `connected` is a _current_ status. Pairing and connected are different. Pairing is the initial handshake protocol for a controller to talk to a device. Trust is the allowance for auto-connecting. Connected means there is a current bluetooth link between the two. A device can be paired and trusted but not connected, and thus the controller will not work.

## Buttons

`PS`: PS4 logo in the bottom center of the controller
`Share`: Top left on the front face

Turning on/Wake: Press the `PS` button quickly
Turning off: Hold the `PS` button until the light bar turns off

## Pairing the Controller

## Pairing Mode (+ light bar colors)

To put the controller into pairing mode, first connect the controller to the device you want to pair it to via USB. When plugged in, the controller is charging and the light bar will be blue. Wait a few seconds (~3-5s), then disconnect the controller. The light bar should turn off.

Now, put the controller in _Pairing Mode_. Press the `Share` button and the `PS` button at the same time (try to press the `Share button` a tiny tiny bit first, this is just so the device goes into pairing mode rather than search and instantly connect to a previous device. This is only important if the controller was paired to a different device previously). The light bar should pulse fast white. If the light bar goes sold white, restart this process by plugging the controller in. Solid white means it is looking to pair to the previous device. If the light bar turns blue (while cable is disconnected), the controller is paired. If it is paired to the wrong device, turn the controller off and restart this process by plugging the controller in.

The general pairing process (except common errors, see below) goes as follows:
Start Bluetooth Control Service: `bluetoothctl`

```
power on
discoverable on
pairable on
scan on
pair MAC
trust MAC
connect MAC
```

Sub in MAC with the MAC address of each controller. I have tried to put labels on the back of each controller as we go. Otherwise, the MAC address can be found after the `scan on` command. Look in the terminal output. You should see something like: `[NEW] Device MAC Wireless Controller`, where MAC is the unique MAC address of that controller. **Please check to make sure the MAC address is not one of the listed controllers above, as you might "steal" a controller from a different robot.**

### How to know if controller is connected?

If controller is not connected, the `bluetoothctl` prompt will be: `[bluetooth]#`
If controller is connected, the prompt will read: `[Wireless Controller]#`
![[Pasted image 20250113132124.png]]

## Charging

Only charge the controller with it's intended connection device. Pairing occurs over USB, so if you connect the controller to a new device it will try to pair with it and you will have to repair it. Charging will not occur via a USB block/phone charger style charger. It needs a USB connection. Device is charging when the light bar is solid blue.

## Errors

**Connection Error**

```
[CHG] Device 30:0E:D5:92:26:3E Connected: yes
Failed to connect: org.bluez.Error.Failed br-connection-create-socket
[CHG] Device 30:0E:D5:92:26:3E Connected: no
```

```
sudo apt update && sudo apt upgrade -y
sudo apt install bluetooth bluez bluez-tools python3-dbus python3-pip
pip3 install ds4drv
sudo nano /lib/systemd/system/bluetooth.service
```

Look for the ExecStart line, which should look like this: `ExecStart=/usr/lib/bluetooth/bluetoothd`
Modify it to include the --compat option: `ExecStart=/usr/lib/bluetooth/bluetoothd --compat`

sudo systemctl daemon-reload
sudo systemctl restart bluetooth

\*\*The error will probably persist. Try disabling ERTM (Enhanced Re-Transmission Mode)
`echo 1 | sudo tee /sys/module/bluetooth/parameters/disable_ertm`

`AttributeError: 'Roboclaw' object has no attribute '_port'`: Roboclaw is not connected properly

# Github

Auth Errors:

```
(venv) **me72@raspberrypi**:**~/ME72/WI $** git push
Username for 'https://github.com': bramschork
Password for 'https://bramschork@github.com': 
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/get-started/getting-started-with-git/about-remote-repositories#cloning-with-https-urls for information on currently recommended modes of authentication.
```

Remove current origin: `git remote remove origin`
Add new origin: `git remote add origin https://bramschork:TOKEN@github.com/bramschork/ME72.git`
Then, `git push -u origin main`
Ask Bram for the token. It's a private key and cannot be shared on Github.

# Electronics

Wiring: https://resources.basicmicro.com/packet-serial-with-the-raspberry-pi-3/

| **Raspberry Pi** | **RoboClaw**                                   |
| ---------------- | ---------------------------------------------- |
| GPIO 14          | S1 signal pin (pin closest to board edge)      |
| GPIO 15          | S2 signal pin (pin closest to board edge)      |
| Any ground pin   | S1 ground pin (pin closest to inside of board) |

nano ~/.ssh/config
![[Pasted image 20250207141220.png]]

## Label Schema

### Controllers

Front: C* (* = controller number)
Back: C\* MAC

Roboclaw naming convention. All roboclaws use “Packet Serial Mode”, Baud Rate = 38400

A1D = Attacker #1, Drive motors controller, 128 = Packet Serial Address of 128
A1S = Attacher #1 Shooter motors controller, 130 = Packet Serial Address of 130

![[Pasted image 20250207151031.png]]

![[Pasted image 20250207163147.png]]

Pin 1, 2 VCC
Pin 3 GND
S1, TX, Pin 4
S2, RX, Pin 5

AttributeError: 'Roboclaw' object has no attribute '\_port'

One of two causes. 1) wiring issue, check all connections. 2) UART not enabled (Pi default). You can check if this is the case by running `ls -l /dev/serial*`. If the output is `ls: cannot access '/dev/serial*': No such file or directory`, UART is disable. To fix:
`sudo raspi-config`

1. **Go to**: Interfacing Options
2. **Select**: Serial Port
3. **Disable shell login over serial** (select **No**)
4. **Enable serial hardware** (select **Yes**)
   sudo reboot
   Check: ls /dev/ | grep tty

I changed the wiring on the Pi. Since we are communicating over serial the connections can be daisy chained.

For each roboclaw,:

S1 closest to board edge pins connect to the TX (Pin 4) of the RPI
S2 pins connect to the RX (pin 4) of the RPI
S1 furthest from board edge connect to GND (Pin 3) of the RPI

The GitHub has two scripts, single_roboclaw_test and dual_roboclaw_test. The RPI is successfully connecting to the controllers and controlling the motors. Once we have the chassis assembled I will fine tune the tank drive. Same with mechanism when it is ready. I talked with Claire regarding the button/controller schema.

Electronics are good for now. When I come in this weekend I’m free to help do whatever until we are assembled enough for testing

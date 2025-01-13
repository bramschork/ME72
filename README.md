<<<<<<< HEAD
# ME72

## Raspberry Pi Zero 2 W Login

User: me72\
Pass: mello\
Current IP (may change for other Pi's. You can check the IP by logging into the router and checking connected devices. See below for instructions): 192.168.8.135\
SSH (Port 22): me72@RPI_IP (ex. me72@192.168.8.135)

## Router

Static IP: 192.168.8.1\
Password: Will change. Ask Bram if needed.

## Virtual Environment

Install venv tool: `sudo apt install python3-venv`\
Create venv: `python3 -m venv venv`

ACTIVATE venv: `source venv/bin/activate`

## Required Packages

Pygame for bluetooth PS4 controller: `pip install pygame`

Roboclaw: `pip install roboclaw`

## Blueooth

Open bluetooth panel:\
`bluetooth ctl`\
`discoverable on`\
`pair MAC`\
`trust MAC`\
`connect MAC`

Scan will list all bluetooth devices. Aftwr you find the device with the name "Wireless Controller", you can run
`scan off`. Then you can pair, trust, and connect to the controller.

Running `devices` will list all devices the RPI has paired to (INCLUDING presently unconnected devices). To check if the
PS4 controller is currently connect, run `info MAC`. This will list all stats.

**Substitute MAC for the MAC address of the controller found when you run** `scan on`.
=======
This repository contains the test file 'packet_serial.py'
and the BasicMicro Python library 'roboclaw.py'. The test file
operates a RoboClaw in packet serial mode with a Raspberry Pi single board computer. The accompanying
Application Note can be [found here](https://resources.basicmicro.com/packet-serial-with-the-raspberry-pi-3/).
>>>>>>> master

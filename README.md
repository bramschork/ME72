# ME72

## Virtual Environment

Install venv tool: `sudo apt install python3-venv`
Create venv: `python3 -m venv venv`

ACTIVATE venv: `source venv/bin/activate`

## Required Packages

Pygame for bluetooth PS4 controller: `pip install pygame`
Roboclaw: `pip install roboclaw`

## Blueooth

Open bluetooth panel: `bluetooth ctl`
`discoverable on`\
`pair MAC`\
`trust MAC`\
`connect MAC`

Scan will list all bluetooth devices. Aftwr you find the device with the name "Wireless Controller", you can run
`scan off`. Then you can pair, trust, and connect to the controller.

Running `devices` will list all devices the RPI has paired to (INCLUDING presently unconnected devices). To check if the
PS4 controller is currently connect, run `info MAC`. This will list all stats.

**Substitute MAC for the MAC address of the controller found when you run** `scan on`.

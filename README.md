# raspberrypi-weather-station
This allows your Raspberry Pi 4 device to show the current weather

Requirements:
- Unicorn HAT Mini https://shop.pimoroni.com/en-us/products/unicorn-hat-mini
- Slack to post error messages: https://slack.com/
- Systemd to run the clock on boot

Set your internal clock in your Raspberry Pi to your local time and update the GPS coordinates in your main.py file to a location close enough for you.

See an example of this: TBD

This displays vertically, i.e. where most of the LEDs are positioned from top to bottom, as this allows the best use of the LEDs offered by the Unicorn HAT Mini.

The Unicorn Hat Mini comes with 4 buttons, all functional with this program.

Press the upper left button once TBD
Press the upper right button once TBD
Press the lower left button once TBD
Press the lower right button once TBD

Run this on startup:
Systemd allows a script to run on startup. In this repository there is a folder /etc/systemd/system. This matches the
file structure of where you should place the raspberrypi-weather-station.service file.

Additionally, you should create a ".env" file in this directory with your OPENWEATHER_API_KEY value set, like this:
OPENWEATHER_API_KEY=abcdefghijklmnop

Once you place it, run these commands:
sudo systemctl enable --now systemd-timesyncd.service
sudo systemctl enable --now systemd-time-wait-sync.service
sudo systemctl enable --now raspberrypi-weather-station.service

And when you reboot, it should start running on startup

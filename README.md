# PiHeaterControl


### Starting the script automatically

1.  `sudo nano /etc/xdg/lxsession/LXDE-pi/autostart`

    Add:
    
    `@lxterminal -e /usr/bin/python /home/pi/new_temp_sensor.py`

2. Configure pigpio to start on boot:

    `sudo systemctl enable pigpiod`

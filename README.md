# PiHeaterControl


### Starting the script automatically

`sudo nano /etc/xdg/lxsession/LXDE-pi/autostart`

Add

`@lxterminal -e /usr/bin/python /home/pi/new_temp_sensor.py`

---

Also requires pigpiod to be running

`sudo systemctl enable pigpiod`

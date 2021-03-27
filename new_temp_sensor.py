import pigpio # for PWM dimming of LEDs
import time
from datetime import datetime
import signal # for CTRL+C handling
import sys    # for CTRL+C handling
import DHT22 # temperature sensor
             # from https://github.com/joan2937/pigpio/blob/master/EXAMPLES/Python/DHT22_AM2302_SENSOR/DHT22.py

print("Program started")

# Pigpio documentation - http://abyz.me.uk/rpi/pigpio/python.html
# To start pigpio : sudo pigpiod
GPIO_HIGH = 1
GPIO_LOW = 0
pi = pigpio.pi()


# Set up temperature sensor on GPIO port 22
sensor = DHT22.sensor(pi, 22, LED=27) 
# LED on GPIO 27 blinks every time a reading is taken
# If the sensor becomes disconnected, the LED will stay lit
# to indicate an error state.



def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    # Switch everything off
    pi.write(5, GPIO_LOW) # red LED off
    pi.write(6, GPIO_LOW) # yellow LED off
    pi.write(7, GPIO_LOW) # white LED off
    pi.write(8, GPIO_LOW) # green LED off
    pi.write(9, GPIO_LOW) # blue LED off
    pi.write(14, GPIO_LOW) # relay off
    sensor.cancel() # temperature sensor off
    pi.stop() # release pigpio resources
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler) # handle CTRL+C




def write_log_file(temp, relay_status):
    f = open("log.txt", "a")
    f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\t" + str(temp) + "\t" + relay_status + "\n")
    f.close()

def switch_on_led(number, brightness):
    # number: GPIO port number
    # brightness: a number between 0 and 255
    # Note: Most tutorials recommend GPIO.PWM,
    #       but that uses software PWM which causes
    #       visible (uneven) flickering.
    #       pigpio PWM is much better.
    # see also https://raspberrypi.stackexchange.com/a/40256 
    #      and https://raspberrypi.stackexchange.com/a/37945
    pi.set_PWM_dutycycle(5, 0 if number != 5 else brightness) # red LED
    pi.set_PWM_dutycycle(6, 0 if number != 6 else brightness) # yellow LED
    pi.set_PWM_dutycycle(7, 0 if number != 7 else brightness) # white LED 
    pi.set_PWM_dutycycle(8, 0 if number != 8 else brightness) # green LED
    pi.set_PWM_dutycycle(9, 0 if number != 9 else brightness) # blue LED



# MAIN LOOP
# Print out the temperature until the program is stopped.
iteration_number = -1 # -1 to write log file on *second*, not first, iteration
                      # (first temperature reading can sometimes be inaccurate)
pi.write(14, GPIO_LOW) # relay off
relay_status = "OFF"
last_relay_status = "OFF"
ON_TEMPERATURE = 16.5
OFF_TEMPERATURE = 17.0
while True:
    sensor.trigger() # take temperature reading
    time.sleep(0.2) # wait for data to populate (otherwise first reading comes back as -999!)
    temp = sensor.temperature()
    temp = round(temp, 1) # round to 1 decimal place
    print(temp)
    currentHour = time.localtime().tm_hour
    isNighttime = (currentHour >= 22 or currentHour <= 6)
    isDaytime = not isNighttime
    # ===== Relay =====
    if temp <= ON_TEMPERATURE and isNighttime:
        pi.write(14, GPIO_HIGH) # relay on
        relay_status = "ON" # for log file
    if temp >= OFF_TEMPERATURE or isDaytime:
        pi.write(14, GPIO_LOW) # relay off
        relay_status = "OFF" # for log file
    # NB if temp is between ON_TEMPERATURE and OFF_TEMPERATURE
    #    then the relay stays in its current position
    #    to wait for new temperature to be reached
    # ===== LEDs =====
    brightness = 8 if isNighttime else 255 # dim at night
    if temp > 24.0: # 24 and above = hot
        switch_on_led(5, brightness) # red LED on
    elif temp > 21.0: # 21-24 = getting hot
        switch_on_led(6, brightness) # yellow LED on
    elif temp > 18.0: # 18-21 = comfortable
        switch_on_led(7, brightness) # white LED on
    elif relay_status == "OFF": # 18 or below, heater NOT on
        switch_on_led(8, brightness) # green LED on
    elif relay_status == "ON": # heater is on
        switch_on_led(9, brightness) # blue LED on
    # ===== Log file =====
    if iteration_number % 400 == 0 or relay_status != last_relay_status:
        # write to the log file every 20 minutes (approx 400 iterations)
        # OR if the relay status changes
        write_log_file(temp, relay_status)
        last_relay_status = relay_status
    time.sleep(3) # wait 3 seconds (any less will hang the DHT22).
    iteration_number += 1



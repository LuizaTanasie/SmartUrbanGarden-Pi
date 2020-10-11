import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

from HttpUtils import HttpUtils
from SmartPotData import SmartPotData

api_url = ""

dht_device = adafruit_dht.DHT22(board.D4)
rain_channel = 14
soil_moisture_channel = 15
needs_water = False
is_raining = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(rain_channel, GPIO.IN)

GPIO.setmode(GPIO.BCM)
GPIO.setup(soil_moisture_channel, GPIO.IN)


def rainCallback(channel):
    global is_raining
    if GPIO.input(channel) == 0:
        is_raining = True
    else:
        is_raining = False

def soilMoistureCallback(channel):
    global needs_water
    print(GPIO.input(channel))
    if GPIO.input(channel):
        needs_water = True
    else:
        needs_water = False


while True:
    try:
        # Print the values to the serial port
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        if GPIO.input(soil_moisture_channel):
            needs_water = True
        else:
            needs_water = False

        if GPIO.input(rain_channel):
            is_raining = False
        else:
            is_raining = True
        print(
            "Temp: {:.1f} C    Humidity: {}%    Needs water: {}     Is raining: {} ".format(
                temperature_c, humidity, needs_water, is_raining)
        )
        data = SmartPotData(temperature_c,humidity,needs_water,is_raining)
        HttpUtils.post(api_url, data)

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dht_device.exit()
        raise error

    time.sleep(5.0)

import time
import datetime
import adafruit_dht
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from uuid import getnode as get_mac


from Config import Config
from HttpUtils import HttpUtils
from PiUtils import PiUtils
from SmartPotData import SmartPotData

config = Config()
dht_device = None
soil_moisture_channel = None
photoresistor_channel = None
pi_id = PiUtils.get_serial()

dht_sensor_error = False
soil_sensor_error = False
rain_sensor_error = False
photoresistor_error = False
mcp_error = False


def initialize():
    initialize_dht_sensor()
    initialize_rain_sensor()
    mcp = initialize_mcp()
    initialize_soil_sensor(mcp)
    initialize_photoresistor(mcp)


def initialize_dht_sensor():
    global dht_device, dht_sensor_error
    try:
        dht_device = adafruit_dht.DHT22(board.D4)
    except Exception as error:
        print(error.args[0])
        dht_sensor_error = True


def initialize_rain_sensor():
    global rain_sensor_error
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.RAIN_CHANNEL, GPIO.IN)
    except Exception as error:
        print(error.args[0])
        rain_sensor_error = True


def initialize_mcp():
    global mcp_error
    try:
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = digitalio.DigitalInOut(board.D5)
        return MCP.MCP3008(spi, cs)
    except Exception as error:
        print(error.args[0])
        mcp_error = True


def initialize_soil_sensor(mcp):
    global soil_moisture_channel, soil_sensor_error
    try:
        soil_moisture_channel = AnalogIn(mcp, MCP.P1)
    except Exception as error:
        print(error.args[0])
        soil_sensor_error = True


def initialize_photoresistor(mcp):
    global photoresistor_channel, photoresistor_error
    try:
        photoresistor_channel = AnalogIn(mcp, MCP.P0)
    except Exception as error:
        print(error.args[0])
        photoresistor_error = True


def get_soil_moisture():
    return get_percentage(soil_moisture_channel.value, config.SOIL_VERY_WET, config.SOIL_VERY_DRY)


def get_light_intensity():
    return get_percentage(photoresistor_channel.value, config.STRONG_LIGHT, config.DIM_LIGHT)


def get_percentage(value, min, max):
    percentage = 100 - (((value - max) * 100) /
                        (min - max))
    percentage = 100 if percentage > 100 else percentage
    percentage = 0 if percentage < 0 else percentage
    return percentage


def get_is_raining():
    if GPIO.input(config.RAIN_CHANNEL):
        return False
    else:
        return True


initialize()
while True:
    try:
        if not dht_sensor_error:
            try:
                temperature_c = dht_device.temperature
                humidity = dht_device.humidity
            except Exception as error:
                temperature_c = None
                humidity = None
        if not rain_sensor_error:
            try:
                is_raining = get_is_raining()
            except Exception as error:
                is_raining = None

        if not mcp_error:
            if not soil_sensor_error:
                try:
                    soil_moisture = get_soil_moisture()
                except Exception as error:
                    soil_moisture = None
            if not soil_sensor_error:
                try:
                    light = get_light_intensity()
                except Exception as error:
                    light = None

        data = SmartPotData(pi_id, temperature_c, humidity, soil_moisture, light, is_raining, str(datetime.datetime.utcnow()))
        print(HttpUtils.post(config.API + "SaveSensorsData", data))

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue

    except Exception as error:
        print(error.args[0])
        time.sleep(5.0)
        continue

    time.sleep(5.0)

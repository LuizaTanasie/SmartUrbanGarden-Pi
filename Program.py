import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

from Config import Config
from HttpUtils import HttpUtils
from SmartPotData import SmartPotData

config = Config()
dht_device = None
soil_moisture_channel = None


def initialize():
    global dht_device, soil_moisture_channel
    # config temperature and humidity sensor
    dht_device = adafruit_dht.DHT22(board.D4)

    # config rain sensor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.RAIN_CHANNEL, GPIO.IN)

    # config soil moisture sensor
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)
    soil_moisture_channel = AnalogIn(mcp, MCP.P0)


def get_soil_moisture():
    percentage = 100 - (((soil_moisture_channel.value - config.SOIL_VERY_WET) * 100) / (config.SOIL_VERY_DRY - config.SOIL_VERY_WET))
    return percentage


def get_is_raining():
    if GPIO.input(config.RAIN_CHANNEL):
        return False
    else:
        return True


initialize()
while True:
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        is_raining = get_is_raining()
        soil_moisture = get_soil_moisture()
        print(
            "Temp: {:.1f} C    Humidity: {}%    Soil moisture: {:.2f}%     Is raining: {} ".format(
                temperature_c, humidity, soil_moisture, is_raining)
        )
        data = SmartPotData(temperature_c, humidity, soil_moisture, is_raining)
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

import time
import datetime
import adafruit_dht
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import requests


from Config import Config
from HttpUtils import HttpUtils
from PiUtils import PiUtils
from FileUtils import FileUtils
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
        soil_moisture_channel = AnalogIn(mcp, MCP.P2)
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
    return get_percentage(soil_moisture_channel.value, config.SOIL_VERY_DRY, config.SOIL_VERY_WET)


def get_light_intensity():
    return get_percentage(photoresistor_channel.value, config.DIM_LIGHT, config.STRONG_LIGHT)


def get_percentage(value, minValue, maxValue):
    percentage = 100 - (((value - maxValue) * 100) /
                        (minValue - maxValue))
    percentage = 100 if percentage > 100 else percentage
    percentage = 0 if percentage < 0 else percentage
    return percentage


def get_is_raining():
    if GPIO.input(config.RAIN_CHANNEL):
        return False
    else:
        return True


def send_backups():
    lines = FileUtils.read_lines(config.BACKUP_FILE)
    lines = lines[-config.BACKUP_ENTRIES_TO_SEND:]

    for line in lines:
        sensors_data = line.split(";")
        smart_pot = SmartPotData(sensors_data[0], sensors_data[1], sensors_data[2], sensors_data[3], sensors_data[4],
                                 sensors_data[5], sensors_data[6])
        HttpUtils.post(config.API + "SaveSensorsData", smart_pot)
    FileUtils.remove_file(config.BACKUP_FILE)
    print("Backups sent")


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
        try:
            if FileUtils.file_exists(config.BACKUP_FILE):
                send_backups()
            print(HttpUtils.post(config.API + "SaveSensorsData", data))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Server down")
            if FileUtils.get_file_size(config.BACKUP_FILE) > config.BACKUP_FILE_MAX_SIZE:
                FileUtils.remove_file(config.BACKUP_FILE)
            FileUtils.append(config.BACKUP_FILE, data.to_string())
        except requests.exceptions.HTTPError:
            print("Server error")
            if FileUtils.get_file_size(config.BACKUP_FILE) > config.BACKUP_FILE_MAX_SIZE:
                FileUtils.remove_file(config.BACKUP_FILE)
            FileUtils.append(config.BACKUP_FILE, data.to_string())


    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue

    except Exception as error:
        print(error.args[0])
        time.sleep(5.0)
        continue

    time.sleep(5.0)

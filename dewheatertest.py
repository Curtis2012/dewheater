#
#  dew-heater-test
#
# Dew heater test utility
#


import sys
import RPi.GPIO as GPIO
import time
import json
#import Adafruit_DHT
from meteocalc import dew_point
# Added for BME
import smbus2
import bme280

# Commented out, left for ref.
#DHT_SENSOR = Adafruit_DHT.DHT22

# Initialize BME
port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

ON = 1
OFF = 0

class ConfigClass:

    def loadConfig(self):
        try:
            with open('/home/pi/dewheater/dewheaterconfig.json', 'r') as f:
                self.configFile = json.load(f)
                print(json.dumps(self.configFile, indent=4, sort_keys=True))
                self.dewHeaterPin = self.configFile['dewHeaterPin']
                self.dewHeaterOnOffDelay = self.configFile['dewHeaterOnOffDelay']
                #self.dhtPin = self.configFile['dhtPin']
        except:
            sys.stderr.flush()
            sys.exit("\nError opening or parsing config file, exiting")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.dewHeaterPin, GPIO.OUT)
        print("dew-heater-test started.")
        return (True)

config = ConfigClass()

class DewHeaterClass:

    def __init__(self):
        self.status = OFF

    def on(self):
            if (self.status == ON):
                print("Dew heater already on, 'on' command ignored")
                return
            else:
                GPIO.output(config.dewHeaterPin, GPIO.HIGH)
                self.status = ON
                print("Dew heater on")

    def off(self):

            if (self.status == OFF):
                print("Dew heater already off, 'off' command ignored")
                return
            else:
                GPIO.output(config.dewHeaterPin, GPIO.LOW)
                self.status = OFF
                print("Dew heater off")

    def checkTemp(self):
       # grab BME280 readings
        data = bme280.sample(bus, address, calibration_params)
        self.humidity = data.humidity
        self.temperature = data.temerature
        print("Temp = %3.1fC Humidity %3.1f%%" % (temperature, humidity))

dewHeater = DewHeaterClass()


def main():

    config.loadConfig()
    while True:
        dewHeater.checkTemp()   # read and display temps for reference
        dewHeater.on()
        print("On for %i seconds..." % config.dewHeaterOnOffDelay)
        time.sleep(config.dewHeaterOnOffDelay)
        dewHeater.off()
        print("Off for %i seconds..." % config.dewHeaterOnOffDelay)
        time.sleep(config.dewHeaterOnOffDelay)

if __name__ == "__main__":
    main()
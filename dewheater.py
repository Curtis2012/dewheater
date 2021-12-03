#
#  dew-heater-control
#
#  2021-10-18 C. Collins created
#
#  This code assumes a hacked USB dew heater. The hack consists of nothing more than removing the switch from the dew heater
#  and directly connecting the power leads to the NO side of a relay.
#
#  A DHT sensor is used to monitor temperature vs dew point. When dew point cut-in set point is reached then the dew heater relay is closed.
#  When the cut-out set point is reached the dew heater relay is opened. Both the cut-in and cut-out set points are defined in the configuration file as
#  an offset from degrees Celsius of the dew point. This method of temperature control is primitive, but is sufficient for this purpose.
#
#
#  The design is based upon a dew heater like the one at the link below:
#
#         https://www.amazon.com/dp/B08LGN222F?psc=1&ref=ppx_yo2_dt_b_product_details
#
#
#

import sys
import RPi.GPIO as GPIO
import time
import json
import Adafruit_DHT
from meteocalc import dew_point

DHT_SENSOR = Adafruit_DHT.DHT22
ON = 1
OFF = 0


class ConfigClass:

    def loadConfig(self):
        try:
            with open('/home/pi/dewheater/dewheaterconfig.json', 'r') as f:
                self.configFile = json.load(f)
                print(json.dumps(self.configFile, indent=4, sort_keys=True))
                self.debug = self.configFile['debug']
                self.dhtPin = self.configFile['dhtPin']
                self.dewHeaterPin = self.configFile['dewHeaterPin']
                self.dewHeaterCutinOffset = self.configFile['dewHeaterCutinOffset']
                self.dewHeaterCutoutOffset = self.configFile['dewHeaterCutoutOffset']
                self.dewHeaterSafetyTempOFF = self.configFile['dewHeaterSafetyTempOFF']
                self.dewHeaterMaxTemp = self.configFile['dewHeaterMaxTemp']
                self.dewHeaterMinTemp = self.configFile['dewHeaterMinTemp']
                self.dewPtCheckDelay = self.configFile['dewPtCheckDelay']

        except:
            sys.stderr.flush()
            sys.exit("\nError opening or parsing config file, exiting")

        return (True)

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.dewHeaterPin, GPIO.OUT)
        GPIO.setup(config.dhtPin, GPIO.IN)
        dewHeater.cycleRelay()    # cycle the relay just as a start up test, if you dont hear it clicking then it aint working
        dewHeater.shutoff = False


config = ConfigClass()


class DewHeaterClass:

    def __init__(self):
        self.status = OFF

    def on(self, force=False):
        if (self.shutoff == True):
            sys.stderr.write("'On' command ignored: ")
            sys.stderr.write("Safety temperature exceeded, dew heater shut down, resolve issue then restart")
            return

        if (force == False and self.status == ON):
            print("Dew heater already on, 'on' command ignored")
            return

        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        self.status = ON
        print("Dew heater on")

        return


    def off(self, force=False):

        if (self.shutoff == True):
            sys.stderr.write("'Off' command ignored: ")
            sys.stderr.write("Saftey temperature exceeded, dew heater shut down, resolve issue then restart")
            return

        if (force == False and self.status == OFF):
            print("Dew heater already off, 'off' command ignored")
            return

        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        self.status = OFF
        print("Dew heater off")
        return

    def cycleRelay(self):
        self.status = OFF
        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        return

    def checkTemps(self):
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, config.dhtPin)
        if (temperature is not None):
            if (temperature > config.dewHeaterSafetyTempOFF):
                sys.stderr.write("Saftey temperature exceeded, shutting down dew heater, restart of service required to clear shutdown")
                self.off(True)
                self.shutoff = True
                return()
            if (temperature > config.dewHeaterMaxTemp):
                print("Dew heater max temp reached, turning dew heater off")
                self.off(True)
                return ()
            if (temperature < config.dewHeaterMinTemp):
                print("Dew heater min temp reached, turning dew heater on")
                self.off(True)
                return ()
        return

dewHeater = DewHeaterClass()


def checkDewPoint():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, config.dhtPin)
    if humidity is not None and temperature is not None:
        if ((temperature >= -40) and (temperature <= 80)) and ((humidity >= 0) and (humidity <= 100)):
            dp = dew_point(temperature, humidity)
        else:
            sys.stderr.write("\nError calculating dew point, input out of range:")
            sys.stderr.write("\nTemp = %3.1fC" % temperature)
            sys.stderr.write("\nHumdidity = %3.1f%%\n" % humidity)
            return

        if (config.debug): print("Temp = %3.1fC Humidity %3.1f%% Dew Point = %3.1fC" % (temperature, humidity, dp.c))

        if temperature <= (dp.c + config.dewHeaterCutinOffset):
            if (dewHeater.status == OFF):
                print("Dew point reached, turning dew heater on")
                dewHeater.on()

        if temperature >= (dp.c + config.dewHeaterCutoutOffset):
            if (dewHeater.status == ON):
                print("Dew point exceeded, turning dew heater off")
                dewHeater.off()
    else:
        sys.stderr.write("No reading from DHT22 module")

    return


def main():
    config.loadConfig()
    config.setup()

    while True:
        checkDewPoint()
        dewHeater.checkTemps()
        time.sleep(config.dewPtCheckDelay)

if __name__ == "__main__":
    main()

#
#  dew-heater-control
#
#  2021-10-18 C. Collins created
#
#  This code assumes a hacked USB dew heater. The hack consists of nothing more than removing the switch from the dew heater
#  and directly connecting the power leads to the NO side of a relay. This same logic should work with resistor based designs too, but this  has not yet been tested.
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

    def __init__(self):
        self.loadConfig()
        self.setup()

    # def checkConfig(self):
    # future edits...

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
                self.dewHeaterMaxTemp = self.configFile['dewHeaterMaxTemp']
                self.dewHeaterMinTemp = self.configFile['dewHeaterMinTemp']
                self.dewPtCheckDelay = self.configFile['dewPtCheckDelay']
                self.fakeDewPoint = self.configFile['fakeDewPoint']
                self.fakeDewPointSamples = self.configFile['fakeDewPointSamples']
                self.invertOnOff = self.configFile['invertOnOff']
                if (self.invertOnOff):
                    self.relayOn = GPIO.LOW
                    self.relayOff = GPIO.HIGH
                else:
                    self.relayOn = GPIO.HIGH
                    self.relayOff = GPIO.LOW

        except:
            sys.stderr.flush()
            sys.exit("\nError opening or parsing config file, exiting")

        return (True)

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dewHeaterPin, GPIO.OUT)
        GPIO.setup(self.dhtPin, GPIO.IN)


config = ConfigClass()


class conditionsClass:

    def __init__(self):
        self.fakeDewPointCounter = 0

    def update(self):
        self.humidity, self.temperature = Adafruit_DHT.read_retry(DHT_SENSOR, config.dhtPin)

        if self.humidity is not None and self.temperature is not None:
            if ((self.temperature >= -40) and (self.temperature <= 80)) and (
                    (self.humidity >= 0) and (self.humidity <= 100)):
                self.temp_actual = self.temperature  # set actual temp for use when fakeDewPoint is true
                self.dewPoint = dew_point(self.temperature, self.humidity)

                if (config.fakeDewPoint):
                    self.fakeDewPointCounter += 1
                    if (self.fakeDewPointCounter < config.fakeDewPointSamples):
                        self.temperature = self.dewPoint.c - 2
                    else:
                        config.fakeDewPoint = False  # fake done, clear flag

                if (self.temperature <= self.dewPoint.c + config.dewHeaterCutinOffset):
                    self.dewPointMet = True
                else:
                    if (self.temperature >= self.dewPoint.c + config.dewHeaterCutoutOffset):
                        self.dewPointMet = False
            else:
                sys.stderr.write("\nError calculating dew point, input out of range:")
                sys.stderr.write("\nTemp = %3.1fC" % self.temperature)
                sys.stderr.write("\nHumdidity = %3.1f%%\n" % self.humidity)
                return


conditions = conditionsClass()


class DewHeaterClass:

    def __init__(self):
        self.cycleRelay()  # cycle the relay just as a start up test, if you dont hear it clicking then it aint working
        self.status = OFF
        self.off(True)  # force off in case left on by previous session
        self.minTempOn = False
        self.maxTempOff = False
        self.temp_actual = 0.0

    def on(self, forced=False):

        if (forced):
            GPIO.output(config.dewHeaterPin, config.relayOn)
            self.status = ON
            return

        if (self.maxTempOff):
            print("Max temp reached, 'on' command ignored")
            return

        GPIO.output(config.dewHeaterPin, config.relayOn)
        self.status = ON


    def off(self, forced=False):
        if (forced):
            GPIO.output(config.dewHeaterPin, config.relayOff)
            self.status = OFF
            return

        if (self.minTempOn):
            print("Min temp on, 'off' command ignored")
            return


        GPIO.output(config.dewHeaterPin, config.relayOff)
        self.status = OFF


    def cycleRelay(self):
        self.status = OFF
        GPIO.output(config.dewHeaterPin, config.relayOn)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, config.relayOff)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, config.relayOn)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, config.relayOff)


    def checkTemps(self):
        conditions.update()

        if (conditions.temp_actual > config.dewHeaterMaxTemp):  # use temp_actual for when fakeDewPoint is set
            self.maxTempOff = True
            self.off(True)
            return ()
        else:
            if (self.maxTempOff):
                self.maxTempOff = False
                self.on(False)

        if (conditions.temperature < config.dewHeaterMinTemp):
            self.minTempOn = True
            self.on(False)
            return ()
        else:
            if (self.minTempOn):
                self.minTempOn = False
                self.off(False)
                return

        if conditions.dewPointMet:
            if (not self.maxTempOff):
                self.on(False)
        else:
            if (not self.minTempOn):
                self.off(False)


dewHeater = DewHeaterClass()


def dispalySatus():
    print("====================================================")
    print("Temp = %3.1fC, temp_actual = %3.1fC, Humidity %3.1f%% Dew Point = %3.1fC" % (
        conditions.temperature, conditions.temp_actual, conditions.humidity, conditions.dewPoint.c))
    print("Dew heater state =", end=" ")
    if (dewHeater.status == ON):
        print("ON", end=", ")
    else:
        print("OFF", end=", ")
    print("invertOnOff = %s" % (config.invertOnOff))
    print("MinTempOn set point = %3.1fC, MinTempOn = %s" % (config.dewHeaterMinTemp, dewHeater.minTempOn))
    print("MaxTempOff set point = %3.1fC, MaxTempOff = %s" % (config.dewHeaterMaxTemp, dewHeater.maxTempOff))
    print("Dew point met = %s, fakeDewPoint = %s, fakeDewPointCounter = %i " % (conditions.dewPointMet, config.fakeDewPoint, conditions.fakeDewPointCounter))
    print("====================================================")


def main():
    while True:
        dewHeater.checkTemps()
        dispalySatus()
        time.sleep(config.dewPtCheckDelay)


if __name__ == "__main__":
    main()

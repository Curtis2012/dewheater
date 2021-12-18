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

        except:
            sys.stderr.flush()
            sys.exit("\nError opening or parsing config file, exiting")

        return (True)

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.dewHeaterPin, GPIO.OUT)
        GPIO.setup(config.dhtPin, GPIO.IN)




config = ConfigClass()


class DewHeaterClass:

    def __init__(self):
        self.cycleRelay()    # cycle the relay just as a start up test, if you dont hear it clicking then it aint working
        self.status = OFF
        self.off(True)    # force off in case left on by previous session
        self.minTempOn = False
        self.maxTempOff = False
        self.temp_actual = 0.0

    def on(self, forced=False):

        if (forced):
            GPIO.output(config.dewHeaterPin, GPIO.HIGH)
            self.status = ON
            print("Dew heater on")
            return

        if (self.status == ON):
            print("Dew heater already on, 'on' command ignored")
            return

        if (self.maxTempOff):
            print("Dew heater maxTempOff reach, 'on' command ignored")
            return

        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        self.status = ON
        print("Dew heater on")


    def off(self, forced=False):

        if (forced):
            GPIO.output(config.dewHeaterPin, GPIO.LOW)
            self.status = OFF
            print("Dew heater off")
            return

        if (self.status == OFF):
            print("Dew heater already off, 'off' command ignored")
            return

        if (self.minTempOn):
            print("Dew heater minTempOn reached, 'off' command ignored")
            return

        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        self.status = OFF
        print("Dew heater off")

    def cycleRelay(self):
        self.status = OFF
        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(config.dewHeaterPin, GPIO.LOW)

    def checkTemps(self):
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, config.dhtPin)
        if (temperature is not None):

            if (self.temp_actual > config.dewHeaterMaxTemp):      # use temp_actual for when fakeDewPoint is set
                print("Dew heater max temp set point exceeded, turning dew heater off")
                self.maxTempOff = True
                self.off(True)
                return ()
            else:
                if (self.maxTempOff == True):
                    self.maxTempOff = False
                    self.on(False)

            if (temperature < config.dewHeaterMinTemp and self.status == OFF):
                print("Dew heater min temp set point reached, turning dew heater on")
                self.minTempOn = True
                self.on(False)
                return ()
            else:
                if (self.minTempOn == True):
                    self.minTemp = False
                    self.off(False)
                return

    def checkDewPoint(self):
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, config.dhtPin)
        self.temp_actual = temperature   # set actual temp for use when fakeDewPoint is true

        if humidity is not None and temperature is not None:
            if ((temperature >= -40) and (temperature <= 80)) and ((humidity >= 0) and (humidity <= 100)):
                dp = dew_point(temperature, humidity)
                if (config.fakeDewPoint):
                    temperature = dp.c - 2
            else:
                sys.stderr.write("\nError calculating dew point, input out of range:")
                sys.stderr.write("\nTemp = %3.1fC" % temperature)
                sys.stderr.write("\nHumdidity = %3.1f%%\n" % humidity)
                return

            if (config.debug):
                print("====================================================")
                print("Temp = %3.1fC, temp_actual = %3.1fC, Humidity %3.1f%% Dew Point = %3.1fC" % (temperature, self.temp_actual, humidity,  dp.c))
                print("Dew Heater State = %i, Min Temp On = %s, Max Temp Off = %s" % (self.status, self.minTempOn, self.maxTempOff))
                print("minTempOn = %3.1fC, maxTempOff = %3.1fC, fakeDewPoint = %s" % (config.dewHeaterMinTemp, config.dewHeaterMaxTemp, config.fakeDewPoint))
                print("====================================================")

            if temperature <= (dp.c + config.dewHeaterCutinOffset):
                if (self.status == OFF and not self.maxTempOff):
                    print("Dew point reached, turning dew heater on")
                    self.on(False)

            if temperature >= (dp.c + config.dewHeaterCutoutOffset):
                if (self.status == ON and not self.minTempOn):
                    print("Dew point exceeded, turning dew heater off")
                    self.off(False)
        else:
            sys.stderr.write("No reading from DHT22 module")


def main():
    config.loadConfig()
    config.setup()
    dewHeater = DewHeaterClass()

    while True:
        dewHeater.checkDewPoint()
        dewHeater.checkTemps()
        time.sleep(config.dewPtCheckDelay)

if __name__ == "__main__":
    main()

#
#  dew-heater-test
#
# Dew heater test utility
#


import sys
import RPi.GPIO as GPIO
import time
import json

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

dewHeater = DewHeaterClass()


def main():

    config.loadConfig()
    while True:
        dewHeater.on()
        print("On for %i seconds..." % config.dewHeaterOnOffDelay)
        time.sleep(config.dewHeaterOnOffDelay)
        dewHeater.off()
        print("Off for %i seconds..." % config.dewHeaterOnOffDelay)
        time.sleep(config.dewHeaterOnOffDelay)

if __name__ == "__main__":
    main()
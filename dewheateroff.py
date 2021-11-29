#
#  dew-heater-test
#
# Dew heater turn off relay
#


import sys
import RPi.GPIO as GPIO
#import time
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

    def off(self):
        GPIO.output(config.dewHeaterPin, GPIO.LOW)
        self.status = OFF
        print("Dew heater off")


dewHeater = DewHeaterClass()


def main():
    config.loadConfig()
    print("Turning dew heater OFF")
    dewHeater.off()


if __name__ == "__main__":
    main()

# dewheater

Dew heater controller for allksycam.


This code controls a hacked USB powered dew heater or resistor based design. The dew heater hack consists of nothing more than removing the switch from the dew heater 
and directly connecting the power leads to the NO side of a relay. This code should work with other designs also, but this has not yet been tested.

A DHT sensor is used to monitor temperature vs dew point. When dew point cut-in set point is reached then the dew heater relay is closed.
When the cut-out set point is reached the dew heater relay is opened. Both the cut-in and cut-out set points are defined in the configuration file as
an offset from degrees Celsius of the dew point. This offset allows for a rough degree of hysterisis control. This method of temperature control is primitive, but is sufficient for this purpose.

The hacked dew heater is based upon a dew heater like the one at the link below:

   https://www.amazon.com/dp/B08LGN222F?psc=1&ref=ppx_yo2_dt_b_product_details
   
   
   
Configuration file options:


  "debug": true                        # debug on/off
  
  "dhtPin": 4,                         # DHT sensor GPIO pin, BCM mode
  
  "dewHeaterPin": 23,                  # Dew Heater relay control pin, BCM mode
  
  "dewHeaterCutinOffset": 1.0,         # Dew Heater cut-in (on) offset in degrees C. This offset is relative to the dew point. 
  
  "dewHeaterCutoutOffset": 1.0,        # Dew Heater cut-out (off) offset in degrees C. This offset is relative to the dew point.

  "dewHeaterMaxTemp": 35,              # Dew Heater max temp, dew heater relay is opened if this temp is reached, but conrol is not shutdown thus the dew heater relay may be 						closed later if a set point is met. 
  
  "dewHeaterMinTemp": 3,               # Dew Heater min temp, dew heater relay closed at this temp regardless of dew point calculations. This parameter is intended to force
                                        the dew heater on in cold conditions regardless of whether the dew point has been reached.

  "dewHeaterOnOffDelay": 5,            # Delay between on/off cycle, used only by dewheatertest.py
  
  "dewPtCheckDelay": 5                 # Time in seconds to wait between each dew point calculation (this includes reading the DHT sensor and making the dew point calculation).

  "fakeDewPoint": false                # enables dew point faking for test purposes. If enabled, temperature will be set to 
                                         the dew point minus 2C.

  "fakeDewPointSamples": 20            # number of samples for which dew point will be faked, after that samples are normal.

  "invertOnOff": false                 # invert hi/low relay control signals for relay on/off to support relays wired to close on low signal and open on high
  
  
DHT Sensor Placement. The current code assumes that the DHT sensor is under the acrylic dome. This allows for monitoring of
actual conditions under the dome. The dew point offset values are implemented so that cut in/out points can be offset 
relative to what works best for your installation to keep the dome dew free, and to adjust for hysteresis (which is considerable
in my configuration). Note that features like max temp shutoff will only work properly with the DHT sensor under 
the acrylic dome. I plan to add a second DHT sensor to sense outside ambient conditions too.

  
  Modules

	dewheater.py  	   The main module, designed to be run as a service

	dewheatertest.py   Simple timed on/of test script. Delay between on/off cycle is controlled by "dewHeaterOnOffDelay" parameter above.

	dewheateron.py     Closes dew heater relay unconditionally (no cut in/out points, no timer). CAUTION: It does NOT open the relay again!

	dewheateroff.py    Opens dew heater relay unconditionally (no cut in/out points, no timer).
	
	

Dew Heater Service Install

The following instructions were created by installing the dewheater service on a fresh install of Raspian Buster.  This installation assumes you are using python3 and pip3

 1   Install source code
 1.1  Create dewheater directory: mkdir dewheater below $HOME 
 1.2  Copy the following files to dewheater directory
        dewheaterconfig.json
        dewheateron.py
        dewheater.service
        dewheateroff.py
        dewheater.py
        dewheatertest.py

 2  Install libraries
 2.1  sudo apt update
 2.2  sudo apt upgrade
 2.3  Adafruit_DHT

 2.3.1  Follow instructions at this link: https://learn.adafruit.com/adafruit-io-basics-temperature-and-humidity/python-setup

 2.4  Install meteocalc
 2.4.1  sudo pip3 install meteocalc
 2.5  Other libraries referenced (sys, json, GPIO, and time) should not require an explicit install
 3  Configure Service
 3.1  Copy dewheater.service from dewheater directory to /lib/systemd/system/
 3.2  sudo cp /home/pi/dewheater/dewheater.service /lib/systemd/system/
 3.3  Start dewheater service
 3.4  sudo systemctl start dewheater
 3.5  Enable dewheater service to start at boot
 3.6  sudo systemctl enable dewheater
 3.7  Check status of dewheater service
 3.8  sudo systemctl status dewheater

Example output:

● dewheater.service - dewheater
Loaded: loaded (/lib/systemd/system/dewheater.service; disabled; vendor preset: enabled)
Active: active (running) since Fri 2022-01-21 17:44:20 PST; 6s ago
Main PID: 30059 (python3)
Tasks: 1 (limit: 2062)
CGroup: /system.slice/dewheater.service
└─30059 /usr/bin/python3 /home/pi/dewheater/dewheater.py



  




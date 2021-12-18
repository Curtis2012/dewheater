# dewheater (beta)

Dew heater controller for allksycam.


Help with testing requested! I just built this code and have not yet tested it extensively. Also testing in multiple climates would be good. So, pitch in and test please!


This code controls a hacked USB powered dew heater. The hack consists of nothing more than removing the switch from the dew heater 
and directly connecting the power leads to the NO side of a relay. This code should work with resistore based
designs also, but this has not yet been tested.


A DHT sensor is used to monitor temperature vs dew point. When dew point cut-in set point is reached then the dew heater relay is closed.
When the cut-out set point is reached the dew heater relay is opened. Both the cut-in and cut-out set points are defined in the configuration file as
an offset from degrees Celsius of the dew point. This offset allows for a rough degree of hysterisis control. This method of temperature control is primitive, but is sufficient for this purpose.

The design is based upon a dew heater like the one at the link below:

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

  "fakeDewPoint": false                # enables dew point faking for test purposes. If enable temperature will be set to 
                                          the dew point minus 2C. 
  
  
  
  Modules

	dewheater.py  	   The main module, designed to be run as a service

	dewheatertest.py   Simple timed on/of test script. Delay between on/off cycle is controlled by "dewHeaterOnOffDelay" parameter above.

	dewheateron.py     Closes dew heater relay unconditionally (no cut in/out points, no timer). CAUTION: It does NOT open the relay again!

	dewheateroff.py    Opens dew heater relay unconditionally (no cut in/out points, no timer).
	
	



  




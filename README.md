# dewheater

Dew heater controller for allksycam

This code controls a hacked USB dew heater. The hack consists of nothing more than removing the switch from the dew heater 
and directly connecting the power leads to the NO side of a relay.

A DHT sensor is used to monitor temperature vs dew point. When dew point cut-in set point is reached then the dew heater relay is closed.
When the cut-out set point is reached the dew heater relay is opened. Both the cut-in and cut-out set points are defined in the configuration file as
an offset from degrees Celsius of the dew point. This method of temperature control is primitive, but is sufficient for this purpose.

The design is based upon a dew heater like the one at the link below:

   https://www.amazon.com/dp/B08LGN222F?psc=1&ref=ppx_yo2_dt_b_product_details
   
Configuration file options:


  "debug": true                        # debug on/off
  
  "dhtPin": 4,                         # DHT sensor GPIO pin, per BCM 
  
  "dewHeaterPin": 23,                  # Dew Heater relay control pin, per BCM
  
  "dewHeaterCutinOffset": 1.0,         # Dew Heater cut-in (on) offset in degrees C
  
  "dewHeaterCutoutOffset": 1.0,        # Dew Heater cut-out (off) offset in degrees C
  
  "dewHeaterSafetyTempOFF": 35,        # Dew Heater safety shut off temp in degrees C, if reached the dew heater control is shutdown with heater off until service restarted
  
  "dewHeaterMaxTemp": 35,              # Dew Heater max temp, dew heater relay is opened if this temp is reached, but conrol is not shutdown
  
  "dewHeaterMinTemp": 3,               # Dew Heater min temp, dew heater relay closed at this temp regardless of dew point calculations. This parameter is intended to force
                                       #    the dew heater on in cold conditions
				       
  "dewHeaterOnOffDelay": 5,            # Delay between on/off cycle, used only by dewheatertest.py
  
  "dewPtCheckDelay": 5                 # Time in seconds to wait between read of DHT sensor and dew point calculation
  




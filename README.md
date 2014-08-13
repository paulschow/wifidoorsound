# WifiDoorsound #
# README #

### What is this repository for? ###

* Wifi fork of Doorsound
* Uses wifi to tell when someone gets home, then plays a sound when they walk in the door
* (https://github.com/paulschow/doorsound)[https://github.com/paulschow/doorsound]

### How do I get set up? ###

* Get Raspberry Pi
* Clone files
* Pair bluetooth devices
* Use a sqlite db editor to change the macs.db
* Add their MAC addresses into macs.db with a song
* Attach reed switch to GPIO pin 14
* Optinally attach LED(s) to pin 15
* Run bluepinger.py to start the pinging
* Run doorcheck.py monitor the door

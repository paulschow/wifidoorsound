#! /usr/bin/env python

# doorcheck.py looks for the door opening by reading an infafred sensor
# it need to be run as sudo for GPIO access
# I usually run this as:
# sudo nohup python doorcheck.py &

import sqlite3
from pygame import mixer
from pygame import time
#import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# Set pin 14 as GPIO input with a pull up resistor
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# connect to the database
conn = sqlite3.connect('gone.db')
# the cursor is c
c = conn.cursor()

# initalize pygame mixer for audio
mixer.init()

#counter = 0
while True:
    # Wait for the rising edge
    # AKA detect when something gets too close
    print "Waiting for sensor event"
    GPIO.wait_for_edge(14, GPIO.RISING)
    print '\033[1;32m Object Detected \033[00m'
    search = 1  # 1 is the last marker
    query = "SELECT * FROM gone WHERE last=? ORDER BY {0}".format('Last')
    c.execute(query, (search,))
    for row in c:
        #print row
        print 'Last person was:', row[4]
        print 'MP3 file is:', row[3]
        # Remove their last person tag
        keyid = row[0]
        c.execute("UPDATE gone SET Last = 0 WHERE key = %d" % keyid)
        conn.commit()  # commit changes to the db

        mixer.music.load(row[3])  # load the file for the person
        mixer.music.play()  # play the loaded file
        #time.sleep(10)
        while mixer.music.get_busy():
            time.Clock().tick(0)
        print "Sound played! \n"
        #print counter

GPIO.cleanup()

#! /usr/bin/env python

import sqlite3
import pygame
import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Set pin 14 as GPIO input with a pull up resistor
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# connect to the database
conn = sqlite3.connect('gone.db')
# the cursor is c
c = conn.cursor()

# initalize pygame mixer for audio
pygame.mixer.init()

#counter = 0
while True:
    # Wait for the rising edge
    # AKA detect when something gets too close
    print "Waiting for sensor event"
    GPIO.wait_for_edge(14, GPIO.RISING)
    print ' Object Detected '
    search = 1  # 1 is the last marker
    query = "SELECT * FROM gone WHERE last=? ORDER BY {0}".format('Last')
    c.execute(query, (search,))
    for row in c:
        #print row
        print 'Last person was:', row[4]
        print 'MP3 file is:', row[3]
        pygame.mixer.music.load(row[3])  # load the file for the person
        pygame.mixer.music.play()  # play the loaded file
        #time.sleep(10)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(0)
        print "Sound played! \n"
        #print counter

GPIO.cleanup()

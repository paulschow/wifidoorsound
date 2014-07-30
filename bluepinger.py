#!/usr/bin/env python

# Modified from doorpinger.py
# This one uses bluetooth instead of wifi

# You have to pair the devices and add them to macs.db

# Note: Requires sqlite3 and python bluez

#import os
#import socket
#import struct
#import select
#import time
import sqlite3
import subprocess
import re
import bluetooth
import multiprocessing
import RPi.GPIO as GPIO


# connect to the database
conn = sqlite3.connect('macs.db')
# the cursor is c
c = conn.cursor()

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)
# Status LED is in pin 15
GPIO.setup(15, GPIO.OUT)

#log = open('track1.txt', 'w')  # open a text file for logging
#print log  # print what the log file is
#log.write('Time,IP,Ping\n')  # write to log


def newping(btaddr):
# Adapted from
# https://github.com/jeffbryner/bluetoothscreenlock
# Basically just tries to connect to the device
# And reports if it is there or not
    btsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    #print("searching for device..."), btaddr
    try:
        btsocket.connect((btaddr, 3))
        if btsocket.send("hey"):
            #print("Device Found")
            gstatus.value = 1
            return 1
            btsocket.close()
    except bluetooth.btcommon.BluetoothError:
        print("Bluetooth Error. Is device paired?")
        gstatus.value = 0
        return 0


def pingtimer(mac):
# This is a pretty awful use of multiprocessing to time the pings
# But it works pretty well
# Maybe later I will use pools or something
    p = multiprocessing.Process(target=newping, name="ping", args=(mac,))
    p.start()
    p.join(4)  # Timeout after seconds
    #print result
    if p.is_alive():
        #print "Connection Timed Out"
        # Terminate foo
        gstatus.value = 0
        p.terminate()
        p.join()


def l2ping(phonemac):
# Bluetooth ping command
# Uses l2ping linux command
# Returns a 0 if mac is gone
# Returns a 1 if mac is here
# This takes ~5 seconds per device, there's probably a better way
# Probably takes even longer on rpi
    #p = os.popen("sudo l2ping -t 1 -c 1 E8:99:C4:D8:C9:91")
    #subprocess.call("ls")
    #ping = p.read()
    #print ping
    #subprocess.call("l2ping")
    #phonemac = "E8:99:C4:D8:C9:91"
    p = subprocess.Popen(["sudo", "l2ping", "-t 1", "-c 1", phonemac],
    stdout=subprocess.PIPE)
    # run the l2ping (bluetooth ping) command for phonemac
    # with timeout 1 second
    # and count 1 (a single ping)
    #p = subprocess.Popen("date", stdout=subprocess.PIPE, shell=True)
    (ping, err) = p.communicate()
    return regping(ping)


def regping(ping):
# URL that generated this code:
# http://txt2re.com
# Uses regular expressions to look through l2ping result
# This is pretty awful, but it works

    txt = str(ping)

    re1 = '.*?'     # Non-greedy match on filler
    re2 = '( 1 received)'     # Command Seperated Values 1

    rg = re.compile(re1 + re2, re.IGNORECASE | re.DOTALL)
    m = rg.search(txt)
    if m:
        csv1 = m.group(1)
        #print "(" + csv1 + ")" + "\n"
    try:
        if csv1 == " 1 received":
            print "Ping received"
            return 1
        else:
            print "How did you even get this error"
            return 0
    except NameError:
        print "No Ping received"
        return 0


# function for marking someone as gone in the db
def db_gone(keyid, prestatus):
    if prestatus == 0:
        # Already marked as gone
        # Do nothing
        return
    else:
        # They where here before
        # Mark them as gone
        #print "key = %d" % keyid
        #c.execute("SELECT * FROM gone")
        # Also mark them as not being last
        c.execute("UPDATE gone SET Last = 0 WHERE key = %d" % keyid)
        c.execute("UPDATE gone SET Status = 0 WHERE key = %d" % keyid)
        conn.commit()  # commit changes to the db
        # Turn the LED
        print "LED OFF"
        GPIO.output(15, GPIO. LOW)
        #print "Total number of rows updated :", conn.total_changes


def db_here(keyid, prestatus):
    #print "key = %d" % keyid
    #print "Previous Status is  = %d" % prestatus
    if prestatus == 0:
        # They just showed up!
        print '\033[1;32m Person Arrived \033[00m'
        # Set everyone else to not last
        c.execute("UPDATE gone SET Last = 0 WHERE key != %d" % keyid)
        # Set them as the last person
        c.execute("UPDATE gone SET Last = 1 WHERE key = %d" % keyid)
        # Turn on LED
        print "LED %d ON" % (15)
        GPIO.output(15, GPIO. HIGH)
        conn.commit()  # commit changes to the db
    else:
        print "They were already here"

    #c.execute("SELECT * FROM gone")
    c.execute("UPDATE gone SET Status = 1 WHERE key = %d" % keyid)
    conn.commit()  # commit changes to the db
    #print "Total number of rows updated :", conn.total_changes

#Main loop
if __name__ == '__main__':
    # Set up shared status variable
    gstatus = multiprocessing.Value('i', 0)
    #pool = multiprocessing.Pool(processes=1)
    #counter = 0
    #Loop for awhile
    while True:
        c.execute("SELECT * FROM gone")
        rows = c.fetchall()
        countrow = len(rows)  # Counts the number of rows
        print "Number of Rows:", countrow
        x = countrow
        for row in rows:
            #print "MAC = %s" % row[5]
            #print "Name = %s" % row[4]
            #status = l2ping(row[5])  # ping the MAC, get status
            #status = newping(row[5])  # ping the MAC, get status
            pingtimer(row[5])  # ping the MAC, get status
            if gstatus.value == 1:
                #print "They're here!"
                print "\033[94m %s is Here \033[00m" % row[4]
                # Send the row to db_here
                db_here(row[0], row[2])
                print " "
                #print "Total number of rows updated :", conn.total_changes
            else:
                #print "Not Here"
                # Send the row to db_gone
                print "\033[91m %s is Not Here \033[00m" % row[4]
                print " "
                db_gone(row[0], row[2])
        #counter = counter + 1
        print "\033[33m Done \033[00m \n"

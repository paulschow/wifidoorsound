#!/usr/bin/env python

# Modified from doorpinger.py
# This one uses bluetooth instead of wifi

# You have to pair the devices and add them to macs.db

# Note: Requires sqlite3 I think

#import os
#import socket
#import struct
#import select
#import time
import sqlite3
import subprocess
import re

# connect to the database
conn = sqlite3.connect('macs.db')
# the cursor is c
c = conn.cursor()

#log = open('track1.txt', 'w')  # open a text file for logging
#print log  # print what the log file is
#log.write('Time,IP,Ping\n')  # write to log

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

    #p.poll()
    #print p.returncode
    #print str(ping)


def regping(ping):
# URL that generated this code:
# http://txt2re.com

    txt = str(ping)

    re1 = '.*?'	 # Non-greedy match on filler
    re2 = '( 1 received)'	 # Command Seperated Values 1

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
        c.execute("UPDATE gone SET Status = 0 WHERE key = %d" % keyid)
        conn.commit()  # commit changes to the db
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
        conn.commit()  # commit changes to the db
    else:
        print "They were already here"

    #c.execute("SELECT * FROM gone")
    c.execute("UPDATE gone SET Status = 1 WHERE key = %d" % keyid)
    conn.commit()  # commit changes to the db
    #print "Total number of rows updated :", conn.total_changes

#Main loop
if __name__ == '__main__':
    counter = 0
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
            status = l2ping(row[5])  # ping the MAC, get status
            # 1 is here, 0 is gone or error
            #print "status is %s" % status
            if status == 1:
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
        counter = counter + 1
        print "\033[33m Done \033[00m \n"

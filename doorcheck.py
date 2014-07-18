#!/usr/bin/env python

import sqlite3
import pygame
import time

# connect to the database
conn = sqlite3.connect('gone.db')
# the cursor is c
c = conn.cursor()

# initalize pygame mixer for audio
pygame.mixer.init()


def play_song(song):
    # Let's play their song
    print 'MP3 file is:', song
    pygame.mixer.music.load(song)  # load the file for the person
    pygame.mixer.music.play()  # play the loaded file
    time.sleep(30)
    #pygame.mixer.music.stop()
    #while pygame.mixer.music.get_busy():
    #    pygame.time.Clock().tick(0)

#Main loop
if __name__ == '__main__':
    c.execute("SELECT * FROM gone")
    rows = c.fetchall()
    countrow = len(rows)  # Counts the number of rows
    print "Number of Rows:", countrow
    for row in rows:
        print row[1]
        #status = verbose_ping(row[5])  # ping the IP, get status
        # 1 is here, 0 is gone or error
        last = row[1]
        print "Last is %d" % last
        if last == 1:
            #print "They're here!"
            print "The Last Person Was %s" % row[4]
            play_song(row[3])
            # Send the row to db_here
            #db_here(row[0], row[2], row[3])
            #print "Total number of rows updated :", conn.total_changes
        else:
            #print "Not Here"
            # Send the row to db_gone
            print "Not Here"
            #db_gone(row[0])
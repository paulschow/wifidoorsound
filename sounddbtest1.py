import sqlite3
import pygame  # for audio
import time
#import wave

column_name = 'Last'

# connect to the database
conn = sqlite3.connect('gone.db')
# the cursor is c
c = conn.cursor()

pygame.mixer.init()

#print 'Searching in', column_name
#search = raw_input("Enter Search Term: ")
search = 0  # 1 is the last marker
query = "SELECT * FROM gone WHERE last=? ORDER BY {0}".format(column_name)
c.execute(query, (search,))
for row in c:
    print row
    print 'Last person was:', row[4]
    print 'MP3 file is:', row[3]
    pygame.mixer.music.load(row[3])  # load the file for the person
    pygame.mixer.music.play()  # play the loaded file

# keeps from exiting before the sound ends
if pygame.mixer.music.get_busy():
    #pygame.time.Clock().tick(10)
    time.sleep(30)  # limit it to 30 seconds


conn.commit()  # commit the changes to the db
conn.close()  # close the db
#!/usr/bin/env python

# Modified from track.py
# http://www.paulschow.com/2013/12/raspberry-pi-visual-ping-indicator.html

# Originally modified from ping.py
# http://www.g-loaded.eu/2009/10/30/python-ping/
# Which is under GNU General Public License version 2

# Note: Requires sqlite3 I think


import os, sys, socket, struct, select, time, sqlite3, pygame
from time import strftime
#import RPi.GPIO as GPIO #import GPIO

#GPIO.setmode(GPIO.BCM) #set mode BCM
#GPIO.setup(11, GPIO.OUT) #Use pin 11
#GPIO.setup(9, GPIO.OUT) #Use pin 9
#GPIO.setup(8, GPIO.OUT) #Use pin 11
#GPIO.setup(25, GPIO.OUT) #Use pin 9

# connect to the database
conn = sqlite3.connect('gone.db')
# the cursor is c
c = conn.cursor()

# initalize pygame mixer for audio
pygame.mixer.init()

# From ping.py
# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris

#log = open('track1.txt', 'w')  # open a text file for logging
#print log  # print what the log file is
#log.write('Time,IP,Ping\n')  # write to log


# From ping.py
def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


# From ping.py
def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return

        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


# From ping.py
def send_one_ping(my_socket, dest_addr, ID):
    """
    Send one ping to the given >dest_addr<.
    """
    dest_addr  =  socket.gethostbyname(dest_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1


# From ping.py
def do_one(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
            raise socket.error(msg)
        raise  # raise the original error

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


# From ping.py
def verbose_ping(dest_addr, timeout = 2, count = 1):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and display
    the result.
    """
    for i in xrange(count):
        print "ping %s..." % dest_addr,
        try:
            delay  =  do_one(dest_addr, timeout)
        except socket.gaierror, e:
            print "failed. (socket error: '%s')" % e[1]
            #log.write('%s,socketerr\n' % ((strftime("%H:%M"))))
            #led_off(pin)
            return 0  # Return a 0 if there's an error'
            break
        if delay  ==  None:
            print "failed. (timeout within %ssec.)" % timeout
            #log.write('%s,%s,timeout\n' % (strftime("%H:%M"), dest_addr))
            # write to log
            #led_off(pin)
            return 0  # Return a 0 if they're not here'
        else:
            delay = delay * 1000
            print "get ping in %0.4fms" % delay
            #log.write('%s,%s,%0.4f\n' % (strftime("%H:%M"), dest_addr, delay))
            # write to log
            #led_on(pin)
            return 1  # Return a 1 if the person is here


# function for marking someone as gone in the db
def db_gone(keyid):
    print "key = %d" % keyid
    #c.execute("SELECT * FROM gone")
    c.execute("UPDATE gone SET Status = 0 WHERE key = %d" % keyid)
    conn.commit()
    #print "Total number of rows updated :", conn.total_changes


def db_here(keyid):
    print "key = %d" % keyid
    #c.execute("SELECT * FROM gone")
    c.execute("UPDATE gone SET Status = 1 WHERE key = %d" % keyid)
    conn.commit()
    #print "Total number of rows updated :", conn.total_changes
    #conn.close

#def led_on(pin):
#    GPIO.output(pin,GPIO.HIGH)
#    print "LED %d ON" % (pin)


#def led_off(pin):
#    GPIO.output(pin,GPIO.LOW)
#    print "LED %d OFF" % (pin)

#Main loop
if __name__ == '__main__':
    counter = 0
    #Loop for awhile
    while counter < 20:
        c.execute("SELECT * FROM gone")
        rows = c.fetchall()
        countrow = len(rows)  # Counts the number of rows
        print "Number of Rows:", countrow
        x = countrow
        for row in rows:
            print row[5]
            status = verbose_ping(row[5])  # ping the IP, get status
            # 1 is here, 0 is gone or error
            print "status is %s" % status
            if status == 1:
                #print "They're here!"
                print "Here"
                # I'm just making this play music for fun
                #print 'MP3 file is:', row[3]
                #pygame.mixer.music.load(row[3])  # load the file for the person
                #pygame.mixer.music.play()  # play the loaded file
                #time.sleep(10)
                # Send the row to db_here
                db_here(row[0])
                #conn.execute("UPDATE gone SET Status = 1 WHERE key = 4")
                #conn.commit
                #print "Total number of rows updated :", conn.total_changes
            else:
                #print "Not Here"
                # Send the row to db_gone
                print "Not Here"
                db_gone(row[0])
            print " "
            #print rows
            #print len(row)
            #print x

        #search = 1  # 1 is the last marker
        #query = "SELECT * FROM gone WHERE last=? ORDER BY {0}".format('Last')
        #c.execute(query, (search,))
        #for row in c:
            #print row
            #print 'Last person was:', row[4]
            #print 'MP3 file is:', row[3]
            #pygame.mixer.music.load(row[3])  # load the file for the person
            #pygame.mixer.music.play()  # play the loaded file
        #verbose_ping("192.168.1.5",11) #W
        #verbose_ping("192.168.1.24",9) #T
        #verbose_ping("192.168.1.12",8) #L
        #verbose_ping("192.168.1.26",25) #P
        counter = counter + 1
        print "done"
        #time.sleep(10)
        #conn.close

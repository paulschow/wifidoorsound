#import os
import subprocess
import re


def l2ping(phonemac):
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

print l2ping("E8:99:C4:D8:C9:91")
print l2ping("E8:99:C4:D8:C9:90")

#!/huge/PNSN/python-seis/bin/python
# Plot Mag residuals versus time.
import sys
import datetime
import time
#import netUtils
#import timeUtils
import calendar
#from catalogTools import catalog,UWevent,AQMStools
#from timeUtils import parseTimeStr
import math
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print ("USAGE: timemag.py filename start end (YYYYMMDD)")
    sys.exit()

filename = sys.argv[1]
time.start=time.strptime(sys.argv[2], "%Y%m%d")
start=calendar.timegm(time.start)
time.end=time.strptime(sys.argv[3], "%Y%m%d")
end=calendar.timegm(time.end)


x=[]
y=[]
fp=open(filename,'r')
#except IOError:
#print 'Error opening list file %s' %filename
#exit()
for line in fp:
    if line[0]=='#' or not line.strip():   # comment line
        continue
    words=line.split()
    #time.now=time.strptime(words[0], "%Y/%m/%d")
    time.now=time.strptime(words[0]+words[1], "%Y/%m/%d%H:%S:%M")
    now=calendar.timegm(time.now)
    if now < start:
        continue
    if now > end:
        break
    x.append(float(now))
    y.append(float(words[7]))
fp.close()

mean=np.mean(y)
print (start, end, "epoc seconds, mean: ",mean," of ",len(y)," magnitudes.")
title = "Mag Vers Time ",sys.argv[1]
plt.scatter(x,y,s=3)

plt.ylabel('Preferred Magnitude')
xlab = "Time: ",sys.argv[2]," - ",sys.argv[3]
plt.xlabel(xlab)
plt.xlim(start,end)
#plt.xticks([1246684800,1104364800, 1262044800,1419724800])
plt.plot([start,end],[mean,mean],linestyle="dotted")
plt.ylim(-2.01,2.01)
plt.title(title)
plt.show()

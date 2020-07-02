#!/huge/PNSN/python-seis/bin/python
# res_dist_scatter does a scatter plot of mag res by distance.
import sys
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print ("USAGE: dist_scatter.py filename max_dist ")
    sys.exit()

maxx = 200.0
filename = sys.argv[1]
if len(sys.argv) > 2:
    maxx = float(sys.argv[2])


x=[]
y=[]
fp=open(filename,'r')
for line in fp:
    if not line[0].isdigit() or not line.strip():   # comment line
        continue
    words=line.split()
    y.append(float(words[7]))
    x.append(float(words[10]))
fp.close()

z=np.polyfit(x, y, 1)
mean=np.mean(y)

plt.scatter(x,y,s=3)
x1=[0., maxx]
y1=[0.0, 0.0]
y2 = [z[1], z[0] * maxx]
print ("Line fit", z, "Mean: ",mean)
title = "Mag residual by distance %s with %d picks " %(filename,len(x))
plt.plot(x1,y1, linestyle="dashed")
plt.plot(x1,[mean,mean],linestyle="dotted")
plt.plot(x1,y2)
plt.xlim(0.01,maxx)
plt.ylim(-1.0, 1.0)
plt.ylabel(" Mag Residual ")
plt.xlabel("Distance (km) ")
plt.title(title)
plt.show()

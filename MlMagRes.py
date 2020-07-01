#!/huge/PNSN/python-seis/bin/python
#!/usr/bin/env python
'''
Script to generate summaries of Amplitude Magnitude (Ml) station residuals
USAGE:
    MlMagRes.py [filename] | STA NET start_date end_date (YYYYMMDD)
    where filename is a file containing only STA NET pairs per line
    filename must be longer than 4 characters
If not a filename then the variable  detail="true" which lists lots
of details and will make a plot of residual distributions to the screen.
There is a veriable called verbose and if set to 1 (true) then
an output file with station name is created with all the details.
'''

import sys
import os
import datetime
import time
import calendar
import netUtils
import timeUtils
from catalogTools import catalog,UWevent,AQMStools
import math
import numpy as np
import matplotlib.pyplot as plt

def getMlMagRes(connect,sta,net,start,stop):
    '''
    Archdb database access routine.
    '''
    curs=connect.cursor()

    selstr = "select truetime.getString(o.datetime),o.datetime,o.evid,o.depth,o.distance,n.magnitude,a.seedchan,a.location,aam.mag,aam.magres,aam.magcorr,aam.weight,amo.delta "

    fromstr="from event e, origin o, netmag n, assocamm aam, amp a, assocamo amo "

    # The o.evid is between two dates
    timestr=("where truetime.getString(o.datetime) > '%s' and truetime.getString(o.datetime) < '%s' " %(start,stop))

    # Example to only get events within a lat lon selection
    # wherestr=" and o.lat > 46.1 and o.lat < 46.3 and o.lon > -122.35 and o.lon < -122.05 and o.orid=e.prefor and o.prefmag=n.magid and e.selectflag=1 and n.uncertainty < 1.0 and n.nobs > 3 and n.magalgo='RichterMl2' and amo.ampid=a.ampid and amo.orid=o.orid and aam.magid=n.magid and aam.ampid=a.ampid and aam.weight > -0.5 and a.net=:net and a.sta=:sta and amptype in ('WAS','WASF') and "

    # Only use local earthquakes or probable blasts and mag uncertainty is less than 0.5 with more than 5 readings
    wherestr=" and o.gtype='l' and (e.etype='eq' or e.etype='px') and o.orid=e.prefor and o.prefmag=n.magid and e.selectflag=1 and n.uncertainty < 0.5 and n.nobs > 5 and n.magalgo='RichterMl2' and amo.ampid=a.ampid and amo.orid=o.orid and aam.magid=n.magid and aam.ampid=a.ampid and aam.weight > -0.5 and amptype in ('WAS','WASF') and "

    stastr=("a.net='%s' and a.sta='%s' " %(net,sta))

    orderstr=" order by o.datetime"
    getstr = selstr + fromstr + timestr + wherestr + stastr + orderstr

    # print (getstr)

    curs.execute(getstr)
    r=curs.fetchall()

    curs.close()
    return r
# END OF getMlMagRes

def getNetStaList():
    '''
    Parse either STA and NET or file with these in it
    '''
    if len(sys.argv) < 4:
        print ("USAGE: MlMagRes.py STA NET START STOP (YYYYMMDD)")
        print ("STA may be a filename (longer than 5 chars) containing STA NET pairs")
        sys.exit()

    outl=[]
    global start, stop
    staCode = sys.argv[1]
    netCode = sys.argv[2]
    time.start=time.strptime(sys.argv[3], "%Y%m%d")
    time.stop=time.strptime(sys.argv[4], "%Y%m%d")
    # Put these into format for database query
    start = ("%4d/%02d/%02d" %(time.start.tm_year, time.start.tm_mon, time.start.tm_mday))
    stop = ("%4d/%02d/%02d" %(time.stop.tm_year, time.stop.tm_mon, time.stop.tm_mday))
    if len(staCode) < 5:
        outl=[[staCode,netCode]]
    else:
        filelist=staCode
        fp=open(filelist,'r')
        for line in fp:
            if line[0]=='#' or not line.strip():   # comment line
                continue
            words=line.split()
            outl.append(words)

    return outl
# END OF getNetStaList


if __name__=='__main__':
    '''
        Get mag residuals for a station or list of stations
    '''
    
    #  Set detail to "true" if stdout complete listing and plots are wanted
    # Automatically set to true if only one stations is being used.
    detail=0
    # Set verbose if all details for each station should be written to its file
    verbose=1
    
    # Database connection information Defaults to secondary host to keep load off primary.
    try:
        host=os.environ['DB_HOST']
        dbname=os.environ['DB_NAME']
        user=os.environ['DB_USER']
        password=os.environ['DB_PASS']
    except KeyError:
        sys.exit("Requires ENV vars DB_NAME, DB_USER, DB_PASS and DB_HOST")
    print ('From ',host,dbname)
    
    aqscat="host={} dbname={} user={} password={}".format(host,dbname,user,password)
    aqsdbtype='postgresql'
    connect=AQMStools.getDbConnect(connectString=aqscat, dbtype=aqsdbtype)
    
    outlist=getNetStaList()
    if len(outlist) < 2:
        detail=1
        import matplotlib.pyplot as plt
    title = "Amplitude (Ml) Magnitude Residuals for stations:"
    print (title)
    print (outlist)

    for (staCode, netCode) in outlist:
        r = getMlMagRes(connect,staCode,netCode,start,stop)
        if len(r) == 0:
            print ("No measurements for station %s.%s\n"%(netCode,staCode))
        else:
            filename="%s.%s_Magres.txt" %(staCode,netCode)
            header=("#   datetime,        evid,  depth min-dist mag chanmag res corr  weight sta-delta chan loc\n")
            ft = open(filename, 'w')
            ft.write(header),
            if detail:
                print(header)
            VertMagnitudes = []
            HorzMagnitudes = []
            VertResiduals = []
            HorzResiduals = []
            VertResiduals_raw = []
            HorzResiduals_raw = []
            vertcorr=horizcorr=0.0
            for (datetime,otime,evid,depth,dist,mag,seedchan,location,chanmag,magres,magcorr,weight,delta) in r:
                 if verbose:
                     outs = ("%s  %d %5.2f %5.1f %5.2f %5.2f %5.2f %6.2f %4.1f %6.1f   %s %s" %(datetime,evid,depth,dist,mag,chanmag,magres,magcorr,weight,delta,seedchan,location))
                     ft.write(outs)
                     ft.write('\n')
                 if detail:
                     print (outs)
                 if seedchan == 'EHZ' or seedchan == 'BHZ' or seedchan == 'HHZ':
                     vertcorr=magcorr
                     VertMagnitudes.append(mag)
                     VertResiduals.append(magres)
                     VertResiduals_raw.append(magres-magcorr)
                 else:
                     horizcorr=magcorr
                     HorzMagnitudes.append(mag)
                     HorzResiduals.append(magres)
                     HorzResiduals_raw.append(magres-magcorr)
            VertMagnitudes = np.array(VertMagnitudes)
            VertResiduals = np.array(VertResiduals)
            VertResiduals_raw = np.array(VertResiduals_raw)
            HorzMagnitudes = np.array(HorzMagnitudes)
            HorzResiduals = np.array(HorzResiduals)
            HorzResiduals_raw = np.array(HorzResiduals_raw)
    
            if len(VertResiduals) > 3:
               outz= ("# %s.%s EHZ   Average: %4.2f +/- %4.2f, Median: %4.2f (N=%s),  without correction: %4.2f +/- %4.2f, Median: %4.2f, Corr: %4.2f\n" %(staCode,netCode,np.mean(VertResiduals),np.std(VertResiduals),np.median(VertResiduals),VertMagnitudes.size,np.mean(VertResiduals_raw),np.std(VertResiduals_raw),np.median(VertResiduals_raw),vertcorr))
               print (outz,)
               ft.write(outz)

            if len(HorzResiduals) > 3:
               outh = ("# %s.%s H[EN] Average: %4.2f +/- %4.2f, Median: %4.2f (N=%s),  without correction: %4.2f +/- %4.2f, Median: %4.2f, Corr: %4.2f\n" %(staCode,netCode,np.mean(HorzResiduals),np.std(HorzResiduals),np.median(HorzResiduals),HorzMagnitudes.size,np.mean(HorzResiduals_raw),np.std(HorzResiduals_raw),np.median(HorzResiduals_raw),horizcorr))
               print (outh,)
               ft.write(outh)
    
            # Now do the plotting
            if detail:
                print ("Yellow - raw, blue - corrected, green - overlap\n")
                if HorzMagnitudes.size > 1:
                    plt.hist(HorzResiduals,bins=20,label='magnitude residual')
                    plt.hist(HorzResiduals_raw,bins=20,facecolor='yellow',label='without station correction',alpha=0.5)
                else:
                    plt.hist(VertResiduals,bins=20,label='magnitude residual')
                    plt.hist(VertResiduals_raw,bins=20,facecolor='yellow',label='without station correction',alpha=0.5)
    
                title = "Magnitude Residuals for sta: %s.%s  %s - %s" %(staCode,netCode,start,stop)
                plt.ylabel('Number')
                plt.xlabel('Residual (mags)')
                plt.title(title)
                plt.show()
        if len(r) != 0 and verbose:
            ft.close()
    connect.close()

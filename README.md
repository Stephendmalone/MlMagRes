# MlMagRes
Python code to help determine Ml magnitude corrections for PNSN stations

USAGE: MlMagRes.py STA NET START STOP (YYYYMMDD)

STA may be a filename (longer than 5 chars) containing STA NET pairs

The three programs, MlMagRes, res_time_scatter and res_distance_scatter are used in combination to determine local magntude station corrections. 'MlMagRes' accesses the data in the PNSN sarchdb (secondary database to not load the primary during big requests) for basic magnitude information from a given station, computes averages and means of stored magnitude residuals (along with some statistics).  The negative of the average should then be put into the 'corr' value of the "stacorrections" table as described in https://pnsndocs.ess.washington.edu/LOCAL/WikiDocs/index.php/Ml_Corrections

Giving the program a single 'STA NET' pair will also list station information for each event selected and then the summary information. If data exists for EHZ channels it is handeled separately in the summary information, otherwise all horizontal data (BH, HH, EN, HN) are all lumped together. Finally a plot is produced of the distribution of residules color coded by raw - yellow, corrected - blue and overlap (both) - green.

If instead of a 'STA NET' pair a 'filename NET' is given as the first two arguments then the filename file must contain 'STA NET' pairs per line and the program will compute the summary statistics for each station but not produce the long listing nor distribution plot.  Only events between START and STOP dates (YYYMMDD format) will be selected for computing.  This program produces an output file called, 'STA.NET_Magres.txt' containing the same information as the long listing for use by the other two programs.

To assist in looking for possible problems in station data over time the "res_time_scatter" program will plot the magnitude residuals over time and the 'res_dist_scatter' does the same for distance (not sure if this can be used for anything but may be of interest anyway).

USAGE: timemag.py filename start end (YYYYMMDD)

USAGE: dist_scatter.py filename max_dist


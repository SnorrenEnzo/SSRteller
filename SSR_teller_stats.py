# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 11:57:12 2016

@author: Jelle Mes
"""

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
#for downloading
from urllib.request import urlretrieve
#for removing the downloaded file
import os

plt.close()


#start and end time of borrel data
starttime = dt.time(20)
endtime = dt.time(5)
#start and end time of plot
startPlot = dt.time(19,30)
endPlot = dt.time(2,30)

#earliest and latest start of counting
earliest = dt.datetime.now()
latest = dt.datetime(1900, 1, 1)

#list of first and last data points for each day. From these the plotting
#range is determined
earliestlist = []
latestlist = []

downloadname = "./teller_log.txt"

url = "https://api.joostvansomeren.nl/teller/log.txt"

try:
	#import data
	data = np.loadtxt(downloadname, dtype = str).T
	print("Loading old data. Remove 'Teller_log.txt' to download new data.")
except:
	#download log
	print("Downloading new data")
	urlretrieve(url, downloadname)
	data = np.loadtxt(downloadname, dtype = str).T

#remove downloaded file
#os.remove(downloadname)


def loadData(download_date):
	"""
	Load the data of the day given by download_date
	"""
	monthlist = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	
	#arrays containing the data
	dates = []
	amount = []
	
	with open(downloadname, 'r') as f:
		prevdate = dt.datetime(1900, 1, 1)
		prevamount = 0
		
		for line in f:
			#split the line using the spaces
			sl = line.split()
			#convert the text month to a month number
			monthN = monthlist.index(sl[3]) + 1
			#find the date of the line
			tempstring = '{0}-{1}-{2} {3}'.format(monthN, sl[4], sl[5], sl[6])
			tdatetime = dt.datetime.strptime(tempstring, '%m-%d-%Y %H:%M:%S')
			
			#add the date to the array if it is the correct day
			if tdatetime.date() == download_date or tdatetime.date() == download_date + dt.timedelta(days = 1):
				#check if the current time is not equal to the previous one. If so,
				#add the sum of the last few entries

				if (tdatetime - prevdate) > dt.timedelta(seconds = 0) and prevdate > dt.datetime(1900, 1, 1):
					dates = np.append(dates, prevdate)
					amount = np.append(amount, prevamount)
					
				prevdate = tdatetime
				prevamount = int(sl[0])

	return dates, amount
	

#plots teller data of single day
def plotsingleday(yr, m, d, colour, earliest, latest):
	checkdate = dt.date(yr, m, d)
	
	#loads that day and the day after (because events go on past 24:00 h)
	slicedamount1, slicedtime1 = sliceDates(checkdate, starttime, endtime, True)
	slicedamount2, slicedtime2 = sliceDates(checkdate, starttime, endtime, False)
	slicedamount = np.append(slicedamount1, slicedamount2)
	#slicedtime = np.append(slicedtime1, slicedtime2)
	#makes a datetime array which can be used for plotting (crossing 00:00 h)
	sliceddate = []
	for i in np.arange(len(slicedtime1)):
		tempappend1 = dt.datetime.combine(dt.date(2016,5,1), slicedtime1[i].time())
		sliceddate = np.append(sliceddate, tempappend1)
	for i in np.arange(len(slicedtime2)):
		tempappend2 = dt.datetime.combine(dt.date(2016,5,2), slicedtime2[i].time())
		sliceddate = np.append(sliceddate, tempappend2)
	#checks the earliest and latest times
	if sliceddate[0] < earliest:
		earliest = sliceddate[0]
	if sliceddate[len(sliceddate) - 1] > latest:
		latest = sliceddate[len(sliceddate) - 1]
		
	#print the latest 8 registrations
	print("----------------")
	print("Latest entries:")
	for i in np.arange(8)[::-1]:
		print(sliceddate[len(sliceddate) - i - 1].time(), slicedamount[len(sliceddate) - i - 1])
	print("----------------")
	
	#plotting
#	fig, ax = plt.subplots()
	#plt.scatter(sliceddate, slicedamount, edgecolor = 'none', color = colour, label = checkdate)
	plt.plot(sliceddate, slicedamount, color = colour, label = checkdate)
	#plt.xlim(dt.datetime.combine(sliceddate[0].date(), startPlot), dt.datetime.combine(sliceddate[len(sliceddate)-1].date(), endPlot))
	
	#set the x ticks in appropriate positions
#	xax = ax.get_xaxis() # get the x-axis
#	adf = xax.get_major_formatter() # the the auto-formatter
#	adf.scaled[1./24] = '%H:%M'  # set the < 1d scale to H:M
#	adf.scaled[1.0] = '%Y-%m-%d' # set the > 1d < 1m scale to Y-m-d
#	adf.scaled[30.] = '%Y-%m' # set the > 1m < 1Y scale to Y-m
#	adf.scaled[365.] = '%Y' # set the > 1y scale to Y
	
	earliestlist.append(earliest)
	latestlist.append(latest)
	
	#plot the most recent date
def plotRecent(earliest, latest):
	#first load the most recent date
	#loop through dates starting at the most recent
	rdate = date[::-1]
	ramount = amount[::-1]
	for i in np.arange(len(rdate)):
		if rdate[i].time() > dt.time(12) and ramount[i] > 0:
			recDate = rdate[i]
			break
	print(recDate)
	#then plot it
	earliest, latest = plotsingleday(recDate.year, recDate.month, recDate.day, 'b', earliest, latest)
	return earliest, latest, recDate

	
def plotAllBorrels():
	"""
	Plots a bar graph of maximum number of people at the tuesday borrels at SSR.
	"""
	firstdate = dt.date(2016, 9, 9)
	lastdate = dt.date(2017, 4, 4)
	
	#array containing all the tuesday dates and max values
	tuesdaylist = []
	tuesdaymax = []
	#the date counter
	datecounter = firstdate
	
	while datecounter <= lastdate:
		try:
			#loads that day and the day after (because events go on past 24:00 h)
			slicedamount1, slicedtime1 = sliceDates(datecounter, starttime, endtime, True)
			slicedamount2, slicedtime2 = sliceDates(datecounter, starttime, endtime, False)
			slicedamount = np.append(slicedamount1, slicedamount2)
			
			tuesdaymax = np.append(tuesdaymax, np.max(slicedamount))
			tuesdaylist = np.append(tuesdaylist, datecounter)
		except:
			print("Skipping date without data (" + str(datecounter) + ")")
			
		datecounter += dt.timedelta(days = 7)
	
	for i in np.arange(len(tuesdaylist)):
		print(tuesdaylist[i], tuesdaymax[i])
		
	#now we plot
	plt.bar(tuesdaylist, tuesdaymax, width = 7)
	plt.xlabel("Datum")
	plt.ylabel("Maximaal aantal mensen in het pand")
	plt.title("Maximaal aantal mensen in het pand per vrijdag van dit collegejaar")
	plt.savefig("Maximaal # mensen alle vrijdagen.png", dpi = 200)
	plt.show()
	
earliest, latest, recDate = plotRecent(earliest, latest)	

'''
'''
	#plot data per day

#first borrels in september 2016
#earliest, latest = plotsingleday(2016, 9, 6, '#FB07FF', earliest, latest)
#earliest, latest = plotsingleday(2016, 9, 13, '#FF0635', earliest, latest)
#earliest, latest = plotsingleday(2016, 9, 20, '#FF6404', earliest, latest)
#earliest, latest = plotsingleday(2016, 9, 27, '#FFCC26', earliest, latest)

#Ik week 2017
#earliest, latest = plotsingleday(2017, 2, 13, '#02B7FF', earliest, latest)
#earliest, latest = plotsingleday(2017, 2, 14, '#FB07FF', earliest, latest)
#earliest, latest = plotsingleday(2017, 2, 15, '#7306FF', earliest, latest)
#earliest, latest = plotsingleday(2017, 2, 16, '#FF060D', earliest, latest)
#earliest, latest = plotsingleday(2017, 2, 17, '#FF8E06', earliest, latest)


#Oud & nieuw
#earliest, latest = plotsingleday(2016, 12, 31, 'b', earliest, latest)
#KSF 
#earliest, latest = plotsingleday(2016, 12, 23, 'g', earliest, latest)

#random date
recDate = dt.datetime(2017,3,7)
earliest, latest = plotsingleday(recDate.year, recDate.month, recDate.day, 
								'b', earliest, latest)



#EL CID 2017
#plotsingleday(2017, 8, 14, '#02B7FF', earliest, latest)
#plotsingleday(2017, 8, 15, '#FB07FF', earliest, latest)
#plotsingleday(2017, 8, 16, '#7306FF', earliest, latest)
#plotsingleday(2017, 8, 17, '#FF060D', earliest, latest)
#plotsingleday(2017, 8, 18, '#FF8E06', earliest, latest)

#EL CID 2016
#plotsingleday(2016, 8, 15, '#02B7FF', earliest, latest)
#plotsingleday(2016, 8, 16, '#FB07FF', earliest, latest)
#plotsingleday(2016, 8, 17, '#7306FF', earliest, latest)
#plotsingleday(2016, 8, 18, '#FF060D', earliest, latest)
#plotsingleday(2016, 8, 19, '#FF8E06', earliest, latest)
plotsingleday(2016, 9, 12, '#FF8E06', earliest, latest)

plotsingleday(2017, 12, 22, '#02B7FF', earliest, latest)

plotstart = np.min(earliestlist)
plotend = np.max(latestlist)

	#the plotting commands for plotting a single or multiple days
#makes plot nicer
sns.set_style("darkgrid", {'grid.color': '0.4', 'grid.linestyle': u':', 'legend.frameon': True})

##sets the xlim 
plt.xlim(plotstart - dt.timedelta(minutes = 30), plotend + dt.timedelta(minutes = 30))
plt.ylim(-10, 310)

plt.legend(loc = 'lower right', shadow = True).draggable()
#plt.title('Aantal mensen te S.C.R.E.D. op ' + str(recDate.date()))
plt.title('Aantal mensen te S.C.R.E.D. tijdens KSF 2017')
plt.xlabel('Tijd')
plt.ylabel('Aantal')
#plt.savefig("Aantal mensen te S.C.R.E.D. EL CID 2016.png", bbox_inches='tight', dpi = 200)
plt.show()
'''
#plotAllBorrels()

dates, amount = loadData(dt.date(2017,12,22))

plt.plot(dates, amount)
plt.show()

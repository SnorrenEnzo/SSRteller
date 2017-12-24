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
#for getting many plotting colours
import matplotlib.colors as colors
import matplotlib.cm as cmx

sns.set()
plt.close()


#start and end time of borrel data
starttime = dt.time(20)
endtime = dt.time(5)
#start and end time of plot
startPlot = dt.time(19,30)
endPlot = dt.time(2,30)

#list of first and last data points for each day. From these the plotting
#range is determined
earliestlist = []
latestlist = []

#remove downloaded file
#os.remove(downloadname)

def loadData(download_date):
	"""
	Load the data of the day given by download_date
	"""

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

'''
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

'''

def plotsingleday(plotdate, colorval, hourshift, alpha = 1):
	"""
	Loads and plots the SSR teller data of a single day.

	Input:
		year, month, day (ints): the year, month and day of the date of which the
		data must be plotted. The date is defined as the starting date of the evening (
		parties almost always go beyond 24:00 h).\n
		colorval (matpotlib color value or str): the colour to be used for plotting the graph. \n
		hourshift (int): the amount of hours the dates will be shifted by for plotting.\n
		alpha (float): the translucence of the plot line. 0: completely translucent. 1: 
		completely opaque. Can be used to plot multiple dates with different line opacities.

	Output:
		min_dates (datetime): the first time stamp of the data.\n
		max_dates (datetime): the last time stamp of the data.
	"""

	#download the data and convert it to the correct format
	dates, amount = loadData(plotdate.date())

	#set the label of the plot
	label = str(np.min(dates).date())

	#change the dates array to make it span only a single day
	#and also set the day to a single one, to make plotting of multiple graphs possible
	for i in np.arange(len(dates)):
		dates[i] -= dt.timedelta(hours = hourshift)
		dates[i] = dt.datetime.combine(dt.date.today(), dates[i].time())

	plt.plot(dates, amount, label = label, color = colorval, alpha = alpha)

	plotstart = np.min(dates)
	plotend = np.max(dates)

		#the plotting commands for plotting a single or multiple days
	#makes plot nicer
	sns.set_style("darkgrid", {'grid.color': '0.4', 'grid.linestyle': u':', 'legend.frameon': True})

	#sets the xlim 
	plt.xlim(plotstart - dt.timedelta(minutes = 30), plotend + dt.timedelta(minutes = 30))
	plt.ylim(-10, 310)

	return np.min(dates), np.max(dates)


#lists containing the dates to be plotted
'''
#KSF 2016 and 2017
years = [2016, 2017]
months = [12, 12]
days = [23, 22]
date_list = []
for y, m, d in zip(years, months, days):
	date_list.append(dt.date(y,m,d))
'''
#All dinsdagborrels of the autumn of 2017
date_list = np.arange(dt.date(2017, 9, 5), dt.date(2017, 12, 20), dt.timedelta(days = 7)).astype(dt.date)


#initialize functions to get many plotting colours
jet = plt.get_cmap('jet') 
cNorm  = colors.Normalize(vmin=0, vmax=len(date_list)+1)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

#the first and last time stamps found for each date
firstdates = []
lastdates = []
#the amount of hours the dates will be shifted in the plotsingleday() function
#this shifting is necessary to facilitate plotting different dates in a single plot
hourshift = 6

#plot all the dates
for i in np.arange(len(date_list)):
	colorVal = scalarMap.to_rgba(i)		
	
	fd, ld = plotsingleday(date_list[i], colorval = colorVal, hourshift = hourshift)
	#append the found first and last time stamps
	firstdates.append(fd)
	lastdates.append(ld)

	#Change the xticks to display hours and minutes only
#first find the minimum date/time
orig_mindate = np.min(firstdates)
# print(orig_mindate.time())
#then round this down to the hour
discard = dt.timedelta(minutes=orig_mindate.minute)
mindate = orig_mindate - discard
#then make arrays needed to change the ticks
oldLabels = np.arange(mindate, np.max(lastdates) + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
newLabels = []
for d in oldLabels:
	#add the 'hourshift' amount of hours again to make it show the correct hours
	newLabels.append((d + dt.timedelta(hours = hourshift)).strftime("%H:%M"))
#change the x ticks
plt.xticks(oldLabels, newLabels, rotation = 40)

plt.legend(loc = 'best', shadow = True).draggable()
plt.title('Aantal mensen te S.C.R.E.D.')
plt.xlabel('Tijd')
plt.ylabel('Aantal')
#plt.savefig("Aantal mensen te S.C.R.E.D. KSF 16-17.png", bbox_inches='tight', dpi = 200)
plt.show()

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


#list of first and last data points for each day. From these the plotting
#range is determined
# earliestlist = []
# latestlist = []

class processTeller(object):

	def __init__(self):
		#start and end time of borrel data
		self.starttime = dt.time(20)
		self.endtime = dt.time(5)
		#start and end time of plot
		self.startPlot = dt.time(19,30)
		self.endPlot = dt.time(2,30)

		#name of the local log file
		self.downloadname = "./teller_log.txt"
		#url of the log file
		self.url = "https://api.ssr-leiden.nl/teller/logs/ssr.log"

		self.hourshift = 6
		self.dt_hourshift = dt.timedelta(hours = self.hourshift)

		self.cmap = 'jet'

		self.fig_savename = 'Teller Grafiek EL CID 2018.png'

	def loadData(self, download_date):
		"""
		Load the data of the day given by download_date
		"""

		try:
			#import data
			data = np.loadtxt(self.downloadname, dtype = str).T
			print("Loading old data. Remove 'Teller_log.txt' to download new data.")
		except:
			#download log
			print("Downloading new data")
			urlretrieve(self.url, self.downloadname)
			data = np.loadtxt(self.downloadname, dtype = str).T

		monthlist = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
		
		#arrays containing the data
		dates = []
		amount = []
		
		with open(self.downloadname, 'r') as f:
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
				#and if the time is not too early
				#for this we need to shift the time
				if (tdatetime - self.dt_hourshift).date() == download_date and tdatetime.time() > dt.time(20 - self.hourshift):
					#check if the current time is not equal to the previous one. If so,
					#add the sum of the last few entries

					if (tdatetime - prevdate) > dt.timedelta(seconds = 0) and prevdate > dt.datetime(1900, 1, 1):
						dates = np.append(dates, prevdate)
						amount = np.append(amount, prevamount)
						
					prevdate = tdatetime
					prevamount = int(sl[0])

		return dates, amount

	def plotsingleday(self, plotdate, colorval = 'green', alpha = 1, plotmultiplegraphs = False):
		"""
		Loads and plots the SSR teller data of a single day.

		Input:
			plotdate (datetime): The date of which the data must be plotted.
			The date is defined as the starting date of the evening (parties almost always 
			go beyond 24:00 h).\n
			colorval (matpotlib color value or str): the colour to be used for plotting the graph. \n
			hourshift (int): the amount of hours the dates will be shifted by for plotting.\n
			alpha (float): the translucence of the plot line. 0: completely translucent. 1: 
			completely opaque. Can be used to plot multiple dates with different line opacities.

		Output:
			min_dates (datetime): the first time stamp of the data.\n
			max_dates (datetime): the last time stamp of the data.
		"""

		#download the data and convert it to the correct format
		dates, amount = self.loadData(plotdate.date())

		#set the label of the plot
		label = str(np.min(dates).date())

		newdates = np.copy(dates)

		if plotmultiplegraphs:
			#change the dates array to make it span only a single day
			#and also set the day to a single one, to make plotting of multiple graphs possible
			for i in np.arange(len(dates)):
				newdates[i] -= self.dt_hourshift
				newdates[i] = dt.datetime.combine(dt.date.today(), newdates[i].time())

		plt.plot(newdates, amount, label = label, color = colorval, alpha = alpha)

		plotstart = np.min(newdates)
		plotend = np.max(newdates)

			#the plotting commands for plotting a single or multiple days
		#makes plot nicer
		sns.set_style("darkgrid", {'grid.color': '0.4', 'grid.linestyle': u':', 'legend.frameon': True})

		#sets the xlim 
		plt.xlim(plotstart - dt.timedelta(minutes = 30), plotend + dt.timedelta(minutes = 30))
		plt.ylim(-10, 310)

		return np.min(newdates), np.max(newdates)

	def plotMultipleDates(self, date_list):
		"""
		This function plots the graphs of the amount of people in the building for different
		dates in a single figure.

		Input:
			date_list (datetime array): array of dates.
		"""
		#initialize functions to get many plotting colours
		jet = plt.get_cmap(self.cmap) 
		cNorm  = colors.Normalize(vmin = 0, vmax = len(date_list) + 1)
		scalarMap = cmx.ScalarMappable(norm = cNorm, cmap = jet)

		#the first and last time stamps found for each date
		firstdates = []
		lastdates = []
		#the amount of hours the dates will be shifted in the plotsingleday() function
		#this shifting is necessary to facilitate plotting different dates in a single plot
		hourshift = 6

		#plot all the dates
		for i in np.arange(len(date_list)):
			colorVal = scalarMap.to_rgba(i)	
			
			fd, ld = self.plotsingleday(date_list[i], colorval = colorVal, plotmultiplegraphs = True)
			#append the found first and last time stamps
			firstdates.append(fd)
			lastdates.append(ld)

			#Change the xticks to display hours and minutes only
		#first find the minimum date/time
		orig_mindate = np.min(firstdates)
		#then round this down to the hour
		discard = dt.timedelta(minutes = orig_mindate.minute)
		mindate = orig_mindate - discard
		#then make arrays needed to change the ticks
		oldLabels = np.arange(mindate, np.max(lastdates) + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
		newLabels = []
		for d in oldLabels:
			#add the 'hourshift' amount of hours again to make it show the correct hours
			newLabels.append((d + dt.timedelta(hours = hourshift)).strftime("%H:%M"))
		#change the x ticks
		plt.xticks(oldLabels, newLabels)

		fig = plt.gcf()

		#auto rotate the labels
		fig.autofmt_xdate()

		plt.legend(loc = 'best', shadow = True).draggable()
		plt.title('Aantal mensen te S.C.R.E.D.')
		plt.xlabel('Tijd')
		plt.ylabel('Aantal')
		plt.savefig(self.fig_savename, bbox_inches='tight', dpi = 200)
		plt.show()

	def plotDates_separate(self, date_list1, datelist2 = None, saveloc = 'Dinsdagborrels_herfst_2017/'):
		"""
		Plot multiple dates, but each as a separate file. This way the images can later be 
		used as frames in a video. 

		Input:
			date_list1 (datetime array): list of dates to be plotted. \n
			date_list2 (datetime array): an optional second list of dates to be plotted together
			with the first list in the same figures.\n
			saveloc (str): location where the files should be saved.
		"""

		#the colour used for plotting
		colorVal = 'g'

		#the amount of hours the dates will be shifted in the plotsingleday() function
		#this shifting is necessary to facilitate plotting different dates in a single plot
		hourshift = 6

		#array containing the dates that contain good data. These can be used
		#for training
		train_dates = []

		#plot all the dates
		for i in np.arange(len(date_list1)):	

			print('Processing {0}'.format(date_list1[i].date()))

			fig = plt.figure(figsize=(9,6))	
			
			try:
				fd, ld = plotsingleday(date_list1[i], colorval = colorVal)
				if datelist2 is not None:
					fd, ld = plotsingleday(date_list2[i], colorval = 'b', hourshift = hourshift)

					#Change the xticks to display hours and minutes only
				#first find the minimum date/time
				starttime = dt.datetime.combine(dt.date.today(), dt.time(20 - hourshift, 0))
				endtime = dt.datetime.combine(dt.date.today(), dt.time(24 + 4 - hourshift, 0))
				orig_mindate = starttime
				#then round this down to the hour
				discard = dt.timedelta(minutes=orig_mindate.minute)
				mindate = orig_mindate - discard
				#then make arrays needed to change the ticks
				oldLabels = np.arange(mindate, endtime + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
				newLabels = []
				for d in oldLabels:
					#add the 'hourshift' amount of hours again to make it show the correct hours
					newLabels.append((d + dt.timedelta(hours = hourshift)).strftime("%H:%M"))
				#change the x ticks
				plt.xticks(oldLabels, newLabels)
				plt.xlim(np.min(oldLabels), np.max(oldLabels))

				#auto rotate the labels
				fig.autofmt_xdate()

				plt.legend(loc = 'upper right', shadow = True).draggable()
				plt.title('Aantal mensen te S.C.R.E.D.')
				plt.xlabel('Tijd')
				plt.ylabel('Aantal')
				plt.savefig("{0}img{1}_{2}.png".format(saveloc, len(date_list1) - i, date_list1[i].date()), dpi = 200)
				#plt.show()
				plt.close()

				train_dates.append(str(date_list1[i].date()))
			except:
				print('No data')

	def barGraphWeekday(self, loadolddata = False):
		"""
		Plots a bar graph of maximum number of people on certain days 
		throughout the year
		"""

		'''
		2016-2017
		dinsdag: 6-9-2016
		vrijdag: 9-9-2016

		2017-2018
		dinsdag: 5-9-2017
		vrijdag: 8-9-2017

		2018-2019
		dinsdag: 4-9-2018
		vrijdag: 7-9-2018
		'''
		firstdate = dt.date(2017, 9, 5)
		lastdate = dt.date(2018, 7, 1)

		if loadolddata:
			daylist = np.load('daylist.npy')
			daymax = np.load('daymax.npy')
		else:
			#array containing all the dates and max values
			daylist = []
			daymax = []
			#the date counter
			datecounter = firstdate
			
			while datecounter <= lastdate:
				print(f'Processing {datecounter}')

				try:
					dates, amount = self.loadData(datecounter)
					
					if np.max(amount) < 610:
						daymax = np.append(daymax, np.max(amount))
						daylist = np.append(daylist, datecounter)
				except:
					print("Skipping date without data (" + str(datecounter) + ")")
					
				datecounter += dt.timedelta(days = 7)
			
			for i in np.arange(len(daylist)):
				print(daylist[i], daymax[i])

			np.save('daylist.npy', daylist)
			np.save('daymax.npy', daymax)
		
		
		#now we plot
		plt.bar(daylist, daymax, width = 7, edgecolor = 'black')
		plt.xlabel("Maand")
		plt.ylabel("Maximaal aantal mensen")
		plt.title("Maximaal aantal mensen in het pand per dinsdag")

		plt.xticks(rotation=40)

		fig = plt.gcf()
		fig.subplots_adjust(bottom=0.21)

		plt.savefig("Maximaal aantal mensen alle dinsdagen 2017-2018.png", dpi = 200)
		plt.show()

	#np.savetxt('Dinsdagborrel_train_dates.txt', np.array(train_dates), fmt='%s')

teller = processTeller()

teller.barGraphWeekday()

# teller.plotsingleday(dt.datetime(2016, 9, 9))
# plt.show()

'''
#EL CID 2018
days = [13, 14, 15, 16, 17]
#EL CID 2017
# days = [14, 15, 16, 17, 18]

date_list = []
for day in days:
	date_list.append(dt.datetime(2018, 8, day))

teller.plotMultipleDates(date_list)

'''


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




def plotOneDay(saveloc = './Plots/', hourshift = 6):
	"""
	Plots a single day including saving it and adding labels etc
	"""
	#23-6-2017: ZSF 2017
	starttime, endtime = plotsingleday(dt.datetime(2017, 6, 20), colorval = 'b', hourshift = hourshift)	

		#Change the xticks to display hours and minutes only
	#first find the minimum date/time
	#starttime = dt.datetime.combine(dt.date.today(), dt.time(20 - hourshift, 0))
	#endtime = dt.datetime.combine(dt.date.today(), dt.time(24 + 4 - hourshift, 0))

	orig_mindate = starttime
	#then round this down to the hour
	discard = dt.timedelta(minutes=orig_mindate.minute)
	mindate = orig_mindate - discard
	#then make arrays needed to change the ticks
	oldLabels = np.arange(mindate, endtime + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
	newLabels = []
	for d in oldLabels:
		#add the 'hourshift' amount of hours again to make it show the correct hours
		newLabels.append((d + dt.timedelta(hours = hourshift)).strftime("%H:%M"))
	#rotate xticks and change the labels
	plt.xticks(oldLabels, newLabels, rotation = 40)
	plt.title('Aantal mensen te S.C.R.E.D.')
	plt.xlabel('Tijd')
	plt.ylabel('Aantal')
	plt.savefig("{0}plot.png".format(saveloc), dpi = 200, bbox_inches = 'tight')
	plt.show()

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
# date_list1 = np.arange(dt.date(2017, 9, 5), dt.date(2017, 12, 20), dt.timedelta(days = 7)).astype(dt.date)
# date_list2 = np.arange(dt.date(2016, 9, 6), dt.date(2016, 12, 21), dt.timedelta(days = 7)).astype(dt.date)

#date range for the training data of the random forest
#date_list1 = np.arange(dt.date(2016, 9, 6), dt.date(2017, 6, 20), dt.timedelta(days = 7)).astype(dt.date)
#data range for the test data
#date_list1 = np.arange(dt.date(2017, 9, 5), dt.date(2017, 12, 20), dt.timedelta(days = 7)).astype(dt.date)
#plotDates_separate(date_list1, saveloc = 'Dinsdagborrels_collegejaar_2017-2018/')



	#plot a single date
# plotOneDay()


'''
#plot many lines using colors from a color map, with MAX the amount of lines
#more color maps: http://matplotlib.org/users/colormaps.html
import matplotlib.colors as colors
import matplotlib.cm as cmx
jet = plt.get_cmap('jet') 
cNorm  = colors.Normalize(vmin = 0, vmax = len(days) - 1)
scalarMap = cmx.ScalarMappable(norm = cNorm, cmap = jet)
			
for i, day in enumerate(days):
	print(day)
	colorVal = scalarMap.to_rgba(i)	

	plotsingleday(dt.datetime(2017, 8, day), colorVal, 6)


plt.savefig('EL CID 2017.png', dpi = 200)
# plotsingleday(dt.datetime(2017, 9, 5), 'blue', 6)

plt.show()
'''

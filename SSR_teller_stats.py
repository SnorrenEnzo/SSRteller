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

		self.fig_savename = 'plot.png'
		self.saveloc = './Plots/'

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
				if (tdatetime - self.dt_hourshift).date() == download_date and (tdatetime - self.dt_hourshift).time() > dt.time(14 - self.hourshift):
					#check if the current time is not equal to the previous one. If so,
					#add the sum of the last few entries

					if (tdatetime - prevdate) > dt.timedelta(seconds = 0) and prevdate > dt.datetime(1900, 1, 1):
						# dates = np.append(dates, prevdate)
						# amount = np.append(amount, prevamount)
						dates.append(prevdate)
						amount.append(prevamount)
						
					prevdate = tdatetime
					prevamount = int(sl[0])

		return np.array(dates), np.array(amount)

	def plotsingleday(self, plotdate, colorval = 'green', alpha = 1, plotmultiplegraphs = False):
		"""
		Loads and plots the SSR teller data of a single day. Do no 
		use this function yourself! Call the plotMultipleDates()
		or plotOneDay() function.

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

		plt.xlabel('Tijd')
		plt.ylabel('Aantal mensen')

		return np.min(newdates), np.max(newdates)

	def plotOneDay(self, date):
		"""
		Plots a single day including saving it and adding labels etc
		"""

		starttime, endtime = self.plotsingleday(date, colorval = 'g')	

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
			newLabels.append(d.strftime("%H:%M"))

		#rotate xticks and change the labels
		plt.xticks(oldLabels, newLabels, rotation = 40)

		plt.title(f'Aantal mensen te S.C.R.E.D. op {date.date()}')
		plt.xlabel('Tijd')
		plt.ylabel('Aantal')

		fig = plt.gcf()
		fig.subplots_adjust(bottom=0.19)

		plt.savefig(f'{self.saveloc}{date.date()}_teller_stats.png', dpi = 200, bbox_inches = 'tight')
		plt.show()

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

	def barGraphWeekday(self, year, loadolddata = False, mode = 'maximum'):
		"""
		Plots a bar graph of certain features of the data, determined by
		the parameter 'mode'. Current options:
		mode: 'maximum', 'peakstart'
		"""

		if year == 2016:
			firstdate = dt.date(2016, 9, 6)
			lastdate = dt.date(2017, 7, 1)
		elif year == 2017:
			firstdate = dt.date(2017, 9, 5)
			lastdate = dt.date(2018, 7, 1)
		elif year == 2018:
			firstdate = dt.date(2018, 9, 4)
			lastdate = dt.date(2019, 7, 1)

		if loadolddata:
			daylist = np.load('daylist.npy')
			dayfeat_value = np.load('dayfeat_value.npy')
		else:
			#array containing all the dates and feature values
			daylist = []
			dayfeat_value = []
			#the date counter
			datecounter = firstdate
			
			while datecounter <= lastdate:
				print(f'Processing {datecounter}')


				# try:
				dates, amount = self.loadData(datecounter)
				print(amount)
				try:
					print(np.where(amount == 300)[0])
				except:
					pass

				#choose which feature we want to extract:
				if mode == 'maximum':
					if np.max(amount) < 610:
						dayfeat_value = np.append(dayfeat_value, np.max(amount))
						daylist = np.append(daylist, datecounter)
				elif mode == 'peakstart':
					dayfeat_value = np.append(dayfeat_value, 1)
					# dayfeat_value = np.append(dayfeat_value, dates[np.where(amount == 300)[0][0]].time())
					daylist = np.append(daylist, datecounter)

				# except:
				# 	print("Skipping date without data (" + str(datecounter) + ")")
					
				datecounter += dt.timedelta(days = 7)
			
			for i in np.arange(len(daylist)):
				print(daylist[i], dayfeat_value[i])

			np.save('daylist.npy', daylist)
			np.save('dayfeat_value.npy', dayfeat_value)
		
		print(dayfeat_value)
		
		#now we plot
		plt.bar(daylist, dayfeat_value, width = 7, edgecolor = 'black')
		plt.xlabel("Maand")

		if mode == 'maximum':
			plt.ylabel("Maximaal aantal mensen")
			plt.title("Maximaal aantal mensen in het pand per dinsdag")
		elif mode == 'peakstart':
			plt.ylabel("Tijd")
			plt.title("Tijd dat het pand vol zit")
		
		plt.xticks(rotation=40)

		fig = plt.gcf()
		fig.subplots_adjust(bottom=0.21)

		plt.savefig(teller.fig_savename, dpi = 200)
		plt.show()

	#np.savetxt('Dinsdagborrel_train_dates.txt', np.array(train_dates), fmt='%s')

#start the class
teller = processTeller()

# teller.fig_savename = teller.saveloc + 'Tijd van rij 2017-2018.png'
teller.fig_savename = teller.saveloc + '10 oktober 2017.png'
print(teller.saveloc)

# teller.barGraphWeekday(2017, loadolddata = False, mode = 'peakstart')

teller.plotOneDay(dt.datetime(2017, 10, 17))
'''
date_list = [
			dt.datetime(2016, 9, 6),
			dt.datetime(2017, 9, 5),
			dt.datetime(2018, 9, 4)
		]

teller.plotMultipleDates(date_list)
'''


######################
# All relevant dates #
######################
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

#EL CID 2018
days = [13, 14, 15, 16, 17]
#EL CID 2017
# days = [14, 15, 16, 17, 18]

#KSF 
2016-12-23
2017-12-22

#Open week
2017:
2017-2-13 - 2017-2-17

2018:
2018-2-26 - 2018-3-2
'''



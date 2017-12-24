import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
#for downloading
from urllib.request import urlretrieve
#for removing the downloaded file
import os
#for making and reading an SQL database
import sqlite3 as lite
#to make the program sleep
import time
#for displaying a notification
import tkinter as tk
from tkinter import ttk
#used for model fitting
from scipy.optimize import curve_fit
plt.close()

'''
#start and end time of borrel data
starttime = dt.time(20)
endtime = dt.time(5)
#start and end time of plot
startPlot = dt.time(19,30)
endPlot = dt.time(2,30)

#earliest and latest start of counting
earliest = dt.datetime.now()
latest = dt.datetime(1900, 1, 1)
'''
#maximum number of people in the building
maxnum = 300

#name where the data will be downloaded
downloadname = "./teller_log.txt"


def downloadData():
	#list of first and last data points for each day. From these the plotting
	#range is determined
	earliestlist = []
	latestlist = []

	url = "https://api.joostvansomeren.nl/teller/log.txt"

	#download log
	print("Downloading data")
	urlretrieve(url, downloadname)
	
def loadData(now):
	"""
	Load the data of today
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
			if tdatetime.date() == now.date() or tdatetime.date() + dt.timedelta(days = 1) == now.date():
				#check if the current time is not equal to the previous one. If so,
				#add the sum of the last few entries
				if (tdatetime - prevdate) > dt.timedelta(seconds = 0) and prevdate > dt.datetime(1900, 1, 1):
					dates = np.append(dates, prevdate)
					amount = np.append(amount, prevamount)
					
				prevdate = tdatetime
				prevamount = int(sl[0])

	return dates, amount

def findDeriv(dates, amount, nowmoment, diffwidth = 10):
	"""
	Find the growth in the number of people in the building and send a warning
	if the building is almost full.
	
	Input:
		dates (1D array, datetime): array of datetimes of the data.\n
		amount (1D array, int): array containing the amount of people in the building
		at every moment in dates.\n
		nowmoment (datetime): the moment defined as now. Could be different than desired
		if looking at historical data.\n
		diffwidth (int): length of time in minutes of which data will be aggregated to 
		calculate the derivative.
	"""
	#slice the data to the last diffwidth number of minutes
	diffbegin = 0
	diffend = 0
	for i in np.arange(len(dates)):
		if dates[i] > (nowmoment - dt.timedelta(minutes = diffwidth)) and diffbegin == 0:
			diffbegin = i			
		if dates[i] > nowmoment and diffend == 0:
			diffend = i
			break
		if i == len(dates) - 1:
			diffend = i
			break
			
	print(diffbegin, diffend)

	deriv = (amount[diffend] - amount[diffbegin])/(dates[diffend] - dates[diffbegin]).seconds

	#determine how long it will take until the building is full
	fulltime = (maxnum - amount[diffend]) / deriv
	
	print('Capacity: {0}/{1}, full in: {2}:%02d'.format(int(amount[diffend]), maxnum, int(fulltime/60)) % int(fulltime % 60))
	print('------------------\n')
	
	return deriv, fulltime, amount[diffend]
	
def findFullTime(dates, amount, nowmoment, diffwidth = 10):
	"""
	Find when the building will be full using a second- or third order approximation
	
	Input:
		dates (1D array, datetime): array of datetimes of the data.\n
		amount (1D array, int): array containing the amount of people in the building
		at every moment in dates.\n
		nowmoment (datetime): the moment defined as now. Could be different than desired
		if looking at historical data.\n
		diffwidth (int): length of time in minutes of which data will be aggregated to 
		calculate the derivative.
	"""
		
	#slice the data to the last diffwidth number of minutes
	diffbegin = 0
	diffend = 0
	for i in np.arange(len(dates)):
		if dates[i] > (nowmoment - dt.timedelta(minutes = diffwidth)) and diffbegin == 0:
			diffbegin = i			
		if dates[i] > nowmoment and diffend == 0:
			diffend = i
			break
		if i == len(dates) - 1:
			diffend = i
			break
	
	#cut the data to the slice
	cutdates = dates[diffbegin:diffend]
	cutamount = []
	#transform cutamount from datetime objects to number of seconds before now
	for a in amount[diffbegin:diffend]:
		n_s = a - (nowmoment - dt.timedelta(minutes = diffwidth))
		print(n_s)
	
def makeplot(dates, amount, now):
	sns.set()

	#select all dates before our measurement point
	amount = amount[dates < now]
	dates = dates[dates < now]
	
	#model to be used by the fitting routine
	def model(x, a, b, c, d):
		return a*x**3 + b*x**2 + c*x + d

	#convert the dates to seconds for the model
	x_seconds = np.zeros(len(dates))
	for i in np.arange(len(dates)):
		x_seconds[i] = (dates[i]-dt.datetime(1970,1,1)).total_seconds()

	#ts = dt.datetime.fromtimestamp(x_seconds[0]).strftime('%Y-%m-%d %H:%M:%S')
	#print(ts)

	#apply the fit
	popt, pcov = curve_fit(model, x_seconds - 1.5e9, amount)
	#the standard deviation is given by:
	#perr = np.sqrt(np.diag(pcov))
	#get the residuals:
	#residuals = ydata- model(xdata, popt)
	#to get R^2:
	#ss_res = np.sum(residuals**2)
	#ss_tot = np.sum((ydata-np.mean(ydata))**2)
	#r_squared = 1 - (ss_res / ss_tot)

	#plot with two axes:
	# fig, ax1 = plt.subplots()
	#makes another y-axis
	# ax2 = ax1.twinx()
	#plots the normal data
	# lns1 = ax1.plot(dates, amount, color = 'b')
	#plots the fit
	# lns2 = ax2.plot(dates, model(x_seconds, *popt), color = 'r')

	# for tl1 in ax1.get_yticklabels():
	# 	tl1.set_color('b')
	# for tl2 in ax2.get_yticklabels():
	# 	tl2.set_color('r')

	print(popt)

	plt.plot(dates, amount, color = 'b')
	plt.plot(dates, model(x_seconds - 1.5e9, *popt), color = 'r')
	plt.xticks(rotation = 40)
	
	plt.show()
	
def plotFulltime(dates, amount, diffwidth = 5):
	"""
	Plot the time until the building is full for an entire evening
	"""
	derivlist = []
	fulltimelist = []
	plotdates = []

	for d in dates:
		try:
			deriv, fulltime = findDeriv(dates, amount, d, diffwidth = diffwidth)
			derivlist = np.append(derivlist, deriv)
			fulltimelist = np.append(fulltimelist, fulltime)
			plotdates = np.append(plotdates, d)
		except:
			print('Date/time incorrect')
			derivlist = np.append(derivlist, 0)
			fulltimelist = np.append(fulltimelist, 0)
			plotdates = np.append(plotdates, d)
	
	sns.set()
	
	#plot with two axes:
	fig, ax1 = plt.subplots()
	#makes another y-axis
	ax2 = ax1.twinx()
	#plots first line
	lns1 = ax1.plot(dates, amount, color = 'b')
	#plots second line
	#lns2 = ax2.plot(plotdates, derivlist * 60, color = 'r')
	lns2 = ax2.scatter(plotdates, fulltimelist / 60, color = 'r', marker = 'x')

	#find where the time until full was less than 10 minutes
	f_dates = plotdates[((fulltimelist / 60) < 10) * ((fulltimelist / 60) > 0)]
	ax1.scatter(f_dates, np.zeros(len(f_dates)), color = 'grey')

	for tl1 in ax1.get_yticklabels():
		tl1.set_color('b')
	for tl2 in ax2.get_yticklabels():
		tl2.set_color('r')

	ax2.set_ylabel('Time untill full [min]')
	#ax2.set_ylabel('People per minute')

	plt.show()

def popupmsg(msg, title = 'Warning!'):
	"""
	Creates a popup message
	"""
	XL_FONT = ('Verdana', 30)
	LARGE_FONT= ("Verdana", 12)
	NORM_FONT= ("Verdana", 10)
	SMALL_FONT= ("Verdana", 8)

	popup = tk.Tk()
	popup.wm_title(title)
	label = ttk.Label(popup, text=msg, font=XL_FONT)
	label.pack(side='top', fill='x', pady=20, padx = 35)
	B1 = ttk.Button(popup, text='Okay', command = popup.destroy)
	B1.pack()
	popup.mainloop()

def check():
	"""
	Continiously checks the predicted amount of people in the building. 
	"""
	#time to wait between each run, in seconds
	waittime = 30

	#number of minutes that the warning should be in advance of the building being full
	warningmin = 20

	#initializing the amount of people in the building
	currentamount = 0

	while currentamount < maxnum:
		now = dt.datetime.today()
		#now = dt.datetime.strptime('10-31-2017 22:15:00', '%m-%d-%Y %H:%M:%S')

		downloadData()
		dates, amount = loadData(now)
		
		#break the loop if the data is not of today
		if len(dates) < 1:
			print('No data of today yet. Skipping check...')
		else:
			deriv, fulltime, currentamount = findDeriv(dates, amount, now)
		
			#print the message indicating how full the building is
			fullmessage = 'S.C.R.E.D. at {0}/{1} capacity. Full in {2}:%02d'.format(int(currentamount), maxnum, int(fulltime/60)) % int(fulltime % 60)
			print(fullmessage)

			#show a warning when the building will be full in less than 15 minutes
			if currentamount > 180 and (fulltime / 60) < warningmin and fulltime > 0:
				popupmsg(fullmessage)
			
		#wait for a few seconds
		time.sleep(waittime)
   
now = dt.datetime.strptime('10-31-2017 22:15:00', '%m-%d-%Y %H:%M:%S')

downloadData()
dates, amount = loadData(now)

makeplot(dates, amount, now)

#check()






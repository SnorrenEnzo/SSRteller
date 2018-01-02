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
#for interpreting random forests etc
from treeinterpreter import treeinterpreter as ti

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

#name of the file containing the dates for the train data
train_data_name = 'Dinsdagborrel_train_dates.txt'


def downloadData():
	#list of first and last data points for each day. From these the plotting
	#range is determined
	earliestlist = []
	latestlist = []

	url = "https://api.joostvansomeren.nl/teller/log.txt"

	#download log
	print("Downloading data")
	urlretrieve(url, downloadname)
	
def loadData(load_date):
	"""
	Load the data of today.

	Input:
		load_date (datetime or date): the date of day the data should be loaded from
	"""
	monthlist = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

	try:
		#convert the date to a date object if it is not already
		load_date = load_date.date()
	except:
		pass
	
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
			if tdatetime.date() == load_date or tdatetime.date() == load_date + dt.timedelta(days = 1):
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

def datesToSeconds(dates, current_date, hourshift = 6):
	"""
	Convert dates to seconds for easy application of models. The reference point is
	00:00 h of the 'current' date. The dates will also be shifted back a few hours, 
	as most parties/evenings will go beyond 24:00 h.
	"""

	try:
		#convert the date to a date object if it is not already
		current_date = current_date.date()
	except:
		pass

	x_seconds = np.zeros(len(dates))
	for i in np.arange(len(dates)):
		x_seconds[i] = (dates[i] - dt.timedelta(hours = hourshift) - dt.datetime.combine(current_date, dt.time(0, 0))).total_seconds()

	return x_seconds

def secondsToDates(seconds, current_date, hourshift = 6):
	"""

	"""
	time = []
	for sec in seconds:
		h = int(sec / 3600.)
		m = int(sec / 60. - h * 60.)
		s = int(sec - m * 60. - h * 3600.)
		
		if h < 24:
			time.append(dt.datetime.combine(current_date, dt.time(h, m, s)) + dt.timedelta(hours = hourshift))
		else:
			time.append(dt.datetime.combine(current_date, dt.time(h - 24, m, s)) + dt.timedelta(days = 1, hours = hourshift))

	return time

def applyForest(train_set, test_set, test_dates, train_date, test_date, hourshift):
	"""
	Applies a random forest to the data.

	Input:
		train_set (length 3 float array): array containing the training data. The
		first entry contains the time of day in seconds (note that this time has
		been shifted), the second entry the amount of people and the third the number
		of seconds before the peak (300 people) is reached.\n
		test_set (length 3 float array): the same, but now for the test data.\n
		test_dates (datetime array): datetime objects for each data point 
		in the test data.
		train_date, test_date (datetime date): the date for the train and test data.\n
		hourshift (int): the amount of hours the time arrays are shifted
		back by.
	"""
	from sklearn.ensemble import RandomForestClassifier
	sns.set()
	
	#select all dates before our measurement point
	#amount = amount[dates < now]
	#dates = dates[dates < now]

	X_train = np.array([train_set[0], train_set[1]]).T
	X_test = np.array([test_set[0], test_set[1]]).T

	#create and train the random forest
	#multi-core CPUs can use: 
	clf = RandomForestClassifier(n_estimators=50, n_jobs=3)
	clf.fit(X_train, train_set[2])

	#print(clf.predict(test_set))
	print(clf.score(X_test, test_set[2]))
	
	prediction = clf.predict(X_test)

	#convert the seconds data back to time
	test_time = secondsToDates(test_set[0], test_date, hourshift = hourshift)
	prediction_timeto = secondsToDates(test_set[0] + prediction, test_date, hourshift = hourshift)
	test_timeto = secondsToDates(test_set[0] + test_set[2], test_date, hourshift = hourshift)


	#plot with two axes:
	fig, ax1 = plt.subplots()
	#plot the prediction data
	lns1 = ax1.plot(test_time, prediction_timeto, label = 'Prediction', color = '#3E3FE3')
	lns2 = ax1.plot(test_time, test_timeto, label = 'Actual', color = '#B53BE3')

	#find the minimum date/time
	starttime = dt.datetime.combine(dt.date.today(), dt.time(20, 0))
	endtime = dt.datetime.combine(dt.date.today(), dt.time(20, 0)) + dt.timedelta(hours = 9)

		#Change the xticks to display hours and minutes only
	orig_mindate = np.min(prediction_timeto)
	#then round this down to the hour
	discard = dt.timedelta(minutes=orig_mindate.minute)
	mindate = orig_mindate - discard
	#then make arrays needed to change the ticks
	oldLabels = np.arange(mindate, np.max(prediction_timeto) + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
	newLabels = []
	for d in oldLabels:
		newLabels.append(d.strftime("%H:%M"))
	#change the y ticks
	plt.yticks(oldLabels, newLabels)
	plt.ylim(np.min(oldLabels), np.max(oldLabels))


	#makes another y-axis
	ax2 = ax1.twinx()

	#plot amount of people in the building
	lns3 = ax2.plot(test_dates, test_amount, color = 'r', label = 'Amount')
	#Changes the colour of the tick labels to match the line colour
	for tl in ax2.get_yticklabels():
		tl.set_color('r')

		#Change the xticks to display hours and minutes only
	orig_mindate = np.min(test_time)
	#then round this down to the hour
	discard = dt.timedelta(minutes=orig_mindate.minute)
	mindate = orig_mindate - discard
	#then make arrays needed to change the ticks
	oldLabels = np.arange(mindate, np.max(test_time) + dt.timedelta(hours = 1), dt.timedelta(hours = 1)).astype(dt.time)
	newLabels = []
	for d in oldLabels:
		#add the 'hourshift' amount of hours again to make it show the correct hours
		newLabels.append(d.strftime("%H:%M"))
	#change the x ticks
	plt.xticks(oldLabels, newLabels)
	plt.xlim(np.min(oldLabels), np.max(oldLabels))
	

	#auto rotate the labels
	fig.autofmt_xdate()

	#turn off the grid
	#plt.grid()

	#combines all labels into a single legend
	lns = lns1 + lns2 + lns3
	labs = [l.get_label() for l in lns]
	ax1.legend(lns, labs, loc='upper left')

	ax1.set_xlabel('Time')
	ax1.set_ylabel('Predicted time')
	ax2.set_ylabel('Amount of people in the building')
	plt.title('Predicted time of the building to be full for {0}\nusing Random Forests'.format(test_date))

	plt.savefig('{0} Time until full prediction with RF - more train data.png'.format(test_date), bbox_inches = 'tight', dpi = 200)
	plt.show()
	
	#ts = dt.datetime.fromtimestamp(x_seconds[0]).strftime('%Y-%m-%d %H:%M:%S')
	#print(ts)
	'''
		#here we implement code from:
		# http://blog.datadive.net/random-forest-interpretation-with-scikit-learn/
		#it can be used to interpret the tree chosen by the random forests method
	prediction, bias, contributions = ti.predict(clf, X_test)

	for i in range(len(X_test)):
		print("Instance", i)
		print("Bias (trainset mean)", bias[i])
		print("Feature contributions:")
		for c, feature in sorted(zip(contributions[i], test_dates), key=lambda x: -abs(x[0])):
			print(feature, round(c, 2))
		print("-"*20 )
	'''

def timeTo(sec, amount, peakvalue = 300):
	"""
	This function makes an array containing the time in seconds until the peak 
	is reached.

	Input:
		sec (float array); the time in seconds.\n
		amount (float array): the amount of people in the building.\n
		peakvalue (int): the peak amount of which we want to predict the time it 
		is reached.

	Output:
		timeto (float array): time until the peakvalue is reached.
	"""

	try:
		#find the moment at which the max of 300 people is reached
		peakloc = np.where(amount == peakvalue)[0][0]
	except:
		return np.zeros(len(sec)) + sec[0]

	timeto = np.zeros(len(sec))
	for i in np.arange(len(timeto)):
		timeto[i] = sec[peakloc] - sec[i]

	return timeto

   
#now = dt.datetime.strptime('10-31-2017 22:15:00', '%m-%d-%Y %H:%M:%S')

# train_date = dt.date(2016, 12, 6)


#instead of a single train date, we will use multiple
#date_list_train = np.arange(dt.date(2016, 9, 6), dt.date(2016, 12, 21), dt.timedelta(days = 7)).astype(dt.date)
traindates_str = np.loadtxt(train_data_name, dtype = str)[4:10]
#convert string to date objects
date_list_train = []
for dstr in traindates_str:
	date_list_train.append(dt.datetime.strptime(dstr[0], '%Y-%m-%d'))
date_list_train = np.array(date_list_train)

#the test date
test_date = dt.date(2017, 10, 17)

#download the data again
#downloadData()
# train_set = np.array(loadData(train_date))
# test_set = np.array(loadData(test_date))

#the date ranges for the train and test set
# date_list_train = np.arange(dt.date(2016, 9, 6), dt.date(2016, 12, 21), dt.timedelta(days = 7)).astype(dt.date)
# date_list_test = np.arange(dt.date(2017, 9, 5), dt.date(2017, 12, 20), dt.timedelta(days = 7)).astype(dt.date)

#the amount of hours the date arrays are shifted by
hourshift = 6

#the arrays containing the training data
train_dates = []
train_amount = []
train_sec = []
train_timeto = []
#loop over all the train dates and append the data
for d in date_list_train:
	print('Loading data of {0}'.format(d.date()))

	dates, amount = loadData(d)

	train_dates = np.append(train_dates, dates)
	train_amount = np.append(train_amount, amount)

	#convert the dates to seconds
	sec = datesToSeconds(dates, d, hourshift = hourshift)
	train_sec = np.append(train_sec, sec)

	#now we also make arrays for the time until the building was full. This is what
	#we want to classify
	train_timeto = np.append(train_timeto, timeTo(sec, amount))

# train_dates, train_amount = loadData(train_date)
	#now do the same for the test data
test_dates, test_amount = loadData(test_date)

#convert the dates to seconds	
test_sec = datesToSeconds(test_dates, test_date, hourshift = hourshift)

#now we also make arrays for the time until the building was full. This is what
#we want to classify
test_timeto = timeTo(test_sec, test_amount)

#slice the test data so that the program does not know when it is actually full
sliceloc = np.where(test_dates < dt.datetime.combine(test_date, dt.time(22, 30)))
test_dates = test_dates[sliceloc]
test_amount = test_amount[sliceloc]
test_sec = test_sec[sliceloc]
test_timeto = test_timeto[sliceloc]

applyForest(np.array([train_sec, train_amount, train_timeto]), np.array([test_sec, test_amount, test_timeto]), test_dates, date_list_train[0], test_date, hourshift)

#check()






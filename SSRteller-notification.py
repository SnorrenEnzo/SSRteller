import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
#for downloading
from urllib.request import urlretrieve
#for removing the downloaded file
import os
#for making and reading an SQL database
# import sqlite3 as lite
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
#number of people when it is almost full
almost_full = 240

#name where the data will be downloaded
downloadname = "./teller_log.txt"

#name of the file containing the dates for the train and test data
train_data_name = 'Dinsdagborrel_train_dates.txt'
test_data_name = 'Dinsdagborrel_test_dates.txt'

#the time before which data is thrown away
mintime = dt.time(20, 0)

#the amount of hours the date arrays are shifted by
hourshift = 6


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

def applyForest(X_train, X_test, Y_train, Y_test, train_dates, test_dates, hourshift, feat_names, append_results = True):
	"""
	Applies a random forest to the data.

	Input:
		X_train, X_test (2D float arrays): arrays containing the features for
		the training and test sets.\n
		Y_train, Y_test (2D float arrays); arrays containing the outcome and
		desired outcome for the training and test set respectively.\n
		train_date, test_date (datetime date): the date for the train and test data.\n
		hourshift (int): the amount of hours the time arrays are shifted
		back by.\n
		feat_names (str array): names of the features used.\n
		append_results (boolean): whether to append the difference between the 
		predicted and true end time for the test data to a csv file.
	"""
	from sklearn.ensemble import RandomForestClassifier
	#for handling mission X data
	from sklearn.preprocessing import Imputer
	import pandas as pd
	#for interpreting random forests etc
	from treeinterpreter import treeinterpreter as ti

	sns.set()

	#preprocessing strategy
	strat = 'mean'

	#the type of features used 
	feat_type = 'avg,deriv,n=1000,diffdataStop'

		#preprocess the data: take out the nans
	# Create our imputer to replace missing values with the mean e.g.
	imp = Imputer(missing_values='NaN', strategy=strat, axis=0)
	imp = imp.fit(X_train)

	# Impute our data, then train
	X_train_imp = imp.transform(X_train)

	# Impute each test item, then predict
	X_test_imp = imp.transform(X_test)

	#create and train the random forest
	#multi-core CPUs can use: 
	clf = RandomForestClassifier(n_estimators=1000, n_jobs=3)
	clf.fit(X_train_imp, Y_train)

	#print(clf.predict(test_set))
	#print(clf.score(X_test, test_set[2]))
	
	prediction = clf.predict(X_test_imp)

	#print the prediction and comparison with truth
	predic_offset = np.zeros(len(prediction))
	for j in np.arange(len(prediction)):
		print('\nDate: {0}'.format(test_dates[j].date()))
		print('Predicted full time: {0}'.format(secondsToDates([prediction[j]], test_dates[j], hourshift = hourshift)))
		offset = (Y_test[j] - prediction[j])/60.
		print('Time difference: {0} min'.format(round(offset, 1)))
		predic_offset[j] = offset

	if append_results:
		#write the prediction offset to a csv
		csv_input = pd.read_csv('Prediction_offset_results.csv')
		csv_input['Strat={0}|{1}'.format(strat, feat_type)] = predic_offset
		csv_input.to_csv('Prediction_offset_results.csv', index=False)


	importances = clf.feature_importances_
	indices = np.argsort(importances)[::-1]
	# print(feat_names)
	# print(importances)
	# print(np.shape(X_train))
	# print(np.shape(importances), np.shape(range(X_test.shape[1])))
	# std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
	# plt.bar(range(X_test.shape[1]), importances,color="r", yerr=std, align="center")
	#plt.xticks(range(X_test.shape[1]), indices)
	#plt.xlim([-1, X_test.shape[1]])
	# plt.show()

	'''
		#here we implement code from:
		# -
		#it can be used to interpret the tree chosen by the random forests method
	ti_pred, bias, contributions = ti.predict(clf, X_test_imp)
	print('contributions')
	print(np.shape(contributions))
	print(len(X_test))

	for i in range(len(X_test)):
		print("Instance", i)
		print("Bias (trainset mean)", bias[i])
		print("Feature contributions:")
		for c, feat in zip(contributions[i], feat_names):
			print(feat, c)#round(c, 2)
		print("-"*20 )
	'''

	'''
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
	loc = np.where(amount == peakvalue)

	if len(loc[0]) > 0:
		peakloc = np.where(amount == peakvalue)[0][0]
	else:
		return np.zeros(len(sec)) + sec[0]

	timeto = np.zeros(len(sec))
	for i in np.arange(len(timeto)):
		timeto[i] = sec[peakloc] - sec[i]

	return timeto

def loadRFdata(date_list, mintime, hourshift):
	"""
	Load the train or test data for the random forests classifier.

	"""

	downloadData()

	#the dictionaries containing the training data. We do not use arrays, because
	#the data is of different lengths
	dates = {}
	amount = {}
	sec = {}
	#the maximum amount of people in the building at that date
	max_amount = []
	#the time at which the building is full, in seconds
	fulltime = []

	#loop over all the train dates and append the data
	for d, i in zip(date_list, np.arange(len(date_list))):
		print('Loading data of {0}'.format(d.date()))

		temp_dates, temp_amount = loadData(d)

		#check if there is actually any useful data
		if len(temp_dates) > 10:
			#cut out the data points which are way to early
			nottooearly = np.where(temp_dates > dt.datetime.combine(d.date(), mintime))
			temp_dates = temp_dates[nottooearly]
			temp_amount = temp_amount[nottooearly]

			#find the max
			maxamount = np.max(temp_amount)
			max_amount = np.append(max_amount, maxamount)

			#slice the data to the point where it almost full
			peakloc = np.argmax(temp_amount)
			sliceidx = (np.arange(len(temp_amount)) < peakloc) * (temp_amount < 290)
			temp_dates = temp_dates[sliceidx]
			temp_amount = temp_amount[sliceidx]

			dates[i] = temp_dates
			amount[i] = temp_amount

			temp_sec = datesToSeconds(temp_dates, d, hourshift = hourshift)
			sec[i] = temp_sec

			#now we also make arrays for the time until the max is reached. This is what
			#we want to classify
			#train_timeto[i] = timeTo(sec, amount, peakvalue = maxamount)

			#get the time of the peak (the last entry in the sec array)
			fulltime = np.append(fulltime, temp_sec[-1])

	return dates, amount, sec, max_amount, fulltime


def getFeatures(train_date, dates, amount, sec):
	"""
	Extracts desired features from the data. Corrently the features are the 
	average values of the amount and the derivatives in half hour time bins.

	Input:
		train_date (date object): the date of the given data.\n
		dates (datetime array): the datetime objects indicating the time for each 
		data point.\n
		amount (float array): the amount of people in the building at each data point.\n
		sec (float array): the time of the data point converted to seconds and 
		shifted a few hours forward (see 'hourshift').

	Output:
		features (float array): values of the features concatenated to a single 
		array.
	"""
	#Feature 1 and 2: averages and derivates of time bins, starting at mintime
	#the range of datetimes that is used as the bin edges
	timerange = np.arange(dt.datetime.combine(train_date, mintime), dt.datetime.combine((train_date + dt.timedelta(days = 1)), dt.time(3, 0)), dt.timedelta(minutes = 15)).astype(dt.datetime)

	avg = np.zeros(len(timerange)-1) * np.nan
	deriv = np.zeros(len(timerange)-1) * np.nan

	for i in np.arange(len(timerange) - 1):
		#slice the train_amount array between timerange entry i and i+1
		sliceloc = (dates > timerange[i]) * (dates < timerange[i+1])
		
		#check if there still is data
		if np.sum(sliceloc) > 0:
			sliced_amount = amount[sliceloc]
			#obtain the average 
			avg[i] = np.mean(sliced_amount)

			#slice the seconds array as well
			sliced_sec = sec[sliceloc]

			#obtain the derivative
			deriv[i] = (sliced_amount[-1] - sliced_amount[0]) / (sliced_sec[-1] - sliced_sec[0])

	return np.append(avg, deriv)

   
#now = dt.datetime.strptime('10-31-2017 22:15:00', '%m-%d-%Y %H:%M:%S')

#obtain the names of the features
fdate = dt.date(2017, 10, 5)
feat_timerange = np.arange(dt.datetime.combine(fdate, mintime), dt.datetime.combine((fdate + dt.timedelta(days = 1)), dt.time(3, 0)), dt.timedelta(minutes = 15)).astype(dt.datetime)
feat_names = []
for f in ['avg', 'deriv']:
	for t in feat_timerange:
		feat_names.append('{0} {1}'.format(f, t.time()))

#The dates of the training data
#date_list_train = np.arange(dt.date(2016, 9, 6), dt.date(2016, 12, 21), dt.timedelta(days = 7)).astype(dt.date)
traindates_str = np.loadtxt(train_data_name, dtype = str)
#convert string to date objects
date_list_train = []
for dstr in traindates_str:
	date_list_train.append(dt.datetime.strptime(dstr, '%Y-%m-%d'))
date_list_train = np.array(date_list_train)

#The dates of the test data
#date_list_test = np.arange(dt.date(2017, 9, 5), dt.date(2017, 10, 2), dt.timedelta(days = 7)).astype(dt.date)
'''
testdates_str = np.loadtxt(test_data_name, dtype = str)

#convert string to date objects
date_list_test = []
for dstr in testdates_str:
	date_list_test.append(dt.datetime.strptime(dstr, '%Y-%m-%d'))
date_list_test = np.array(date_list_test)
'''
date_list_test = np.array([dt.datetime(2018, 1, 9)])


#load the trainings data
train_dates, train_amount, train_sec, train_max, train_fulltime = loadRFdata(date_list_train, mintime, hourshift)

	#Extract features from the training data
#the matrix containing all the features
train_features = []
for k in train_dates.keys():
	train_features.append(getFeatures(date_list_train[k].date(), train_dates[k], train_amount[k], train_sec[k]))
train_features = np.reshape(np.array(train_features), (len(train_dates.keys()), -1))


#load the test data
test_dates, test_amount, test_sec, test_max, test_fulltime = loadRFdata(date_list_test, mintime, hourshift)

#slice the test data so that the program does not know when it is actually full
for k in test_dates.keys():
	#sliceloc = np.where(test_dates[k] < dt.datetime.combine(test_dates[k][0].date(), dt.time(22, 30)))
	#location of the peak
	peakloc = np.argmax(test_amount[k])
	#slice to everything earlier than the peak and with an amount lower than the peak
	sliceloc = (test_amount[k] < peakloc) * (test_amount[k] < almost_full)
	test_dates[k] = test_dates[k][sliceloc]
	test_amount[k] = test_amount[k][sliceloc]
	test_sec[k] = test_sec[k][sliceloc]


	#Extract features from the test data
#the matrix containing all the features
test_features = []
for k in test_dates.keys():
	test_features.append(getFeatures(date_list_test[k].date(), test_dates[k], test_amount[k], test_sec[k]))
test_features = np.reshape(np.array(test_features), (len(test_dates.keys()), -1))


applyForest(train_features, test_features, train_fulltime, test_fulltime, date_list_train, date_list_test, hourshift, feat_names, append_results = False)


#continuously loop the program
#check()


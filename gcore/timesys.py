import time

def nowDateTime():
	return (time.strftime("%Y-%m-%d %H:%M:%S"))

def convepoch(date):
	return time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(int(date)/1000.))

def humanTime(time_string):
	if time_string <= 60:
		time_string = str(time_string)+' Seconds'
	elif time_string > 60 and time_string < 3600:
		time_string = str(round(float(time_string)/60,2))+' Minutes'
	elif time_string >= 3600:	
		time_string = str(round(float(time_string)/3600,2))+' Hours'
	return time_string
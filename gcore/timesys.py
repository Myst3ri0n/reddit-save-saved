import time

def nowDateTime():
	return (time.strftime("%Y-%m-%d %H:%M:%S"))

def convepoch(date):
	return time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(int(date)/1000.))
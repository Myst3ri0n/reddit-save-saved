from random import randint
from .timesys import nowDateTime
import os
import csv

class logWriter(object):
    def __init__(self):
        self.logFile = "log.csv"
        self.firstLog = os.path.isfile(self.logFile)
        self.logA = open(self.logFile, 'a')
        if not self.firstLog:
            self.logA.write("Job Number,Date/Time,Log Message\n")
            self.jobNum = str(randint(1000,1000000))
        else:
            jobNums = []
            with open("log.csv", 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    jobNums.append(row[0])
            jobNums.remove('Job Number')
            self.jobNum = str(int(max(jobNums))+1)
            
    def logUp(self, msg):
        self.logStr = "\""+self.jobNum+"\",\""+nowDateTime()+"\",\""+msg+"\""
        self.logA.write(self.logStr+"\n")

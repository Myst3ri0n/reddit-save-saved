import os


#checks for existence of file and removes if present
def exRm(fileName):
	fileCheck = os.path.isfile(fileName)
	if fileCheck == True:
		os.remove(fileName)

#Outputs file size to human readable format.
def getFileSize(file):
	fileSize = os.path.getsize(file)
	if fileSize<1024:
		return str(fileSize)+' Bytes'
	elif fileSize >=1024 and fileSize<1048576:
		return str(fileSize/1024)+' KB'
	elif fileSize>=1048576 and fileSize<1073741824:
		return str(fileSize/1048576)+' MB'
	elif fileSize>=1073741824 and fileSize<1099511627776:
		return str(fileSize/1073741824)+' GB'
	else: return str(fileSize/1099511627776)+' TB'

#List directorys and remove hidden files from result
def lsDirVis(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f
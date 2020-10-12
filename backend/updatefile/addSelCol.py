import os,subprocess,psutil,re,shutil,datetime,sys,glob
import csv
import ctypes

def addSelCol():
	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	filename='ReportBook_mother_file.csv'
	filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
	addselfile="addsel.csv"
	aoutput= open(addselfile,'w')
	with open(filepath,'r') as f:
		for line in f:
			info=line.rstrip().split('\t')
			if 'UniProtKB Accession' in info:
				info.insert(0,"sel")
				aoutput.write(('\t'.join(info))+'\n')
			else:
				info.insert(0,"")
				aoutput.write(('\t'.join(info))+'\n')
	aoutput.close()
	movefilepath=os.path.join(homedir, 'updatefile', filename)
	os.rename(addselfile,filename)
	shutil.move(movefilepath,filepath)
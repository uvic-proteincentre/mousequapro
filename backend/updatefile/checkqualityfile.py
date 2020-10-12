import os,subprocess,psutil,re,shutil,datetime,sys,glob
import random, time
import csv
import requests
import operator
import ctypes

#increase the field size of CSV
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
filename='ReportBook_mother_file.csv'
filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
modrepfile="modreprot.csv"
moutput= open(modrepfile,'w')
with open(filepath,'r') as f:
	for line in f:
		data=line.rstrip()
		info=data.split('\t')
		if '502' in info:
			info[1]='Q9H7Z3'
		moutput.write(('\t'.join(info))+'\n')
moutput.close()
movefilepath=os.path.join(homedir, 'updatefile', filename)
os.rename(modrepfile,filename)
shutil.move(movefilepath,filepath)
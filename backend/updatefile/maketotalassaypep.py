import os,subprocess,psutil,re,shutil,datetime,sys,glob
from socket import error as SocketError
import errno
import random, time
import csv
import json
import pandas as pd
from collections import Counter
from itertools import combinations
import operator
import collections
import ctypes

def totalAssayPep():
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	filename='ReportBook_mother_file.csv'
	pepfilepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)

	pepresult = csv.DictReader(open(pepfilepath,'r'), delimiter='\t')

	totalpepseq=[]
	for reppeprow in pepresult:
		totalpepseq.append(str(reppeprow['Peptide Sequence']).strip())
	unqtotalpepseq=list(set(totalpepseq))
	calfilename='totalpepassay.py'
	calmovefilepath=os.path.join(homedir, 'updatefile', calfilename)
	calfilepath = os.path.join(homedir, 'src/qmpkbapp', calfilename)

	totalassayresult={}
	totalassayresult['totalpepassay']=unqtotalpepseq

	calfileoutput=open(calfilename,'w')
	calfileoutput.write("totalpepassay=")
	calfileoutput.write(json.dumps(totalassayresult))
	calfileoutput.close()
	shutil.move(calmovefilepath,calfilepath)
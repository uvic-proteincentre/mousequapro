# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import Counter
from itertools import combinations
import ast
from operator import itemgetter
import operator
import json
import re,sys
import itertools
from collections import OrderedDict
import datetime
from statistics import mean
# function to generate peptidebased info into nested json format
def updateDataToDownload(jfinaldata):
	tempjfinaldata=[]
	for jitem in jfinaldata:
		sumtempconcendata=jitem["Summary Concentration Range Data"]
		alltempconcendata=jitem["All Concentration Range Data"]
		allConDataSampleLLOQ=jitem["All Concentration Range Data-Sample LLOQ Based"]


		sumconcinfo=jitem["Summary Concentration Range Data"].split(';')

		sumtempconcendata=['|'.join(x.split('|')[1:]) for x in sumtempconcendata.split(';')]
		alltempconcendata=['|'.join(x.split('|')[1:]) for x in alltempconcendata.split(';')]
		allConDataSampleLLOQ=['|'.join(x.split('|')[1:]) for x in allConDataSampleLLOQ.split(';')]

		sumconclist=[]
		for scitem in sumconcinfo:
			scinfo =scitem.split('|')
			measuredSampSize=int(scinfo[5].split('/')[1])
			for i in range(0,measuredSampSize):
				tempStempidInfo=scinfo[1:5]
				tempStempidInfo.insert(2,str(i+1))
				stempid='|'.join(map(str,tempStempidInfo))
				sumconclist.append([stempid,'NA|NA|NA'])
		for s in sumconclist:
			for x in allConDataSampleLLOQ:
				if len(x)>0:
					tempID='|'.join(x.split('|')[:5])
					if tempID == s[0]:
						s[1]='|'.join(x.split('|')[5:])
		finalAllConDataSampleLLOQ=['|'.join(y) for y in sumconclist]
		jitem["Summary Concentration Range Data"]=';'.join(sumtempconcendata)

		jitem["All Concentration Range Data"]=';'.join(alltempconcendata)
		jitem["All Concentration Range Data-Sample LLOQ Based"]=';'.join(finalAllConDataSampleLLOQ)

		tempjfinaldata.append(jitem)

	return tempjfinaldata
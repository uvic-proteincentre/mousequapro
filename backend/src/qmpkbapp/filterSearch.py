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
def filterSearch(jfinaldata,searchterm,searchtype):
	sexQuery=''
	strainQuery=''
	bioMatQuery=''
	knockoutQuery=''
	panelQuery=''
	tempjfinaldata=[]
	filteredUniProtIDs=[]
	try:
		sexQuery=searchterm[searchtype.index('sex')].strip()
	except ValueError:
		pass
	try:
		strainQuery=searchterm[searchtype.index('strain')].strip()
	except ValueError:
		pass
	try:
		bioMatQuery=searchterm[searchtype.index('biologicalMatrix')].strip()
	except ValueError:
		pass
	try:
		knockoutQuery=searchterm[searchtype.index('knockout')].strip()
	except ValueError:
		pass
	try:
		panelQuery=searchterm[searchtype.index('panel')].strip()
	except ValueError:
		pass
	for jitem in jfinaldata:
		sumConData=str(jitem["Summary Concentration Range Data"])
		allConData=str(jitem["All Concentration Range Data"])
		allConDataSampleLLOQ=str(jitem["All Concentration Range Data-Sample LLOQ Based"])
		sumConDataInfo=sumConData.split(';')
		allConDataInfo=allConData.split(';')
		allConDataSampleLLOQInfo=allConDataSampleLLOQ.split(';')


		if len(bioMatQuery.strip()) >0 and bioMatQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]
			allConDataInfo=[s for s in allConDataInfo for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]

		if len(strainQuery.strip()) >0 and strainQuery.strip().lower() !='na':
			sumConDataInfo=[s  for s in sumConDataInfo for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[3]]
			allConDataInfo=[s for s in allConDataInfo for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[4]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[4]]

		if len(sexQuery.strip()) >0 and sexQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[4]]
			allConDataInfo=[s for s in allConDataInfo for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[5]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[5]]

		if len(knockoutQuery.strip()) >0 and knockoutQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in  str(s).strip().lower().split('|')[1].split(' ')[0]]
			allConDataInfo=[s for s in allConDataInfo for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in str(s).strip().lower().split('|')[1].split(' ')[0]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in str(s).strip().lower().split('|')[1].split(' ')[0]]

		if len(panelQuery.strip()) >0 and panelQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  panelQuery.lower().split('|') if q in str(s).strip().lower().split('|')[0]]
			allConDataInfo=[s for s in allConDataInfo for q in  panelQuery.lower().split('|') if q in str(s).strip().lower().split('|')[0]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  panelQuery.lower().split('|') if q in str(s).strip().lower().split('|')[0]]
		
		
		if len(sumConDataInfo)>0:
			jitem["Summary Concentration Range Data"]=';'.join(sumConDataInfo)
		else:
			jitem["Summary Concentration Range Data"]='NA'

		if len(allConDataInfo)>0:
			jitem["All Concentration Range Data"]=';'.join(allConDataInfo)
		else:
			jitem["All Concentration Range Data"]='NA'

		if len(allConDataInfo)>0:
			jitem["All Concentration Range Data-Sample LLOQ Based"]=';'.join(allConDataSampleLLOQInfo)
		else:
			jitem["All Concentration Range Data-Sample LLOQ Based"]='NA'


		if len(jitem["Summary Concentration Range Data"].strip())>0  and (str(jitem["Summary Concentration Range Data"]).strip()).lower() !='na':
			coninfo=(jitem["Summary Concentration Range Data"].strip()).split(';')
			if len(coninfo)>0:
				subconinfo=coninfo[0].split('|')
				condata="Mean Conc.:"+str(subconinfo[6])+"<br/>Matix:"+str(subconinfo[2])
				tempSampleLLOQInfo=str(jitem['Sample LLOQ'].strip()).split(';')
				if str(subconinfo[6]) =='NA':
					for samLLOQ in tempSampleLLOQInfo:
						if str(subconinfo[2]) in samLLOQ.split('|'):
							condata="<"+str(samLLOQ.split('|')[1].strip())+"(Sample LLOQ)<br/>Matix:"+str(subconinfo[2])
				jitem["Concentration View"]=condata
				strainlist=[]
				sexlist=[]
				matrixlist=[]
				panellist=[]
				knockoutlist=[]
				meanConclist=[]
				unitlist=[]
				for i in coninfo:
					l=i.split('|')
					strainlist.append(l[3])
					sexlist.append(l[4])
					matrixlist.append(l[2])
					panellist.append(l[0])
					knockoutlist.append(l[1])
					meanConcData=l[6]
					unitlist.append(l[6].split(' (')[-1])
					if meanConcData !='NA':
						meanConclist.append(l[2]+':'+str(meanConcData))
					else:
						for samXLLOQ in tempSampleLLOQInfo:
							if str(l[2]) in samXLLOQ.split('|'):
								meanConclist.append("<"+str(samXLLOQ.split('|')[1].strip())+"(Sample LLOQ-"+str(l[2])+")")
				if len(strainlist)>0:
					jitem["Strain"]='<br>'.join(list(set(strainlist)))
					jitem["Sex"]='<br>'.join(list(set(sexlist)))
					jitem["Biological Matrix"]='<br>'.join(list(set(matrixlist)))
					panellist=[x for p in panellist for x in p.split(',')]
					jitem["Panel"]=';'.join(list(set(panellist)))
					jitem["knockout"]=';'.join(list(set(knockoutlist)))
					countSampleLLOQ=len([mc for mc in meanConclist if 'Sample LLOQ' in mc])
					if len(meanConclist) ==countSampleLLOQ:
						meanConclist=list(set(meanConclist))
						jitem['Concentration Range']='<br/>'.join(meanConclist[:2])
					else:
						meanConclist=[m for m in meanConclist if 'Sample LLOQ' not in m]
						meanConclist=list(set(meanConclist))
						jitem['Concentration Range']='<br/>'.join(meanConclist[:2])

				else:
					jitem["Strain"]='NA'
					jitem["Sex"]='NA'
					jitem["Biological Matrix"]='NA'
					jitem["Panel"]='NA'
					jitem["knockout"]='NA'
					jitem["Concentration Range"]='NA'

			jitem["Summary Concentration Range Data"]=jitem["Summary Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
			jitem["Summary Concentration Range Data"]=jitem["Summary Concentration Range Data"].replace('ug protein/u','µg protein/µ')
			jitem["Summary Concentration Range Data"]=jitem["Summary Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

			jitem["All Concentration Range Data"]=jitem["All Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
			jitem["All Concentration Range Data"]=jitem["All Concentration Range Data"].replace('ug protein/u','µg protein/µ')
			jitem["All Concentration Range Data"]=jitem["All Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

			jitem["All Concentration Range Data-Sample LLOQ Based"]=jitem["All Concentration Range Data-Sample LLOQ Based"].replace('fmol target protein/u','fmol target protein/µ')
			jitem["All Concentration Range Data-Sample LLOQ Based"]=jitem["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/u','µg protein/µ')
			jitem["All Concentration Range Data-Sample LLOQ Based"]=jitem["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/mg','µg protein/mg')

			jitem["Concentration View"]=jitem["Concentration View"].replace('fmol target protein/u','fmol target protein/µ')
			jitem["Concentration Range"]=jitem["Concentration Range"].replace('fmol target protein/u','fmol target protein/µ')
			
			tempjfinaldata.append(jitem)
		else:
			filteredUniProtIDs.append(jitem["UniProtKB Accession"])

	return tempjfinaldata,filteredUniProtIDs


def filterConcentration(jfinaldata,searchterm,searchtype):
	sexQuery=''
	strainQuery=''
	bioMatQuery=''
	knockoutQuery=''
	tempjfinaldata=[]
	try:
		sexQuery=searchterm[searchtype.index('sex')].strip()
	except ValueError:
		pass
	try:
		strainQuery=searchterm[searchtype.index('strain')].strip()
	except ValueError:
		pass
	try:
		bioMatQuery=searchterm[searchtype.index('biologicalMatrix')].strip()
	except ValueError:
		pass
	try:
		knockoutQuery=searchterm[searchtype.index('knockout')].strip()
	except ValueError:
		pass


	for jitem in jfinaldata:
		sumConData=str(jitem["Summary Concentration Range Data"])
		allConData=str(jitem["All Concentration Range Data"])
		allConDataSampleLLOQ=str(jitem["All Concentration Range Data-Sample LLOQ Based"])
		sumConDataInfo=sumConData.split(';')
		allConDataInfo=allConData.split(';')
		allConDataSampleLLOQInfo=allConDataSampleLLOQ.split(';')

		if len(bioMatQuery.strip()) >0 and bioMatQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]
			allConDataInfo=[s for s in allConDataInfo for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  bioMatQuery.lower().split('|') if q == str(s).strip().lower().split('|')[2]]

		if len(strainQuery.strip()) >0 and strainQuery.strip().lower() !='na':
			sumConDataInfo=[s  for s in sumConDataInfo for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[3]]
			allConDataInfo=[s for s in allConDataInfo for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[4]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  strainQuery.lower().split('|') if q == str(s).strip().lower().split('|')[4]]

		if len(sexQuery.strip()) >0 and sexQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[4]]
			allConDataInfo=[s for s in allConDataInfo for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[5]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  sexQuery.lower().split('|') if q==str(s).strip().lower().split('|')[5]]

		if len(knockoutQuery.strip()) >0 and knockoutQuery.strip().lower() !='na':
			sumConDataInfo=[s for s in sumConDataInfo for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in  str(s).strip().lower().split('|')[1].split(' ')[0]]
			allConDataInfo=[s for s in allConDataInfo for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in str(s).strip().lower().split('|')[1].split(' ')[0]]
			if 'NA' != ''.join(list(set(allConDataSampleLLOQInfo))):
				allConDataSampleLLOQInfo=[s for s in allConDataSampleLLOQInfo if 'NA' !=str(s).strip().upper() for q in  knockoutQuery.lower().split('|') if q.split(' ')[0] in str(s).strip().lower().split('|')[1].split(' ')[0]]

		
		if len(sumConDataInfo)>0:
			jitem["Summary Concentration Range Data"]=';'.join(sumConDataInfo)
		else:
			jitem["Summary Concentration Range Data"]='NA'

		if len(allConDataInfo)>0:
			jitem["All Concentration Range Data"]=';'.join(allConDataInfo)
		else:
			jitem["All Concentration Range Data"]='NA'
		if len(allConDataInfo)>0:
			jitem["All Concentration Range Data-Sample LLOQ Based"]=';'.join(allConDataSampleLLOQInfo)
		else:
			jitem["All Concentration Range Data-Sample LLOQ Based"]='NA'
	
		tempjfinaldata.append(jitem)

	return tempjfinaldata
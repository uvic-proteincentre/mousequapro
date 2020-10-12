#!/usr/bin/env.python
# -*- coding: utf-8 -*-
# encoding: utf-8
from __future__ import unicode_literals
from collections import Counter
from itertools import combinations
import ast
from operator import itemgetter
from summaryKeggCoverage import *
import operator
import json
import re
import itertools
from collections import OrderedDict
import datetime
from functools import partial

# function to generate stat based on user search result
def summaryStatcal(pepresult):
	specieslist=[]
	unqisostat=[]
	subcell={}
	godic={}
	diseasedic={}
	statKeggDic={}
	prodataseries={}
	pepseqdataseries={}
	strainData=[]
	bioMatData=[]
	noOfHumanOrtholog=0
	noOfDiseaseAssProt=0
	databaseNameList=['Peptide ID']
	pattern = re.compile(r"-\d+")
	mouseQuaReplace=('<br/>','|'),('<br>','|')
	utf8 = partial(unicode.encode, encoding="utf8")
	

	listOfSubcell=list((object['SubCellular'] for object in pepresult)) #reading subcellular data from result
	listOfSubcell=filter(None, listOfSubcell) #filter out empty value
	if len(listOfSubcell)>0:
		listOfSubcell=filter(lambda k: 'NA' != k.upper(), listOfSubcell) #filter out NA value
		if len(listOfSubcell)>0:
			subcellcount=Counter((('|'.join(listOfSubcell)).split('|'))) #split subcellular location then count the occurance
			tempsortedsubcell=OrderedDict(sorted(dict(subcellcount).items(), key=lambda x: x[1],reverse=True)) #sorting dictionary based on number of unique items in dict and reverse order
			listOfSubcell=(dict(itertools.islice(tempsortedsubcell.items(), 0, 50))).keys() # only top 50 restult will be displayed

	listOfSpecies=list((object['Organism'] for object in pepresult)) #reading organism data from result
	listOfSpecies=list(set(filter(None, listOfSpecies))) #filter out empty value

	listOfGoName=list((object['Mouse Go Name'] for object in pepresult)) #reading GO name data from result
	listOfGoName=filter(None, listOfGoName) #filter out empty value
	if len(listOfGoName)>0:
		listOfGoName=filter(lambda k: 'NA' != k.upper(), listOfGoName) #filter out NA value
		if len(listOfGoName)>0:
			listOfGoNamecount=Counter((('|'.join(listOfGoName)).split('|'))) #split data then count the occurance
			tempsortedgo=OrderedDict(sorted(dict(listOfGoNamecount).items(), key=lambda x: x[1],reverse=True)) #sorting dictionary based on number of unique items in dict and reverse order
			listOfGoName=(dict(itertools.islice(tempsortedgo.items(), 0, 50))).keys() # only top 50 restult will be displayed

	listOfKeggName=list((object['Mouse Kegg Pathway Name'] for object in pepresult)) #reading kegg data from result
	listOfKeggName=filter(None, listOfKeggName) #filter out empty value
	if len(listOfKeggName)>0:
		listOfKeggName=filter(lambda k: 'NA' != k.upper(), listOfKeggName) #filter out NA value
		if len(listOfKeggName)>0:
			listOfKeggNamecount=Counter((('|'.join(listOfKeggName)).split('|'))) #split data then count the occurance
			tempsortedkegg=OrderedDict(sorted(dict(listOfKeggNamecount).items(), key=lambda x: x[1],reverse=True)) #sorting dictionary based on number of unique items in dict and reverse order
			listOfKeggName=(dict(itertools.islice(tempsortedkegg.items(), 0, 20))).keys()# only top 20 restult will be displayed



	listOfHumanOrtholog=list((object['Human UniProtKB Accession'] for object in pepresult)) #reading human homolog data from result
	listOfHumanOrtholog=filter(None, listOfHumanOrtholog) #filter out empty value
	listOfHumanOrtholog=list(set(listOfHumanOrtholog))
	if 'NA' in listOfHumanOrtholog:
		listOfHumanOrtholog.remove('NA')
	noOfHumanOrtholog=len(listOfHumanOrtholog)
	

	listOfHumanAssocDis=list((object['Human Disease Name'] for object in pepresult)) #reading disease data from result
	listOfHumanAssocDis=filter(None, listOfHumanAssocDis) #filter out empty value
	listOfHumanAssocDis='|'.join(listOfHumanAssocDis)
	listOfHumanAssocDis=list(set(listOfHumanAssocDis.split('|')))
	if 'NA' in listOfHumanAssocDis:
		listOfHumanAssocDis.remove('NA')
	noOfDiseaseAssProt=len(listOfHumanAssocDis)
	if len(listOfHumanAssocDis)>0:
		listOfHumanAssocDiscount=Counter(listOfHumanAssocDis)
		tempsortedHumanDis=OrderedDict(sorted(dict(listOfHumanAssocDiscount).items(), key=lambda x: x[1],reverse=True)) #sorting dictionary based on number of unique items in dict and reverse order
		listOfHumanAssocDis=(dict(itertools.islice(tempsortedHumanDis.items(), 0, 20))).keys()# only top 20 restult will be displayed

	listOfBiomatrix=list((object['Biological Matrix'] for object in pepresult)) #reading tissues data from result
	listOfBiomatrix=filter(None, listOfBiomatrix) #filter out empty value
	listOfBiomatrix='|'.join(listOfBiomatrix)
	listOfBiomatrix=reduce(lambda a,kv: a.replace(*kv), mouseQuaReplace, listOfBiomatrix)
	listOfBiomatrix=list(set(listOfBiomatrix.split('|')))



	listOfStrain=list((object['Strain'] for object in pepresult)) #reading strain data from result
	listOfStrain=filter(None, listOfStrain) #filter out empty value
	listOfStrain='|'.join(listOfStrain)
	listOfStrain=reduce(lambda a,kv: a.replace(*kv), mouseQuaReplace, listOfStrain)
	listOfStrain=list(set(listOfStrain.split('|')))

	for i in listOfBiomatrix:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in (str(pepdata["Biological Matrix"]).strip()).lower(), pepresult)
		subdataprot=list((object['UniProtKB Accession'] for object in subdatafilter))
		subdatapep=list((object['Peptide Sequence'] for object in subdatafilter))
		subdataprot=list(set([pattern.sub("", item) for item in subdataprot]))
		subdatapep=list(set([pattern.sub("", item) for item in subdatapep]))
		#bioMatData.append([i,len(subdataprot),len(subdatapep)])
		bioMatData.append([i,len(subdataprot)])

	for i in listOfStrain:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in (str(pepdata["Strain"]).strip()).lower(), pepresult)
		subdataprot=list((object['UniProtKB Accession'] for object in subdatafilter))
		subdatapep=list((object['Peptide Sequence'] for object in subdatafilter))
		subdataprot=list(set([pattern.sub("", item) for item in subdataprot]))
		subdatapep=list(set([pattern.sub("", item) for item in subdatapep]))
		strainData.append([i,len(subdataprot),len(subdatapep)])

	for i in listOfSubcell:
		subdatafilter=filter(lambda pepdata: (str(i).strip()).lower() in (str(pepdata['SubCellular']).strip()).lower().split('|'), pepresult)
		subdata=list((object['UniProtKB Accession'] for object in subdatafilter))
		subcell[str(i).strip()]=len(list(set([pattern.sub("", item) for item in subdata])))

	for i in listOfSpecies:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in (str(pepdata["Organism"]).strip()).lower(), pepresult)
		subdataprot=list((object['UniProtKB Accession'] for object in subdatafilter))
		subdatapep=list((object['Peptide Sequence'] for object in subdatafilter))
		subdataprot=list(set([pattern.sub("", item) for item in subdataprot]))
		subdatapep=list(set([pattern.sub("", item) for item in subdatapep]))
		specieslist.append([i,len(subdataprot),len(subdatapep)])

	for i in listOfKeggName:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in (str(pepdata["Mouse Kegg Pathway Name"]).strip()).lower().split('|'), pepresult)
		subdata=list((object['UniProtKB Accession'] for object in subdatafilter))
		statKeggDic[str(i).strip()]=list(set([pattern.sub("", item) for item in subdata]))

	for i in listOfGoName:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in (str(pepdata["Mouse Go Name"]).strip()).lower().split('|'), pepresult)
		subdata=list((object['UniProtKB Accession'] for object in subdatafilter))
		godic[str(i).strip()]=len(list(set([pattern.sub("", item) for item in subdata])))

	for i in listOfHumanAssocDis:
		subdatafilter=filter(lambda pepdata: str(i).strip().lower() in map(str,map(utf8,pepdata["Human Disease Name"].strip().lower().split('|'))), pepresult)
		subdata=list((object['UniProtKB Accession'] for object in subdatafilter))
		diseasedic[str(i).strip()]=len(list(set([pattern.sub("", item) for item in subdata])))

	for i in databaseNameList:
		subdatafilter=filter(lambda pepdata: ((str(pepdata[i]).strip()).lower() !='na' and len(str(pepdata[i]).strip()) >0), pepresult)
		subdataprot=list((object['UniProtKB Accession'] for object in subdatafilter))
		subdatapep=list((object['Peptide Sequence'] for object in subdatafilter))
		prodataseries[(str(i).strip()).split(' ')[0]]=list(set([pattern.sub("", item) for item in subdataprot]))
		pepseqdataseries[(str(i).strip()).split(' ')[0]]=list(set([pattern.sub("", item) for item in subdatapep]))

		isostatus=list((object['Present in isoforms'] for object in subdatafilter))

		unqstatus=list((object['Unique in protein'] for object in subdatafilter))
		tempcalunq='0.0%'
		tempcaliso='0.0%'
		if len(isostatus)>0:
			isostatus = map(lambda x: 'NA' if x.strip() == '' else x, isostatus)
			tempcaliso=str(100-(round((100.00-(float(isostatus.count('NA'))/float(len(isostatus)))*100),2)))+'%'
		if len(unqstatus)>0:
			tempcalunq=str(round(((float(unqstatus.count('Yes'))/float(len(unqstatus)))*100),2))+'%'
		unqisostat.append([(str(i).strip()).split(' ')[0],tempcalunq,tempcaliso])

	sortedKeggStatdic=OrderedDict(sorted(statKeggDic.items(), key=lambda x: len(x[1]), reverse=True))
	top10keggdict=dict(itertools.islice(sortedKeggStatdic.items(), 0, 10))
	keggchart=summarykeggcal(top10keggdict,prodataseries)

	statfinalresult={}
	statfinalresult['total']=[len(set(reduce(operator.concat, prodataseries.values()))),len(set(reduce(operator.concat, pepseqdataseries.values())))]
	statfinalresult['pepseqdataseries']=pepseqdataseries
	statfinalresult['prodataseries']=prodataseries
	statfinalresult['specieslist']=specieslist
	statfinalresult['unqisostat']=unqisostat
	statfinalresult['keggchart']=keggchart
	#statfinalresult['BioMat']=[['Biological Matrix','Total unique proteins','Total unique peptide']]+bioMatData
	statfinalresult['BioMat']=[['Biological Matrix','No. of assays']]+bioMatData
	statfinalresult['Strain']=[['Strain','Total unique proteins', 'Total unique peptide']]+strainData
	statfinalresult['noOfHumanortholog']=noOfHumanOrtholog
	statfinalresult['noOfDiseaseAssProt']=noOfDiseaseAssProt
	sortedGodic=OrderedDict(sorted(godic.items(), key=lambda x: x[1],reverse=True))

	sortedSubcelldic=OrderedDict(sorted(subcell.items(), key=lambda x: x[1],reverse=True))
	sortedDiseasedic=OrderedDict(sorted(diseasedic.items(), key=lambda x: x[1],reverse=True))

	statfinalresult['subcell']=[['SubCellular localization','No. of proteins covered']]+map(list,(sorted(list(sortedSubcelldic.items()),key=lambda l:l[1], reverse=True))[:10])
	statfinalresult['godic']=[['GO Term Name','No. of proteins covered']]+map(list,(sorted(sortedGodic.items(),key=lambda l:l[1], reverse=True))[:10])
	statfinalresult['disdic']=[['Disease Name','No. of proteins associated']]+map(list,(sorted(sortedDiseasedic.items(),key=lambda l:l[1], reverse=True))[:10])
	return statfinalresult
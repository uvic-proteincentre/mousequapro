import urllib,urllib2
from bioservices.kegg import KEGG
import os,subprocess,psutil,re,shutil,datetime,sys,glob
from operator import itemgetter
import numpy as np
import random, time
from itertools import count, groupby
import pandas as pd
import csv
import itertools
import json
import ctypes

#increase the field size of CSV
csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
filename='ReportBook_mother_file.csv'
filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)

statfilename='overallstat.py'
statmovefilepath=os.path.join(homedir, 'updatefile', statfilename)
statfilepath = os.path.join(homedir, 'src/qmpkbapp', statfilename)

orglist=[]
orglistID=[]
statKeggDic={}
with open(filepath) as pepcsvfile:
	pepreader=csv.DictReader(pepcsvfile, delimiter='\t')
	for peprow in pepreader:
		if  str(peprow['UniprotKb entry status']).strip().upper()=='YES':
			orglist.append(' '.join(str(peprow['Organism']).strip().split(' ')[:2]))
			orglistID.append(str(peprow['Organism ID']).strip())
			statuniID=str(peprow['UniProtKB Accession']).strip().split('-')[0]
			statPathway=str(peprow['Mouse Kegg Pathway Name']).strip()
			statSpeciesID=str(peprow['Organism ID']).strip()
			if len(statPathway)>0:
				statPathwayList=statPathway.split('|')
				for stpItem in statPathwayList:
					if stpItem.lower() !='na':
						keggid=stpItem.strip()
						if statKeggDic.has_key(keggid):
							statKeggDic[keggid].append(statuniID.strip())
						else:
							statKeggDic[keggid] =[statuniID.strip()]

unqorglist=list(set(orglist))
unqorglist.sort(key=str.lower)
speciesList=unqorglist
speciesProt={}
speciesPep={}
godic={}
speciesdic={}
keggpathwaycoverage=[]
#print speciesList
with open(filepath) as pepcsvfile:
	pepreader=csv.DictReader(pepcsvfile, delimiter='\t')
	for frow in pepreader:
		if str(frow['UniprotKb entry status']).strip().upper()=='YES':
			pepseq=frow['Peptide Sequence'].strip()
			Calorg=str(frow['Organism']).strip()
			CalorgID=str(frow['Organism ID']).strip()
			speciesdic[CalorgID]=Calorg
			acccode=None
			acccode=str(frow['UniProtKB Accession']).split('-')[0]
			if acccode != None:
				for spitem in speciesList:
					if spitem in Calorg:
						if speciesProt.has_key(spitem):
							speciesProt[spitem].append(acccode)
						else:
							speciesProt[spitem]=[acccode]

						if speciesPep.has_key(spitem):
							speciesPep[spitem].append(pepseq)
						else:
							speciesPep[spitem]=[pepseq]
				if frow["Mouse Go Name"].upper() !='NA' and len(str(frow["Mouse Go Name"]).strip())>0:
					goname=(str(frow["Mouse Go Name"]).strip()).split('|')
					for gitem in goname:
						if godic.has_key(str(gitem).strip()):
							godic[str(gitem).strip()].append(acccode)
						else:
							godic[str(gitem).strip()]=[acccode]


sys.path.append(os.path.join(homedir, 'src/qmpkbapp'))
from calculationprog import *
pepfinalresult=finalresult['prodataseries']

keggpathwaycoverage=[]
for kskey in statKeggDic:
	keggpathwayname=(kskey.strip()).split('|')[0]
	tempUniqKeggUniIDList=list(set(statKeggDic[kskey]))
	peptrack=[]
	for ckey in pepfinalresult:
		if ckey == "PeptideTracker":
			peptrack=list(set(pepfinalresult[ckey]).intersection(tempUniqKeggUniIDList))

	temppeptrack=len(list(set(peptrack)))
	tempTotal=len(list(set(tempUniqKeggUniIDList)))
	templist=[keggpathwayname,tempTotal,temppeptrack]
	keggpathwaycoverage.append(templist)

statsepcies=[]
speciesProt={k:len(list(set(j))) for k,j in speciesProt.items()}
speciesPep={k:len(list(set(j))) for k,j in speciesPep.items()}

godic={k:len(set(v)) for k, v in godic.items()}
 
for skey in speciesProt:
	if skey in speciesPep:
		statsepcies.append([skey,speciesProt[skey],speciesPep[skey]])

sortedstatsepcies=sorted(statsepcies, key= itemgetter(1), reverse=True)

golist=[]
for gkey in godic:
	golist.append([gkey,godic[gkey]])

sortedgolist=sorted(golist, key= itemgetter(1), reverse=True)

keggpathwaycoverage.sort()
unqkeggpathwaycoverage=list(keggpathwaycoverage for keggpathwaycoverage,_ in itertools.groupby(keggpathwaycoverage))
sortedkeggpathwaycoverage=sorted(unqkeggpathwaycoverage, key= itemgetter(1), reverse=True)

overallSumresult={}
overallSumresult['organism']=unqorglist
unqorglist.insert(0,"")
overallSumresult['species']=unqorglist
overallSumresult['speciesstat']=sortedstatsepcies
overallSumresult['mousegostat']=sortedgolist
overallSumresult['mousekeggstat']=sortedkeggpathwaycoverage

statfileoutput=open(statfilename,'w')
statfileoutput.write("overallSumresult=")
statfileoutput.write(json.dumps(overallSumresult))
statfileoutput.close()
shutil.move(statmovefilepath,statfilepath)
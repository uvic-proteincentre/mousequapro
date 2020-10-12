
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata
import datetime,glob
import time
import os,subprocess,psutil,re,sys,shutil,datetime
import csv
import datetime
import urllib,urllib2,urllib3
import json
import numpy as np
from statistics import mean
import ctypes

def preLoadJsonData(homedir,filepath):
	print ("Preload, job starts",str(datetime.datetime.now()))
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	calfilename='preloadHomeData.json'
	calmovefilepath=os.path.join(homedir, 'updatefile', calfilename)
	calfilepath = os.path.join(homedir, 'src/resultFile/jsonData/preLoadData', calfilename)
	prodataseries={}
	pepseqdataseries={}
	totalpeptideseq=''
	aacountlist=[]
	biomatCalDicPep={}
	biomatCalDicPro={}
	sexCalDicPep={}
	sexCalDicPro={}
	strainCalDicPep={}
	strainCalDicPro={}
	biopepList=[]
	bioproList=[]
	biomatList=[]
	sexpepList=[]
	sexproList=[]
	sexList=[]
	uniqueAssaysList=[]
	strainpepList=[]
	strainproList=[]
	strainList=[]
	meanStrainDic={}
	meanBioMatDic={}
	finalMeanConcDic={}
	finalmeanBioMatDic={}
	pepSeqPresenceHumanOrtholog=[]
	pepSeqPresenceHumanOrthologUniId=[]
	finalreader = csv.DictReader(open(filepath),delimiter='\t')
	for frow in finalreader:
		pepseq=frow['Peptide Sequence'].strip()
		acccode=None
		acccode=str(frow['UniProtKB Accession']).split('-')[0]
		genecode=str(frow['Gene']).strip()
		biomat=frow['Biological Matrix'].strip().split('|')
		sex=frow['Sex'].strip().split('|')
		strain=frow['Strain'].strip().split('|')
		sumconcdata=str(frow["Summary Concentration Range Data"]).strip().split(';')
		if acccode !=None and str(frow['UniprotKb entry status']).strip().upper()=='YES':
			totalpeptideseq +=pepseq.upper()

			if 'PeptideTracker' in prodataseries:
				prodataseries['PeptideTracker'].append(acccode)
			else:
				prodataseries['PeptideTracker']=[acccode]

			if 'PeptideTracker' in pepseqdataseries:
				pepseqdataseries['PeptideTracker'].append(pepseq.upper())
			else:
				pepseqdataseries['PeptideTracker']=[pepseq.upper()]


			for si in sumconcdata:
				meanConc=si.split('|')[6].split('(')[0].strip()
				if meanConc.upper() != 'NA':
					meanConc=float(meanConc)
					meanConclog10=round(np.log10(meanConc),2)
					strainConc=si.split('|')[3]
					matConc=si.split('|')[2]
					sexConc=si.split('|')[4]
					updatedAcccode='UniProtKB:'+acccode+'<br>Gene:'+genecode
					if meanStrainDic.has_key(strainConc):
						meanStrainDic[strainConc].append([meanConclog10,updatedAcccode,sexConc,matConc])
					else:
						meanStrainDic[strainConc]=[[meanConclog10,updatedAcccode,sexConc,matConc]]

					if meanBioMatDic.has_key(matConc):
						meanBioMatDic[matConc].append([meanConclog10,updatedAcccode])
					else:
						meanBioMatDic[matConc]=[[meanConclog10,updatedAcccode]]

			for bi in biomat:
				uniqueAssaysList.append(pepseq+bi)
				if bi  in biomatCalDicPep:
					biomatCalDicPep[bi].append(pepseq)
				else:
					biomatCalDicPep[bi]=[pepseq]

				if bi in biomatCalDicPro:
					biomatCalDicPro[bi].append(acccode)
				else:
					biomatCalDicPro[bi]=[acccode]

			for si in sex:
				if si in sexCalDicPep:
					sexCalDicPep[si].append(pepseq)
				else:
					sexCalDicPep[si]=[pepseq]

				if si in sexCalDicPro:
					sexCalDicPro[si].append(acccode)
				else:
					sexCalDicPro[si]=[acccode]

			for sti in strain:
				if sti in strainCalDicPep:
					strainCalDicPep[sti].append(pepseq)
				else:
					strainCalDicPep[sti]=[pepseq]

				if sti in strainCalDicPro:
					strainCalDicPro[sti].append(acccode)
				else:
					strainCalDicPro[sti]=[acccode]

			if str(frow['Present in human ortholog']) == 'Yes':
				pepSeqPresenceHumanOrtholog.append(pepseq.upper())
				pepSeqPresenceHumanOrthologUniId.append(frow['Human UniProtKB Accession'].strip().upper().split('-')[0])


	for mi in meanStrainDic:
		tempMeanjsonData=[]
		tempMeanMatdic={}
		for i in range(0,len(meanStrainDic[mi])):
			if meanStrainDic[mi][i][3] in tempMeanMatdic:
				tempMeanMatdic[meanStrainDic[mi][i][3]].append(meanStrainDic[mi][i][:3])
			else:
				tempMeanMatdic[meanStrainDic[mi][i][3]]=[meanStrainDic[mi][i][:3]]

		for tmati in tempMeanMatdic:
			tempMatJsonData={}
			tempMeanSexDic={}
			for j in range(0,len(tempMeanMatdic[tmati])):
				if tempMeanMatdic[tmati][j][2] in tempMeanSexDic:
					tempMeanSexDic[tempMeanMatdic[tmati][j][2]].append(tempMeanMatdic[tmati][j][:2])
				else:
					tempMeanSexDic[tempMeanMatdic[tmati][j][2]]=[tempMeanMatdic[tmati][j][:2]]
			for tsi in tempMeanSexDic:
				tempDic={}
				for z in range(0,len(tempMeanSexDic[tsi])):
					if tempMeanSexDic[tsi][z][1] in tempDic:
						tempDic[tempMeanSexDic[tsi][z][1]].append(tempMeanSexDic[tsi][z][0])
					else:
						tempDic[tempMeanSexDic[tsi][z][1]]=[tempMeanSexDic[tsi][z][0]]
				updatedConcData=[[mean(tempDic[k]),k] for k in tempDic]
				updatedConcData.sort(key=lambda x:x[0], reverse=True)
				tempMeanData='|'.join(map(str,list(zip(*updatedConcData)[0])))
				tempaccData='|'.join(list(zip(*updatedConcData)[1]))
				tempMatJsonData[tsi]={'MeanConcData':tempMeanData,'MeanProtein':tempaccData}
			tempMeanjsonData.append({tmati:tempMatJsonData})
		finalMeanConcDic[mi]=tempMeanjsonData



	for biomi in meanBioMatDic:
		tempDic={}
		for ai in meanBioMatDic[biomi]:
			if ai[1] in tempDic:
				tempDic[ai[1]].append(ai[0])
			else:
				tempDic[ai[1]]=[ai[0]]
		updatedConcData=[[round(mean(tempDic[k]),2),k] for k in tempDic]
		updatedConcData.sort(key=lambda x:x[0], reverse=True)
		tempMeanData='|'.join(map(str,list(zip(*updatedConcData)[0])))
		tempaccData='|'.join(list(zip(*updatedConcData)[1]))
		finalmeanBioMatDic[biomi]={'MeanConcData':tempMeanData,'MeanProtein':tempaccData}

		
	prodataseries['PeptideTracker']=list(set(prodataseries['PeptideTracker']))
	uniqueProtein=len(list(set(prodataseries['PeptideTracker'])))
	pepseqdataseries['PeptideTracker']=list(set(pepseqdataseries['PeptideTracker']))
	uniquePeptide=len(list(set(pepseqdataseries['PeptideTracker'])))
	uniqueAssays=len(list(set(uniqueAssaysList)))

	biomatList=biomatCalDicPro.keys()
	biomatList.sort()
	for bkey in biomatList:
		if bkey in biomatCalDicPep and bkey in biomatCalDicPro:
			bioproList.append(len(set(biomatCalDicPro[bkey])))
			biopepList.append(len(set(biomatCalDicPep[bkey])))


	for skey in sexCalDicPro:
		if skey in sexCalDicPep:
			sexList.append(skey)
			sexproList.append(len(set(sexCalDicPro[skey])))
			sexpepList.append(len(set(sexCalDicPep[skey])))


	strainList=strainCalDicPro.keys()
	strainList.sort()
	for stkey in strainList:
		if stkey in strainCalDicPep and stkey in strainCalDicPro:
			strainproList.append(len(set(strainCalDicPro[stkey])))
			strainpepList.append(len(set(strainCalDicPep[stkey])))

	strainDic={'Strain':'|'.join(strainList),'PeptideSeq':'|'.join(map(str,strainpepList)),'Protein':'|'.join(map(str,strainproList))}
	biomatDic={'BioMat':'|'.join(biomatList),'PeptideSeq':'|'.join(map(str,biopepList)),'Protein':'|'.join(map(str,bioproList))}
	sexDic={'Sex':'|'.join(sexList),'PeptideSeq':'|'.join(map(str,sexpepList)),'Protein':'|'.join(map(str,sexproList))}
	finalresultdic={}
	finalresultdic['uniqueAssays']=uniqueAssays
	finalresultdic['uniquePeptide']=uniquePeptide
	finalresultdic['uniqueProtein']=uniqueProtein
	finalresultdic['pepSeqPresenceHumanOrtholog']=len(set(pepSeqPresenceHumanOrtholog))
	finalresultdic['pepSeqPresenceHumanOrthologUniId']=len(set(pepSeqPresenceHumanOrthologUniId))
	finalresultlist=[]
	finalresultlist.append(finalresultdic)
	finalresultlist.append(biomatDic)
	finalresultlist.append(strainDic)
	finalresultlist.append(sexDic)
	finalresultlist.append(finalMeanConcDic)
	finalresultlist.append(finalmeanBioMatDic)

	finalresultJson={"data":finalresultlist}
	calfileoutput=open(calfilename,'w')
	calfileoutput.write(json.dumps(finalresultJson))
	calfileoutput.close()
	shutil.move(calmovefilepath,calfilepath)
	print ("Preload, job done",str(datetime.datetime.now()))
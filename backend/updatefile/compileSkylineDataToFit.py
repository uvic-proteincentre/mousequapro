#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata
import datetime,glob
import time
import os,subprocess,psutil,re,sys,shutil
import csv
from map_mouse_to_human import mapSpecies
import datetime
from Bio.SeqUtils.ProtParam import molecular_weight,ProteinAnalysis
import urllib,urllib2,urllib3,datetime
import more_itertools as mit
import pickle
import cPickle
from xml.etree import cElementTree as ET
import xmltodict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from statistics import mean
from tissueInfo import *
import ctypes

def compileSkylineFile():
	print ("Skyline Data compilation, job starts",str(datetime.datetime.now()))
	curr_dir=os.getcwd()
	colname=['UniProtKB Accession','Protein','Gene','Organism','Peptide Sequence','Summary Concentration Range Data','All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based','Peptide ID',\
	'Special Residues','Molecular Weight','GRAVY Score','Transitions','Retention Time','Analytical inofrmation',\
	'Gradients','AAA Concentration','CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ','Protocol','Trypsin','QC. Conc. Data']
	gradData='Time[min]|A[%]|B[%];0.00|98.00|2.00;2.00|93.00|7.00;50.00|70.00|30.00;53.00|55.00|45.00;53.00|20.00|80.00;55.00|20.00|80.00;56.00|98.00|2.00'

	skylineMouseConcfile=''
	pathwayConcenRes='/home/bioinf/datastoreageiv/bioinformatics/mouse_concen_results/data'
	listOfFileConcen=[]
	if os.path.exists(pathwayConcenRes):
		listOfFileConcen=os.listdir(pathwayConcenRes)
	else:
		mountsCMD='echo "xxxxx" | sudo -S mount -t cifs -o username=xxxxx,password=xxxxx //datastorage /yourlocalDIR/'
		subprocess.Popen(mountsCMD,shell=True).wait()
		listOfFileConcen=os.listdir(pathwayConcenRes)

	updatedConcenDataList=[]
	onlyUpdatedConcenFileList=[]
	currentdate=datetime.datetime.now().strftime("%B-%d-%Y")
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

	updatedConcenDatafilename='updatedConcenDataInfo.txt'
	with open(updatedConcenDatafilename,'r') as f:
		for l in f:
			d=l.strip()
			updatedConcenDataList.append(d)
			onlyUpdatedConcenFileList.append(d.split(' ')[0])

	for c in listOfFileConcen:
		if c not in onlyUpdatedConcenFileList:
			skylineMouseConcfile=c
			updatedConcenDataList.append(c+' '+currentdate)

	if len(skylineMouseConcfile.strip())>0:
		mouseConcDic={}
		finalresult=[]
		finalresult.append(colname)
		skylineMouseConcfilePath=pathwayConcenRes+'/'+skylineMouseConcfile
		with open(skylineMouseConcfilePath,'r') as skMCfile:
			skMCcsvreader = csv.DictReader(skMCfile)
			headers = skMCcsvreader.fieldnames
			for skMCrow in skMCcsvreader:
				skylineMouseConcDic={}
				sex=str(skMCrow['Sex']).strip()
				if sex=='M':
					sex='Male'
				if sex=='F':
					sex='Female'
				knockout=str(skMCrow['Knockout']).strip()
				panel=str(skMCrow['Panel']).strip()
				panel=panel.replace(';',',')
				strain=str(skMCrow['Strain']).strip()

				concData=str(skMCrow['Conc. Data']).strip()
				sampleConcData=str(skMCrow['Conc. Data SampleLLOQ-Based']).strip()
				updatedMatrix=str(skMCrow['Matrix']).strip()
				sampleProteinContent=[]
				calculatedProteinContent=[]
				allConcentrationRange=[]

				concDataInfo=concData.split(';')
				sampleCountWithoutSampleLLOQ=0
				for conItem in concDataInfo[1:]:
					sampleCountWithoutSampleLLOQ+=1
					tempallConcentrationRange=[str(sampleCountWithoutSampleLLOQ),strain,sex]
					subConInfo=conItem.split('|')
					for ukey in unitDic:
						if ukey in skMCrow['Matrix'].strip().lower():
							tempallConcentrationRange.append(str(subConInfo[0])+unitDic[ukey][0])
							tempallConcentrationRange.append(str(subConInfo[1])+unitDic[ukey][1])
							tempallConcentrationRange.append(str(subConInfo[2])+unitDic[ukey][2])


					tempallConcentrationRange.insert(0,updatedMatrix)
					tempallConcentrationRange.insert(0,knockout)
					tempallConcentrationRange.insert(0,panel)
					allConcentrationRange.append('|'.join(map(str,tempallConcentrationRange)))
				sampleCountWithoutSampleLLOQ=0

				allSampleConcentrationRange=[]
				sampleConcDataInfo=sampleConcData.split(';')
				sampleCountWithSampleLLOQ=0
				if len(sampleConcDataInfo) > 1:
					for sconItem in sampleConcDataInfo[1:]:
						sampleCountWithSampleLLOQ+=1
						sampleTempallConcentrationRange=[str(sampleCountWithSampleLLOQ),strain,sex]
						subSampleConInfo=sconItem.split('|')
						for ukey in unitDic:
							if ukey in skMCrow['Matrix'].strip().lower():
								sampleTempallConcentrationRange.append(str(subSampleConInfo[0])+unitDic[ukey][0])
								sampleTempallConcentrationRange.append(str(subSampleConInfo[1])+unitDic[ukey][1])
								sampleTempallConcentrationRange.append(str(subSampleConInfo[2])+unitDic[ukey][2])


						sampleTempallConcentrationRange.insert(0,updatedMatrix)
						sampleTempallConcentrationRange.insert(0,knockout)
						sampleTempallConcentrationRange.insert(0,panel)
						sampleProteinContent.append(float(subSampleConInfo[1]))
						calculatedProteinContent.append(float(subSampleConInfo[0]))
						allSampleConcentrationRange.append('|'.join(map(str,sampleTempallConcentrationRange)))
				sampleCountWithSampleLLOQ=0

				minsampleProteinContent='NA'
				maxsampleProteinContent='NA'
				meansampleProteinContent='NA'
				if len(sampleProteinContent)>0:
					minsampleProteinContent=str(min(sampleProteinContent))
					maxsampleProteinContent=str(max(sampleProteinContent))
					meansampleProteinContent=str(round(mean(sampleProteinContent),2))


				mincalculatedProteinContent='NA'
				maxcalculatedProteinContent='NA'
				meancalculatedProteinContent='NA'
				if len(calculatedProteinContent)>0:
					mincalculatedProteinContent=str(min(calculatedProteinContent))
					maxcalculatedProteinContent=str(max(calculatedProteinContent))
					meancalculatedProteinContent=str(round(mean(calculatedProteinContent),2))

				sumConcentrationRange=[]
				for ukey in unitDic:
					 if ukey in skMCrow['Matrix'].strip().lower():
						if len(str(skMCrow['Mean Conc.']).strip()) >0 and str(skMCrow['Mean Conc.']).strip().upper() !='NA':
							skMCrow['Mean Conc.']=str(skMCrow['Mean Conc.']).strip()+unitDic[ukey][2]
						if len(str(skMCrow['Min Conc.']).strip()) >0 and str(skMCrow['Min Conc.']).strip().upper() !='NA':
							skMCrow['Min Conc.']=str(skMCrow['Min Conc.']).strip()+unitDic[ukey][2]
						if len(str(skMCrow['Max Conc.']).strip()) >0 and str(skMCrow['Max Conc.']).strip().upper() !='NA':
							skMCrow['Max Conc.']=str(skMCrow['Max Conc.']).strip()+unitDic[ukey][2]
						if len(str(skMCrow['LLOQ']).strip()) >0 and str(skMCrow['LLOQ']).strip().upper() !='NA':
							skMCrow['LLOQ']=str(skMCrow['LLOQ']).strip()+unitDic[ukey][0]
						if len(str(skMCrow['ULOQ']).strip()) >0 and str(skMCrow['ULOQ']).strip().upper() !='NA':
							skMCrow['ULOQ']=str(skMCrow['ULOQ']).strip()+unitDic[ukey][0]
						if len(str(skMCrow['Sample LLOQ']).strip()) >0 and str(skMCrow['Sample LLOQ']).strip().upper() !='NA':
							skMCrow['Sample LLOQ']=str(skMCrow['Sample LLOQ']).strip()+unitDic[ukey][0]
						if len(sampleProteinContent) >0:
							minsampleProteinContent=minsampleProteinContent+unitDic[ukey][1]
							maxsampleProteinContent=maxsampleProteinContent+unitDic[ukey][1]
							meansampleProteinContent=meansampleProteinContent+unitDic[ukey][1]

						if len(calculatedProteinContent) >0:
							mincalculatedProteinContent=mincalculatedProteinContent+unitDic[ukey][0]
							maxcalculatedProteinContent=maxcalculatedProteinContent+unitDic[ukey][0]
							meancalculatedProteinContent=meancalculatedProteinContent+unitDic[ukey][0]

				LLOQ=str(skMCrow['LLOQ']).strip()
				sampleLLOQ=str(skMCrow['Sample LLOQ']).strip()
				ULOQ=str(skMCrow['ULOQ']).strip()
				
				meanConc=str(skMCrow['Mean Conc.']).strip()
				minConc=str(skMCrow['Min Conc.']).strip()
				maxConc=str(skMCrow['Max Conc.']).strip()
				tempnrSamples=str(skMCrow['Nr. samples']).strip()
				nrSamples=str(tempnrSamples.split('/')[-1])+'/'+str(tempnrSamples.split('/')[0])
				sumConcentrationRange=[panel,knockout,updatedMatrix,strain,sex,nrSamples,meancalculatedProteinContent,meansampleProteinContent,meanConc,mincalculatedProteinContent,minsampleProteinContent,minConc,maxcalculatedProteinContent,maxsampleProteinContent,maxConc]
				if len(sumConcentrationRange)>0:
					skylineMouseConcDic['Summary Concentration Range Data']='|'.join(sumConcentrationRange)
				else:
					skylineMouseConcDic['Summary Concentration Range Data']='NA'

				if len(allConcentrationRange)>0:
					skylineMouseConcDic['All Concentration Range Data']=';'.join(allConcentrationRange)
				else:
					skylineMouseConcDic['All Concentration Range Data']='NA'


				if len(allSampleConcentrationRange)>0:
					skylineMouseConcDic['All Concentration Range Data-Sample LLOQ Based']=';'.join(allSampleConcentrationRange)
				else:
					skylineMouseConcDic['All Concentration Range Data-Sample LLOQ Based']='NA'

				skylineMouseConcDic['Special Residues']= 'NA'
				molw=molecular_weight(str(skMCrow['Peptide Sequence']).strip().upper(), "protein", monoisotopic=True)
				molw=round(molw,2)
				skylineMouseConcDic['Molecular Weight']= str(molw)
				protanalys=ProteinAnalysis(str(skMCrow['Peptide Sequence']).strip().upper())
				gravScore=round((protanalys.gravy()),2)
				skylineMouseConcDic['GRAVY Score']= str(gravScore)

				transitionData=str(skMCrow['Transition Data']).strip()
				instrument=str(skMCrow['Instrument']).strip()
				transitionDataList=[]
				if len(transitionData)>0 and transitionData.upper() !='NA':
					subTransDataInfo=transitionData.split(';')
					subTransDataHeader='Instrument|'+subTransDataInfo[0]
					transitionDataList.append(subTransDataHeader)
					for t in subTransDataInfo[1:]:
						subTDInfo=t.split('|')
						subTDInfo.insert(0,instrument)
						transitionDataList.append('|'.join(subTDInfo))

				if len(transitionDataList)>0:
					skylineMouseConcDic['Transitions']= ';'.join(list(set(transitionDataList)))
				else:
					skylineMouseConcDic['Transitions']= 'NA'
				skylineMouseConcDic['Retention Time']= str(skMCrow['Retention Time']).strip()
				skylineMouseConcDic['Analytical inofrmation']= 'Agilent Zorbax Eclipse Plus C18 RRHD 2.1 x 150mm 1.8um'
				skylineMouseConcDic['Gradients']= gradData
				skylineMouseConcDic['AAA Concentration']= 'NA'
				skylineMouseConcDic['CZE Purity']= 'NA'
				panel=panel.replace(',',';')
				skylineMouseConcDic['Panel']= panel
				skylineMouseConcDic['Knockout']= knockout
				skylineMouseConcDic['LLOQ']= updatedMatrix+'|'+LLOQ
				skylineMouseConcDic['ULOQ']= updatedMatrix+'|'+ULOQ
				skylineMouseConcDic['Sample LLOQ']= updatedMatrix+'|'+sampleLLOQ
				skylineMouseConcDic['Protocol']= str(skMCrow['Protocol']).strip()
				skylineMouseConcDic['Trypsin']= str(skMCrow['Trypsin']).strip()
				skylineMouseConcDic['QC. Conc. Data']= str(skMCrow['QC. Conc. Data']).strip()
				skylineConcKey=str(skMCrow['Accession Number']).strip()+'_'+str(skMCrow['Peptide Sequence']).strip().upper()
				if mouseConcDic.has_key(skylineConcKey):
					mouseConcDic[skylineConcKey].append(skylineMouseConcDic)
				else:
					mouseConcDic[skylineConcKey]=[skylineMouseConcDic]
		countProt=0
		for mckey in mouseConcDic:
			tempConcDic={}
			tempConcDic['UniProtKB Accession']=mckey.split('_')[0]
			tempConcDic['Peptide Sequence']=mckey.split('_')[1]
			currdate=str(datetime.datetime.now())
			currdate=currdate.replace('-','')
			currdate=currdate.replace(' ','')
			currdate=currdate.replace(':','')
			currdate=currdate.replace('.','')
			generatePepid='PEP'+currdate+'FAKE'
			tempConcDic['Peptide ID']= generatePepid
			subDickey=['Summary Concentration Range Data','All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based',\
			'Special Residues','Molecular Weight','GRAVY Score','Transitions','Retention Time','Analytical inofrmation',\
			'Gradients','AAA Concentration','CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ','Protocol','Trypsin','QC. Conc. Data']
			sumConcData=[]
			allConcData=[]
			sampleAllConcData=[]
			spRes=[]
			molW=[]
			gravScore=[]
			transData=[]
			retTime=[]
			analytInfo=[]
			grad=[]
			aaConc=[]
			czePur=[]
			panel=[]
			lloq=[]
			uloq=[]
			samlloq=[]
			protocol=[]
			tryps=[]
			qcConcData=[]
			knockoutData=[]
			for item in mouseConcDic[mckey]:
				sumConcData.append(item['Summary Concentration Range Data'])
				for ac in item['All Concentration Range Data'].split(';'):
					allConcData.append(ac)
				for s in item['All Concentration Range Data-Sample LLOQ Based'].split(';'):
					sampleAllConcData.append(s)
				spRes.append(item['Special Residues'])
				molW.append(item['Molecular Weight'])
				gravScore.append(item['GRAVY Score'])
				for t in item['Transitions'].split(';'):
					transData.append(t)
				for r in item['Retention Time'].split(';'):
					retTime.append(r)
				analytInfo.append(item['Analytical inofrmation'])
				grad.append(item['Gradients'])
				aaConc.append(item['AAA Concentration'])
				czePur.append(item['CZE Purity'])
				for p in item['Panel'].split(';'):
					panel.append(p)
				lloq.append(item['LLOQ'])
				uloq.append(item['ULOQ'])
				samlloq.append(item['Sample LLOQ'])
				protocol.append(item['Protocol'])
				tryps.append(item['Trypsin'])
				qcConcData.append(item['QC. Conc. Data'])
				knockoutData.append(item['Knockout'])

			panel =list(set(panel))
			if len(panel)>1:
				 panel=[y for x in panel for y in x.split(';') if 'na' != y.lower()]
			knockoutData =list(set(knockoutData))
			if len(knockoutData)>1:
				knockoutData=[x for x in knockoutData if 'na' != x.lower()]
			transHeader='Instrument|Isotope Label Type|Precursor Mz|Collision Energy|Fragment Ion|Product Charge|Product Mz'
			transData=list(set(transData))
			transData.sort()
			del transData[transData.index(transHeader)]
			retTime.sort()
			sampleAllConcData.sort()
			allConcData.sort()
			panel.sort()
			tempConcDic['Summary Concentration Range Data']=';'.join(map(str,list(set(sumConcData))))
			tempConcDic['All Concentration Range Data']=';'.join(map(str,list(set(allConcData))))
			tempConcDic['All Concentration Range Data-Sample LLOQ Based']=';'.join(map(str,list(set(sampleAllConcData))))
			tempConcDic['Special Residues']=';'.join(map(str,list(set(spRes))))
			tempConcDic['Molecular Weight']=';'.join(map(str,list(set(molW))))
			tempConcDic['GRAVY Score']=';'.join(map(str,list(set(gravScore))))
			tempConcDic['Transitions']=transHeader+';'+';'.join(map(str,list(set(transData))))
			tempConcDic['Retention Time']=';'.join(map(str,list(set(retTime))))
			tempConcDic['Analytical inofrmation']=';'.join(map(str,list(set(analytInfo))))
			tempConcDic['Gradients']=';'.join(map(str,list(set(grad))))
			tempConcDic['AAA Concentration']=';'.join(map(str,list(set(aaConc))))
			tempConcDic['CZE Purity']=';'.join(map(str,list(set(czePur))))
			tempConcDic['Panel']=';'.join(map(str,list(set(panel))))
			tempConcDic['LLOQ']=';'.join(map(str,list(set(lloq))))
			tempConcDic['ULOQ']=';'.join(map(str,list(set(uloq))))

			tempConcDic['Sample LLOQ']=';'.join(map(str,list(set(samlloq))))
			tempConcDic['Protocol']=';'.join(map(str,list(set(protocol))))
			tempConcDic['Trypsin']=';'.join(map(str,list(set(tryps))))
			tempConcDic['QC. Conc. Data']=';'.join(map(str,list(set(qcConcData))))
			tempConcDic['Knockout']=';'.join(map(str,list(set(knockoutData))))


			time.sleep(2)
			PN='NA'
			GN='NA'
			OG='NA'
			uacc=str(mckey.split('_')[0]).strip()
			subcode=uacc.split('-')[0]
			try:
				countProt+=1
				if countProt%1000 ==0:
					print str(countProt), "th protein Protein Name, Gene, Organism Name job starts",str(datetime.datetime.now())

				SGrequestURL="https://www.uniprot.org/uniprot/"+str(subcode)+".xml"
				SGunifile=urllib.urlopen(SGrequestURL)
				SGunidata= SGunifile.read()
				SGunifile.close()

				try:
					SGunidata=minidom.parseString(SGunidata)

					try:
						try:
							PN=(((SGunidata.getElementsByTagName('protein')[0]).getElementsByTagName('recommendedName')[0]).getElementsByTagName('fullName')[0]).firstChild.nodeValue

						except:
							PN=(((SGunidata.getElementsByTagName('protein')[0]).getElementsByTagName('submittedName')[0]).getElementsByTagName('fullName')[0]).firstChild.nodeValue

					except IndexError:
						pass

					try:
						try:
							GN=((SGunidata.getElementsByTagName('gene')[0]).getElementsByTagName('name')[0]).firstChild.nodeValue
						except:
							GN='NA'
					except IndexError:
						pass

					try:
						try:
							OG=((SGunidata.getElementsByTagName('organism')[0]).getElementsByTagName('name')[0]).firstChild.nodeValue
						except:
							OG='NA'
					except IndexError:
						pass

				except ExpatError:
					pass
			except IOError:
				pass

			tempConcDic['Protein']=str(PN)
			tempConcDic['Gene']=str(GN)
			tempConcDic['Organism']=str(OG)

			tempList=[]
			for col in colname: 
				tempList.append(tempConcDic[col])
			finalresult.append(tempList)

		outputresultpeptrack='mouse_report_peptrack_data.csv'
		with open(outputresultpeptrack,'wb') as pf:
			pwriter =csv.writer(pf,delimiter='\t')
			pwriter.writerows(finalresult)

		with open(updatedConcenDatafilename,'w') as ufile:
			for i in updatedConcenDataList:
				ufile.write(i+"\n")

		mapSpecies(outputresultpeptrack)
		print ("Skyline Data compilation, job done",str(datetime.datetime.now()))
		return 1

	else:
		return 0
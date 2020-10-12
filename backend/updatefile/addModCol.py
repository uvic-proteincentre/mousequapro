import urllib,urllib2
from bioservices.kegg import KEGG
import os,subprocess,psutil,re,shutil,datetime,sys,glob
from operator import itemgetter
import numpy as np
import random, time
from itertools import count, groupby
import pandas as pd
import csv
import json
import ctypes

def addModCol():
	print ("Adding or updating data, job starts",str(datetime.datetime.now()))
	mousepeptrackfilename='mouse_report_peptrack_data.csv'
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	mousePeptrackData=[]
	with open(mousepeptrackfilename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter='\t')
		for row in reader:
			mousePeptrackData.append(row)

	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	filename='ReportBook_mother_file.csv'
	filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)

	columns=['UniProtKB Accession','Protein','Gene','Organism','Organism ID','SubCellular','Peptide Sequence',\
	'Summary Concentration Range Data','All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based',\
	'Peptide ID','Special Residues','Molecular Weight','GRAVY Score','Transitions','Retention Time',\
	'Analytical inofrmation','Gradients','AAA Concentration','CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ',\
	'Protocol','Trypsin','QC. Conc. Data','Unique in protein','Present in isoforms',\
	'Mouse Kegg Pathway Name','Mouse Kegg Pathway','Human Disease Name','Human UniProt DiseaseData','Human UniProt DiseaseData URL',\
	'Human DisGen DiseaseData','Human DisGen DiseaseData URL','Mouse Go ID','Mouse Go Name','Mouse Go Term','Mouse Go','Human Drug Bank',\
	'Human UniProtKB Accession','Human ProteinName','Human Gene','Human Kegg Pathway Name','Human Kegg Pathway',\
	'Human Go ID','Human Go Name','Human Go Term','Human Go','UniprotKb entry status','Concentration View','Strain','Sex',\
	'Biological Matrix','Concentration Range']
	finalSexData=[]
	finalStrainData=[]
	finalknockoutData=[]
	finalBioMatData=[]
	finalPanelData=[]
	finalResultData=[]
	finalResultData.append(columns)
	modrepfile="modreprot.csv"
	with open(filepath,'r') as f:
		repreader = csv.DictReader(f,delimiter="\t")
		for row in repreader:
			if len(row['UniProtKB Accession'].strip())>0:
				if len(row['Summary Concentration Range Data'].strip())>0  and (str(row['Summary Concentration Range Data']).strip()).lower() !='na':
					coninfo=(row['Summary Concentration Range Data'].strip()).split(';')
					if len(coninfo)>0:
						subconinfo=coninfo[0].split('|')
						condata="Mean Conc.:"+str(subconinfo[6])+"<br/>Matix:"+str(subconinfo[2])
						tempSampleLLOQInfo=str(row['Sample LLOQ'].strip()).split(';')
						if str(subconinfo[6]) =='NA':
							for samLLOQ in tempSampleLLOQInfo:
								if str(subconinfo[2]) in samLLOQ.split('|'):
									condata="<"+str(samLLOQ.split('|')[1].strip())+"(Sample LLOQ-"+str(subconinfo[2])+")"
						row['Concentration View']=condata
						strainlist=[]
						sexlist=[]
						matrixlist=[]
						meanConclist=[]
						unitlist=[]
						for i in coninfo:
							l=i.split('|')
							finalSexData.append(l[4])
							finalStrainData.append(l[3])
							finalBioMatData.append(l[2])
							strainlist.append(l[3])
							sexlist.append(l[4])
							matrixlist.append(l[2])
							meanConcData=l[6]
							unitlist.append(l[6].split(' (')[-1])
							if meanConcData.upper() !='NA':
								meanConclist.append(l[2]+':'+str(meanConcData))
							else:
								for samXLLOQ in tempSampleLLOQInfo:
									if str(l[2]) in samXLLOQ.split('|'):
										meanConclist.append("<"+str(samXLLOQ.split('|')[1].strip())+"(Sample LLOQ-"+str(l[2])+")")
						if len(strainlist)>0:
							strainlist =list(set(strainlist))
							if len(strainlist)>1:
								strainlist=[x for x in strainlist if 'na' != x.lower()]
							sexlist =list(set(sexlist))
							if len(sexlist)>1:
								sexlist=[x for x in sexlist if 'na' != x.lower()]
							matrixlist =list(set(matrixlist))
							if len(matrixlist)>1:
								matrixlist=[x for x in matrixlist if 'na' != x.lower()]
							row['Strain']='|'.join(list(set(strainlist)))
							row['Sex']='|'.join(list(set(sexlist)))
							row['Biological Matrix']='|'.join(list(set(matrixlist)))
							countSampleLLOQ=len([mc for mc in meanConclist if 'Sample LLOQ' in mc])
							if len(meanConclist) ==countSampleLLOQ:
								meanConclist=list(set(meanConclist))
								row['Concentration Range']='<br/>'.join(meanConclist[:2])
							else:
								meanConclist=[m for m in meanConclist if 'Sample LLOQ' not in m]
								meanConclist=list(set(meanConclist))
								row['Concentration Range']= 'Mean Conc.:'+'<br/>'+'<br/>'.join(meanConclist[:2])
								#row['Concentration Range']="Max. Mean Conc.:"+str(max(meanConclist))+' ('+str(unitlist[meanConclist.index(max(meanConclist))])+"<br/>Min. Mean Conc.:"+str(min(meanConclist))+' ('+str(unitlist[meanConclist.index(min(meanConclist))])
						else:
							row['Strain']='NA'
							row['Sex']='NA'
							row['Biological Matrix']='NA'
							row['Concentration Range']='NA'
					if len(row['Panel'].strip())>0  and (str(row['Panel']).strip()).lower() !='na':
						panelinfo=(row['Panel'].strip()).split(';')
						for i in panelinfo:
							finalPanelData.append(i)

					if len(row['Knockout'].strip())>0  and (str(row['Knockout']).strip()).lower() !='na':
						knockoutinfo=(row['Knockout'].strip()).split(';')
						for i in knockoutinfo:
							finalknockoutData.append(i)
				templist=[]
				for c in columns:
					templist.append(row[c])
				finalResultData.append(templist)
	#finalknockoutData.append('Mutant type')
	finalSexData=list(set(finalSexData))
	if len(finalSexData)>1:
		finalSexData=[x for x in finalSexData if 'na' != x.lower()]
	finalknockoutData=list(set(finalknockoutData))
	if len(finalknockoutData)>1:
		finalknockoutData=[x for x in finalknockoutData if 'na' != x.lower()]
	finalStrainData=list(set(finalStrainData))
	if len(finalStrainData)>1:
		finalStrainData=[x for x in finalStrainData if 'na' != x.lower()]
	finalBioMatData=list(set(finalBioMatData))
	if len(finalBioMatData)>1:
		finalBioMatData=[x for x in finalBioMatData if 'na' != x.lower()]
	finalPanelData=list(set(finalPanelData))
	if len(finalPanelData)>1:
		finalPanelData=[x for x in finalPanelData if 'na' != x.lower()]

	finalresultlist=[]
	finalSexData.sort()
	finalStrainData.sort()
	finalBioMatData.sort()
	finalknockoutData.sort()
	finalPanelData=sorted(finalPanelData, key=lambda p: int(p.split('-')[1]))
	for s in finalSexData:
		finalresultdic={}
		finalresultdic["id"]=s
		finalresultdic["selectid"]="sex"
		finalresultdic["name"]=s
		finalresultlist.append(finalresultdic)

	for k in finalknockoutData:
		finalresultdic={}
		finalresultdic["id"]=k
		finalresultdic["selectid"]="mutant"
		finalresultdic["name"]=k
		finalresultlist.append(finalresultdic)

	for st in finalStrainData:
		finalresultdic={}
		finalresultdic["id"]=st
		finalresultdic["selectid"]="strain"
		finalresultdic["name"]=st
		finalresultlist.append(finalresultdic)

	for bm in finalBioMatData:
		finalresultdic={}
		finalresultdic["id"]=bm
		finalresultdic["selectid"]="biologicalMatrix"
		finalresultdic["name"]=bm
		finalresultlist.append(finalresultdic)

	for p in finalPanelData:
		finalresultdic={}
		finalresultdic["id"]=p
		finalresultdic["selectid"]="panel"
		finalresultdic["name"]=p
		finalresultlist.append(finalresultdic)

	finalresultJson={"data":finalresultlist}
	adsearchopfilename='advanceSearchOptions.json'
	adsearchopmovefilepath=os.path.join(homedir, 'updatefile', adsearchopfilename)
	adsearchopfilepath = os.path.join(homedir, 'src/resultFile/jsonData/preLoadData', adsearchopfilename)
	adsearchopfileoutput=open(adsearchopfilename,'w')
	adsearchopfileoutput.write(json.dumps(finalresultJson))
	adsearchopfileoutput.close()


	with open(modrepfile,'wb') as mf:
		mwriter =csv.writer(mf,delimiter='\t')
		mwriter.writerows(finalResultData)


	movefilepath=os.path.join(homedir, 'updatefile', filename)
	os.rename(modrepfile,filename)
	shutil.move(movefilepath,filepath)
	shutil.move(adsearchopmovefilepath,adsearchopfilepath)
	print ("Adding or updating data, job done",str(datetime.datetime.now()))

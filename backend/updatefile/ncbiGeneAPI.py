import json
from Bio import Entrez
import sys,urllib3,requests,time,datetime,urllib2
import os,subprocess,psutil,re,shutil,glob
from socket import error as SocketError
import errno
import random
import csv
import requests
import ctypes

def ncbiGeneExp():
	#increase the field size of CSV
	print ("NCBI Gene transcription, job starts",str(datetime.datetime.now()))
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	filename='ReportBook_mother_file.csv'
	filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
	finalresult=[]
	RETRY_TIME=20
	Entrez.email = "pbhowmick@uvic.ca"
	handleNCBI = Entrez.einfo()
	recordNCBI = Entrez.read(handleNCBI)
	with open(filepath) as tsvfile:
		reader = csv.DictReader(tsvfile, delimiter='\t')
		colName=reader.fieldnames
		addNewCol=['Gene Expression Data','Gene Expression View']
		colName=colName+addNewCol
		finalresult.append(colName)
		for row in reader:
			expData='No'
			maxRPKMMeanOrgan='No'
			mouseUniID=row['UniProtKB Accession'].strip()
			RETRY_TIME = 20.0
			while True:
				try:
					handleIDNCBI = Entrez.esearch(db="gene",term=mouseUniID+"[Protein Accession]")
					recordIDNCBI = Entrez.read(handleIDNCBI)
					try:
						hitIDNCBI=recordIDNCBI["IdList"][0]
						httpNCBI = urllib3.PoolManager()
						expNCBIURL='https://www.ncbi.nlm.nih.gov/gene/'+hitIDNCBI+'/?report=expression'
						urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
						try:
							expNCBIResponse = httpNCBI.request('GET', expNCBIURL)
							expNCBIData=str(expNCBIResponse.data)
							tempExpNCBIList=[]
							for eData in expNCBIData.split('\n'):
								if 'var tissues_data = {' in eData.strip():
									organSpecExpData=str(eData.strip().replace('\\','').split('=')[1].replace('}};','}}'))
									organSpecExpData=organSpecExpData.replace("'", "\"")
									organSpecExpDic=json.loads(organSpecExpData)
									for eKey in organSpecExpDic:
										geneID=organSpecExpDic[eKey]['gene']
										meanExpRPKM=organSpecExpDic[eKey]['exp_rpkm']
										if int(hitIDNCBI) == int(geneID):
											if float(str(meanExpRPKM).strip()) >0:
												tempExpNCBIList.append([str(eKey).strip(),str(meanExpRPKM).strip()])

							if len(tempExpNCBIList)>0:
								expData='MeanExpressionInRPKM|Tissue'
								tempData=';'.join(['|'.join(i) for i in tempExpNCBIList])
								expData=expData+';'+tempData
								tempExpNCBIList.sort(key=lambda x: float(x[1]))
								maxRPKMMeanOrgan=str(tempExpNCBIList[-1][1])+' (Mean RPKM in '+str(tempExpNCBIList[-1][0])+')'
						except urllib3.exceptions.NewConnectionError:
							print('Connection failed.')
							pass
					except IndexError:
						pass
						
					break
				except urllib2.HTTPError:
					time.sleep(RETRY_TIME)
					print 'Hey, I am trying again until succeeds to get data from NCBI Gene Exp!',str(datetime.datetime.now())
					pass
			row['Gene Expression Data']=expData
			row['Gene Expression View']=maxRPKMMeanOrgan
			tempList=[]
			for col in colName: 
				tempList.append(row[col])
			finalresult.append(tempList)

	outputresultpeptrack=dgnosvoutputresultpeptrack=filepath
	with open(outputresultpeptrack,'wb') as pf:
		pwriter =csv.writer(pf,delimiter='\t')
		pwriter.writerows(finalresult)
	print ("NCBI Gene transcription, job done",str(datetime.datetime.now()))
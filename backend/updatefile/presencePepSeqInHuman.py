import os,subprocess,psutil,re,shutil,datetime,sys,glob
import urllib,urllib2,urllib3
from socket import error as SocketError
import errno
from Bio import SeqIO
import random, time
import csv
import requests
import ctypes

def presencePepSeqHuman():
	print ("Checking peptide sequence presence in Human homolog sequence, job starts",str(datetime.datetime.now()))
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	filename='ReportBook_mother_file.csv'
	filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
	finalresult=[]
	with open(filepath) as tsvfile:
		reader = csv.DictReader(tsvfile, delimiter='\t')
		colName=reader.fieldnames
		addNewCol=['Present in human ortholog','Unique in human protein', 'Present in human isoforms']
		colName=colName+addNewCol
		finalresult.append(colName)
		for row in reader:
			pepSeq=row['Peptide Sequence'].strip()
			humanUniId=row['Human UniProtKB Accession'].strip()
			row['Present in human ortholog']='No'
			row['Unique in human protein']='NA'
			row['Present in human isoforms']='NA'
			pepisodata=[]
			humanCanoPepUnId=''
			humanPepUnIdVer=''
			unqStatus=False
			otherProPresentStatus=False
			if '-' in humanUniId:
				pepUnIdInfo=humanUniId.split('-')
				humanCanoPepUnId=pepUnIdInfo[0]
				humanPepUnIdVer=pepUnIdInfo[-1]
			else:
				humanCanoPepUnId=humanUniId
			try:
				tempfastaseq=''
				unifastaurl="https://www.uniprot.org/uniprot/"+str(humanUniId)+".fasta"
				fastaresponse = urllib.urlopen(unifastaurl)
				for seq in SeqIO.parse(fastaresponse, "fasta"):
					tempfastaseq=(seq.seq).strip()

				if len(tempfastaseq.strip()) >0 and pepSeq in tempfastaseq:
					row['Present in human ortholog']='Yes'
					while True:
						try:
							PIRpepMatrequestURLUnq ="https://research.bioinformatics.udel.edu/peptidematchapi2/match_get?peptides="+str(pepSeq)+"&taxonids=9606&swissprot=true&isoform=true&uniref100=false&leqi=false&offset=0&size=-1"
							urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
							PIRPepMatrUnq = requests.get(PIRpepMatrequestURLUnq, headers={ "Accept" : "application/json"},verify=False)

							if not PIRPepMatrUnq.ok:
							  PIRPepMatrUnq.raise_for_status()
							  sys.exit()

							PIRPepMatresponseBodyUnq = PIRPepMatrUnq.json()

							if len(PIRPepMatresponseBodyUnq['results'][0]['proteins'])>0:
								for piritemUnq in PIRPepMatresponseBodyUnq['results'][0]['proteins']:
									uniId=piritemUnq['ac'].strip()
									pirRevStatUnq=piritemUnq['reviewStatus'].strip()

									if 'sp' == (str(pirRevStatUnq).lower()).strip():
										canoUniId=''
										uniIdVer=''
										if '-' in uniId:
											uniIdinfo=uniId.split('-')
											canoUniId=uniIdinfo[0]
											uniIdVer=uniIdinfo[-1]
										else:
											canoUniId=uniId
										for mxmatchpep in piritemUnq["matchingPeptide"]:
											uimatchpeptide=mxmatchpep["peptide"]
											if str(uimatchpeptide).strip() ==pepSeq:
												if (canoUniId.strip()).lower() == (humanCanoPepUnId.strip()).lower():
													if len(uniIdVer.strip()) ==0:
														unqStatus=True
													if len(uniIdVer.strip()) !=0:
														unqStatus=False
														pepisodata.append(str(uniId))
												if (canoUniId.strip()).lower() != (humanCanoPepUnId.strip()).lower():
													otherProPresentStatus=True

							break
						except requests.exceptions.ConnectionError:
							time.sleep(RETRY_TIME)
							print ('Hey, I am trying again until succeeds to get data from Peptide Match Server!',str(datetime.datetime.now()))
							pass
						except requests.exceptions.ChunkedEncodingError:
							time.sleep(RETRY_TIME)
							print ('chunked_encoding_error happened',str(datetime.datetime.now()))
							pass
							
			except IOError:
				pass

			if row['Present in human ortholog'] =='Yes':
				if unqStatus:
					if otherProPresentStatus:
						row['Unique in human protein']='Not unique'
					else:
						row['Unique in human protein']='Yes'
				else:
					row['Unique in human protein']='Not unique'

				if len(pepisodata)>0:
					row['Present in human isoforms']=','.join(list(set(pepisodata)))
				else:
					row['Present in human isoforms']='No'

			tempList=[]
			for col in colName: 
				tempList.append(row[col])
			finalresult.append(tempList)

	outputresultpeptrack=filepath
	with open(outputresultpeptrack,'wb') as pf:
		pwriter =csv.writer(pf,delimiter='\t')
		pwriter.writerows(finalresult)
	print ("Checking peptide sequence presence in Human ortholog sequence, job done",str(datetime.datetime.now()))

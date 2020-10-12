import os,subprocess,psutil,re,shutil,datetime,sys,glob
import urllib,urllib2,urllib3
from bioservices.kegg import KEGG
from socket import error as SocketError
import errno
from Bio import SeqIO
import xmltodict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import random, time
from goatools import obo_parser
import csv
import json
import pandas as pd
import requests
from collections import Counter
from itertools import combinations
from xml.etree import cElementTree as ET
import pickle
import cPickle
import operator
from compileSkylineDataToFit import compileSkylineFile
import numpy as np
from statistics import mean
from presencePepSeqInHuman import presencePepSeqHuman
from ncbiGeneAPI import ncbiGeneExp
from addModCol import addModCol
from addSelCol import addSelCol
from maketotalassaypep import totalAssayPep
from preloadData import preLoadJsonData
from uploadDataElasticSearch import uploadData
import ctypes
from generate_pre_downloadable_file import preDownloadFile

def makemergedict(listOfResourceFile,colname,humanuniprotdic,humankdeggic):
	mergedictdata={}
	humanmousemergedic={}
	humanfuncdict = cPickle.load(open(humanuniprotdic, 'rb'))
	humanKEGGdict = cPickle.load(open(humankdeggic, 'rb'))
	for fitem in listOfResourceFile:
		with open(fitem,'r') as pepfile:
			reader = csv.DictReader(pepfile, delimiter='\t')
			for row in reader:
				info=[]
				for i in colname:
					info.append(str(row[i]).strip())
				if mergedictdata.has_key(info[0].strip()):
					mergedictdata[info[0].strip()].append(info[4])
				else:
					mergedictdata[info[0].strip()]=[info[4]]
				temphumanunilist=info[-1].split(',')
				hPNlist=[]
				hGNlist=[]
				hdislist=[]
				hunidislist=[]
				hunidisURLlist=[]
				hdisgenlist=[]
				hdisgenURLlist=[]
				hDruglist=[]
				hGoIDList=[]
				hGoNamList=[]
				hGoTermList=[]
				hGoList=[]
				hKeggList=[]
				hKeggdetailsList=[]
				for h in temphumanunilist:
					if h in humanfuncdict:
						hPNlist.append(humanfuncdict[h][0])
						hGNlist.append(humanfuncdict[h][1])
						hdislist.append(humanfuncdict[h][4])
						hunidislist.append(humanfuncdict[h][5])
						hunidisURLlist.append(humanfuncdict[h][6])
						hdisgenlist.append(humanfuncdict[h][7])
						hdisgenURLlist.append(humanfuncdict[h][8])
						hDruglist.append(humanfuncdict[h][9])
						hGoIDList.append(humanfuncdict[h][10])
						hGoNamList.append(humanfuncdict[h][11])
						hGoTermList.append(humanfuncdict[h][12])
						hGoList.append(humanfuncdict[h][-1])
					if h in humanKEGGdict:
						hKeggList.append(humanKEGGdict[h][0])
						hKeggdetailsList.append(humanKEGGdict[h][1])
				hPN='NA'
				hGN='NA'
				hdis='NA'
				hunidis='NA'
				hunidisURL='NA'
				hdisgen='NA'
				hdisgenURL='NA'
				hDrug='NA'
				hGoiddata='NA'
				hGonamedata='NA'
				hGotermdata='NA'
				hGodata='NA'
				hKeggdata='NA'
				hKeggdetails='NA'
				if len(hPNlist)>0:
					hPN='|'.join(list(set([l.strip() for k in hPNlist for l in k.split('|') if len(l.strip()) >0])))
				if len(hGNlist)>0:
					hGN='|'.join(list(set([l.strip() for k in hGNlist for l in k.split('|') if len(l.strip()) >0])))
				if len(hdislist)>0:
					hdis='|'.join(list(set([l.strip() for k in hdislist for l in k.split('|') if len(l.strip()) >0])))
				if len(hunidislist)>0:
					hunidis='|'.join(list(set([l.strip() for k in hunidislist for l in k.split('|') if len(l.strip()) >0])))
				if len(hunidisURLlist)>0:
					hunidisURL='|'.join(list(set([l.strip() for k in hunidisURLlist for l in k.split('|') if len(l.strip()) >0])))
				if len(hdisgenlist)>0:
					hdisgen='|'.join(list(set([l.strip() for k in hdisgenlist for l in k.split('|') if len(l.strip()) >0])))
				if len(hdisgenURLlist)>0:
					hdisgenURL='|'.join(list(set([l.strip() for k in hdisgenURLlist for l in k.split('|') if len(l.strip()) >0])))
				if len(hDruglist)>0:
					hDrug='|'.join(list(set([l.strip() for k in hDruglist for l in k.split('|') if len(l.strip()) >0])))
				if len(hGoIDList)>0:
					hGoiddata='|'.join(list(set([l.strip() for k in hGoIDList for l in k.split('|') if len(l.strip()) >0])))
				if len(hGoNamList)>0:
					hGonamedata='|'.join(list(set([l.strip() for k in hGoNamList for l in k.split('|') if len(l.strip()) >0])))
				if len(hGoTermList)>0:
					hGotermdata='|'.join(list(set([l.strip() for k in hGoTermList for l in k.split('|') if len(l.strip()) >0])))
				if len(hGoList)>0:
					hGodata='|'.join(list(set([l.strip() for k in hGoList for l in k.split('|') if len(l.strip()) >0])))
				if len(hKeggList)>0:
					hKeggdata='|'.join(list(set([str(l).strip() for k in hKeggList for l in k ])))
				if len(hKeggdetailsList)>0:
					hKeggdetails='|'.join(list(set([l.strip() for k in hKeggdetailsList for l in k.split('|') if len(l.strip()) >0])))
				humanmousemergedic[info[0].strip()]=[str(hPN),str(hGN),str(hdis),str(hunidis),str(hunidisURL),\
				str(hdisgen),str(hdisgenURL),str(hDrug),str(info[-1]),str(hGoiddata),str(hGonamedata),str(hGotermdata),\
				str(hGodata),str(hKeggdata),str(hKeggdetails)]
		print (str(fitem),"data dictionay job done",str(datetime.datetime.now()))
	return mergedictdata,humanmousemergedic


def runprog():
	# runcomplete=compileSkylineFile()
	# if runcomplete ==0:
	# 	print("No new data has been added!",str(datetime.datetime.now()))
	runcomplete=1
	return runcomplete
	
if __name__ == '__main__':
	colname=['UniProtKB Accession','Protein','Gene','Organism','Peptide Sequence','Summary Concentration Range Data','All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based','Peptide ID',\
	'Special Residues','Molecular Weight','GRAVY Score','Transitions','Retention Time','Analytical inofrmation',\
	'Gradients','AAA Concentration','CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ','Protocol','Trypsin','QC. Conc. Data','Human UniProtKB Accession']
	print (datetime.datetime.now())
	print ("Update mother file job starts now")
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	runcomplete=runprog()
	if runcomplete==1:
		#get home directory path
		homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
		outfilefilename ='outfilefile.csv'
		filename='ReportBook_mother_file.csv'
		kdicfile='keggdic.obj'
		filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
		# #copy mother file from its source to working directory
		if os.path.exists(filepath):
			movefilepath=os.path.join(homedir, 'updatefile', filename)
			if os.path.exists(movefilepath):
				os.remove(movefilepath)
			if not os.path.exists(movefilepath):
				shutil.copy2(filepath, movefilepath)
				#create backup folder before update and then move that folder with old version mother file for backup
				mydate = datetime.datetime.now()
				folder_name="version_"+mydate.strftime("%B_%d_%Y_%H_%M_%S")
				if not os.path.exists('./backup/'+folder_name):
					os.makedirs('./backup/'+folder_name)
				if not os.path.exists('./backup/'+folder_name+'/ReportBook_mother_file.csv'):
					shutil.copy2(movefilepath, './backup/'+folder_name+'/ReportBook_mother_file.csv')
				listOfResourceFile=['mouse_report_peptrack_data.csv']
				humanuniprotdic='humanUniprotfuncinfodic.obj'
				humankdeggic='humankeggdic.obj'
				mergedictdata,humanmousemergedic=makemergedict(listOfResourceFile,colname,humanuniprotdic,humankdeggic)
				if len(mergedictdata)>0:
					print ("Data formatting and checking pep seq present in uniprot specified seq, job starts",str(datetime.datetime.now()))
					uniidlist=[]
					dicmrm={}
					orgidDic={}
					unqisocheckdic={}
					unifuncdic={}
					countProt=0
					countPep=0
					RETRY_TIME = 20.0
					curr_dir = os.getcwd()
					below_curr_dir=os.path.normpath(curr_dir + os.sep + os.pardir)
					totalUniId=list(set(mergedictdata.keys()))

					tempcanonicalUnId=[]
					canonisounidic={}
					for tuid in totalUniId:
						tuempcode=(str(tuid).split('-'))[0]
						if canonisounidic.has_key(tuempcode):
							canonisounidic[tuempcode].append(tuid)
						else:
							canonisounidic[tuempcode]=[tuid]

					canonisounidic={a:list(set(b)) for a, b in canonisounidic.items()}
					unqcanonicalUnId=list(set(canonisounidic.keys()))
					print ("Total Unique protein in this file: ",len(unqcanonicalUnId))
					countProt=0
					print ("Extracting Protein Name, Gene, Organism Name,GO,Sub cellular data, drug bank data ,disease data and checking pep seq present in uniprot specified seq, job starts",str(datetime.datetime.now()))
					tempgotermdic={}
					tempsubcdic={}
					protgnogscgofilename='uniprotfuncdata.csv'
					protgnogscgofile=open(protgnogscgofilename,'w')
					protgnogscgoHeader=['ActualUniID','UpdatedUniID','PepSeq','ProteinName','Gene','Organism',\
					'OrganismID','Subcellular','Mouse GOID','Mouse GOName','Mouse GoTerm','Mouse Go',\
					'Human DrugBank','Human DiseaseData','Human UniProt DiseaseData','Human UniProt DiseaseData URL',\
					'Human DisGen DiseaseData','Human DisGen DiseaseData URL','PresentInSeq','Human UniProtKB Accession',\
					'Human ProteinName','Human Gene','Human Kegg Pathway Name',\
					'Human Kegg Pathway','Human Go ID','Human Go Name','Human Go Term','Human Go']
					protgnogscgofile.write('\t'.join(protgnogscgoHeader)+'\n')
					for subcgcode in unqcanonicalUnId:
						time.sleep(2)
						ScAllLocList=[]
						GoIDList=[]
						GoNamList=[]
						GoTermList=[]
						GOinfo=[]
						PN='NA'
						GN='NA'
						OG='NA'
						OGID='NA'
						try:
							countProt+=1
							if countProt%1000 ==0:
								print (str(countProt), "th protein Protein Name, Gene, Organism Name, GO, sub cellular and checking pep seq present in uniprot specified seq job starts",str(datetime.datetime.now()))

							SGrequestURL="https://www.uniprot.org/uniprot/"+str(subcgcode)+".xml"
							SGunifile=urllib.urlopen(SGrequestURL)
							SGunidata= SGunifile.read()
							SGunifile.close()

							try:
								SGunidata=minidom.parseString(SGunidata)
								try:
									subcelldata=(SGunidata.getElementsByTagName('subcellularLocation'))
									for subcItem in subcelldata:
										try:
											subloc=(subcItem.getElementsByTagName('location')[0]).firstChild.nodeValue
											if len(str(subloc).strip()) >0:
												ScAllLocList.append(str(subloc).strip())
										except:
											pass

								except IndexError:
									pass
								try:
									godata=(SGunidata.getElementsByTagName('dbReference'))
									for gItem in godata:
										if (gItem.attributes['type'].value).upper() == 'GO':
											try:
												gonamedetails=(str(gItem.getElementsByTagName('property')[0].attributes['value'].value).strip()).split(':')[1]
												gotermdetails=(str(gItem.getElementsByTagName('property')[0].attributes['value'].value).strip()).split(':')[0]
												GoNamList.append(gonamedetails)
												goid=str(gItem.attributes['id'].value).strip()
												GoIDList.append(goid)
												tempGoTerm=None
												
												if gotermdetails.lower()=='p':
													tempGoTerm='Biological Process'
												if gotermdetails.lower()=='f':
													tempGoTerm='Molecular Function'
												if gotermdetails.lower()=='c':
													tempGoTerm='Cellular Component'
												GoTermList.append(tempGoTerm)
												tempGOData=gonamedetails+';'+goid+';'+tempGoTerm
												GOinfo.append(tempGOData)
							
											except:
												pass

										if (gItem.attributes['type'].value).strip() == 'NCBI Taxonomy':
											try:
												OGID=str(gItem.attributes['id'].value).strip()
											except:
												pass
								except IndexError:
									pass

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
						subcelldata='NA'
						goiddata='NA'
						gonamedata='NA'
						gotermdata='NA'
						goData='NA'
						if len(ScAllLocList)>0:
							subcelldata='|'.join(list(set(ScAllLocList)))
						if len(GoIDList)>0:
							goiddata='|'.join(list(set(GoIDList)))
						if len(GoNamList)>0:
							gonamedata='|'.join(list(set(GoNamList)))
						if len(GoTermList)>0:
							gotermdata='|'.join(list(set(GoTermList)))
						if len(GOinfo)>0:
							goData='|'.join(list(set(GOinfo)))

						if subcgcode in canonisounidic:
							for canisoitem in canonisounidic[subcgcode]:
								time.sleep(1)
								try:
									tempfastaseq=''
									unifastaurl="https://www.uniprot.org/uniprot/"+str(canisoitem)+".fasta"
									fr = requests.get(unifastaurl)
									fAC=(str(fr.url).split('/')[-1].strip()).split('.')[0].strip()
									fastaresponse = urllib.urlopen(unifastaurl)
									for seq in SeqIO.parse(fastaresponse, "fasta"):
										tempfastaseq=(seq.seq).strip()
									if len(tempfastaseq.strip()) >0:
										if canisoitem in mergedictdata:
											for temppgopepseq in mergedictdata[canisoitem]:
												pepinfastapresent='No'
												if temppgopepseq in tempfastaseq:
													pepinfastapresent='Yes'
												protFileDataList=['NA']*28
												if '-' in fAC:
													if canisoitem in humanmousemergedic:
														protFileDataList[0]=str(canisoitem)
														protFileDataList[1]=str(fAC)
														protFileDataList[2]=str(temppgopepseq)
														protFileDataList[3]=str(PN)
														protFileDataList[4]=str(GN)
														protFileDataList[5]=str(OG)
														protFileDataList[6]=str(OGID)
														protFileDataList[12]=str(humanmousemergedic[canisoitem][7])
														protFileDataList[13]=str(humanmousemergedic[canisoitem][2])
														protFileDataList[14]=str(humanmousemergedic[canisoitem][3])
														protFileDataList[15]=str(humanmousemergedic[canisoitem][4])
														protFileDataList[16]=str(humanmousemergedic[canisoitem][5])
														protFileDataList[17]=str(humanmousemergedic[canisoitem][6])
														protFileDataList[18]=str(pepinfastapresent)
														protFileDataList[19]=str(humanmousemergedic[canisoitem][8])
														protFileDataList[20]=str(humanmousemergedic[canisoitem][0])
														protFileDataList[21]=str(humanmousemergedic[canisoitem][1])
														protFileDataList[22]=str(humanmousemergedic[canisoitem][-2])
														protFileDataList[23]=str(humanmousemergedic[canisoitem][-1])
														protFileDataList[24]=str(humanmousemergedic[canisoitem][9])
														protFileDataList[25]=str(humanmousemergedic[canisoitem][10])
														protFileDataList[26]=str(humanmousemergedic[canisoitem][11])
														protFileDataList[27]=str(humanmousemergedic[canisoitem][12])
													else:
														protFileDataList[0]=str(canisoitem)
														protFileDataList[1]=str(fAC)
														protFileDataList[2]=str(temppgopepseq)
														protFileDataList[3]=str(PN)
														protFileDataList[4]=str(GN)
														protFileDataList[5]=str(OG)
														protFileDataList[6]=str(OGID)
														protFileDataList[18]=str(pepinfastapresent)
														
												else:
													if canisoitem in humanmousemergedic:
														protFileDataList[0]=str(canisoitem)
														protFileDataList[1]=str(fAC)
														protFileDataList[2]=str(temppgopepseq)
														protFileDataList[3]=str(PN)
														protFileDataList[4]=str(GN)
														protFileDataList[5]=str(OG)
														protFileDataList[6]=str(OGID)
														protFileDataList[7]=str(subcelldata)
														protFileDataList[8]=str(goiddata)
														protFileDataList[9]=str(gonamedata)
														protFileDataList[10]=str(gotermdata)
														protFileDataList[11]=str(goData)
														protFileDataList[12]=str(humanmousemergedic[canisoitem][7])
														protFileDataList[13]=str(humanmousemergedic[canisoitem][2])
														protFileDataList[14]=str(humanmousemergedic[canisoitem][3])
														protFileDataList[15]=str(humanmousemergedic[canisoitem][4])
														protFileDataList[16]=str(humanmousemergedic[canisoitem][5])
														protFileDataList[17]=str(humanmousemergedic[canisoitem][6])
														protFileDataList[18]=str(pepinfastapresent)
														protFileDataList[19]=str(humanmousemergedic[canisoitem][8])
														protFileDataList[20]=str(humanmousemergedic[canisoitem][0])
														protFileDataList[21]=str(humanmousemergedic[canisoitem][1])
														protFileDataList[22]=str(humanmousemergedic[canisoitem][-2])
														protFileDataList[23]=str(humanmousemergedic[canisoitem][-1])
														protFileDataList[24]=str(humanmousemergedic[canisoitem][9])
														protFileDataList[25]=str(humanmousemergedic[canisoitem][10])
														protFileDataList[26]=str(humanmousemergedic[canisoitem][11])
														protFileDataList[27]=str(humanmousemergedic[canisoitem][12])

													else:
														protFileDataList[0]=str(canisoitem)
														protFileDataList[1]=str(fAC)
														protFileDataList[2]=str(temppgopepseq)
														protFileDataList[3]=str(PN)
														protFileDataList[4]=str(GN)
														protFileDataList[5]=str(OG)
														protFileDataList[6]=str(OGID)
														protFileDataList[7]=str(subcelldata)
														protFileDataList[8]=str(goiddata)
														protFileDataList[9]=str(gonamedata)
														protFileDataList[10]=str(gotermdata)
														protFileDataList[11]=str(goData)
														protFileDataList[18]=str(pepinfastapresent)
												protgnogscgofile.write('\t'.join(protFileDataList)+'\n')
								except IOError:
									pass
					protgnogscgofile.close()
					mergedictdata.clear()
					countProt=0
					print ("Extracting Protein Name, Gene, Organism Name,GO,Sub cellular data, and checking pep seq present in uniprot specified seq, job done",str(datetime.datetime.now()))

					countProt=0
					countPep=0
					tempunifuncdic={}
					with open(protgnogscgofilename) as pgosgfile:
						preader = csv.DictReader(pgosgfile, delimiter='\t')
						for prow in preader:
							tempCol=['ActualUniID','ProteinName','Gene','Organism',\
							'OrganismID','Subcellular','PepSeq','Human DiseaseData',\
							'Human UniProt DiseaseData','Human UniProt DiseaseData URL',\
							'Human DisGen DiseaseData','Human DisGen DiseaseData URL',\
							'Mouse GOID','Mouse GOName','Mouse GoTerm','Mouse Go',\
							'Human DrugBank','Human UniProtKB Accession','Human ProteinName','Human Gene',\
							'Human Kegg Pathway Name','Human Kegg Pathway',\
							'Human Go ID','Human Go Name','Human Go Term','Human Go','PresentInSeq']
							templist=[]
							for tc in tempCol:
								templist.append(str(prow[tc]).strip())
							tempfuncid=str(prow['UpdatedUniID']).strip()+'_'+str(prow['PepSeq']).strip()
							tempunifuncdic[tempfuncid]=templist

							uniidlist.append((((prow['UpdatedUniID']).split('-'))[0]).strip())

							if str(prow['PresentInSeq']).strip() =='Yes':
								tempid=str(prow['UpdatedUniID']).strip()+'_'+str(prow['OrganismID']).strip()
								if unqisocheckdic.has_key(tempid):
									unqisocheckdic[tempid].append(str(prow['PepSeq']).strip())
								else:
									unqisocheckdic[tempid]=[str(prow['PepSeq']).strip()]

					unquniidlist=list(set(uniidlist))
					print ("Extracting KEGG pathway name, job starts",str(datetime.datetime.now()))
					keggdictfile={}
					uniproturl = 'https://www.uniprot.org/uploadlists/'
					k = KEGG()
					for kx in range(0,len(unquniidlist),2000):
						countProt+=kx+2000
						if countProt%2000 ==0:
							print (str(countProt), "th protein kegg job starts",str(datetime.datetime.now()))

						uniprotcodes=' '.join(unquniidlist[kx:kx+2000])
						uniprotparams = {
						'from':'ACC',
						'to':'KEGG_ID',
						'format':'tab',
						'query':uniprotcodes
						}
						
						while True:
							try:
								kuniprotdata = urllib.urlencode(uniprotparams)
								kuniprotrequest = urllib2.Request(uniproturl, kuniprotdata)
								kuniprotresponse = urllib2.urlopen(kuniprotrequest)
								for kuniprotline in kuniprotresponse:
									kudata=kuniprotline.strip()
									if not kudata.startswith("From"):
										kuinfo=kudata.split("\t")
										if len(kuinfo[1].strip()):
											kegg=k.get(kuinfo[1].strip())
											kudict_data = k.parse(kegg)
											try:
												try:
													if len(str(kuinfo[0]).strip()) >5:
														tempkeggData='|'.join('{};{}'.format(key, value) for key, value in kudict_data['PATHWAY'].items())
														keggdictfile[kuinfo[0].strip()]=[kudict_data['PATHWAY'].values(),tempkeggData]
												except TypeError: 
													pass
											except KeyError:
												pass
								break
							except urllib2.HTTPError:
								time.sleep(RETRY_TIME)
								print ('Hey, I am trying again until succeeds to get data from KEGG!',str(datetime.datetime.now()))
								pass
					kdicf = open(kdicfile, 'wb')
					pickle.dump(keggdictfile, kdicf , pickle.HIGHEST_PROTOCOL)
					kdicf.close()

					diseasefilepath = os.path.join(below_curr_dir, 'src/UniDiseaseInfo/' 'humsavar.txt')
					print ("Extracting disease data, job starts",str(datetime.datetime.now()))
					try:
						urllib.urlretrieve('ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/variants/humsavar.txt',diseasefilepath)
						urllib.urlcleanup()
					except:
						print ("Can't able to download humsavar.txt file!!")

					print ("Extracting Human disease data, job done",str(datetime.datetime.now()))

					print ("Checking uniqueness of peptide sequence and presence in isoforms, job starts",str(datetime.datetime.now()))
					countProt=0
					countPep=0
					outfilefileUnqIsoname='UnqIsoresult.csv'
					outfilefileUnqIso = open(outfilefileUnqIsoname,'w')
					outfilefileUnqIso.write('UniProtKB Accession'+'\t'+'Peptide Sequence'+'\t'+'Unique in protein'+'\t'+'Present in isoforms'+'\n')
					for mkey in unqisocheckdic.keys():
						pepunid=mkey.split('_')[0]
						unqtemppepseqList=list(set(unqisocheckdic[mkey]))
						pepUnqDic={}
						pepIsodic={}
						nonprotuniqstatDic={}
						peppresentUniFastaDic={}
						canopepunid=''
						pepunidver=''
						if '-' in pepunid:
							pepunidinfo=pepunid.split('-')
							canopepunid=pepunidinfo[0]
							pepunidver=pepunidinfo[-1]
						else:
							canopepunid=pepunid
						pirUqorgid=mkey.split('_')[1]

						countProt+=1
						if countProt%1000 ==0:
							print (str(countProt), "th protein peptide uniqueness job starts",str(datetime.datetime.now()))
							time.sleep(10)

						for mx in range(0,len(unqtemppepseqList),90):
							countPep+=mx+90
							if countPep%4000 ==0:
								print (str(countPep), "th peptide seq uniqueness check job starts",str(datetime.datetime.now()))

							unqtemppepseq=','.join(unqtemppepseqList[mx:mx+90])

							while True:
								try:
									PIRpepMatrequestURLUnq ="https://research.bioinformatics.udel.edu/peptidematchapi2/match_get?peptides="+str(unqtemppepseq)+"&taxonids="+str(pirUqorgid)+"&swissprot=true&isoform=true&uniref100=false&leqi=false&offset=0&size=-1"
									urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
									PIRPepMatrUnq = requests.get(PIRpepMatrequestURLUnq, headers={ "Accept" : "application/json"},verify=False)

									if not PIRPepMatrUnq.ok:
									  PIRPepMatrUnq.raise_for_status()
									  sys.exit()

									PIRPepMatresponseBodyUnq = PIRPepMatrUnq.json()

									if len(PIRPepMatresponseBodyUnq['results'][0]['proteins'])>0:
										for piritemUnq in PIRPepMatresponseBodyUnq['results'][0]['proteins']:
											uniID=piritemUnq['ac'].strip()
											pirRevStatUnq=piritemUnq['reviewStatus'].strip()

											if pepunid.lower() == (str(uniID).lower()).strip():
												for sxmatchpep in piritemUnq["matchingPeptide"]:
													matchpeptide=sxmatchpep["peptide"]
													if str(matchpeptide).strip() in unqtemppepseqList[mx:mx+90]:
														peppresentUniFastaDic[str(matchpeptide).strip()]=True

											if 'sp' == (str(pirRevStatUnq).lower()).strip():
												canouniID=''
												uniIDver=''
												if '-' in uniID:
													uniIDinfo=uniID.split('-')
													canouniID=uniIDinfo[0]
													uniIDver=uniIDinfo[-1]
												else:
													canouniID=uniID
												for mxmatchpep in piritemUnq["matchingPeptide"]:
													uimatchpeptide=mxmatchpep["peptide"]
													if str(uimatchpeptide).strip() in unqtemppepseqList[mx:mx+90]:
														if (canouniID.strip()).lower() == (canopepunid.strip()).lower():
															if len(uniIDver.strip()) ==0:
																pepUnqDic[str(uimatchpeptide).strip()]=True
															if len(uniIDver.strip()) !=0:
																if pepIsodic.has_key(str(uimatchpeptide).strip()):
																	pepIsodic[str(uimatchpeptide).strip()].append(uniID)
																else:
																	pepIsodic[str(uimatchpeptide).strip()]=[uniID]
														if canouniID.strip() !=canopepunid.strip():
															nonprotuniqstatDic[str(uimatchpeptide).strip()]=True

									break
								except requests.exceptions.ConnectionError:
									time.sleep(RETRY_TIME)
									print ('Hey, I am trying again until succeeds to get data from Peptide Match Server!',str(datetime.datetime.now()))
									pass
								except requests.exceptions.ChunkedEncodingError:
									time.sleep(RETRY_TIME)
									print ('chunked_encoding_error happened',str(datetime.datetime.now()))
									pass
									
						for peptideseq in unqtemppepseqList:
							peptideunique='NA'
							pepisodata='No'
							if peptideseq not in nonprotuniqstatDic:
								if peptideseq in pepUnqDic:
									if pepUnqDic[peptideseq]:
										peptideunique='Yes'
									else:
										peptideunique='Not unique'
							else:
								peptideunique='NA'
							if peptideseq in pepIsodic:
								pepisodata=','.join(list(set(pepIsodic[peptideseq])))
							outfilefileUnqIso.write(str(pepunid)+'\t'+str(peptideseq)+'\t'+str(peptideunique)+'\t'+str(pepisodata)+'\n')

					outfilefileUnqIso.close()
					print ("Checking uniqueness of peptide sequence and presence in isoforms, job done",str(datetime.datetime.now()))

					tempunqisodic={}
					with open(outfilefileUnqIsoname) as unqisofile:
						uireader = csv.DictReader(unqisofile, delimiter='\t')
						for uirow in uireader:
							tempunqisodic[str(uirow['UniProtKB Accession']).strip()+'_'+str(uirow['Peptide Sequence']).strip()]=[str(uirow['Unique in protein']).strip(),str(uirow['Present in isoforms']).strip()]
					
					keggdict = cPickle.load(open(kdicfile, 'rb'))

					tempunikeggunqisofuncdic={}
					for tukey in tempunifuncdic:
						tempkeggdata='NA'
						tempkeggdetails='NA'
						tempunqdata='NA'
						tempisodata='NA'
						tuniID=tukey.split('_')[0]
						if tuniID in keggdict:
							tempkeggdata='|'.join(list(set(keggdict[tuniID][0])))
							tempkeggdetails=keggdict[tuniID][1]
						if tukey in tempunqisodic:
							tempunqdata=tempunqisodic[tukey][0]
							tempisodata=tempunqisodic[tukey][1]

						tuitem=tempunifuncdic[tukey]
						tuitem.insert(7,tempunqdata)
						tuitem.insert(8,tempisodata)
						tuitem.insert(9,tempkeggdata)
						tuitem.insert(10,tempkeggdetails)
						tempolduniid=tuitem[0]
						tuitem[0]=tuniID
						modtukey=tempolduniid+'_'+tukey.split('_')[1]
						tempunikeggunqisofuncdic[modtukey]=tuitem
					print ("Functional data dictionay job done",str(datetime.datetime.now()))

					keggdict.clear()
					tempunifuncdic.clear()
					tempunqisodic.clear()
					temptransdic={}

					for fitem in listOfResourceFile:
						with open(fitem,'r') as pepfile:
							reader = csv.DictReader(pepfile, delimiter='\t')
							for row in reader:
								resinfo=[]
								for i in colname:
									resinfo.append(str(row[i]).strip())
								restempid=resinfo[0].strip()+'_'+resinfo[4].strip()
								if temptransdic.has_key(restempid):
									temptransdic[restempid].append(resinfo[5:])
								else:
									temptransdic[restempid]=[resinfo[5:]]
						print (str(fitem),"transition data dictionay job done",str(datetime.datetime.now()))
					outFileColName=['UniProtKB Accession','Protein','Gene','Organism','Organism ID','SubCellular',\
					'Peptide Sequence','Summary Concentration Range Data','All Concentration Range Data',\
					'All Concentration Range Data-Sample LLOQ Based','Peptide ID','Special Residues','Molecular Weight',\
					'GRAVY Score','Transitions','Retention Time','Analytical inofrmation','Gradients','AAA Concentration',\
					'CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ','Protocol','Trypsin','QC. Conc. Data',\
					'Unique in protein','Present in isoforms','Mouse Kegg Pathway Name','Mouse Kegg Pathway',\
					'Human Disease Name','Human UniProt DiseaseData','Human UniProt DiseaseData URL',\
					'Human DisGen DiseaseData','Human DisGen DiseaseData URL','Mouse Go ID',\
					'Mouse Go Name','Mouse Go Term','Mouse Go','Human Drug Bank',\
					'Human UniProtKB Accession','Human ProteinName','Human Gene',\
					'Human Kegg Pathway Name','Human Kegg Pathway','Human Go ID',\
					'Human Go Name','Human Go Term','Human Go','UniprotKb entry status']

					outFileColNameData='\t'.join(outFileColName)
					outfilefile = open(outfilefilename,'w')
					outfilefile.write(outFileColNameData+'\n')
					for key in temptransdic:

						for subtempitem in temptransdic[key]:
							temprow=['NA']*52
							peptracktemprowpos=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
							for i,j in zip(subtempitem,peptracktemprowpos):
								temprow[j]=str(i)
							functemprowpos=[0,1,2,3,4,5,6,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51]
							if key in tempunikeggunqisofuncdic:
								for x,y in zip(tempunikeggunqisofuncdic[key],functemprowpos):
									temprow[y]=str(x)
							if (temprow[0].strip()).upper() != 'NA' and (temprow[6].strip()).upper() != 'NA':
								finalreportdata='\t'.join(temprow)
								outfilefile.write(finalreportdata+'\n')
							temprow=[]

					outfilefile.close()
					print ("Initial report file creation, job done",str(datetime.datetime.now()))
					temptransdic.clear()
					tempunikeggunqisofuncdic.clear()
					os.rename(outfilefilename,filename)
					shutil.move(movefilepath,filepath)
					print ("Initial report file transfer, job done",str(datetime.datetime.now()))

		addModCol()

		keggcmd='python statKEGGcoverage.py'
		subprocess.Popen(keggcmd, shell=True).wait()
		
		statjobcmd='python generateSummaryReport.py'
		subprocess.Popen(statjobcmd, shell=True).wait()

		totalAssayPep()
		addSelCol()
		presencePepSeqHuman()
		ncbiGeneExp()
		preLoadJsonData(homedir,filepath)
		uploadData()
		print ("Extracting Prepare download, job starts",str(datetime.datetime.now()))
		preDownloadFile()
		print ("Extracting Prepare download, job starts",str(datetime.datetime.now()))

'''
this script based on jax lab pre-calculated homolog file
'''

import os,subprocess,psutil,re,shutil,datetime,sys,glob
import urllib,urllib2,urllib3,httplib
from socket import error as SocketError
import errno
from Bio import SeqIO
import random, time
import csv
import more_itertools as mit
import pickle
import cPickle
from xml.etree import cElementTree as ET
import xmltodict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from bioservices.kegg import KEGG
import pandas as pd
import ctypes
from extractDisGenData import disGenData

def mapSpecies(mousepeptrackfilename):
	RETRY_TIME = 20.0
	mouseTohumanfilepath = os.path.join(os.getcwd(), 'MouseToHuman.tsv')
	print ("Extracting Mouse to Human Map data, job starts",str(datetime.datetime.now()))
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	try:
		urllib.urlretrieve('http://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt',mouseTohumanfilepath)
		urllib.urlcleanup()
	except:
		print ("Can't able to download MouseToHuman.tsv file!!")

	colnameMousHu=['HomoloGene ID','Common Organism Name','NCBI Taxon ID','Symbol','EntrezGene ID','Mouse MGI ID','HGNC ID','OMIM Gene ID','Genetic Location','Genomic Coordinates (mouse: , human: )','Nucleotide RefSeq IDs','Protein RefSeq IDs','SWISS_PROT IDs']

	mouseHumandata=[]
	homologID=[]
	with open(mouseTohumanfilepath) as mhtsvfile:
		mhreader = csv.DictReader(mhtsvfile, delimiter='\t')
		for mhrow in mhreader:
			mhtemplist=[]
			for i in colnameMousHu:
				mhtempdata=str(mhrow[i]).strip()
				mhtemplist.append(mhtempdata)
			if len(mhtemplist[-1].strip()) >0:
				homologID.append(mhtemplist[0])
				mouseHumandata.append(mhtemplist)
	homologID=list(set(homologID))
	homologID.sort()

	mousehumandic={}
	for homologidItem in homologID:
		tempHumanHomoUniID=''
		tempMouseHomoUniID=''
		for item in mouseHumandata:
			if homologidItem == item[0]:
				if 'mouse' in item[1].strip().lower():
					tempMouseHomoUniID=item[-1].strip()
				else:
					tempHumanHomoUniID=item[-1].strip()
		if len(tempMouseHomoUniID.strip()) >0 and len(tempHumanHomoUniID.strip()) >0 and tempHumanHomoUniID.strip().upper() !='NA':
			mousehumandic[tempMouseHomoUniID]=tempHumanHomoUniID

	colname=['UniProtKB Accession','Protein','Gene','Organism','Peptide Sequence','Summary Concentration Range Data','All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based','Peptide ID',\
	'Special Residues','Molecular Weight','GRAVY Score','Transitions','Retention Time','Analytical inofrmation',\
	'Gradients','AAA Concentration','CZE Purity','Panel','Knockout','LLOQ','ULOQ','Sample LLOQ','Protocol','Trypsin','QC. Conc. Data','Human UniProtKB Accession']

	finalresult=[]
	finalresult.append(colname)
	humanUniprotID=[]
	with open(mousepeptrackfilename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter='\t')
		for row in reader:
			templist=[]
			for i in colname[:-1]:
				tempdata=str(row[i]).strip()
				templist.append(tempdata)
			if len(str(templist[0]).strip())>0:
				if templist[0].split('-')[0] in mousehumandic:
					humanUniprotID.append(mousehumandic[templist[0].split('-')[0]])
					templist.append(mousehumandic[templist[0].split('-')[0]])
				else:
					templist.append('NA')

			finalresult.append(templist)

	with open(mousepeptrackfilename,'wb') as pf:
		pwriter =csv.writer(pf,delimiter='\t')
		pwriter.writerows(finalresult)

	disGenDataDicName=disGenData()
	#disGenDataDicName='disGen.obj'
	disGenDataDic = cPickle.load(open(disGenDataDicName, 'rb'))
	unqhumanUniprotID=list(set(humanUniprotID))
	humanUniprotfuncinfodic={}
	countProt=0
	for subcode in unqhumanUniprotID:
		time.sleep(2)
		drugbanklist=[]
		PN='NA'
		GN='NA'
		OG='NA'
		OGID='NA'
		dislist=[]
		unidislist=[]
		unidisURLlist=[]
		disgendislist=[]
		disgendisURLlist=[]
		GoIDList=[]
		GoNamList=[]
		GoTermList=[]
		GOinfo=[]
		try:
			countProt+=1
			if countProt%1000 ==0:
				print str(countProt), "th protein Protein Name, Gene, Organism Name,drug bank data,disease data job starts",str(datetime.datetime.now())

			SGrequestURL="https://www.uniprot.org/uniprot/"+str(subcode)+".xml"
			SGunifile=urllib.urlopen(SGrequestURL)
			SGunidata= SGunifile.read()
			SGunifile.close()

			try:
				SGunidata=minidom.parseString(SGunidata)
				try:
					drugdata=(SGunidata.getElementsByTagName('dbReference'))
					for duItem in drugdata:
						if (duItem.attributes['type'].value).upper() == 'DRUGBANK':
							try:
								drugname=(str(duItem.getElementsByTagName('property')[0].attributes['value'].value).strip())
								drugid=str(duItem.attributes['id'].value).strip()
								durl='<a target="_blank" href="https://www.drugbank.ca/drugs/'+drugid+'">'+drugname+'</a>'
								drugbanklist.append(durl)
							except:
								pass
						if (duItem.attributes['type'].value).strip() == 'NCBI Taxonomy':
							try:
								OGID=str(duItem.attributes['id'].value).strip()
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

				try:
					disdata=SGunidata.getElementsByTagName('disease')
					for dItem in disdata:
						disname=''
						disshort=''
						disURL=''
						disID=''
						try:
							disname=(dItem.getElementsByTagName('name')[0]).firstChild.nodeValue
							disID=(dItem.attributes['id'].value).upper()
						except:
							pass
						try:
							disshort=(dItem.getElementsByTagName('acronym')[0]).firstChild.nodeValue
						except:
							pass
						if len(disname.strip())>0:
							disURL='<a target="_blank" href="https://www.uniprot.org/diseases/'+disID+'">'+str(disname.strip())+'('+str(disshort)+')'+'</a>'
							dislist.append(str(disname.strip())+'('+str(disshort)+')')
							unidislist.append(str(disname.strip())+'('+str(disshort)+')')
							unidisURLlist.append(disURL)
				except IndexError:
					pass

			except ExpatError:
				pass
		except IOError:
			pass
		drugbankdata='NA'
		disdata='NA'
		uniDisData='NA'
		uniDisURLData='NA'
		disgenDisData='NA'
		disgenDisURLData='NA'
		goiddata='NA'
		gonamedata='NA'
		gotermdata='NA'
		goData='NA'
		if GN != 'NA' and GN in disGenDataDic:
			disgendislist=disGenDataDic[GN][0]
			disgendisURLlist=disGenDataDic[GN][1]
			if len(dislist)>0:
				dislist=dislist+disGenDataDic[GN][0]
			else:
				dislist=disGenDataDic[GN][0]
			
		if len(GoIDList)>0:
			goiddata='|'.join(list(set(GoIDList)))
		if len(GoNamList)>0:
			gonamedata='|'.join(list(set(GoNamList)))
		if len(GoTermList)>0:
			gotermdata='|'.join(list(set(GoTermList)))
		if len(GOinfo)>0:
			goData='|'.join(list(set(GOinfo)))
		if len(drugbanklist)>0:
			drugbankdata='|'.join(list(set(drugbanklist)))
		if len(dislist)>0:
			disdata='|'.join(list(set(dislist)))
		if len(unidislist)>0:
			uniDisData='|'.join(list(set(unidislist)))
		if len(unidisURLlist)>0:
			uniDisURLData='|'.join(list(set(unidisURLlist)))
		if len(disgendislist)>0:
			disgenDisData='|'.join(list(set(disgendislist)))
		if len(disgendisURLlist)>0:
			disgenDisURLData='|'.join(list(set(disgendisURLlist)))
		humanUniprotfuncinfodic[subcode]=[PN,GN,OG,OGID,disdata,uniDisData,uniDisURLData,disgenDisData,disgenDisURLData,drugbankdata,goiddata,gonamedata,gotermdata,goData]
	hudicfile='humanUniprotfuncinfodic.obj'
	hudicf = open(hudicfile, 'wb')
	pickle.dump(humanUniprotfuncinfodic, hudicf , pickle.HIGHEST_PROTOCOL)
	hudicf.close()	

	print ("Extracting KEGG pathway name, job starts",str(datetime.datetime.now()))
	hkeggdictfile={}
	huniproturl = 'https://www.uniprot.org/uploadlists/'
	hk = KEGG()
	for hkx in range(0,len(unqhumanUniprotID),2000):
		countProt+=hkx+2000
		if countProt%2000 ==0:
			print (str(countProt), "th protein kegg job starts",str(datetime.datetime.now()))

		huniprotcodes=' '.join(unqhumanUniprotID[hkx:hkx+2000])
		huniprotparams = {
		'from':'ACC',
		'to':'KEGG_ID',
		'format':'tab',
		'query':huniprotcodes
		}
		
		while True:
			try:
				hkuniprotdata = urllib.urlencode(huniprotparams)
				hkuniprotrequest = urllib2.Request(huniproturl, hkuniprotdata)
				hkuniprotresponse = urllib2.urlopen(hkuniprotrequest)
				for hkuniprotline in hkuniprotresponse:
					hkudata=hkuniprotline.strip()
					if not hkudata.startswith("From"):
						hkuinfo=hkudata.split("\t")
						if len(hkuinfo[1].strip()):
							hkegg=hk.get(hkuinfo[1].strip())
							hkudict_data = hk.parse(hkegg)
							try:
								try:
									if len(str(hkuinfo[0]).strip()) >5:
										tempkeggData='|'.join('{};{}'.format(key, value) for key, value in hkudict_data['PATHWAY'].items())
										hkeggdictfile[hkuinfo[0].strip()]=[hkudict_data['PATHWAY'].values(),tempkeggData]
								except TypeError: 
									pass
							except KeyError:
								pass
				break
			except urllib2.HTTPError:
				time.sleep(RETRY_TIME)
				print ('Hey, I am trying again until succeeds to get data from KEGG!',str(datetime.datetime.now()))
				pass

	hkdicfile='humankeggdic.obj'
	hkdicf = open(hkdicfile, 'wb')
	pickle.dump(hkeggdictfile, hkdicf , pickle.HIGHEST_PROTOCOL)
	hkdicf.close()
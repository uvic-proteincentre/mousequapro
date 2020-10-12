'''
this script based on uniprot homolog file
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

def mapSpecies(mousepeptrackfilename):
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
	uniproturl = 'https://www.uniprot.org/uploadlists/'

	RETRY_TIME = 20.0
	mdf= pd.read_csv(mousepeptrackfilename, delimiter='\t')
	mouseGenes=list(mdf['Gene'].unique())
	mouseGenes=[g for g in mouseGenes if str(g) !='nan']

	mousehumandic={}
	for gx in range(0,len(mouseGenes),1000):
		genecodes=' '.join(mouseGenes[gx:gx+1000])
		geneuniprotparams = {
		'from':'GENENAME',
		'to':'ACC',
		'format':'tab',
		'query':genecodes,
		'columns':'id,genes(PREFERRED),organism-id,reviewed'

		}
		while True:
			try:
				geneuniprotdata = urllib.urlencode(geneuniprotparams)
				geneuniprotrequest = urllib2.Request(uniproturl, geneuniprotdata)
				geneuniprotresponse = urllib2.urlopen(geneuniprotrequest)
				for guniprotline in geneuniprotresponse:
					gudata=guniprotline.strip()
					if not gudata.startswith("Entry"):
						guinfo=gudata.split("\t")
						if '9606' == guinfo[2].lower() and 'reviewed' == guinfo[3].lower() and guinfo[-1].lower() ==guinfo[1].lower() and len(guinfo[0].strip())>1:
							mousehumandic[guinfo[-1].strip()]=guinfo[0].strip()
				break
			except urllib2.HTTPError:
				time.sleep(RETRY_TIME)
				print ('Hey, I am trying again until succeeds to get data from uniprot data!',str(datetime.datetime.now()))
			except httplib.BadStatusLine:
				time.sleep(RETRY_TIME)
				print ('Hey, I am trying again until succeeds to get data from  uniprot data!',str(datetime.datetime.now()))


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
			if len(str(templist[2]).strip())>0:
				if templist[2] in mousehumandic:
					huUniId=mousehumandic[templist[2]]
					humanUniprotID.append(huUniId)
					templist.append(huUniId)
				else:
					templist.append('NA')

			finalresult.append(templist)

	with open(mousepeptrackfilename,'wb') as pf:
		pwriter =csv.writer(pf,delimiter='\t')
		pwriter.writerows(finalresult)

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
		GoIDList=[]
		GoNamList=[]
		GoTermList=[]
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
								if gotermdetails.lower()=='p':
									GoTermList.append('Biological Process')
								if gotermdetails.lower()=='f':
									GoTermList.append('Molecular Function')
								if gotermdetails.lower()=='c':
									GoTermList.append('Cellular Component')
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
						try:
							disname=(dItem.getElementsByTagName('name')[0]).firstChild.nodeValue
						except:
							pass
						try:
							disshort=(dItem.getElementsByTagName('acronym')[0]).firstChild.nodeValue
						except:
							pass
						if len(disname.strip())>0:
							dislist.append(str(disname.strip())+'('+str(disshort)+')')
				except IndexError:
					pass

			except ExpatError:
				pass
		except IOError:
			pass
		drugbankdata='NA'
		disdata='NA'
		goiddata='NA'
		gonamedata='NA'
		gotermdata='NA'
		if len(GoIDList)>0:
			goiddata='|'.join(list(set(GoIDList)))
		if len(GoNamList)>0:
			gonamedata='|'.join(list(set(GoNamList)))
		if len(GoTermList)>0:
			gotermdata='|'.join(list(set(GoTermList)))
		if len(drugbanklist)>0:
			drugbankdata='|'.join(list(set(drugbanklist)))
		if len(dislist)>0:
			disdata='|'.join(list(set(dislist)))

		humanUniprotfuncinfodic[subcode]=[PN,GN,OG,OGID,disdata,drugbankdata,goiddata,gonamedata,gotermdata]

	hudicfile='humanUniprotfuncinfodic.obj'
	hudicf = open(hudicfile, 'wb')
	pickle.dump(humanUniprotfuncinfodic, hudicf , pickle.HIGHEST_PROTOCOL)
	hudicf.close()	

	print ("Extracting KEGG pathway name, job starts",str(datetime.datetime.now()))
	hkeggdictfile={}
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
				hkuniprotrequest = urllib2.Request(uniproturl, hkuniprotdata)
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
										hkeggdictfile[hkuinfo[0].strip()]=hkudict_data['PATHWAY'].values()
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
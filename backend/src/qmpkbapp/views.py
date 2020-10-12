#!/usr/bin/env.python
# -*- coding: utf-8 -*-
# encoding: utf-8
from __future__ import unicode_literals
from django.utils.encoding import force_text

from django.shortcuts import render

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from qmpkbapp.models import IpAddressInformation

from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.schemas import SchemaGenerator
from rest_framework.permissions import AllowAny
import coreapi,coreschema
from rest_framework.schemas import ManualSchema
from rest_framework_swagger import renderers
import sys,re,os,glob,shutil,subprocess,socket
import urllib,urllib3
import fileinput
from ipware.ip import get_ip
from time import gmtime, strftime,sleep
import csv
import hashlib, random
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
import json,demjson
import uuid
import json as simplejson
import calendar
from django.contrib import auth
from bioservices.kegg import KEGG
from xml.etree import cElementTree as ET
import xmltodict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from Bio.PDB.Polypeptide import *
from Bio import SeqIO
from requests.exceptions import ConnectionError
import requests
from django.utils.datastructures import MultiValueDictKeyError
from Bio.SeqUtils import seq1
from goatools import obo_parser
from elasticsearch import Elasticsearch,helpers,RequestsHttpConnection
import pandas as pd
from .colName import *
from summaryStat import summaryStatcal
from .calculationprog import *
from .totalpepassay import *
from .modifiedJsondata import *
from .filterSearch import *
from .downLoadData import *
import random
import names
from operator import itemgetter
import ast
from collections import OrderedDict
from itertools import combinations
import pandas as pd
import numpy as np
import operator
from .appTissueInfo import *
#delete after publication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login,logout
import math
from .adjustP import p_adjust_bh
from scipy.stats import mannwhitneyu
# Import Biopython modules to interact with KEGG
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser

# from rpy2.robjects.packages import importr
# from rpy2.robjects.vectors import FloatVector
# statsR= importr('stats')

searchFields=["UniProtKB Accession.ngram","Protein.ngram","Gene.ngram","Organism.ngram",\
				"Organism ID.ngram","SubCellular.ngram","Peptide Sequence.ngram",\
				"Mouse Kegg Pathway Name.ngram","Human Disease Name.ngram","Mouse Go ID.ngram",\
				"Mouse Go Name.ngram","Mouse Go Term.ngram","Human Drug Bank.ngram","Strain.ngram","Knockout.ngram","Panel.ngram","Sex.ngram","Biological Matrix.ngram"]

es = Elasticsearch(
	['http://xxxxx:9200/'],
	connection_class=RequestsHttpConnection
)
# Create your views here.


def basicSearch(request):
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)

	if request.method=='GET':
		searchterm=request.GET.get("searchterm")# user input for searching result
		searchterm= str(searchterm).strip()
		querybiomatrix=''
		if '_' in searchterm:
			tempsearchterm=searchterm.split('_')
			querybiomatrix=tempsearchterm[0]
			searchterm=str(tempsearchterm[1]).strip()
		response_data = {'filename_proteincentric': None,'downloadResultFilePath': None}
		countUnqprot=[]
		if searchterm.lower() !='none':
			#build elasticsearch query to search data
			query={
				"query":{
					"bool":{
						"should":[{
								"multi_match":{
									"query":searchterm,
									"type":"best_fields",
									"fields":searchFields,
									"minimum_should_match":"100%"
								}
						}]
					}
				}
			}
			#generate random file name to store search result in json format
			currdate=str(datetime.datetime.now())
			currdate=currdate.replace('-','_')
			currdate=currdate.replace(' ','_')
			currdate=currdate.replace(':','_')
			currdate=currdate.replace('.','_')
			nameFIle=str(uuid.uuid4())
			jsonfilename_proteincentric=nameFIle+'_search_proteincentric.json'
			jsonfilepath_proteincentric=os.path.join(settings.BASE_DIR, 'resultFile', 'jsonData','resultJson', 'search', 'results', jsonfilename_proteincentric)
			jsonfilepath_proteincentric_download=os.path.join(settings.BASE_DIR, 'resultFile', 'jsonData','resultJson', 'search', 'downloadversion', jsonfilename_proteincentric)
			jsonfileoutput_proteincentric= open(jsonfilepath_proteincentric,'w')
			jfinaldata=[]
			es.indices.refresh(index="xxxxxxxxx-index")
			#elasticsearch will search data
			res=helpers.scan(client=es,scroll='2m',index="xxxxxxxxx-index", doc_type="xxxxxxxx-type",query=query,request_timeout=30)
			jfinaldata=[]
			uniprotpepinfo={}
			#if data is valid based on uniprotkb release then it will display
			for i in res:
				jdic=i['_source']
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				panelFilter=True
				if 'panel' in searchterm.lower():
					if searchterm.lower() in (jdic['Panel'].lower()).split(';') and 'panel' in searchterm.lower():
						panelFilter=True
					else:
						panelFilter=False

				if jdic["UniprotKb entry status"] =="Yes" and panelFilter:
					countUnqprot.append(jdic["UniProtKB Accession"].split('-')[0].upper())
					if uniprotpepinfo.has_key(jdic["UniProtKB Accession"]):
						uniprotpepinfo[jdic["UniProtKB Accession"]].append(jdic["Peptide Sequence"])
					else:
						uniprotpepinfo[jdic["UniProtKB Accession"]]=[jdic["Peptide Sequence"]]
					#if jdic["Retention Time"].lower() =='na' or jdic["Gradients"].lower() =='na':
					if jdic["Retention Time"].lower() =='na':
						jdic["Summary Concentration Range Data"]='NA'
						jdic["Concentration View"]='NA'

					if jdic["Human UniProtKB Accession"].lower() !='na' and jdic["Present in human ortholog"].lower() =='no':
						jdic["Available assays in human ortholog"]='http://mrmassaydb.proteincentre.com/search/hyperlink/?UniProtKB Accession='+jdic["Human UniProtKB Accession"]
					else:
						jdic["Available assays in human ortholog"]='NA'

					if len(str(jdic["Summary Concentration Range Data"]).strip()) >0 and str(jdic["Summary Concentration Range Data"]).strip().upper() !="NA":
						try:
							jdic["Biological Matrix"]=jdic["Biological Matrix"].replace('|','<br/>')
						except KeyError:
							pass
						# try:
						# 	if '<br/>' in jdic["Concentration View"]:
						# 		tempmatrix=jdic["Concentration View"].split()[-1]
						# 		jdic["Concentration View"]=jdic["Concentration View"].replace('tissue',tempmatrix)
						# except KeyError:
						# 	pass
					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/u','µg protein/µ')
					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/u','µg protein/µ')
					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/u','µg protein/µ')
					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/mg','µg protein/mg')

					jdic["Concentration View"]=jdic["Concentration View"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Concentration Range"]=jdic["Concentration Range"].replace('fmol target protein/u','fmol target protein/µ')

					jdic["LLOQ"]=jdic["LLOQ"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["ULOQ"]=jdic["ULOQ"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Sample LLOQ"]=jdic["Sample LLOQ"].replace('fmol target protein/u','fmol target protein/µ')

					if jdic["Unique in protein"].upper() =='NA':
						jdic["Unique in protein"]=jdic["Unique in protein"].replace('NA','No')
					if jdic["Present in isoforms"].upper() =='NA':
						jdic["Present in isoforms"]=jdic["Present in isoforms"].replace('NA','No')

					
					jfinaldata.append(jdic)
			es.indices.refresh(index="xxxxxxxxx-index")
			#checking any result generated by database
			foundHits=len(jfinaldata)
			#storing only 10000 rows in json format
			matchingpepseqquery=[searchterm]
			finalupdatedUniInfo,biomatrixContainUniId,foldchangeData=pepbasedInfo(jfinaldata,uniprotpepinfo,matchingpepseqquery,proteinInfoColname,querybiomatrix)

			biomatrixContainUniId=list(set(biomatrixContainUniId))
			if len(querybiomatrix) >0:
				jfinaldata = [x for x in jfinaldata if x["UniProtKB Accession"] in biomatrixContainUniId]
				finalupdatedUniInfo["data"]=[k for k in finalupdatedUniInfo["data"] if k["UniProtKB Accession"] in biomatrixContainUniId]

			json.dump(finalupdatedUniInfo,jsonfileoutput_proteincentric)
			jsonfileoutput_proteincentric.close()
			# if result found then do other job
			if foundHits >0:
				statsummary=summaryStatcal(jfinaldata) # sent data to this funcation for generating stat
				
				keggchart=statsummary['keggchart']
				keggchart=[i[:2] for i in keggchart]
				specieslist=statsummary['specieslist']
				totallist=statsummary['total']
				subcell=statsummary['subcell']
				sortedgodic=statsummary['godic']
				querybioMatData=statsummary['BioMat']
				querystrainData=statsummary['Strain']
				querynoOfHumanortholog=statsummary['noOfHumanortholog']
				querynoOfDiseaseAssProt=statsummary['noOfDiseaseAssProt']
				humandisease=statsummary['disdic']
				pepseqdataseries=ast.literal_eval(json.dumps(statsummary['pepseqdataseries'])) #dumping data into json format
				prodataseries=statsummary['prodataseries']
				unqisostat=statsummary['unqisostat']
				urlname_proteincentric="search/results/"+jsonfilename_proteincentric
				foldchangeLength=len(foldchangeData)
				with open(jsonfilepath_proteincentric_download,'w') as downloadJsonFile:
					json.dump(jfinaldata,downloadJsonFile)
				response_data={
					"filename_proteincentric":urlname_proteincentric,'query': searchterm,'foundHits':foundHits,
					'keggchart':keggchart[:11],'specieslist':specieslist,
					'totallist':totallist,'subcell':subcell,'querybioMatData':querybioMatData,'querystrainData':querystrainData,'querynoOfHumanOrtholog':querynoOfHumanortholog,'querynoOfDiseaseAssProt':querynoOfDiseaseAssProt,
					'updatedgo':sortedgodic,'pepseqdataseries':pepseqdataseries,'humandisease':humandisease,
					'prodataseries':prodataseries,'unqisostat':unqisostat
					}
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def advancedSearch(request):
	"""
	This is advance search function, based on given search parameters it will generate result datatable along with stat
	from database.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		advancesearchFields={
		 'protein':'Protein',
		 'gene':'Gene',
		 'uniProtKBAccession':'UniProtKB Accession', 
		 'pepSeq':'Peptide Sequence',
		 'panel':'Panel',
		 'strain':'Strain',
		 'mutant':'Knockout',
		 'sex':'Sex',
		 'biologicalMatrix': 'Biological Matrix',
		 'subCellLoc':'SubCellular',
		 'keggPathway':'Mouse Kegg Pathway Name',
		 'disCausMut':'Human Disease Name',
		 'goId':'Mouse Go ID',
		 'goTerm':'Mouse Go Name',
		 'goAspects':'Mouse Go Term',
		 'drugId':'Human Drug Bank',
		 'fastaFileName':'Own protein sequences in FASTA format'
		}
		multiOptions=['panel','strain','mutant','sex','biologicalMatrix']
		filtersearchStatus=0
		response_data={'filename_proteincentric': None,'downloadResultFilePath': None}
		searchterm=[]  # list of search term value associated with searchtype
		searchtype =[]  # list of search parameter
		searchtermlist=[]
		panelQuery=''
		advanceFormDetails=json.loads(request.GET.get('advancedFormData'))
		queryformData=advanceFormDetails["queryformData"]
		optionGroups=queryformData["optionGroups"]
		for opItem in optionGroups:
			searchterm.append(str(opItem["whereInput"]).strip())
			searchtype.append(str(opItem["selectInput"]).strip())
		userInputFastaFileName=''
		userInputFastaFileContext=''
		if "fastaFileName" in searchtype:
			userInputFastaFileName=str(searchterm[searchtype.index("fastaFileName")]).strip()
		nameFIle=str(uuid.uuid4()) # generate random file name to store user search result
		fastaseq=[]
		finalsearhdata=''
		if len(userInputFastaFileName)>0:
			try:
				finalsearhdata+='File'+':'+'Fasta Sequence'+' '
				#storing user provided fasta file
				fastafilepath=os.path.join(settings.BASE_DIR, 'resultFile', 'fastaFile', userInputFastaFileName+'.fasta')

				#reading fasta file
				for useq_record in SeqIO.parse(fastafilepath, 'fasta'):
					seqheader = useq_record.id
					sequniID = seqheader.split(' ')[0]
					sequniID=sequniID.replace('>','')
					tempseqs = str(useq_record.seq).strip()
					fastaseq.append(str(sequniID)+'_'+tempseqs.upper())
			except MultiValueDictKeyError:
				pass

			try:
				fastafileindex=searchtype.index("fastaFileName")
				#delete data based on index from list
				del searchtype[fastafileindex]
				del searchterm[fastafileindex]
			except ValueError:
				pass

		matchingpepseqquery=[]
		for i in range(0,len(searchtype)):
			subsearchtype=searchtype[i]
			subsearchterm=searchterm[i]
			if subsearchtype in multiOptions:
				subsearchterm=map(str,ast.literal_eval(subsearchterm))
				subsearchterm='|'.join(subsearchterm)
				searchterm[i]=subsearchterm
			#build elasticsearch query for all except organism to search data
			if '|' in subsearchterm:
				if 'Peptide Sequence' == subsearchtype:
					for p in (subsearchterm.strip()).split('|'):
						matchingpepseqquery.append(str(p).strip())
				subsearchterm=(subsearchterm.strip()).split('|')
			else:
				if 'Peptide Sequence' == subsearchtype:
					for p in (subsearchterm.strip()).split('\n'):
						matchingpepseqquery.append(str(p).strip())
				subsearchterm=(subsearchterm.strip()).split('\n')
			subsearchterm=map(str, subsearchterm)
			subsearchterm=map(lambda j: j.strip(), subsearchterm)
			subsearchterm=filter(None, subsearchterm)
			if  subsearchtype=='mutant':
				finalsearhdata+=''.join('Mutant')+':'+';'.join(subsearchterm)+' '
			elif subsearchtype=='goTerm':
				finalsearhdata+=''.join('Mouse GO Term')+':'+';'.join(subsearchterm)+' '
			elif subsearchtype=='goAspects':
				finalsearhdata+=''.join('Mouse GO Aspects')+':'+';'.join(subsearchterm)+' '
			else:
				finalsearhdata+=''.join(advancesearchFields[str(subsearchtype)])+':'+';'.join(subsearchterm)+' '
			
			if len(subsearchterm)>0:
				subsearchterm=[(item.strip()).lower() for item in subsearchterm] #converting into lower case
				shouldlist=[]
				for x in subsearchterm:
					tempquery={
								"multi_match":{
									"query":x.strip(),
									"type":"best_fields",
									"fields":[advancesearchFields[str(subsearchtype)]+".ngram"],
									"minimum_should_match":"100%"
								}
							}
					shouldlist.append(tempquery)
				booldic={}
				booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
				searchtermlist.append(booldic)
		unqfastaseq=list(set(fastaseq))

		if len(searchtermlist)>0 or len(unqfastaseq)>0:
			es.indices.refresh(index="xxxxxxxxx-index")

			query=""
			if len(searchtermlist)>0:
				query={
					"query": {
						"bool": {
							"must":searchtermlist
						}
					}
				}
			if len(searchtermlist)==0:
				query={
					"query": {
						"match_all": {}
					}
				}
			try:
				if searchtype.index('sex') >=0:
					filtersearchStatus=1
			except ValueError:
				pass
			try:
				if searchtype.index('strain') >=0:
					filtersearchStatus=1
			except ValueError:
				pass
			try:
				if searchtype.index('biologicalMatrix') >=0:
					filtersearchStatus=1
			except ValueError:
				pass
			try:
				if searchtype.index('panel') >=0:
					panelQuery=searchterm[searchtype.index('panel')].strip()
					filtersearchStatus=1
			except ValueError:
				pass
			try:
				if searchtype.index('mutant') >=0:
					filtersearchStatus=1
			except ValueError:
				pass
			#storing user search result into json format
			currdate=str(datetime.datetime.now())
			currdate=currdate.replace('-','_')
			currdate=currdate.replace(' ','_')
			currdate=currdate.replace(':','_')
			currdate=currdate.replace('.','_')
			jsonfilename_proteincentric=nameFIle+'_search_proteincentric.json'
			jsonfilepath_proteincentric=os.path.join(settings.BASE_DIR, 'resultFile', 'jsonData','resultJson', 'search', 'results', jsonfilename_proteincentric)
			jsonfilepath_proteincentric_download=os.path.join(settings.BASE_DIR, 'resultFile', 'jsonData','resultJson', 'search', 'downloadversion', jsonfilename_proteincentric)
			jsonfileoutput_proteincentric= open(jsonfilepath_proteincentric,'w')

			jfinaldata=[]
			res=helpers.scan(client=es,scroll='2m',index="xxxxxxxxx-index", doc_type="xxxxxxxx-type",query=query,request_timeout=30)
			jfinaldata=[]
			uniprotpepinfo={}
			usersequnq=[]
			for i in res:
				jdic=i['_source']
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				panelFilter=True
				if len(panelQuery) >0:
					for q in  panelQuery.lower().split('|'):
						if q in (jdic['Panel'].lower()).split(';'):
							panelFilter=True
							break
					else:
						panelFilter=False
				#if jdic["Retention Time"].lower() =='na' or jdic["Gradients"].lower() =='na':
				if panelFilter:
					if jdic["Retention Time"].lower() =='na':
						jdic["Summary Concentration Range Data"]='NA'
						jdic["Concentration View"]='NA'

					if jdic["Human UniProtKB Accession"].lower() !='na' and jdic["Present in human ortholog"].lower() =='no':
						jdic["Available assays in human ortholog"]='http://mrmassaydb.proteincentre.com/search/hyperlink/?UniProtKB Accession='+jdic["Human UniProtKB Accession"]
					else:
						jdic["Available assays in human ortholog"]='NA'

					jdic["PPI"] ="View"
					if len(str(jdic["Summary Concentration Range Data"]).strip()) >0 and str(jdic["Summary Concentration Range Data"]).strip().upper() !="NA":
						try:
							jdic["Biological Matrix"]=jdic["Biological Matrix"].replace('|','<br/>')
						except KeyError:
							pass

						# try:
						# 	if '<br/>' in jdic["Concentration View"]:
						# 		tempmatrix=jdic["Concentration View"].split()[-1]
						# 		jdic["Concentration View"]=jdic["Concentration View"].replace('tissue',tempmatrix)
						# except KeyError:
						# 	pass
					if filtersearchStatus==0:
						jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/u','µg protein/µ')
						jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

						jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/u','µg protein/µ')
						jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

						jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/u','µg protein/µ')
						jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/mg','µg protein/mg')

						jdic["Concentration View"]=jdic["Concentration View"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["Concentration Range"]=jdic["Concentration Range"].replace('fmol target protein/u','fmol target protein/µ')

						jdic["LLOQ"]=jdic["LLOQ"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["ULOQ"]=jdic["ULOQ"].replace('fmol target protein/u','fmol target protein/µ')
						jdic["Sample LLOQ"]=jdic["Sample LLOQ"].replace('fmol target protein/u','fmol target protein/µ')

						if jdic["Unique in protein"].upper() =='NA':
							jdic["Unique in protein"]=jdic["Unique in protein"].replace('NA','No')
						if jdic["Present in isoforms"].upper() =='NA':
							jdic["Present in isoforms"]=jdic["Present in isoforms"].replace('NA','No')
					seqhit=0
					# checking any peptide present in user provided fasta sequence
					# classified into 3 catagories
					if len(unqfastaseq)>0:
						pepseq=str(jdic['Peptide Sequence']).strip()
						indices = [i for i, s in enumerate(fastaseq) if pepseq.upper() in s]
						seqhit=len(indices)
						tempuserseqheadermatch='NA'
						tempmatchlist=[]
						if len(indices)>0:
							for i in indices:
								tempmatchlist.append('_'.join(fastaseq[i].split('_')[:-1]))
						if len(tempmatchlist)>0:
							tempuserseqheadermatch='<br/>'.join(tempmatchlist)
						jdic["Peptide in user's database"] =str(tempuserseqheadermatch)
						if len(indices)==0:
							jdic["Peptide unique in user's database"] ="Not present"
						elif len(indices) > 1:
							jdic["Peptide unique in user's database"] ="Present but not unique"
						else:
							jdic["Peptide unique in user's database"] ="Present and unique"
							usersequnq.append("Present and unique")

					if len(searchtermlist)==0:
						if seqhit >0:
							if uniprotpepinfo.has_key(jdic["UniProtKB Accession"]):
								uniprotpepinfo[jdic["UniProtKB Accession"]].append(jdic["Peptide Sequence"])
							else:
								uniprotpepinfo[jdic["UniProtKB Accession"]]=[jdic["Peptide Sequence"]]
							jfinaldata.append(jdic)
					else:
						if jdic["UniprotKb entry status"] =="Yes":
							if uniprotpepinfo.has_key(jdic["UniProtKB Accession"]):
								uniprotpepinfo[jdic["UniProtKB Accession"]].append(jdic["Peptide Sequence"])
							else:
								uniprotpepinfo[jdic["UniProtKB Accession"]]=[jdic["Peptide Sequence"]]
							jfinaldata.append(jdic)

			es.indices.refresh(index="xxxxxxxxx-index")
			#jfinaldata=jfinaldata[0]
			#storing only 10000 rows in json format
			if filtersearchStatus >0:
				jfinaldata,filteredUniProtIDs=filterSearch(jfinaldata,searchterm,searchtype)

			#checking any result generated by database
			foundHits=len(jfinaldata)

			# if result found then do other job
			if foundHits >0:
				querybiomatrix=''
				try:
					if len(filteredUniProtIDs) >0:
						for delKey in filteredUniProtIDs:
							del uniprotpepinfo[delKey]
				except UnboundLocalError:
					pass
				finalupdatedUniInfo,biomatrixContainUniId,foldchangeData=pepbasedInfo(jfinaldata,uniprotpepinfo,matchingpepseqquery,proteinInfoColname,querybiomatrix)

				json.dump(finalupdatedUniInfo,jsonfileoutput_proteincentric)
				jsonfileoutput_proteincentric.close()

				statsummary=summaryStatcal(jfinaldata) # sent data to this funcation for generating stat
				keggchart=statsummary['keggchart']
				keggchart=[i[:2] for i in keggchart]
				specieslist=statsummary['specieslist']
				totallist=statsummary['total']
				subcell=statsummary['subcell']
				sortedgodic=statsummary['godic']
				querybioMatData=statsummary['BioMat']
				querystrainData=statsummary['Strain']
				querynoOfHumanortholog=statsummary['noOfHumanortholog']
				querynoOfDiseaseAssProt=statsummary['noOfDiseaseAssProt']
				humandisease=statsummary['disdic']
				pepseqdataseries=ast.literal_eval(json.dumps(statsummary['pepseqdataseries'])) #dumping data into json format
				prodataseries=statsummary['prodataseries']
				unqisostat=statsummary['unqisostat']
				urlname_proteincentric="search/results/"+jsonfilename_proteincentric
				with open(jsonfilepath_proteincentric_download,'w') as downloadJsonFile:
					json.dump(jfinaldata,downloadJsonFile)
				unqfastaseqlen=0
				unqfastaseqlen=len(unqfastaseq)
				if len(unqfastaseq)>0:
					tempcalunq=str(round(((float(usersequnq.count('Present and unique'))/float(len(jfinaldata)))*100),2))+'%'
					unqisostat.append(["User data",tempcalunq,"NA"])
					#df.to_csv(downloadResultFilePath,index=False, encoding='utf-8', columns=downloadColName)

					response_data={
						"filename_proteincentric":urlname_proteincentric,
						'query': finalsearhdata,'foundHits':foundHits,
						'keggchart':keggchart[:11],'humandisease':humandisease,
						'totallist':totallist,'subcell':subcell,'querybioMatData':querybioMatData,'querystrainData':querystrainData,'querynoOfHumanOrtholog':querynoOfHumanortholog,'querynoOfDiseaseAssProt':querynoOfDiseaseAssProt,
						'updatedgo':sortedgodic,'unqfastaseqlen':unqfastaseqlen,
						'unqisostat':unqisostat,'fastafilename':userInputFastaFileName
						}
				elif len(unqfastaseq)==0:
					#df.to_csv(downloadResultFilePath,index=False, encoding='utf-8',columns=downloadColNameUserSeq)
					response_data={
						"filename_proteincentric":urlname_proteincentric,
						'query': finalsearhdata,'foundHits':foundHits,
						'keggchart':keggchart[:11],'humandisease':humandisease,
						'totallist':totallist,'subcell':subcell,'querybioMatData':querybioMatData,'querystrainData':querystrainData,'querynoOfHumanOrtholog':querynoOfHumanortholog,'querynoOfDiseaseAssProt':querynoOfDiseaseAssProt,
						'updatedgo':sortedgodic,'unqfastaseqlen':unqfastaseqlen,
						'unqisostat':unqisostat
						}
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def protVista(request):
	'''
	This function will display result for Mutation,PTM & Domain.
	'''
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		response_data = {'seqStart':None,'seqEnd':None}
		pepSeqMatchList=[]
		pepSeqMatchDic={}
		domainplotscript=[]
		valid=False
		humanValid=False
		contextpep={}
		humanContextPep={}
		proseq=''
		humanProSeq=''
		match_info=[]
		human_match_info=[]
		fasthead=''
		humanFastHead=''
		fastasq=''
		humanFastaSq=''
		fastalen=0
		humanFastaLen=0
		reachable=True
		humanReachable=True
		pepfilepath = os.path.join(settings.BASE_DIR, 'qmpkbmotherfile', 'ReportBook_mother_file.csv')
		presentunidpepseqstat=False
		listOfPeptide=[]
		listOfHumanPeptide=[]
		pepstart=0
		humanPepStart=0
		pepend=0
		humanPepEnd=0
		jsonprotvistastatus=False
		humanJsonProtvistaStatus=False
		protname=None
		humanUniprotKB='NA'
		es.indices.refresh(index="xxxxxxxxx-index")
		query={"query": {
			"bool": {
				"must": [
					{"match": {"UniProtKB Accession": uniprotkb}},
					{"match": {"UniprotKb entry status": "Yes"}}
				]
			}
		}
		}

		res=helpers.scan(client=es,scroll='2m',index="xxxxxxxxx-index", doc_type="xxxxxxxx-type",query=query,request_timeout=30)

		for hit in res:
			jdic=hit["_source"]
			jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
			if str(jdic["Present in human ortholog"]).strip() == 'Yes':
				humanUniprotKB=str(jdic["Human UniProtKB Accession"]).strip()
				listOfHumanPeptide.append(str(jdic["Peptide Sequence"]).strip())
			listOfPeptide.append(str(jdic["Peptide Sequence"]).strip())
		es.indices.refresh(index="xxxxxxxxx-index")
		foundHits=len(listOfPeptide)
		if '-' not in uniprotkb:
			code=(str(uniprotkb).strip()).upper()
			try:
				sleep(random.randint(5,10))
				requests.get("https://www.uniprot.org/", timeout=1)
				unidatafasta = urllib.urlopen("https://www.uniprot.org/uniprot/" + code + ".fasta")
				for mseq in SeqIO.parse(unidatafasta, "fasta"):
					fasthead=str((mseq.id).strip())
					proseq=str((mseq.seq).strip())
					fastasq=str((mseq.seq).strip())

				unidatafasta.close()
			except ConnectionError as e:
				reachable=False

			if reachable:
				jsonfilestatus=False
				jsonfilename='externalLabeledFeatures_'+uniprotkb+'.json'
				jsonfilepath=os.path.join(settings.BASE_DIR, 'resultFile','jsonData', 'protvistadataJson', 'mouse',jsonfilename)
				if os.path.exists(jsonfilepath):
					if datetime.datetime.fromtimestamp(os.path.getmtime(pepfilepath))< datetime.datetime.fromtimestamp(os.path.getmtime(jsonfilepath)):
						jsonfilestatus=True
						jsonprotvistastatus=True
					else:
						os.remove(jsonfilepath)
						jsonfilestatus=False
				else:
					jsonfilestatus=False
				jsonpepdata={}
				for pepseqitem in listOfPeptide:
					peptide_pattern = re.compile(pepseqitem,re.IGNORECASE)
					for match in re.finditer(peptide_pattern,proseq):
						jsonpepdata[pepseqitem.upper()] =[(int(match.start())+1),match.end()]
						pepstart=int(match.start())+1
						pepend=int(match.end())
						if pepseqitem in pepSeqMatchDic:
							pepSeqMatchDic[pepseqitem].append([pepstart,pepend,'Mouse'])
						else:
							pepSeqMatchDic[pepseqitem]=[[pepstart,pepend,'Mouse']]

						match_info.append([(int(match.start())+1),match.group(),match.end()])
				contextpep[uniprotkb]=[list(x) for x in set(tuple(x) for x in match_info)]
				fastalen=len(fastasq)

				if not jsonfilestatus:
					jsonfileoutput= open(jsonfilepath,'w')
					jsonformatdataprotvista={}
					jsonformatdataprotvista["sequence"]=str(proseq)
					tempfearures=[]
					for jsonkey in jsonpepdata.keys():
						tempdicjsondic={}
						tempdicjsondic["type"]="MRM"
						tempdicjsondic["category"]="Targeted_Proteomics_Assay_Mouse"
						tempdicjsondic["description"]="Suitable MRM Assay for Mouse"
						tempdicjsondic["begin"]=str(jsonpepdata[jsonkey][0])
						tempdicjsondic["end"]=str(jsonpepdata[jsonkey][1])
						tempdicjsondic["color"]="#00B88A"
						tempdicjsondic["accession"]=uniprotkb
						tempfearures.append(tempdicjsondic)
					jsonformatdataprotvista["features"]=tempfearures
					json.dump(jsonformatdataprotvista,jsonfileoutput)
					jsonfileoutput.close()
					jsonprotvistastatus=True

		if ('-' not in humanUniprotKB and humanUniprotKB !='NA'):
			try:
				sleep(random.randint(5,10))
				requests.get("https://www.uniprot.org/", timeout=1)
				humanUniDataFasta = urllib.urlopen("https://www.uniprot.org/uniprot/" + humanUniprotKB + ".fasta")
				for hseq in SeqIO.parse(humanUniDataFasta, "fasta"):
					humanFastHead=str((hseq.id).strip())
					humanProSeq=str((hseq.seq).strip())
					humanFastaSq=str((hseq.seq).strip())
				humanUniDataFasta.close()
			except ConnectionError as e:
				humanReachable=False

			if humanReachable:
				humanJsonFileStatus=False
				humanJsonFileName='externalLabeledFeatures_'+humanUniprotKB+'.json'
				humanJsonFilePath=os.path.join(settings.BASE_DIR, 'resultFile','jsonData', 'protvistadataJson','human', humanJsonFileName)
				if os.path.exists(humanJsonFilePath):
					if datetime.datetime.fromtimestamp(os.path.getmtime(pepfilepath))< datetime.datetime.fromtimestamp(os.path.getmtime(humanJsonFilePath)):
						humanJsonFileStatus=True
						humanJsonProtvistaStatus=True
					else:
						os.remove(jsonfilepath)
						humanJsonFileStatus=False
				else:
					humanJsonFileStatus=False
				humanJsonPepData={}
				for hPepSeqItem in listOfHumanPeptide:
					human_peptide_pattern = re.compile(hPepSeqItem,re.IGNORECASE)
					for hmatch in re.finditer(human_peptide_pattern,humanProSeq):
						humanJsonPepData[hPepSeqItem.upper()] =[(int(hmatch.start())+1),hmatch.end()]
						humanPepStart=int(hmatch.start())+1
						humanPepEnd=int(hmatch.end())
						if hPepSeqItem in pepSeqMatchDic:
							pepSeqMatchDic[hPepSeqItem].append([humanPepStart,humanPepEnd,'Human'])
						else:
							pepSeqMatchDic[hPepSeqItem]=[[humanPepStart,humanPepEnd,'Human']]
						human_match_info.append([(int(hmatch.start())+1),hmatch.group(),hmatch.end()])
				humanContextPep[humanUniprotKB]=[list(x) for x in set(tuple(x) for x in human_match_info)]
				humanFastaLen=len(humanFastaSq)
				if not humanJsonFileStatus:
					humanJsonFileOutput= open(humanJsonFilePath,'w')
					humanJsonFormatDataProtvista={}
					humanJsonFormatDataProtvista["sequence"]=str(humanProSeq)
					htempfearures=[]
					for jsonkey in humanJsonPepData.keys():
						htempdicjsondic={}
						htempdicjsondic["type"]="MRM"
						htempdicjsondic["category"]="Targeted_Proteomics_Assay_Human"
						htempdicjsondic["description"]="Suitable MRM Assay for Human"
						htempdicjsondic["begin"]=str(humanJsonPepData[jsonkey][0])
						htempdicjsondic["end"]=str(humanJsonPepData[jsonkey][1])
						htempdicjsondic["color"]="#00B88A"
						htempdicjsondic["accession"]=humanUniprotKB
						htempfearures.append(htempdicjsondic)
					humanJsonFormatDataProtvista["features"]=htempfearures
					json.dump(humanJsonFormatDataProtvista,humanJsonFileOutput)
					humanJsonFileOutput.close()
					humanJsonProtvistaStatus=True
		for pepMKey in pepSeqMatchDic:
			tempMatchList=[pepMKey,'NA','NA','NA','NA']
			for pepMItem in pepSeqMatchDic[pepMKey]:
				if pepMItem[-1]=='Mouse':
					tempMatchList[1]=pepMItem[0]
					tempMatchList[2]=pepMItem[1]
				else:
					tempMatchList[3]=pepMItem[0]
					tempMatchList[4]=pepMItem[1]
			pepSeqMatchList.append(tempMatchList)

		response_data={'contextpep':contextpep,'humanContextPep':humanContextPep,'fastalen':fastalen,'humanFastaLen':humanFastaLen,'uniprotkb':uniprotkb,'humanUniprotKB':humanUniprotKB,\
		'seqStart':pepstart,'humanPepStart':humanPepStart,'seqEnd':pepend,'humanPepEnd':humanPepEnd,'jsonprotvistastatus':jsonprotvistastatus,'humanJsonProtvistaStatus':humanJsonProtvistaStatus,\
		'pepSeqMatchList':pepSeqMatchList,'reachable':reachable}
		
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def assaydetails(request):
	"""
	This function is searching information for tranisition, based on intrument type
	in database.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		resultFilePath= request.GET['resultFilePath']
		resultFilePath= str(request.GET.get("resultFilePath")).strip()
		fastafilename=request.GET.get("fastafilename")
		fastafilename= str(fastafilename).strip()
		es.indices.refresh(index="xxxxxxxxx-index")
		#build elasticsearch query based on peptide seq and uniprotkb acc
		query={"query": {
			"bool": {
				"must": [
					{"match": {"UniProtKB Accession": uniprotkb}},
					{"match": {"UniprotKb entry status": "Yes"}}
				]
			}
		}
		}
		res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)

		bioMatProtInfo={}
		transdic={}
		temptransdic={}
		gradientlist=[]
		gradinfoheader=[]
		loquantinfo=[]
		foundHits=res["hits"]["total"]
		userFastaStatus=0
		if fastafilename !='NA':
			userFastaStatus=1
		protinfo={}

		with open(resultFilePath) as rjf:
			for resitem in json.load(rjf)['data']:
				if resitem["UniProtKB Accession"]==uniprotkb:
					pepinfo =resitem["Peptide Based Info"]
					for pepItem in pepinfo:
						tempPepSeq=pepItem["Peptide Sequence"].strip()
						panData="NA"
						pepiso="NA"
						huPepiso="NA"
						pepUnq=pepItem["Unique in protein"].strip()
						pepHumanortholog=pepItem["Present in human ortholog"].strip()
						unqInHumanortholog=pepItem["Unique in human protein"].strip()

						if len(pepItem["Concentration View"].strip()) > 0 and pepItem["Concentration View"].strip().upper() !="NA":
							conqueryArray=pepItem["concenQuery"].strip().split('@')
							bioMatProtInfo[tempPepSeq]=conqueryArray[2]

						if len(pepItem["Present in isoforms"].strip()) > 0 and  pepItem["Present in isoforms"].strip().upper() != "NA" and pepItem["Present in isoforms"].strip().upper() != "NO":
							tempLst =pepItem["Present in isoforms"].strip().split(',')
							for idx, val in enumerate(tempLst):
								tempLst[idx] = '<a target="_blank"  routerLinkActive="active" href="https://www.uniprot.org/uniprot/' + val+'.fasta">'+val+ '</a>'
							pepiso="<br>".join(tempLst)

						if len(pepItem["Present in human isoforms"].strip()) > 0 and  pepItem["Present in human isoforms"].strip() != "NA" and pepItem["Present in human isoforms"].strip().upper() != "NO":
							tempLst =pepItem["Present in human isoforms"].strip().split(',')
							for idx, val in enumerate(tempLst):
								tempLst[idx] = '<a target="_blank"  routerLinkActive="active" href="https://www.uniprot.org/uniprot/' + val+'.fasta">'+val+ '</a>'
							huPepiso="<br>".join(tempLst)

						if len(pepItem["Panel"].strip()) > 0 and pepItem["Panel"].strip().upper() != "NA" :
							panview=pepItem["Panel"].strip().split(';')
							panData="<br>".join(panview)
						if userFastaStatus==0:
							protinfo[tempPepSeq]=[pepUnq,pepiso,pepHumanortholog,unqInHumanortholog,huPepiso,panData]
						if userFastaStatus==1:
							pepuserfo=None
							pepInUserDB=pepItem["Peptide in user's database"]
							if  pepItem["Peptide unique in user's database"].strip() == "Not present":
								pepuserfo= pepItem["Peptide unique in user's database"].strip()
							else:
								pepuserfo= '<a target="_blank"  routerLinkActive="active" routerLinkActive="active" href="/dataload/userpepseq_'  + pepItem["UniProtKB Accession"].strip() +'_'+pepItem["Peptide Sequence"].strip() +'_'+fastafilename + '">' + pepItem["Peptide unique in user's database"].strip() + '</a>'

							protinfo[tempPepSeq]=[pepUnq,pepiso,pepHumanortholog,unqInHumanortholog,huPepiso,pepuserfo,pepInUserDB,panData]
					break

		
		for hit in res['hits']['hits']:
			jdic=hit["_source"]
			jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
			jdic["Concentration Range"]=jdic["Concentration Range"].replace('fmol target protein/u','fmol target protein/µ')
			if str(jdic["UniProtKB Accession"]).strip() == uniprotkb and str(jdic["Peptide Sequence"]).strip() in protinfo:
				meanRetentime=0.0
				fragIon=[]
				temploquantinfo={}
				jdic["LLOQ"]=str(jdic["LLOQ"]).strip().replace('fmol target protein/u','fmol target protein/µ')
				jdic["ULOQ"]=str(jdic["ULOQ"]).strip().replace('fmol target protein/u','fmol target protein/µ')
				jdic["Sample LLOQ"]=str(jdic["Sample LLOQ"]).strip().replace('fmol target protein/u','fmol target protein/µ')
				templistOfMatrix=bioMatProtInfo[str(jdic["Peptide Sequence"]).strip()]
				for i in listOfMatrix:
					if i.lower() in templistOfMatrix.lower():
						tmepKey=i+str(jdic["Peptide Sequence"]).strip()
						for l in jdic["LLOQ"].split(';'):
							if i.lower() in l.lower():
								if i in temploquantinfo:
									temploquantinfo[i].append(l.split('|')[1].split('(')[0].strip())
								else:
									temploquantinfo[i]=[l.split('|')[1].split('(')[0].strip()]
						for u in jdic["ULOQ"].split(';'):
							if i.lower() in u.lower():
								if i in temploquantinfo:
									temploquantinfo[i].append(u.split('|')[1].split('(')[0].strip())
								else:
									temploquantinfo[i]=[u.split('|')[1].split('(')[0].strip()]
						for s in jdic["Sample LLOQ"].split(';'):
							if i.lower() in s.lower():
								if i in temploquantinfo:
									temploquantinfo[i].append(s.split('|')[1].split('(')[0].strip())
								else:
									temploquantinfo[i]=[s.split('|')[1].split('(')[0].strip()]
				for bk in temploquantinfo:
					tempList=[str(jdic["Peptide Sequence"]).strip(),bk]+temploquantinfo[bk]
					loquantinfo.append(tempList)

				if (str(jdic["Transitions"]).strip()) >0 and (str(jdic["Transitions"]).strip()).lower() !='na':
					transdata=str(jdic["Transitions"]).strip()
					transinfo=transdata.split(';')
					for titem in transinfo[1:]:
						subtransinfo=titem.split('|')
						if 'instrument' not in titem.lower():
							subtransinfo=[str(x) for x in subtransinfo]
							subtransinfo=[str(jdic["Peptide Sequence"]).strip()]+subtransinfo
							fragIon.append(subtransinfo[5])
							if temptransdic.has_key(subtransinfo[1].strip()):
								temptransdic[subtransinfo[1].strip()].append(subtransinfo)
							else:
								temptransdic[subtransinfo[1].strip()]=[subtransinfo]

				if (str(jdic["Gradients"]).strip()) >0 and (str(jdic["Gradients"]).strip()).lower() !='na':
					graddata=str(jdic["Gradients"]).strip()
					#graddata='Time[min]|A[%]|B[%];0.00|98.00|2.00;2.00|93.00|7.00;50.00|70.00|30.00;53.00|55.00|45.00;53.00|20.00|80.00;55.00|20.00|80.00;56.00|98.00|2.00'
					gradinfo=graddata.split(';')
					retentioninfo=str(jdic["Retention Time"]).strip().split(';')
					for i,j in enumerate(retentioninfo):
						try:
							float(j)
						except ValueError:
							del retentioninfo[i]
					analytdata=str(jdic["Analytical inofrmation"]).strip()
					#analytdata='Agilent Zorbax Eclipse Plus C18 RRHD 2.1 x 150mm 1.8um'
					gradinfoheader=[x for x in (gradinfo[0].strip()).split('|')]
					templist=[x.split('|') for x in gradinfo[1:]]
					tempRetentionTime=[]
					for ritem in range(0,len(retentioninfo)):
						if ritem != 0:
							if (float(ritem)%5.0)==0.0:
								tempRetentionTime.append(' '+retentioninfo[ritem])
							else:
								tempRetentionTime.append(retentioninfo[ritem])
						else:
							tempRetentionTime.append(retentioninfo[ritem])
					gradientlist.append([str(jdic["Peptide Sequence"]).strip(),','.join(tempRetentionTime),analytdata,'Gradient 1',templist])
					# for ritem in range(0,len(retentioninfo)):
					# 	gradientlist.append([retentioninfo[ritem],analytdata,'Gradient '+str(ritem+1),templist])
					retentioninfo=map(float,retentioninfo)
					meanRetentime=round(np.mean(retentioninfo),2)
					protinfo[str(jdic["Peptide Sequence"]).strip()]=[str(jdic["Molecular Weight"]).strip(),str(jdic["GRAVY Score"]).strip()]+protinfo[str(jdic["Peptide Sequence"]).strip()]+['<br>'.join(list(set(fragIon))),meanRetentime]
		
		if len(temptransdic)>0:
			transdic["Transitions"]=temptransdic
		es.indices.refresh(index="xxxxxxxxx-index")
		response_data ={'transdic':transdic,'foundHits':foundHits,'protinfo':protinfo,\
		'gradientlist': gradientlist, 'gradinfoheader':gradinfoheader,'loquantinfo':loquantinfo,\
		'userFastaStatus':userFastaStatus,'fastafilename':fastafilename
		}
		
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def concentration(request):
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		tempQuery=str(request.GET.get("query")).strip()
		tempQuery=tempQuery.replace('!','/')
		queryInfo=tempQuery.split('@')
		uniprotkb=queryInfo[-1]
		pepseq= queryInfo[-2]
		filterSearchTerm=[str(queryInfo[0]),str(queryInfo[1]),str(queryInfo[2]),str(queryInfo[3])]
		filterSearchType=[str('sex'),str('strain'),str('biologicalMatrix'),str('knockout')]
		concUnit=[]
		summaryConcData=[]
		es.indices.refresh(index="xxxxxxxxx-index")
		query={"query": {
			"bool": {
				"must": [
					{"match": {"UniProtKB Accession": uniprotkb}},
					{"match": {"Peptide Sequence": pepseq}},
					{"match": {"UniprotKb entry status": "Yes"}}
				]
			}
		}
		}
		res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)
		sumconclist=[]
		foundHits=res["hits"]["total"]
		protList=[]
		jfinaldata=[]
		sampleLLOQ=''
		ULOQ=''
		for hit in res['hits']['hits']:
			jdic=hit["_source"]
			jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
			if (str(jdic["Summary Concentration Range Data"]).strip()) >0 and (str(jdic["Summary Concentration Range Data"]).strip()).lower() !='na':
				sampleLLOQ=str(jdic["Sample LLOQ"]).strip()
				ULOQ=str(jdic["ULOQ"]).strip()
				jfinaldata.append(jdic)

		es.indices.refresh(index="xxxxxxxxx-index")
		jfinaldata=filterConcentration(jfinaldata,filterSearchTerm,filterSearchType)
		sampleLLOQ=sampleLLOQ.replace(' (fmol target protein/ug extracted protein)','')
		sampleLLOQ=dict([samval.split('|') for samval in sampleLLOQ.split(';')])
		ULOQ=ULOQ.replace(' (fmol target protein/ug extracted protein)','')
		ULOQ=dict([uval.split('|') for uval in ULOQ.split(';')])
		sumconcdata=str(jfinaldata[0]["Summary Concentration Range Data"]).strip()
		allconcdata=str(jfinaldata[0]["All Concentration Range Data"]).strip()
		allconcdataSampleLLOQ=str(jfinaldata[0]["All Concentration Range Data-Sample LLOQ Based"]).strip()
		sumconcdata=sumconcdata.replace('fmol target protein/u','fmol target protein/µ')
		sumconcdata=sumconcdata.replace('ug extracted protein/uL','µg extracted protein/µL')
		sumconcdata=sumconcdata.replace('ug extracted protein/mg','µg extracted protein/mg')

		allconcdata=allconcdata.replace('fmol target protein/u','fmol target protein/µ')
		allconcdata=allconcdata.replace('ug extracted protein/u','µg protein/µ')
		allconcdata=allconcdata.replace('ug extracted protein/mg','µg extracted protein/mg')

		allconcdataSampleLLOQ=allconcdataSampleLLOQ.replace('fmol target protein/u','fmol target protein/µ')
		allconcdataSampleLLOQ=allconcdataSampleLLOQ.replace('ug extracted protein/u','µg extracted protein/µ')

		sumconcinfo=sumconcdata.split(';')
		allconinfo=allconcdata.split(';')

		allconinfoSampleLLOQ=allconcdataSampleLLOQ.split(';')
		for scitem in sumconcinfo:
			scinfo =scitem.split('|')
			tempSampleLLOQ=sampleLLOQ[scinfo[2]]
			tempULOQ=ULOQ[scinfo[2]]
			stempid='|'.join(map(str,scinfo[2:5]))
			tempMatchConcList=[]
			for acitem in allconinfo:
				acinfo =acitem.split('|')
				del acinfo[3]
				atempid='|'.join(map(str,acinfo[2:5]))
				if stempid.lower() ==atempid.lower():
					concUnit.append('(' + acinfo[-2].strip().split(' (')[-1].strip())
					if float(acinfo[-3].strip().split(' ')[0].strip()) >0:
						tempMatchConcList.append(acinfo[-3].strip().split(' ')[0].strip())
			tempMatchConcData='|'.join(map(str,tempMatchConcList))

			tempMatchConcDataSampleLLOQ='NA'
			templen=1
			try:
				templen=len(filter(None,map(str,list(set(allconinfoSampleLLOQ)))))
			except UnicodeEncodeError:
				pass
			if 'NA' != ''.join(list(set(allconinfoSampleLLOQ))) and templen>0:
				tempMatchConcListSampleLLOQ=[]
				for slacitem in allconinfoSampleLLOQ:
					if slacitem.upper().strip() !='NA':
						slacinfo =slacitem.split('|')
						del slacinfo[3]
						slatempid='|'.join(map(str,slacinfo[2:5]))

						if stempid.lower() ==slatempid.lower():
							tempMatchConcListSampleLLOQ.append(slacinfo[-3].strip().split(' ')[0].strip())
				tempMatchConcDataSampleLLOQ='|'.join(map(str,tempMatchConcListSampleLLOQ))

			scinfo.append(str(jfinaldata[0]["UniProtKB Accession"]).strip())
			scinfo.append(str(jfinaldata[0]["Protein"]).strip())
			scinfo.append(str(jfinaldata[0]["Peptide Sequence"]).strip())
			scinfo.append(stempid)
			scinfo.append(tempMatchConcData)
			scinfo.append(tempMatchConcDataSampleLLOQ)
			scinfo.append(tempSampleLLOQ)
			scinfo.append(tempULOQ)
			scinfo=[scI.split('(')[0].strip()  if '(' in scI else scI for scI in scinfo]			
			sumconclist.append(scinfo)
		summaryConcData.insert(0,str(jfinaldata[0]["Peptide Sequence"]).strip())
		summaryConcData.insert(0,str(jfinaldata[0]["Protein"]).strip())
		summaryConcData.insert(0,str(jfinaldata[0]["UniProtKB Accession"]).strip())
		protList=summaryConcData
		concUnit=list(set(concUnit))
		lenOfConcData=len(sumconclist)
		concUnit='&'.join(concUnit)
		sumconclist=sorted(sumconclist,key=lambda l:l[4])
		sumconclist=sorted(sumconclist,key=lambda l:l[3])
		sumconclist=sorted(sumconclist,key=lambda l:l[2])
		response_data ={'conclist':sumconclist,'foundHits':foundHits,'protList':protList,'concUnit':concUnit,'lenOfConcData':lenOfConcData}

		return HttpResponse(json.dumps(response_data), content_type="application/json")


def pathway(request):
	'''
	This function will display result for KEGG pathways and STRING PPI.
	'''
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		if len(uniprotkb)>0:
			pathwayDic={}
			pathWayList=[]
			es.indices.refresh(index="xxxxxxxxx-index")
			query={"query": {
				"bool": {
					"must": [
						{"match": {"UniProtKB Accession": uniprotkb}},
						{"match": {"UniprotKb entry status": "Yes"}}
					]
				}
			}
			}
			res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)
			foundHits=res["hits"]["total"]
			for hit in res['hits']['hits']:
				jdic=hit["_source"]
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				mousePathway=str(jdic["Mouse Kegg Pathway"]).strip()
				humanPathway=str(jdic["Human Kegg Pathway"]).strip()
				if str(mousePathway).strip().lower() != 'na' and len(str(mousePathway).strip()) >0:
					mousePathwayInfo=mousePathway.split('|')
					for i in mousePathwayInfo:
						submousePathwayInfo=i.split(';')
						if submousePathwayInfo[1] in pathwayDic:
							pathwayDic[submousePathwayInfo[1]].append(submousePathwayInfo[0])
						else:
							pathwayDic[submousePathwayInfo[1]]=[submousePathwayInfo[0]]
				if str(humanPathway).strip().lower() != 'na' and len(str(humanPathway).strip()) >0:
					humanPathwayInfo=humanPathway.split('|')
					for i in humanPathwayInfo:
						subhumanPathwayInfo=i.split(';')
						if subhumanPathwayInfo[1] in pathwayDic:
							pathwayDic[subhumanPathwayInfo[1]].append(subhumanPathwayInfo[0])
						else:
							pathwayDic[subhumanPathwayInfo[1]]=[subhumanPathwayInfo[0]]
			es.indices.refresh(index="xxxxxxxxx-index")
			if foundHits >0 :
				if len(pathwayDic)>0:
					for pathKey in pathwayDic:
						tempList=['NA']*4
						tempList[0]=pathKey
						tempPathList=[]
						for j in pathwayDic[pathKey]:
							if 'hsa' in j:
								tempList[2]=j
								tempURL='<a target="_blank" href="https://www.kegg.jp/kegg-bin/show_pathway?'+j+'">'+j+'&nbsp;<i class="fa fa-external-link" aria-hidden="true"></i></a>'
								tempPathList.append(tempURL)
							if 'mmu' in j:
								tempList[1]=j
								tempURL='<a target="_blank" href="https://www.kegg.jp/kegg-bin/show_pathway?'+j+'">'+j+'&nbsp;<i class="fa fa-external-link" aria-hidden="true"></i></a>'
								tempPathList.append(tempURL)
						tempList[3]='<br>'.join(list(set(tempPathList)))
						pathWayList.append(tempList)
		response_data ={'pathWayList':pathWayList}

		return HttpResponse(json.dumps(response_data), content_type="application/json")

def pathwayview(request):
	'''
	This function will display result for KEGG pathways.
	'''
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("Uniprotkb")).strip()
		uniprotid=''
		uniprotname=''
		unikeggid=''
		nodesscript=[]
		edgesscript=[]
		keggurl=''
		reachable=True
		presentunidstat=False
		OSid=str(request.GET.get("organismid")).strip()
		pathwayid=str(request.GET.get("pathwayid")).strip()
		pathwayname=str(request.GET.get("pathwayname")).strip()
		homeURL=str((request.build_absolute_uri()).split('pathwayview')[0]).strip()
		uniProtGeneDic={}
		if len(uniprotkb)>0:
			pepfilegenidlistOther=[]

			es.indices.refresh(index="xxxxxxxxx-index")
			query={"query": {
				"bool": {
					"must": [
						{"match": {"UniProtKB Accession": uniprotkb}},
						{"match": {"Organism ID": OSid}},
						{"match": {"UniprotKb entry status": "Yes"}}
					]
				}
			}
			}
			res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)

			foundHits=res["hits"]["total"]
			es.indices.refresh(index="xxxxxxxxx-index")
			if foundHits >0 :
				presentunidstat=True
			if presentunidstat:
				viewquery={"query": {
					"bool": {
						"must": [
							{"match": {"Mouse Kegg Pathway Name": pathwayname}},
							{"match": {"Organism ID": OSid}},
							{"match": {"UniprotKb entry status": "Yes"}}
						]
					}
				}
				}
				resOrg = helpers.scan(client=es,scroll='2m',index="xxxxxxxxx-index", doc_type="xxxxxxxx-type",query=viewquery)
				
				jfinaldata=[]
				for i in resOrg:
					jdic=i['_source']
					jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
					pepfilegenidlistOther.append(jdic['Gene'])
					uniProtGeneDic[str(jdic['Gene']).strip().lower()]=str(jdic['UniProtKB Accession']).strip()
					jfinaldata.append(jdic)
				es.indices.refresh(index="xxxxxxxxx-index")
				pepfilegenidlistOther=list(set(pepfilegenidlistOther))

				pepfilegenidlistOther=[x.lower() for x in pepfilegenidlistOther]
				code=None
				if '-' in uniprotkb:
					code=(str(uniprotkb).split('-'))[0]
				else:
					code=str(uniprotkb.strip())

				try:
					sleep(random.randint(5,10))
					requests.get("https://www.uniprot.org/", timeout=5)
					unitxtdata = urllib.urlopen("https://www.uniprot.org/uniprot/" + code + ".txt")
					for uline in unitxtdata:
						udata=uline.strip()

						if udata.startswith('ID') and '_' in udata:
							idinfo = udata.split()
							uniprotid=idinfo[1].strip()

						if udata.startswith('GN   Name='):
							uniprotname= (((udata.split()[1]).split('='))[-1]).strip()
							if ';' in uniprotname:
								uniprotname= uniprotname.replace(';','')

						if udata.startswith('DR   KEGG'):
							unikeggid =(udata.split(';'))[1].strip()
					unitxtdata.close()

				except ConnectionError as e:
					reachable=False

		keggimagedict={}
		if len(unikeggid) >0 and reachable:
			k = KEGG()
			kegg=k.get(unikeggid)
			dict_data = k.parse(kegg)
			try:
				keggpathwayid= (dict_data['PATHWAY'].keys())
				for kegpathidietm in keggpathwayid:
					keggentryid = (unikeggid.split(':'))[1].strip()
					subkeggmapid=str(kegpathidietm)+'+'+str(keggentryid)
					if len(subkeggmapid) >0 and str(kegpathidietm).lower() == pathwayid.lower():
						keggpresentgeneIdlist=[]=[]
						notpresentkegggeneid=[]
						updatedcorddatalist=[]
						keggimagepath=''
						pathway = KGML_parser.read(REST.kegg_get(kegpathidietm, "kgml"))
						pathwayName=(str(pathway)).split('\n')[0].split(':')[1].strip()
						listUnqGene=[]
						keggOrgInitial=''
						getGeneList=[]
						pathwayGeneCoord={}
						for g in pathway.genes:
							tempGInfo=(g.name).split( )
							for tg in tempGInfo:
								geneID=tg.split(':')[1].strip()
								keggOrgInitial=tg.split(':')[0].strip()
								getGeneList.append(tg.strip())
								listUnqGene.append(geneID)
							for kgraphic in g.graphics:
								if kgraphic.type=='rectangle':
									kcoord=str(kgraphic.x)+','+str(kgraphic.y)+','+str(kgraphic.width)+','+str(kgraphic.height)
									tempGId=[x.split(':')[1].strip() for x in g.name.split(' ')]
									pathwayGeneCoord[kcoord]=tempGId
						listUnqGene=list(set(listUnqGene))
						getGeneList=list(set(getGeneList))
						geneKeggIdDics={}
						for gI in range(0,len(getGeneList),100):
							keggRESTURL='http://rest.kegg.jp/list/'+'+'.join(getGeneList[gI:gI+100])
							keggResponseREST = requests.get(keggRESTURL,verify=False)
							if not keggResponseREST.ok:
								keggResponseREST.raise_for_status()
								sys.exit()
							keggResponseBodyREST = keggResponseREST.text
							for gN in keggResponseBodyREST.split('\n')[:-1]:
								gnInfo=gN.split('\t')
								tempGeneList=[i.strip().lower() for i in gnInfo[1].split(';')[0].split(',')]
								tempKeggGeneID=gnInfo[0].split(':')[1]
								geneKeggIdDics[tempKeggGeneID]=[i.strip() for i in gnInfo[1].split(';')[0].split(',')]
								if gnInfo[0] != unikeggid:
									for tg in tempGeneList:
										if tg in pepfilegenidlistOther:
											keggpresentgeneIdlist.append(tempKeggGeneID)
						keggpresentgeneIdlist=list(set(keggpresentgeneIdlist))
						notpresentkegggeneid=set(geneKeggIdDics.keys())-set(keggpresentgeneIdlist+[unikeggid.split(':')[1]])
						notpresentkegggeneid=list(notpresentkegggeneid)
												
						presentKeggGeneIDList=set(keggpresentgeneIdlist+[unikeggid.split(':')[1]])
						presentKeggGeneIDList=list(presentKeggGeneIDList)
						presentGeneList=list(set(pepfilegenidlistOther+[uniprotname.lower()]))

						keggurl = "https://www.kegg.jp/kegg-bin/show_pathway?" + str(kegpathidietm)
						keggurl += "/%s%%20%s/" % (unikeggid.split(':')[1],'violet')
						if len(keggpresentgeneIdlist)>0:
							for pgc in keggpresentgeneIdlist:
								keggurl += "/%s%%20%s/" % (pgc,'maroon')
						if len(notpresentkegggeneid)>0:
							for ngc in notpresentkegggeneid:
								keggurl += "/%s%%20%s/" % (ngc,'#ffffff')

						try:
							sleep(random.randint(5,10))
							requests.get("https://www.kegg.jp/", timeout=1)
							kegghttp=urllib3.PoolManager()
							urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
							keggurlreq = kegghttp.request('GET',keggurl)
							keggurldata =keggurlreq.data
							keggurldata=keggurldata.decode('utf-8')
							keggurldata=keggurldata.replace('\t','')
							for kline in keggurldata.split('\n'):
								kline=kline.lstrip()
								try:
									if '<area' in kline.lower() and 'href='.lower() in kline.lower() and 'title=' in kline.lower() and 'shape=' in kline.lower():
										kline=kline.replace('"','')
										kshape=kline.split('shape=')[1].split(' ')[0]
										kcoords=kline.split('coords=')[1].split(' ')[0]
										khref=''
										ktitle=kline.split('title=')[1].replace('/>','').replace('class=module','')
										ktitleData=ktitle.lstrip()
										if kshape=='rect':
											ktitleInfo=ktitleData.split(',')
											ktitleInfoID=[k.strip().split(' ')[0] for k in ktitleInfo]
											commonKeggGeneIDList=list(set(ktitleInfoID)&set(presentKeggGeneIDList))
											if len(commonKeggGeneIDList)>0:
												tempTitle=[]
												commonKeggGeneList=[]
												for ki in ktitleInfoID:
													if ki in geneKeggIdDics:
														keggGeneList=geneKeggIdDics[ki]
														tempcommonKeggGeneList=[str(cg) for cg in keggGeneList if cg.lower() in presentGeneList]
														tempTitle.extend([ki+' ('+str(x)+')' for x in tempcommonKeggGeneList])
														commonKeggGeneList.extend(tempcommonKeggGeneList)
													
												ktitleData=','.join(tempTitle)
												khref='/results/?gene='+str('|'.join(commonKeggGeneList))+'&Organismid='+OSid
												updatedcorddatalist.append([kshape,kcoords,str(khref),ktitleData])
									if kline.startswith('<img src="/tmp/mark_pathway'):
										kinfo=kline.split('name=')
										keggimagepath=(kinfo[0].split('"'))[1].strip()
								except UnicodeDecodeError:
									pass
						except ConnectionError as e:
							reachable=False
						except urllib3.exceptions.MaxRetryError:
							reachable=False
						keggimagedict[subkeggmapid]=[keggimagepath,pathwayName,updatedcorddatalist]

			except KeyError:
				pass
		response_data ={
					'uniprotid':uniprotid,'uniprotname':uniprotname,
					'keggimagedict':keggimagedict,'keggurl':keggurl,
					'reachable':reachable
				}

		return HttpResponse(json.dumps(response_data), content_type="application/json")

def goterm(request):
	'''
	This function will display result for Go term.
	'''
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		contextgoterm =[]
		reachable=True
		jvenndataseries=[]
		response_data = {}
		if len(uniprotkb)>0:
			uniprotkblist=[]
			code=None
			gene=None
			protname=None
			goDic={}
			mouseUniData=[]
			humanUniData=[]
			goStatBioP=[]
			goStatMolF=[]
			goStatCellC=[]
			es.indices.refresh(index="xxxxxxxxx-index")
			#build elasticsearch query based provided uniprotkb acc
			query={"query": {
				"bool": {
					"must": [
						{"match": {"UniProtKB Accession": uniprotkb}},
						{"match": {"UniprotKb entry status": "Yes"}}
					]
				}
			}
			}
			res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)

			foundHits=res["hits"]["total"]
			for hit in res['hits']['hits']:
				jdic=hit["_source"]
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				mouseGo=str(jdic["Mouse Go"]).strip()
				humanGo=str(jdic["Human Go"]).strip()
				if str(mouseGo).strip().lower() != 'na' and len(str(mouseGo).strip()) >0:
					mouseGoInfo=mouseGo.split('|')
					for i in mouseGoInfo:
						submouseGoInfo=i.split(';')
						if submouseGoInfo[1] in goDic:
							goDic[submouseGoInfo[1]].append([submouseGoInfo[0],submouseGoInfo[2],'Mouse'])
						else:
							goDic[submouseGoInfo[1]]=[[submouseGoInfo[0],submouseGoInfo[2],'Mouse']]
				if str(humanGo).strip().lower() != 'na' and len(str(humanGo).strip()) >0:
					humanGoInfo=mouseGo.split('|')
					for i in humanGoInfo:
						subhumanGoInfo=i.split(';')
						if subhumanGoInfo[1] in goDic:
							goDic[subhumanGoInfo[1]].append([subhumanGoInfo[0],subhumanGoInfo[2],'Human'])
						else:
							goDic[subhumanGoInfo[1]]=[[subhumanGoInfo[0],subhumanGoInfo[2],'Human']]
			es.indices.refresh(index="xxxxxxxxx-index")

			if foundHits >0:
				if len(goDic)>0:
					for goKey in goDic:
						tempList=['NA']*4
						tempList[0]=goKey
						tempList[1]=goDic[goKey][0][0]
						tempList[2]=goDic[goKey][0][1]
						orgList=[]
						for j in goDic[goKey]:
							orgList.append(j[2])
						tempList[3]='<br>'.join(list(set(orgList)))
						if tempList[2].lower()=='biological process':
							goStatBioP.append(tempList[0])
						if tempList[2].lower()=='molecular function':
							goStatMolF.append(tempList[0])
						if tempList[2].lower()=='cellular component':
							goStatCellC.append(tempList[0])
						contextgoterm.append(tempList)
		goStat=[]
		if len(goStatBioP)>0:
			goStat.append('Number of Biological Process GO Aspects:'+str(len(set(goStatBioP))))
		if len(goStatMolF)>0:
			goStat.append('Number of Molecular Function GO Aspects:'+str(len(set(goStatMolF))))
		if len(goStatCellC)>0:
			goStat.append('Number of Cellular Component GO Aspects:'+str(len(set(goStatCellC))))

		response_data ={'foundHits': foundHits,'contextgoterminfo': contextgoterm,'goStat':'<br>'.join(goStat)}

		return HttpResponse(json.dumps(response_data), content_type="application/json")

def geneExp(request):
	'''
	This function will display result for Gene Expression.
	'''
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		gene=None
		protname=None
		geneExpData=None
		geneExplist=[]
		if len(uniprotkb)>0:
			es.indices.refresh(index="xxxxxxxxx-index")
			#build elasticsearch query based provided uniprotkb acc
			query={"query": {
				"bool": {
					"must": [
						{"match": {"UniProtKB Accession": uniprotkb}},
						{"match": {"UniprotKb entry status": "Yes"}}
					]
				}
			}
			}
			res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)

			foundHits=res["hits"]["total"]
			for hit in res['hits']['hits']:
				jdic=hit["_source"]
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				gene=str(jdic["Gene"]).strip()
				protname=str(jdic["Protein"]).strip()
				geneExpData=str(jdic["Gene Expression Data"]).strip()
			es.indices.refresh(index="xxxxxxxxx-index")

			if foundHits >0:
				tempgeneExplist=geneExpData.split(';')[1:]
				tempgeneExplist.sort(key=lambda g: g.upper())
				for i in tempgeneExplist:
					tempListExp=[uniprotkb,protname,i.split('|')[0],i.split('|')[1]]
					geneExplist.append(tempListExp)
		protList=[uniprotkb,protname]
		response_data ={'geneExplist':geneExplist,'foundHits':foundHits,'protList':protList,'lenOfGeneExpData':len(geneExplist)}

		return HttpResponse(json.dumps(response_data), content_type="application/json")


class SwaggerRestAPIView(APIView):
	'''
	Creation of Manual schema for REST API
	'''
	schema=ManualSchema(fields=[
		coreapi.Field(
			name="UniProtKB accession",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:O89020'
			),
		coreapi.Field(
			name="Protein",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Afamin'
			),
		coreapi.Field(
			name="Gene",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Afm'
			),
		coreapi.Field(
			name="Peptide sequence",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:AAPITQYLK'
			),
		coreapi.Field(
			name="Panel",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Panel-1'
			),
		coreapi.Field(
			name="Strain",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:NODSCID'
			),
		coreapi.Field(
			name="Mutant",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Wild'
			),
		coreapi.Field(
			name="Sex",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Male'
			),
		coreapi.Field(
			name="Biological matrix",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Plasma'
			),
		coreapi.Field(
			name="Subcellular localization",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Secreted'
			),
		coreapi.Field(
			name="Molecular pathway(s)",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Complement and coagulation cascades'
			),
		coreapi.Field(
			name="Involvement in disease",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Adiponectin deficiency(ADPND)'
			),
		coreapi.Field(
			name="GO ID",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:GO:0008015'
			),
		coreapi.Field(
			name="GO Term",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:blood circulation'
			),
		coreapi.Field(
			name="GO Aspects",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:Biological Process'
			),
		coreapi.Field(
			name="Drug associations ID",
			required=False,
			location="query",
			schema=coreschema.String(),
			description='Example:DB05202'
			)
		])
	def get(self, request):
		"""
		This function is searching results, based on given multi search parameters
		in database.
		"""
		ip = get_ip(request, right_most_proxy=True)
		IpAddressInformation.objects.create(ip_address=ip)

		useruniprotkb =""
		userprotein =""
		usergeneid =""
		userorg=""
		userorgid=""
		usersubcell =""
		userpepseq =""
		userkegg =""
		userdis =""
		usergoid =""
		usergotn =""
		usergot=""
		userdrug=""
		userstrain=""
		userknockout=""
		userpanel=""
		usersex=""
		userbioMatrix=""
		filterSearchTerm=[]
		filterSearchType=[]
		filtersearchStatus=0
		try:
			useruniprotkb = request.GET["UniProtKB accession"]
		except MultiValueDictKeyError:
			pass
		if '|' in useruniprotkb:
			useruniprotkb=(useruniprotkb.strip()).split('|')
		else:
			useruniprotkb=(useruniprotkb.strip()).split('\n')
		useruniprotkb=[(item.strip()).lower() for item in useruniprotkb]
		useruniprotkb=map(str, useruniprotkb)
		useruniprotkb=filter(None, useruniprotkb)

		try:
			userprotein = request.GET["Protein"]
		except MultiValueDictKeyError:
			pass
		if '|' in userprotein:
			userprotein=(userprotein.strip()).split('|')
		else:
			userprotein=(userprotein.strip()).split('\\n')
		userprotein=[(item.strip()).lower() for item in userprotein]
		userprotein=map(str, userprotein)
		userprotein=filter(None, userprotein)

		try:
			usergeneid = request.GET["Gene"]
		except MultiValueDictKeyError:
			pass
		if '|' in usergeneid:
			usergeneid=(usergeneid.strip()).split('|')
		else:
			usergeneid=(usergeneid.strip()).split('\\n')
		usergeneid=[(item.strip()).lower() for item in usergeneid]
		usergeneid=map(str, usergeneid)
		usergeneid=filter(None, usergeneid)

		try:
			userorg = request.GET["Organism"]
		except MultiValueDictKeyError:
			pass
		if '|' in userorg:
			userorg=(userorg.strip()).split('|')
		else:
			userorg=(userorg.strip()).split('\\n')
		userorg=[(item.strip()).lower() for item in userorg]
		userorg=map(str, userorg)
		userorg=filter(None, userorg)

		try:
			userorgid = request.GET["Organism ID"]
		except MultiValueDictKeyError:
			pass
		if '|' in userorgid:
			userorgid=(userorgid.strip()).split('|')
		else:
			userorgid=(userorgid.strip()).split('\\n')
		userorgid=[(item.strip()).lower() for item in userorgid]
		userorgid=map(str, userorgid)
		userorgid=filter(None, userorgid)

		try:
			usersubcell = request.GET["Subcellular localization"]
		except MultiValueDictKeyError:
			pass
		if '|' in usersubcell:
			usersubcell=(usersubcell.strip()).split('|')
		else:
			usersubcell=(usersubcell.strip()).split('\\n')
		usersubcell=[(item.strip()).lower() for item in usersubcell]
		usersubcell=map(str, usersubcell)
		usersubcell=filter(None, usersubcell)

		try:
			userpepseq = request.GET["Peptide sequence"]
		except MultiValueDictKeyError:
			pass
		if '|' in userpepseq:
			userpepseq=(userpepseq.strip()).split('|')
		else:
			userpepseq=(userpepseq.strip()).split('\\n')
		userpepseq=[(item.strip()).lower() for item in userpepseq]
		userpepseq=map(str, userpepseq)
		userpepseq=filter(None, userpepseq)

		try:
			userkegg = request.GET["Molecular pathway(s)"]
		except MultiValueDictKeyError:
			pass
		if '|' in userkegg:
			userkegg=(userkegg.strip()).split('|')
		else:
			userkegg=(userkegg.strip()).split('\\n')
		userkegg=[(item.strip()).lower() for item in userkegg]
		userkegg=map(str, userkegg)
		userkegg=filter(None, userkegg)

		try:
			userdis = request.GET["Involvement in disease"]
		except MultiValueDictKeyError:
			pass
		if '|' in userdis:
			userdis=(userdis.strip()).split('|')
		else:
			userdis=(userdis.strip()).split('\\n')
		userdis=[(item.strip()).lower() for item in userdis]
		userdis=map(str, userdis)
		userdis=filter(None, userdis)

		try:
			usergoid = request.GET["GO ID"]
		except MultiValueDictKeyError:
			pass
		if '|' in usergoid:
			usergoid=(usergoid.strip()).split('|')
		else:
			usergoid=(usergoid.strip()).split('\\n')
		usergoid=[(item.strip()).lower() for item in usergoid]
		usergoid=map(str, usergoid)
		usergoid=filter(None, usergoid)

		try:
			usergotn = request.GET["GO Term"]
		except MultiValueDictKeyError:
			pass
		if '|' in usergotn:
			usergotn=(usergotn.strip()).split('|')
		else:
			usergotn=(usergotn.strip()).split('\\n')
		usergotn=[(item.strip()).lower() for item in usergotn]
		usergotn=map(str, usergotn)
		usergotn=filter(None, usergotn)

		try:
			usergot = request.GET["GO Aspects"]
		except MultiValueDictKeyError:
			pass
		if '|' in usergot:
			usergot=(usergot.strip()).split('|')
		else:
			usergot=(usergot.strip()).split('\\n')
		usergot=[(item.strip()).lower() for item in usergot]
		usergot=map(str, usergot)
		usergot=filter(None, usergot)

		try:
			userdrug = request.GET["Drug associations ID"]
		except MultiValueDictKeyError:
			pass
		if '|' in userdrug:
			userdrug=(userdrug.strip()).split('|')
		else:
			userdrug=(userdrug.strip()).split('\\n')
		userdrug=[(item.strip()).lower() for item in userdrug]
		userdrug=map(str, userdrug)
		userdrug=filter(None, userdrug)

		try:
			userstrain = request.GET["Strain"]
		except MultiValueDictKeyError:
			pass
		if '|' in userstrain:
			userstrain=(userstrain.strip()).split('|')
		else:
			userstrain=(userstrain.strip()).split('\\n')
		userstrain=[(item.strip()).lower() for item in userstrain]
		userstrain=map(str, userstrain)
		userstrain=filter(None, userstrain)

		try:
			userknockout = request.GET["Mutant"]
		except MultiValueDictKeyError:
			pass
		if '|' in userknockout:
			userknockout=(userknockout.strip()).split('|')
		else:
			userknockout=(userknockout.strip()).split('\\n')
		userknockout=[(item.strip()).lower() for item in userknockout]
		userknockout=map(str, userknockout)
		userknockout=filter(None, userknockout)

		try:
			userpanel = request.GET["Panel"]
		except MultiValueDictKeyError:
			pass
		if '|' in userpanel:
			userpanel=(userpanel.strip()).split('|')
		else:
			userpanel=(userpanel.strip()).split('\\n')
		userpanel=[(item.strip()).lower() for item in userpanel]
		userpanel=map(str, userpanel)
		userpanel=filter(None, userpanel)

		try:
			usersex = request.GET["Sex"]
		except MultiValueDictKeyError:
			pass
		if '|' in usersex:
			usersex=(usersex.strip()).split('|')
		else:
			usersex=(usersex.strip()).split('\\n')
		usersex=[(item.strip()).lower() for item in usersex]
		usersex=map(str, usersex)
		usersex=filter(None, usersex)

		try:
			userbioMatrix = request.GET["Biological matrix"]
		except MultiValueDictKeyError:
			pass
		if '|' in userbioMatrix:
			userbioMatrix=(userbioMatrix.strip()).split('|')
		else:
			userbioMatrix=(userbioMatrix.strip()).split('\\n')
		userbioMatrix=[(item.strip()).lower() for item in userbioMatrix]
		userbioMatrix=map(str, userbioMatrix)
		userbioMatrix=filter(None, userbioMatrix)

		spquerylist =[]
		searchtermlist=[]
		if len(useruniprotkb) >0:
			shouldlist=[]
			for x in useruniprotkb:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["UniProtKB Accession.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userprotein)> 0:
			shouldlist=[]
			for x in userprotein:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Protein.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(usergeneid) >0:
			shouldlist=[]
			for x in usergeneid:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Gene.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userorg) > 0:
			shouldlist=[]
			for x in userorg:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Organism.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userorgid) > 0:
			shouldlist=[]
			for x in userorgid:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Organism ID.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(usersubcell) >0:
			shouldlist=[]
			for x in usersubcell:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["SubCellular.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userpepseq) >0:
			shouldlist=[]
			for x in userpepseq:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Peptide Sequence.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userkegg) >0:
			shouldlist=[]
			for x in userkegg:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Mouse Kegg Pathway Name.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userdis) >0:
			shouldlist=[]
			for x in userdis:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Human Disease Name.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(usergoid) >0:
			sdict={}
			sdict["Mouse Go ID.ngram"]=[i.split(' ')[0] for i in usergoid]
			tdict={}
			tdict["terms"]=sdict
			searchtermlist.append(tdict)
			shouldlist=[]
			for x in usergoid:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Mouse Go ID.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(usergotn) >0:
			shouldlist=[]
			for x in usergotn:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Mouse Go Name.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(usergot) > 0:
			shouldlist=[]
			for x in usergot:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Mouse Go Term.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if len(userdrug) > 0:
			shouldlist=[]
			for x in userdrug:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Human Drug Bank.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)

		if len(userstrain) > 0:
			filterSearchType.append('strain')
			filterSearchTerm.append('|'.join(userstrain))
			shouldlist=[]
			for x in userstrain:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Strain.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)

		if len(userknockout) > 0:
			shouldlist=[]
			for x in userknockout:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Knockout.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)

		if len(userpanel) > 0:
			shouldlist=[]
			for x in userpanel:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Panel.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)

		if len(usersex) > 0:
			filterSearchType.append('sex')
			filterSearchTerm.append('|'.join(usersex))
			shouldlist=[]
			for x in usersex:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Sex.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)

		if len(userbioMatrix) > 0:
			filterSearchType.append('biologicalMatrix')
			filterSearchTerm.append('|'.join(userbioMatrix))
			shouldlist=[]
			for x in userbioMatrix:
				tempquery={
							"multi_match":{
								"query":x.strip(),
								"type":"best_fields",
								"fields":["Biological Matrix.ngram"],
								"minimum_should_match":"100%"
							}
						}
				shouldlist.append(tempquery)
			booldic={}
			booldic["bool"]={"should":shouldlist,"minimum_should_match": 1}
			searchtermlist.append(booldic)
		if not searchtermlist or len(searchtermlist)==0:
			return Response({"error": "No information passed!"}, status=status.HTTP_400_BAD_REQUEST)

		es.indices.refresh(index="xxxxxxxxx-index")

		query={
			"query": {
				"bool": {
					"must":searchtermlist
				}
			}
		}

		try:
			if filterSearchType.index('sex') >=0:
				filtersearchStatus=1
		except ValueError:
			pass
		try:
			if filterSearchType.index('strain') >=0:
				filtersearchStatus=1
		except ValueError:
			pass
		try:
			if filterSearchType.index('biologicalMatrix') >=0:
				filtersearchStatus=1
		except ValueError:
			pass
		try:
			if filterSearchType.index('panel') >=0:
				filtersearchStatus=1
		except ValueError:
			pass
		try:
			if filterSearchType.index('knockout') >=0:
				filtersearchStatus=1
		except ValueError:
			pass
		jfinaldata=[]
		res=helpers.scan(client=es,scroll='2m',index="xxxxxxxxx-index", doc_type="xxxxxxxx-type",query=query,request_timeout=30)
		jfinaldata=[]
		uniprotpepinfo={}
		for i in res:
			jdic=i['_source']
			jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
			panelFilter=True
			if len(userpanel) >0:
				for q in userpanel:
					if q.lower() in (jdic['Panel'].lower()).split(';'):
						panelFilter=True
						break
				else:
					panelFilter=False
				#if jdic["Retention Time"].lower() =='na' or jdic["Gradients"].lower() =='na':
			if jdic["UniprotKb entry status"] =="Yes" and panelFilter:
				if uniprotpepinfo.has_key(jdic["UniProtKB Accession"]) and panelFilter:
					uniprotpepinfo[jdic["UniProtKB Accession"]].append(jdic["Peptide Sequence"])
				else:
					uniprotpepinfo[jdic["UniProtKB Accession"]]=[jdic["Peptide Sequence"]]

				if jdic["Human UniProtKB Accession"].lower() !='na' and jdic["Present in human ortholog"].lower() =='no':
					jdic["Available assays in human ortholog"]='http://mrmassaydb.proteincentre.com/search/hyperlink/?UniProtKB Accession='+jdic["Human UniProtKB Accession"]
				else:
					jdic["Available assays in human ortholog"]='NA'

				#if jdic["Retention Time"].lower() =='na' or jdic["Gradients"].lower() =='na':
				if jdic["Retention Time"].lower() =='na':
					jdic["Summary Concentration Range Data"]='NA'
					jdic["Concentration View"]='NA'
				if filtersearchStatus==0:

					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/u','µg protein/µ')
					jdic["Summary Concentration Range Data"]=jdic["Summary Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/u','µg protein/µ')
					jdic["All Concentration Range Data"]=jdic["All Concentration Range Data"].replace('ug protein/mg','µg protein/mg')

					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/u','µg protein/µ')
					jdic["All Concentration Range Data-Sample LLOQ Based"]=jdic["All Concentration Range Data-Sample LLOQ Based"].replace('ug protein/mg','µg protein/mg')

					jdic["Concentration View"]=jdic["Concentration View"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Concentration Range"]=jdic["Concentration Range"].replace('fmol target protein/u','fmol target protein/µ')

					jdic["LLOQ"]=jdic["LLOQ"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["ULOQ"]=jdic["ULOQ"].replace('fmol target protein/u','fmol target protein/µ')
					jdic["Sample LLOQ"]=jdic["Sample LLOQ"].replace('fmol target protein/uL','fmol target protein/µ')

					if jdic["Unique in protein"].upper() =='NA':
						jdic["Unique in protein"]=jdic["Unique in protein"].replace('NA','No')
					if jdic["Present in isoforms"].upper() =='NA':
						jdic["Present in isoforms"]=jdic["Present in isoforms"].replace('NA','No')
				jfinaldata.append(jdic)

		foundHits=len(jfinaldata)
		if foundHits <= 0:
			return Response({"error": "No information found!"}, status=status.HTTP_400_BAD_REQUEST)
		es.indices.refresh(index="xxxxxxxxx-index")
		if filtersearchStatus>0:
		 jfinaldata,filteredUniProtIDs=filterSearch(jfinaldata,filterSearchTerm,filterSearchType)

		foundHits=len(jfinaldata)
		if foundHits <= 0:
			return Response({"error": "No information found!"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			jfinaldata=updateDataToDownload(jfinaldata)
			jsonfilename=str(uuid.uuid4())+'_restapi_search.json'
			jsonfilepath=os.path.join(settings.BASE_DIR, 'resultFile', 'jsonData','resultJson', 'restapisearch', jsonfilename)
			jsonfileoutput= open(jsonfilepath,'w')
			json.dump(jfinaldata,jsonfileoutput)
			jsonfileoutput.close()

			df=pd.read_json(jsonfilepath)
			df.rename(columns ={'UniProtKB Accession':'Mouse UniProtKB accession','Protein':'Mouse Protein name',\
					'Gene':'Mouse Gene','Present in isoforms':'Peptide present in isoforms',\
					'Peptide Sequence':'Peptide sequence','Knockout':'Mutant',\
					'Unique in protein':'Peptide unique in proteome','Human UniProtKB Accession': \
					'UniProtKB accession of human ortholog','Human ProteinName': 'Human ortholog',\
					'Peptide ID':'Assay ID','Present in human isoforms':'Peptide present in human isoforms',\
					'Unique in human protein':'Peptide unique in human protein',\
					'SubCellular':'Subcellular localization','Mouse Kegg Pathway':'Molecular pathway(s) Mouse',\
					'Present in human ortholog':'Peptide present in human ortholog',\
					'Human Kegg Pathway':'Molecular pathway(s) Human','Human UniProt DiseaseData':'Involvement in disease-Human(UniProt)',\
					'Human DisGen DiseaseData':'Involvement in disease-Human(DisGeNET)','Human Drug Bank':\
					'Drug associations-Human','CZE Purity':'CZE','AAA Concentration':'AAA',\
					'Mouse Go':'GO Mouse','Human Go':'GO Human','LLOQ':'Assay LLOQ','ULOQ':'Assay ULOQ'}, inplace =True)
			#df=df.loc[:,restApiColname]
			updatedresult=df.to_json(orient='records')
			updatedresult=json.loads(updatedresult)
			updatedUniInfo=pepbasedInfoRESTAPI(updatedresult,uniprotpepinfo)

		return Response(updatedUniInfo)

def peptideUniqueness(request):
	"""
	This function is searching results, based on given multi search parameters
	in database.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		response_data={}
		useruniprotkb=str(request.GET.get("Uniprotkb")).strip()
		userpepseq=str(request.GET.get("pepseq")).strip()
		userfastafilename=str(request.GET.get("fastafile")).strip()
		userpepseq=userpepseq.upper()
		reachable=True
		valid=False
		pepjsondatalist=[]
		es.indices.refresh(index="xxxxxxxxx-index")
		query={"query": {
			"bool": {
				"must": [
					{"match": {"UniProtKB Accession": useruniprotkb}},
					{"match": {"Peptide Sequence": userpepseq}}				]
			}
		}
		}
		res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)
		foundHits=res["hits"]["total"]
		originalpepunqstatus="Not unique"
		uniprotkbstatus="NA"
		for hit in res['hits']['hits']:
			jdic=hit["_source"]
			jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
			uniprotkbstatus=str(jdic["UniprotKb entry status"]).strip()
			if jdic["Unique in protein"].upper() =='NA':
				jdic["Unique in protein"]=jdic["Unique in protein"].replace('NA','No')
			if jdic["Present in isoforms"].upper() =='NA':
				jdic["Present in isoforms"]=jdic["Present in isoforms"].replace('NA','No')
			if len(str(jdic["Unique in protein"]).strip())>0:
				originalpepunqstatus=str(jdic["Unique in protein"]).strip()
		es.indices.refresh(index="xxxxxxxxx-index")
		fastafilepath=os.path.join(settings.BASE_DIR, 'resultFile', 'fastaFile', userfastafilename+'.fasta')
		if os.path.exists(fastafilepath) and foundHits>0:
			proseq=''
			try:
				sleep(random.randint(5,10))
				requests.get("https://www.uniprot.org/", timeout=1)
				unidatafasta = urllib.urlopen("https://www.uniprot.org/uniprot/" + useruniprotkb + ".fasta")
				for i in range(1):
					header=unidatafasta.next()
					if '>' in header[0]:
						valid=True
				if valid:
					for line in unidatafasta:
						proseq+=line.strip()
				unidatafasta.close()
			except ConnectionError as e:
				reachable=False

			if reachable:
				fastaseq=[]
				contextpepuser=[]
				peptide_pattern = re.compile(userpepseq,re.IGNORECASE)
				
				for match in re.finditer(peptide_pattern,proseq):
					matchpdbseqpos=range(int(match.start()),match.end())
					proseq=proseq.upper()
					tseq=proseq
					seqlen=len(proseq)
					proseqlist=list(proseq)
					for y in range(0,len(proseqlist)):
						if y in matchpdbseqpos:
							proseqlist[y]='<b><font color="red">'+proseqlist[y]+'</font></b>'
						if y%60 ==0 and y !=0:
							proseqlist[y]=proseqlist[y]+'<br/>'
					proseq="".join(proseqlist)
					contextpepuser.append(['<a target="_blank" href="https://www.uniprot.org/uniprot/'+useruniprotkb+'">'+useruniprotkb+'</a>',(int(match.start())+1),match.end(),matchpdbseqpos,tseq,seqlen,proseq,'MouseQuaPro'])

				for useq_record in SeqIO.parse(fastafilepath, 'fasta'):
					seqheader = useq_record.id
					sequniID = seqheader.split(' ')[0]
					sequniID=sequniID.replace('>','')
					tempseqs = str(useq_record.seq).strip()
					fastaseq.append(tempseqs.upper())
					for fmatch in re.finditer(peptide_pattern,tempseqs.upper()):
						fmatchpdbseqpos=range(int(fmatch.start()),fmatch.end())
						tempseqs=tempseqs.upper()
						tseq=tempseqs
						seqlen=len(tempseqs)
						tempseqslist=list(tempseqs)
						for y in range(0,len(tempseqslist)):
							if y in fmatchpdbseqpos:
								tempseqslist[y]='<b><font color="red">'+tempseqslist[y]+'</font></b>'
							if y%60 ==0 and y !=0:
								tempseqslist[y]=tempseqslist[y]+'<br/>'
						tempseqs="".join(tempseqslist)
						contextpepuser.append([sequniID,(int(fmatch.start())+1),fmatch.end(),fmatchpdbseqpos,tseq,seqlen,tempseqs,'User data'])

				useruniqstatus=''
				unqfastaseq=list(set(fastaseq))
				indices = [i for i, s in enumerate(fastaseq) if userpepseq.upper() in s]
				if len(indices)==0:
					useruniqstatus ="Not present"
				elif len(indices) > 1:
					useruniqstatus="Present but not unique"
				else:
					useruniqstatus="Present and unique"
				for x in contextpepuser:
					tempdatadic={}
					tempdatadic["proteinID"]=x[0]
					tempdatadic["peptideSequence"]=userpepseq
					tempdatadic["start"]=str(x[1])
					tempdatadic["end"]=str(x[2])
					tempdatadic["seqlen"]=str(x[-3])
					tempdatadic["seq"]=str(x[-4])
					if 'target' in x[0]:
						tempdatadic["peptideuniqueinprotein"]=originalpepunqstatus
					else:
						tempdatadic["peptideuniqueinprotein"]=useruniqstatus
					tempdatadic["datasource"]=str(x[-1])
					tempdatadic["highlightedpepseq"]=str(x[-2])
					pepjsondatalist.append(tempdatadic)
				pepunqdata={"data":pepjsondatalist}
				response_data={'pepunqdata':json.dumps(pepunqdata),'reachable':reachable}
			else:
				response_data={'reachable':reachable}
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def contact(request):
	"""
	This is contact form where 
	Admin will recieve email from contact page.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		contactdetails=json.loads(request.GET.get('contactdetails').strip())
		form_email = contactdetails["contactFormEmail"].strip() # get email address
		form_full_name = contactdetails["contactFormName"].strip() # get name
		form_message = contactdetails["contactFormMessage"].strip() # get message
		form_userWantForward = contactdetails["contactFormCopy"] # user Want to Forward this email
		subject='Site contact form for QMPKB'
		from_email=settings.EMAIL_HOST_USER
		to_email=[from_email, 'Pallab@proteincentre.com','Yassene@proteincentre.com','bioinformatics@proteincentre.com']
		contact_message="%s: %s via %s"%(
			form_full_name,
			form_message,
			form_email)
		send_mail(subject,contact_message,from_email,to_email,fail_silently=True) # sent email

		#foward user the same email
		if form_userWantForward:
			contact_message_user="%s: %s via %s"%(
				form_full_name,
				form_message,
				form_email)
			send_mail(subject,contact_message_user,from_email,[form_email],fail_silently=True) # sent email

		return HttpResponse({}, content_type="application/json")


def foldChange(request):
	if request.method=='GET':
		dropDownTerm=request.GET.get("dropDownTerm")# user input for searching result
		dropDownTerm= str(dropDownTerm).strip()
		checkBoxTerm=request.GET.get("checkBoxTerm")# user input for searching result
		checkBoxTerm= str(checkBoxTerm).strip()
		resultfileName=request.GET.get("fileName")# user input for searching result
		resultfileName= str(resultfileName).strip()
		queryDataDic=json.loads(request.GET.get("queryData"))# user input for searching result
		
		homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
		matrixFilePath= os.path.join(homedir, 'src/qmpkbmotherfile', 'mouseQuaProMatrix.tsv')
		resultfilePath=os.path.join(homedir, 'src/','/'.join(resultfileName.split('/')[1:]))


		foldChangeStatus=True
		response_data={}
		log2foldChangeData=[]
		foldchangePvalue=[]
		flagData=[]
		foldPairLegend=[]
		defaultDropDownMenus=['Biological Matrix','Sex','Strain']
		dropdownQuery=dropDownTerm
		defaultDropDownMenus.remove(dropdownQuery)
		checkedQuery=checkBoxTerm.split(',')
		resultDF=pd.read_csv(resultfilePath)
		proteinData=list(resultDF['Peptide sequence'] + '_' + resultDF['Mouse UniProtKB accession'])
		df=pd.read_csv(matrixFilePath,delimiter='\t', na_filter=False)
		columns=list(df.columns)[:3]+proteinData
		del queryDataDic[dropdownQuery]
		querkeys=queryDataDic.keys()

		df=df.loc[(df[querkeys[0]].isin(queryDataDic[querkeys[0]])) & (df[querkeys[1]].isin(queryDataDic[querkeys[1]]))]
		df=df[columns]
		df.drop(defaultDropDownMenus, axis=1, inplace=True)
		df = df[(df[dropdownQuery] == checkedQuery[0]) | (df[dropdownQuery] == checkedQuery[1])]
		for protID in proteinData:
			subDF=df[[dropdownQuery,protID]]
			pair1=subDF[protID][(subDF[dropdownQuery]==checkedQuery[0]) & (subDF[protID].astype(str) !='nan')]
			pair1=list(pair1.astype(float))
			pair2=subDF[protID][(subDF[dropdownQuery]==checkedQuery[1]) & (subDF[protID].astype(str) !='nan')]
			pair2=list(pair2.astype(float))
			if len(pair1)>0 and len(pair2)>0:
				meanConcPair1=np.mean(pair1)
				meanConcPair2=np.mean(pair2)
				log2foldChangeData.append(math.log(abs(meanConcPair1/meanConcPair2),2))
				pair1=[math.log(v1) for v1 in pair1]
				pair2=[math.log(v2) for v2 in pair2]
				if len(pair1)==1 or len(pair2)==1:
					flagData.append('Yes')
					foldchangePvalue.append(1)
				else:
					try:
						stat, pval = mannwhitneyu(pair1, pair2)
						foldchangePvalue.append(pval)
						flagData.append('No')
					except ValueError:
						flagData.append('Yes')
						foldchangePvalue.append(1)
				foldPairLegend.append(protID)

		#foldchangePvalue_adjust =statsR.p_adjust(FloatVector(foldchangePvalue), method = 'BH')
		foldchangePvalue_adjust=(p_adjust_bh(foldchangePvalue)).tolist()
		foldchangePvalue_adjust=[-math.log10(p) for p in foldchangePvalue_adjust]
		indicesYes = [i for i, x in enumerate(flagData) if x == "Yes"]
		indicesNo = [i for i, x in enumerate(flagData) if x == "No"]
		try:
			maxAbsValLog2=max(list(map(abs,log2foldChangeData)))
			maxValPval=max(foldchangePvalue_adjust)
			hLine=abs(math.log10(0.05))
			if hLine > maxValPval:
				maxValPval=hLine
			flaggedData={
				'Yes':[list(np.array(log2foldChangeData)[indicesYes]),list(np.array(foldchangePvalue_adjust)[indicesYes]),list(np.array(foldPairLegend)[indicesYes])],
				'No':[list(np.array(log2foldChangeData)[indicesNo]),list(np.array(foldchangePvalue_adjust)[indicesNo]),list(np.array(foldPairLegend)[indicesNo])]
			}

			response_data ={
				'log2FoldData':flaggedData,
				'maxAbsValLog2':maxAbsValLog2,
				'hLine':hLine,
				'maxValPval':maxValPval,
				'foldChangeStatus':foldChangeStatus

			}

		except ValueError:
			foldChangeStatus=False
			response_data ={
				'log2FoldData':{},
				'maxAbsValLog2':0,
				'hLine':0,
				'maxValPval':0,
				'foldChangeStatus':foldChangeStatus

			}
		return HttpResponse(json.dumps(response_data), content_type="application/json")


def detailInformation(request):
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)

	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		resultfileName=request.GET.get("fileName")# user input for searching result
		resultfileName= str(resultfileName).strip()
		homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
		resultfilePath='NA'
		if resultfileName != 'NA':
			resultfilePath=os.path.join(homedir, 'src/resultFile/jsonData/resultJson/search/results/',resultfileName+'_search_proteincentric.json')
		else:
			resultfilePath=os.path.join(homedir, 'src/resultFile/preDownloadFile/json/all_data_proteincentric.json')

		fastafilename=request.GET.get("fastafilename")
		fastafilename= str(fastafilename).strip()
		if fastafilename != 'NA':
			fastafilename=fastafilename.replace('|','_')
		contextgoterm =[]
		reachable=True
		jvenndataseries=[]
		response_data = {}
		if len(uniprotkb)>0:
			uniprotkblist=[]
			code=None
			geneName=None
			protname=None
			humanProtName=None
			humanGeneName=None
			humanUniKb=None
			pepPresentInHumanOrtholog=None
			availableAssayInHumanOrtholog=None
			subcell=None
			humanDiseaseUniProt=['NA']
			humanDiseaseDisGeNet=['NA']
			drugBank=None
			orgID=None
			disStat=0
			drugStat=0
			assayStat=0
			bioMatStat=0
			strainStat=0
			es.indices.refresh(index="xxxxxxxxx-index")
			#build elasticsearch query based provided uniprotkb acc
			query={"query": {
				"bool": {
					"must": [
						{"match": {"UniProtKB Accession": uniprotkb}},
						{"match": {"UniprotKb entry status": "Yes"}}
					]
				}
			}
			}
			res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)

			foundHits=res["hits"]["total"]
			for hit in res['hits']['hits']:
				jdic=hit["_source"]
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				geneName=str(jdic["Gene"]).strip()
				protname=str(jdic["Protein"]).strip()
			es.indices.refresh(index="xxxxxxxxx-index")

			if foundHits >0:
				with open(resultfilePath) as rjf:
					for resitem in json.load(rjf)['data']:
						if resitem["UniProtKB Accession"]==uniprotkb:
							orgID=resitem["Organism ID"].strip()
							if len(resitem["Human ProteinName"].strip()) > 0 and resitem["Human ProteinName"].strip() != "NA":
								tempLst =resitem["Human ProteinName"].strip().split('|')
								humanProtName= "<br>".join(tempLst)
							else:
								humanProtName='NA'

							if len(resitem["Human Gene"].strip()) > 0 and resitem["Human Gene"].strip() != "NA":
								tempLst =(resitem["Human Gene"].strip()).split('|')
								humanGeneName= "<br>".join(tempLst)
							else:
								humanGeneName='NA'

							if len(resitem["Human UniProtKB Accession"].strip()) > 0 and resitem["Human UniProtKB Accession"].strip() != "NA":
								tempLst =(resitem["Human UniProtKB Accession"].strip()).split(',')
								for idx, val in enumerate(tempLst):
									tempLst[idx]='<a target="_blank" routerLinkActive="active" href="https://www.uniprot.org/uniprot/' + val+'">'+val+ '</a>'
								humanUniKb= "<br>".join(tempLst)
							else:
								humanUniKb='NA'
							pepPresentInHumanOrtholog=resitem["Present in human ortholog"][0].strip()

							if resitem["Available assays in human ortholog"].strip() != "NA":
								availableAssayInHumanOrtholog= '<a target="_blank" routerLinkActive="active" href="'+ resitem["Available assays in human ortholog"] + '">' + 'View' + '</a>'
							else:
								availableAssayInHumanOrtholog='NA'

							if len(resitem["SubCellular"].strip()) > 0:
								subcell =(resitem["SubCellular"].strip()).split('|')
							else:
								subcell=['NA']
							if len(resitem["Human UniProt DiseaseData"].strip()) > 0 and resitem["Human UniProt DiseaseData"].strip() != "NA":
								humanDiseaseUniProt=resitem["Human UniProt DiseaseData URL"].strip().split('|')
							else:
								humanDiseaseUniProt=['NA']

							if len(resitem["Human DisGen DiseaseData"].strip()) > 0 and resitem["Human DisGen DiseaseData"].strip() != "NA":
								humanDiseaseDisGeNet=resitem["Human DisGen DiseaseData URL"].strip().split('|')
							else:
								humanDiseaseDisGeNet=['NA']
							if len(resitem['Human Disease Name'].strip()) > 0 and resitem['Human Disease Name'].strip() != "NA":
								disStat=len(resitem['Human Disease Name'].strip().split('|'))
							if len(resitem['Peptide Sequence'].strip()) > 0 and resitem['Peptide Sequence'].strip() != "NA":
								assayStat=len(resitem['Peptide Sequence'].strip().split('<br>'))
							if len(resitem['Biological Matrix'].strip()) > 0 and resitem['Biological Matrix'].strip() != "NA":
								bioMatStat=len(resitem['Biological Matrix'].strip().split('<br>'))
							if len(resitem['Strain'].strip()) > 0 and resitem['Strain'].strip() != "NA":
								strainStat=len(resitem['Strain'].strip().split('<br>'))
							if len(resitem["Human Drug Bank"].strip()) > 0 and resitem["Human Drug Bank"].strip() != "NA":
								#tempLst =resitem["Human Drug Bank"].strip().split('|')
								drugBank=resitem["Human Drug Bank"].strip().split('|')
								drugStat=len(drugBank)
							else:
								drugBank=['NA']
							break
			orthologData=[
				{
					"humanProtName":humanProtName,
					"humanGeneName":humanGeneName,
					"humanUniKb":humanUniKb,
					"pepPresentInHumanortholog":pepPresentInHumanOrtholog,
					"availableAssayInHumanortholog":availableAssayInHumanOrtholog,
					"disStat":disStat,
					"drugStat":drugStat
				}
			]
			response_data ={
				"resultFilePath":resultfilePath,"proteinName":protname,"geneName":geneName,"uniprotkb":uniprotkb,"foundHits":foundHits,
				"orthologData":orthologData,"subcell":subcell,"humanDiseaseUniProt":humanDiseaseUniProt,"humanDiseaseDisGeNet":\
				humanDiseaseDisGeNet,"drugBankData":drugBank,"fastafilename":fastafilename,"orgID":orgID,
				"assayStat":assayStat,"bioMatStat":bioMatStat,"strainStat":strainStat
			}
			return HttpResponse(json.dumps(response_data), content_type="application/json")

def detailConcentration(request):
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		uniprotkb=str(request.GET.get("uniProtKb")).strip()
		resultFilePath= request.GET['resultFilePath']
		resultFilePath= str(request.GET.get("resultFilePath")).strip()

		filterSearchType=[str('sex'),str('strain'),str('biologicalMatrix'),str('knockout')]
		concUnit=[]
		strainData=None
		knockoutData=None
		bioMatData=None
		sexData=None
		allConcSamLLOQ=None
		allConc=None
		summaryConcData=[]
		es.indices.refresh(index="xxxxxxxxx-index")
		query={"query": {
			"bool": {
				"must": [
					{"match": {"UniProtKB Accession": uniprotkb}},
					{"match": {"UniprotKb entry status": "Yes"}}
				]
			}
		}
		}
		res = es.search(index="xxxxxxxxx-index", doc_type="xxxxxxxx-type", body=query)
		protinfo={}

		with open(resultFilePath) as rjf:
			for resitem in json.load(rjf)['data']:
				if resitem["UniProtKB Accession"]==uniprotkb:
					allConcSamLLOQ=resitem["All Concentration Range Data-Sample LLOQ Based"];
					allConc=resitem["All Concentration Range Data"];
					bioMatData=resitem["Biological Matrix Details"]
					strainData=resitem["Strain Details"]
					sexData=resitem["Sex Details"]
					knockoutData=resitem["Knockout Details"]
					pepinfo =resitem["Peptide Based Info"]
					for pepItem in pepinfo:
						tempPepSeq=pepItem["Peptide Sequence"].strip()

						if len(pepItem["concenQuery"].strip()) > 0 and pepItem["concenQuery"].strip().upper() !="NA":
							tempQuery=pepItem["concenQuery"].strip().replace('!','/')
							queryInfo=tempQuery.split('@')
							tempfilterSearchTerm=[str(queryInfo[0]),str(queryInfo[1]),str(queryInfo[2]),str(queryInfo[3])]
							protinfo[tempPepSeq]=tempfilterSearchTerm
					break
		finalconclist=[]
		for protKey in protinfo:
			sumconclist=[]
			foundHits=res["hits"]["total"]
			protList=[]
			jfinaldata=[]
			sampleLLOQ=''
			ULOQ=''
			filterSearchTerm=protinfo[protKey]
			for hit in res['hits']['hits']:
				jdic=hit["_source"]
				jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
				if str(jdic["Peptide Sequence"]).strip() ==protKey:
					if (str(jdic["Summary Concentration Range Data"]).strip()) >0 and (str(jdic["Summary Concentration Range Data"]).strip()).lower() !='na':
						sampleLLOQ=str(jdic["Sample LLOQ"]).strip()
						ULOQ=str(jdic["ULOQ"]).strip()
						jfinaldata.append(jdic)

			es.indices.refresh(index="xxxxxxxxx-index")
			jfinaldata=filterConcentration(jfinaldata,filterSearchTerm,filterSearchType)
			sampleLLOQ=sampleLLOQ.replace(' (fmol target protein/ug extracted protein)','')
			sampleLLOQ=dict([samval.split('|') for samval in sampleLLOQ.split(';')])
			ULOQ=ULOQ.replace(' (fmol target protein/ug extracted protein)','')
			ULOQ=dict([uval.split('|') for uval in ULOQ.split(';')])
			sumconcdata=str(jfinaldata[0]["Summary Concentration Range Data"]).strip()
			allconcdata=str(jfinaldata[0]["All Concentration Range Data"]).strip()
			allconcdataSampleLLOQ=str(jfinaldata[0]["All Concentration Range Data-Sample LLOQ Based"]).strip()
			sumconcdata=sumconcdata.replace('fmol target protein/u','fmol target protein/µ')
			sumconcdata=sumconcdata.replace('ug extracted protein/uL','µg extracted protein/µL')
			sumconcdata=sumconcdata.replace('ug extracted protein/mg','µg extracted protein/mg')

			allconcdata=allconcdata.replace('fmol target protein/u','fmol target protein/µ')
			allconcdata=allconcdata.replace('ug extracted protein/u','µg protein/µ')
			allconcdata=allconcdata.replace('ug extracted protein/mg','µg extracted protein/mg')

			allconcdataSampleLLOQ=allconcdataSampleLLOQ.replace('fmol target protein/u','fmol target protein/µ')
			allconcdataSampleLLOQ=allconcdataSampleLLOQ.replace('ug extracted protein/u','µg extracted protein/µ')

			sumconcinfo=sumconcdata.split(';')
			allconinfo=allconcdata.split(';')
			allconinfoSampleLLOQ=allconcdataSampleLLOQ.split(';')
			for scitem in sumconcinfo:
				scinfo =scitem.split('|')
				tempSampleLLOQ=sampleLLOQ[scinfo[2]]
				tempULOQ=ULOQ[scinfo[2]]
				stempid='|'.join(map(str,scinfo[2:5]))
				tempMatchConcList=[]
				for acitem in allconinfo:
					acinfo =acitem.split('|')
					del acinfo[3]
					atempid='|'.join(map(str,acinfo[2:5]))
					if stempid.lower() ==atempid.lower():
						concUnit.append('(' + acinfo[-2].strip().split(' (')[-1].strip())
						if float(acinfo[-3].strip().split(' ')[0].strip()) >0:
							tempMatchConcList.append(acinfo[-3].strip().split(' ')[0].strip())
				tempMatchConcData='|'.join(map(str,tempMatchConcList))

				tempMatchConcDataSampleLLOQ='NA'
				templen=1
				try:
					templen=len(filter(None,map(str,list(set(allconinfoSampleLLOQ)))))
				except UnicodeEncodeError:
					pass
				if 'NA' != ''.join(list(set(allconinfoSampleLLOQ))) and templen>0:
					tempMatchConcListSampleLLOQ=[]
					for slacitem in allconinfoSampleLLOQ:
						if slacitem.upper().strip() !='NA':
							slacinfo =slacitem.split('|')
							del slacinfo[3]
							slatempid='|'.join(map(str,slacinfo[2:5]))

							if stempid.lower() ==slatempid.lower():
								tempMatchConcListSampleLLOQ.append(slacinfo[-3].strip().split(' ')[0].strip())
					tempMatchConcDataSampleLLOQ='|'.join(map(str,tempMatchConcListSampleLLOQ))

				scinfo.append(str(jfinaldata[0]["UniProtKB Accession"]).strip())
				scinfo.append(str(jfinaldata[0]["Protein"]).strip())
				scinfo.append(str(jfinaldata[0]["Peptide Sequence"]).strip())
				stempid=stempid+'|'+protKey[0:3]+'..'
				scinfo.append(stempid)
				scinfo.append(tempMatchConcData)
				scinfo.append(tempMatchConcDataSampleLLOQ)
				scinfo.append(tempSampleLLOQ)
				scinfo.append(tempULOQ)
				scinfo=[scI.split('(')[0].strip()  if '(' in scI else scI for scI in scinfo]
				sumconclist.append(scinfo)
			summaryConcData.insert(0,str(jfinaldata[0]["Peptide Sequence"]).strip())
			summaryConcData.insert(0,str(jfinaldata[0]["Protein"]).strip())
			summaryConcData.insert(0,str(jfinaldata[0]["UniProtKB Accession"]).strip())
			sumconclist=sorted(sumconclist,key=lambda l:l[4])
			sumconclist=sorted(sumconclist,key=lambda l:l[3])
			sumconclist=sorted(sumconclist,key=lambda l:l[2])
			for conItem in sumconclist:
				finalconclist.append(conItem)
		concUnit=list(set(concUnit))
		concUnit='&'.join(concUnit)
		lenOfConcData=len(finalconclist)
		response_data ={'conclist':finalconclist,'foundHits':foundHits,'concUnit':concUnit,'lenOfConcData':lenOfConcData,
		"strainData":strainData,"knockoutData":knockoutData,"bioMatData":bioMatData,"sexData":sexData,
		"allConcSamLLOQ":allConcSamLLOQ,"allConc":allConc
		}
		
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def saveFastaFile(request):
	"""
	This is function save fasta file.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		userInputFastaFileContext=''
		userInputFastaFileContext=str(request.GET.get('fastaFileContext')).strip()
		userInputFastaFileContext=userInputFastaFileContext.replace('\\n','\n')
		userInputFastaFileContext=userInputFastaFileContext.replace('"','')
		nameFile=str(uuid.uuid4()) # generate random file name to store user search result
		fastaseq=[]
		finalsearhdata=''
		currdate=str(datetime.datetime.now())
		currdate=currdate.replace('-','_')
		currdate=currdate.replace(' ','_')
		currdate=currdate.replace(':','_')
		currdate=currdate.replace('.','_')
		nameFIle=currdate+'_'+nameFile
		fastafilename=nameFile+'.fasta'
		#storing user provided fasta file
		fastafilepath=os.path.join(settings.BASE_DIR, 'resultFile', 'fastaFile', fastafilename)
		fastafilewrite=open(fastafilepath,"w")
		fastafilewrite.write(userInputFastaFileContext)
		fastafilewrite.close()
		response_data={'nameFile':nameFile}
		return HttpResponse(json.dumps(response_data), content_type="application/json")

def submission(request):
	"""
	This is submission form where 
	Admin will recieve email from submission page.
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		submissiondetails=json.loads(request.GET.get('submissiondetails').strip())
		form_email = submissiondetails["submissionFormEmail"].strip() # get email address
		form_full_name = submissiondetails["submissionFormName"].strip() # get name
		form_laboratory = submissiondetails["submissionFormLaboratory"].strip() # get Laboratory
		form_experiment = submissiondetails["submissionFormExperiment"].strip() # get Experiment
		try:
			form_publication = submissiondetails["submissionFormPublication"].strip() # get Publication
		except AttributeError:
			form_publication = 'NA'
		form_data_repository = submissiondetails["submissionFormDataRepository"].strip() # get Data Repository
		form_data_acession_number = submissiondetails["submissionFormDataAcessionNumber"].strip() # get Data Acession Number
		try:
			form_repository_password = submissiondetails["submissionFormRepositoryPassword"].strip() # get Repository Password
		except AttributeError:
			form_repository_password = 'NA'
		form_message = submissiondetails["submissionFormMessage"].strip() # get message
		form_userWantForward = submissiondetails["submissionFormCopy"] # user Want to Forward this email
		subject='Site data submission form for MouseQuaPro'
		from_email=settings.EMAIL_HOST_USER
		to_email=['Pallab@proteincentre.com','Yassene@proteincentre.com','bioinformatics@proteincentre.com']
		submission_message="Full Name:%s, Email:%s,Laboratory:%s, Description of experiment:%s, Publication(s) DOI:%s,Data repository:%s,Data acession number:%s,Repository password:%s,Message: %s"%(
			form_full_name,
			form_email,
			form_laboratory,
			form_experiment,
			form_publication,
			form_data_repository,
			form_data_acession_number,
			form_repository_password,
			form_message)
		send_mail(subject,submission_message,from_email,to_email,fail_silently=True) # sent email

		#foward user the same email
		if form_userWantForward:
			submission_message_user="Full Name:%s, Email:%s,Laboratory:%s, Description of experiment:%s, Publication(s) DOI:%s,Data repository:%s,Data acession number:%s,Repository password:%s,Message: %s"%(
			form_full_name,
			form_email,
			form_laboratory,
			form_experiment,
			form_publication,
			form_data_repository,
			form_data_acession_number,
			form_repository_password,
			form_message)
			send_mail(subject,submission_message_user,from_email,[form_email],fail_silently=True) # sent email

		return HttpResponse({}, content_type="application/json")

def generateDownload(request):
	"""
	This is generate download file
	"""
	ip = get_ip(request, right_most_proxy=True)
	IpAddressInformation.objects.create(ip_address=ip)
	if request.method=='GET':
		resultJsonfilepath=request.GET.get('jsonfile').strip()
		fastaFileStatus=resultJsonfilepath.split('|')[1]
		resultJsonfileName=resultJsonfilepath.split('/')[-1].split('_')[0]
		downloadFilename='Results_'+resultJsonfileName+'_search.csv'
		downloadResultFilePath=os.path.join(settings.BASE_DIR, 'resultFile', 'downloadResult', 'search',  downloadFilename)
		homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
		fullresultfilePath=os.path.join(homedir, 'src/resultFile/jsonData/resultJson/search/downloadversion/',resultJsonfilepath.split('/')[-1].split('|')[0])
		with open(fullresultfilePath) as rjf:
			resultsJsonData=json.load(rjf)
			resultsJsonData=updateDataToDownload(resultsJsonData)
			df=pd.read_json(json.dumps(resultsJsonData))
			df.rename(columns ={'UniProtKB Accession':'Mouse UniProtKB accession','Protein':'Mouse Protein name',\
				'Gene':'Mouse Gene','Present in isoforms':'Peptide present in isoforms',\
				'Peptide Sequence':'Peptide sequence','Knockout':'Mutant',\
				'Unique in protein':'Peptide unique in proteome','Human UniProtKB Accession': \
				'UniProtKB accession of human ortholog','Human ProteinName': 'Human ortholog',\
				'Peptide ID':'Assay ID','Present in human isoforms':'Peptide present in human isoforms',\
				'Unique in human protein':'Peptide unique in human protein',\
				'SubCellular':'Subcellular localization','Mouse Kegg Pathway':'Molecular pathway(s) Mouse',\
				'Present in human ortholog':'Peptide present in human ortholog',\
				'Human Kegg Pathway':'Molecular pathway(s) Human','Human UniProt DiseaseData':'Involvement in disease-Human(UniProt)',\
				'Human DisGen DiseaseData':'Involvement in disease-Human(DisGeNET)','Human Drug Bank':\
				'Drug associations-Human','CZE Purity':'CZE','AAA Concentration':'AAA',\
				'Mouse Go':'GO Mouse','Human Go':'GO Human','LLOQ':'Assay LLOQ','ULOQ':'Assay ULOQ'}, inplace =True)
			if fastaFileStatus == 'NA':
				df.to_csv(downloadResultFilePath,index=False, encoding='utf-8',columns=downloadColName)
			if fastaFileStatus == 'Fasta':
				df.to_csv(downloadResultFilePath,index=False, encoding='utf-8',columns=downloadColNameUserSeq)
		
			response_data ={'downloadFileName':downloadFilename}

			return HttpResponse(json.dumps(response_data), content_type="application/json")
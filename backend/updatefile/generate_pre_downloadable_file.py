#!/usr/bin/env.python
# -*- coding: utf-8 -*-
# encoding: utf-8
from __future__ import unicode_literals
from django.utils.encoding import force_text
import os,subprocess,psutil,re,shutil,datetime,sys,glob
import errno
import csv
import json
import pandas as pd
import numpy as np
from statistics import mean
import ctypes
from elasticsearch import Elasticsearch,helpers,RequestsHttpConnection
from modJsonData import pepbasedInfo
from prePareDownloadFile import updateDataToDownload
def preDownloadFile():
	proteinInfoColname=['sel', 'UniProtKB Accession', 'Protein', 'Gene', 'Peptide Sequence', 'SubCellular','Strain',\
	'Knockout','Biological Matrix','Sex','Concentration Range','Gene Expression View','Human UniProtKB Accession', \
	'Human ProteinName', 'Human Gene', 'Mouse Kegg Pathway Name','Mouse Kegg Pathway','Human Kegg Pathway Name', \
	'Human Kegg Pathway','Human Disease Name','Human UniProt DiseaseData','Human UniProt DiseaseData URL','Human DisGen DiseaseData','Human DisGen DiseaseData URL',\
	'Mouse Go ID','Mouse Go Name','Mouse Go Term','Mouse Go','Human Go ID','Human Go Name','Human Go Term','Human Go',\
	'Human Drug Bank','Available assays in human ortholog']

	downloadColName=['Mouse Protein Name','Mouse Gene','Mouse UniProtKB Accession','Peptide Sequence',\
	'Peptide present in isoforms','Peptide unique in proteome','Strain','Knockout','Human Ortholog','Human Gene',\
	'UniProtKB Accession of Human Ortholog','Peptide present in human ortholog','Peptide unique in human protein',\
	'Peptide present in human isoforms','Available assays in human ortholog','Subcellular localization',\
	'Pathway(s) Mouse','Pathway(s) Human','Involvement in disease-Human(UniProt)','Involvement in disease-Human(DisGeNET)',\
	'Go Mouse','Go Human','Drug Bank-Human','Transitions','Retention Time','Analytical inofrmation',\
	'Gradients','Molecular Weight','GRAVY Score','Summary Concentration Range Data',\
	'All Concentration Range Data-Sample LLOQ Based','Panel','Assay LLOQ','Assay ULOQ','Sample LLOQ','Gene Expression Data']
	es = Elasticsearch(
		['http://xxxxx:9200/'],
		connection_class=RequestsHttpConnection
	)
	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	es.indices.refresh(index="xxxxx-index")
	query={"query": {
		"bool": {
			"must": [
				{"match": {"Organism ID": "10090"}}
			]
		}
	}
	}
	jsonfilename_proteincentric='all_data_proteincentric.json'
	downloadFilename='Results_all.csv'
	jsonfilepath_proteincentric=os.path.join(homedir, 'src/resultFile/preDownloadFile/json', jsonfilename_proteincentric)
	downloadResultFilePath=os.path.join(homedir, 'src/resultFile/preDownloadFile/csv',  downloadFilename)
	jsonfileoutput_proteincentric= open(jsonfilepath_proteincentric,'w')


	res=helpers.scan(client=es,scroll='2m',index="xxxxx-index", doc_type="xxxxx-type",query=query,request_timeout=30)
	jfinaldata=[]
	uniprotpepinfo={}
	for i in res:
		jdic=i['_source']
		jdic={str(tkey):force_text(tvalue) for tkey,tvalue in jdic.items()}
		if jdic["UniprotKb entry status"] =="Yes":
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

	es.indices.refresh(index="xxxxx-index")
	finalupdatedUniInfo=pepbasedInfo(jfinaldata,uniprotpepinfo,proteinInfoColname)
	json.dump(finalupdatedUniInfo,jsonfileoutput_proteincentric)
	jsonfileoutput_proteincentric.close()

	jfinaldata=updateDataToDownload(jfinaldata)
	df=pd.read_json(json.dumps(jfinaldata))
	df.rename(columns ={'UniProtKB Accession':'Mouse UniProtKB Accession','Protein':'Mouse Protein Name',\
		'Gene':'Mouse Gene','Present in isoforms':'Peptide present in isoforms',\
		'Unique in protein':'Peptide unique in proteome','Human UniProtKB Accession': \
		'UniProtKB Accession of Human ortholog','Human ProteinName': 'Human ortholog',\
		'Peptide ID':'Assay ID','Present in human isoforms':'Peptide present in human isoforms',\
		'Unique in human protein':'Peptide unique in human protein',\
		'SubCellular':'Subcellular localization','Mouse Kegg Pathway':'Pathway(s) Mouse',\
		'Present in human ortholog':'Peptide present in human ortholog',\
		'Human Kegg Pathway':'Pathway(s) Human','Human UniProt DiseaseData':'Involvement in disease-Human(UniProt)',\
		'Human DisGen DiseaseData':'Involvement in disease-Human(DisGeNET)','Human Drug Bank':\
		'Drug Bank-Human','CZE Purity':'CZE','AAA Concentration':'AAA',\
		'Mouse Go':'Go Mouse','Human Go':'Go Human','LLOQ':'Assay LLOQ','ULOQ':'Assay ULOQ'}, inplace =True)
	df.to_csv(downloadResultFilePath,index=False, encoding='utf-8', columns=downloadColName)

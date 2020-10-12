#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,subprocess,psutil,re,sys,shutil,datetime,time
import unicodedata
import urllib,urllib2
from socket import error as SocketError
import errno
import xmltodict
import random
import csv,json
from elasticsearch import Elasticsearch,helpers,RequestsHttpConnection
import requests
import unicodedata
import pandas as pd
import ctypes

def uploadData():
	print (datetime.datetime.now())
	print ("Upload mother file job Starts")

	shortmonthdic={"Jan":"January","Feb":"February","Mar":"March","Apr":"April","May":"May","Jun":"June","Jul":"July","Aug":"August","Sep":"September","Oct":"October","Nov":"November","Dec":"December"}
	#increase the field size of CSV
	csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

	uploadDateList=[]
	currentdate=datetime.datetime.now().strftime("%B-%d-%Y")

	uploadfilename='uploadElasticSearchInfo.txt'
	with open(uploadfilename,'r') as f:
		for l in f:
			d=l.strip()
			uploadDateList.append(d)



	homedir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
	filename='ReportBook_mother_file.csv'
	filenameJson='ReportBook_mother_file.json'
	filepath = os.path.join(homedir, 'src/qmpkbmotherfile', filename)
	filepathJson = os.path.join(homedir, 'src/qmpkbmotherfile', filenameJson)


	fileCreateDateList=str(time.ctime(os.path.getmtime(filepath))).split(' ')
	fileCreateDateList=[f for f in fileCreateDateList if len(f.strip()) >0 ]


	fileCreateDate=str(shortmonthdic[fileCreateDateList[1]])+"-"+str(fileCreateDateList[2])+"-"+str(fileCreateDateList[-1])
	if fileCreateDate not in uploadDateList:
		uploadDateList.append(fileCreateDate)

		es = Elasticsearch(['http://xxxxx:9200/'],connection_class=RequestsHttpConnection)

		es.indices.delete(index='xxxxx-index', ignore=[400, 404])
		if not es.indices.exists(index="xxxxx-index"):
			customset={
				"settings": {
					"analysis": {
				  		"analyzer": {
				  			"ngram_analyzer": {
								"tokenizer": "ngram_tokenizer",
								"filter": [
									"lowercase",
									"asciifolding"
								]
				  			}
				  		},
				  		"tokenizer": {
				  			"ngram_tokenizer": {
								"type": "ngram",
								"min_gram": 1,
								"max_gram": 10000,
								"token_chars": [
									"letter",
									"digit",
									"punctuation"
								]
				  			}
				  		}
					}
				},
			  	"mappings": {
					"mousequapro-type": {
				  		"properties": {
				  			"UniProtKB Accession": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Protein": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Gene": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},				  			
				  			"Organism": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Organism ID": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"SubCellular": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Peptide Sequence": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Mouse Kegg Pathway Name": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Human Disease Name": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Mouse Go ID": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Mouse Go Name": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Mouse Go Term": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Mouse Kegg Coverage": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Human Drug Bank": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Strain": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Knockout": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Panel": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Sex": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			},
				  			"Biological Matrix": {
								"type": "text",
								"fields": {
									"ngram": {
					  					"type": "text",
					  					"analyzer": "ngram_analyzer",
					  					"search_analyzer": "standard"
									}
								}
				  			}
				  		}
					}
			  	}
			}
			es.indices.create(index="xxxxx-index", body=customset, ignore=400)
			jsonData=[]
			with open(filepath,'r') as f:
				elasreader = csv.DictReader(f,delimiter="\t")
				for row in elasreader:
					jsonData.append(row)
			finalresultJson={"data":jsonData}
			jsonfileoutput= open(filepathJson,'w')
			jsonfileoutput.write(json.dumps(jsonData))
			jsonfileoutput.close()

			count=1
			json_file_data=open(filepathJson).read()
			json_read_data=json.loads(json_file_data)
			for d in json_read_data:
				res=es.index(index='xxxxx-index',doc_type='xxxxx-type', id=count, body=d)
				res=es.get(index='xxxxx-index',doc_type='xxxxx-type', id=count)
				count=count+1
		es.indices.refresh(index="xxxxx-index")
		with open(uploadfilename,'w') as ufile:
			for i in uploadDateList:
				ufile.write(i+"\n")

		print (datetime.datetime.now())
		print ("Upload mother file job done")
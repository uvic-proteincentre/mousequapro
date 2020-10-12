import os,sys
from operator import itemgetter
import numpy as np
from itertools import count, groupby
import pandas as pd
import ast
from operator import itemgetter

def summarykeggcal(top10keggdict,prodataseries):
	keggpathwaycoverage=[]

	for kskey in top10keggdict:
		keggpathwayname=(kskey.strip()).split('|')[0]
		tempUniqKeggUniIDList=list(set(top10keggdict[kskey]))
		peptrack=[]
		for ckey in prodataseries:
			if "peptidetracker" in ckey.lower():
				peptrack=list(set(prodataseries[ckey]).intersection(tempUniqKeggUniIDList))

		temppeptrack=len(list(set(peptrack)))
		tempTotal=len(list(set(tempUniqKeggUniIDList)))
		templist=[keggpathwayname,tempTotal,temppeptrack]
		keggpathwaycoverage.append(templist)

	unqkeggpathwaycoverage=[list(tupl) for tupl in {tuple(item) for item in keggpathwaycoverage }]
	keggchart=[]
	if len(unqkeggpathwaycoverage)>0:
		sortedkeggpathwaycoverage=sorted(unqkeggpathwaycoverage, key= itemgetter(1), reverse=True)
		keggchart=[['Pathway Name', 'Total unique proteins', 'PeptideTracker']]
		keggchart=keggchart+sortedkeggpathwaycoverage
	return keggchart
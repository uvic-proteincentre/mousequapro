# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import Counter
from itertools import combinations
import ast
from operator import itemgetter
import operator
import json
import re,sys
import itertools
from collections import OrderedDict
import datetime
from statistics import mean
from appTissueInfo import *
from django.contrib.admin.utils import flatten
# function to generate peptidebased info into nested json format
def pepbasedInfo(jfinaldata,uniprotpepinfo,matchingpepseqquery,proteininfoColname,querybiomatrix):
	pepetidebasedinfoCol=['UniProtKB Accession','Peptide ID','Peptide Sequence','Summary Concentration Range Data',\
	'All Concentration Range Data','All Concentration Range Data-Sample LLOQ Based','Special Residues','Molecular Weight',\
	'GRAVY Score','Transitions','Retention Time','Percent Organic Solution','Gradients','AAA Concentration','CZE Purity',\
	'Unique in protein','Present in isoforms','PeptideTracker TransView',"Peptide unique in user's database",\
	"Peptide in user's database","Peptide ID","Concentration View"]
	updatedUniInfo=[]
	biomatrixContainUniId=[]
	finalupdatedUniInfo={}
	tempdiffcol=proteininfoColname
	updatedpepinfocol=['UniProtKB Accession','Peptide Sequence',"Unique in protein",'Present in isoforms',\
	'Present in human ortholog','Unique in human protein','Present in human isoforms',\
	"Peptide unique in user's database", "Peptide in user's database","Panel",'LLOQ','ULOQ','Sample LLOQ']
	assaydinfocol=['Special Residues','Molecular Weight','GRAVY Score','AAA Concentration','CZE Purity']
	tempdiffcol.append('Organism ID')
	foldchangeData={}
	sexData=[]
	strainData=[]
	biomatrixData=[]
	for uniprotid in uniprotpepinfo:
		tempupdatedUniDic={}
		peptidebasedinfo=[]
		tempmatchingpepseq=''
		tempepepseqlist=[]
		biologicalmatrix=[]
		biologicalmatrixdetails=[]
		sexdetails=[]
		straindetails=[]
		knockoutdetails=[]
		meanconcdic={}
		concendataAll=[]
		concendataALLSampleLLOQ=[]
		pepSeqPresence=[]
		for pepseq in list(set(uniprotpepinfo[uniprotid])):
			tempassaydic={}
			tempconcenlist=[]
			tempassaydinfo=[]
			tempgradients=[]
			temptransition=[]
			tempconcendata=[]
			geneExpData='NA'
			concenQuery='NA'
			concenView={}
			for jd in jfinaldata:
				if uniprotid in jd['UniProtKB Accession'] and pepseq in jd['Peptide Sequence']:
					if jd['Gene Expression Data'] != 'NA':
						geneExpData=jd['Gene Expression Data'].split(';')[1:]
						geneExpData.sort(key=lambda g: g.upper())
					concendataAll.append([jd['Peptide Sequence'],jd['All Concentration Range Data']])
					concendataALLSampleLLOQ.append([jd['Peptide Sequence'],jd['All Concentration Range Data-Sample LLOQ Based']])
					biologicalmatrix.append(jd["Biological Matrix"])
					tempepepseqlist.append(jd['Peptide Sequence'])
					tempjfinalkeys=jd.keys()
					subpepinfodic={}

					for i in pepetidebasedinfoCol:
						try:
							subpepinfodic[i]=jd[i]
						except KeyError:
							subpepinfodic[i]='NA'
					for j in updatedpepinfocol:
						try:
							tempassaydic[j]=jd[j]
						except KeyError:
							tempassaydic[j]='NA'
					try:
						tempassaydinfo.append({a:jd[a] for a in assaydinfocol})
					except KeyError:
						pass

					try:
						tempgradients.append(jd['Gradients'])
					except KeyError:
						tempgradients.append('NA')

					try:
						temptransition.append(jd['Transitions'])
					except KeyError:
						temptransition.append('NA')

					pepSeqPresence.append(jd['Present in human ortholog'])

					try:
						if 'NA' != jd["Biological Matrix"].upper():
							tempPlotSampleLLOQ=str(jd['Sample LLOQ'].encode('ascii','ignore').strip())
							tempPlotSampleLLOQ=tempPlotSampleLLOQ.replace(' (fmol target protein/g extracted protein)','')
							tempPlotSampleLLOQ=dict([tempval.split('|') for tempval in tempPlotSampleLLOQ.split(';')])

							tempPlotULOQ=str(jd['ULOQ'].encode('ascii','ignore').strip())
							tempPlotULOQ=tempPlotULOQ.replace(' (fmol target protein/g extracted protein)','')
							tempPlotULOQ=dict([tempval.split('|') for tempval in tempPlotULOQ.split(';')])

							tempSampleLLOQInfo=str(jd['Sample LLOQ'].encode('ascii','ignore').strip()).split(';')
							tempSampleLLOQInfo=dict([tempval.split('|') for tempval in tempSampleLLOQInfo])

							tempULOQInfo=str(jd['ULOQ'].encode('ascii','ignore').strip()).split(';')
							tempULOQInfo=dict([tempval.split('|') for tempval in tempULOQInfo])

							tempSampleAllLLOQ=jd['All Concentration Range Data-Sample LLOQ Based']
							tempSampleAllData=jd['All Concentration Range Data']
							tempMinMaxConDic={}
							tempConVal=[[str(al.split('|')[2]),float(al.split('|')[6].encode('ascii','ignore').strip().replace(' (fmol target protein/g extracted protein)',''))] for al in tempSampleAllData.split(';')]
							for ali in tempConVal:
								if ali[0] in tempMinMaxConDic:
									tempMinMaxConDic[ali[0]].append(ali[1])
								else:
									tempMinMaxConDic[ali[0]]=[ali[1]]							

							if jd['All Concentration Range Data-Sample LLOQ Based'] != 'NA':

								for sal in tempSampleAllLLOQ.split(';'):
									tempSampleAllLLOQInfo=sal.split('|')
									if tempSampleAllLLOQInfo[-1].upper() !='NA' and len(tempSampleAllLLOQInfo)>1:
										if concenView.has_key(tempSampleAllLLOQInfo[2]):
											concenView[tempSampleAllLLOQInfo[2]].append(float(tempSampleAllLLOQInfo[-3].split('(')[0].strip()))
										else:
											concenView[tempSampleAllLLOQInfo[2]]=[float(tempSampleAllLLOQInfo[-3].split('(')[0].strip())]
							else:
								for sampL in tempSampleLLOQInfo:
									if (max(tempMinMaxConDic[str(sampL)]) < float(tempSampleLLOQInfo[str(sampL)].split('(')[0].strip())) and (min(tempMinMaxConDic[str(sampL)]) < float(tempSampleLLOQInfo[str(sampL)].split('(')[0].strip())):
										concenView[sampL]="<"+str(tempSampleLLOQInfo[sampL]).split('(')[0].strip()+"(Sample LLOQ-"+str(sampL)+")"
									elif (max(tempMinMaxConDic[str(sampL)]) > float(tempSampleLLOQInfo[str(sampL)].split('(')[0].strip())) and (min(tempMinMaxConDic[str(sampL)]) > float(tempSampleLLOQInfo[str(sampL)].split('(')[0].strip())):
										concenView[sampL]=">"+str(tempULOQInfo[sampL]).split('(')[0].strip()+"(ULOQ-"+str(sampL)+")"
									else:
										concenView[sampL]="<"+str(tempSampleLLOQInfo[sampL]).split('(')[0].strip()+"(Sample LLOQ-"+str(sampL)+")<br>"+">"+str(tempULOQInfo[sampL]).split('(')[0].strip()+"(ULOQ-"+str(sampL)+")"

							tempMatrix=str(jd["Biological Matrix"]).split('<br/>')
							if '<br>' in str(jd["Biological Matrix"]):
								tempMatrix=str(jd["Biological Matrix"]).split('<br>')
							conQSeq=str(jd["Sex"]).split('<br/>')
							if '<br>' in str(jd["Sex"]):
								conQSeq=str(jd["Sex"]).split('<br>')
							conQStrain=str(jd["Strain"]).split('<br/>')
							if '<br>' in str(jd["Strain"]):
								conQStrain=str(jd["Strain"]).split('<br>')
							concenQuery='|'.join(conQSeq)+'@'+'|'.join(conQStrain)+'@'+'|'.join(tempMatrix)+'@'+str(jd["Knockout"])+'@'+pepseq+'@'+uniprotid
							concenQuery=concenQuery.replace('/','!')
							coninfo=(jd['Summary Concentration Range Data'].strip()).split(';')
							addedType=[]
							tempdetailslist=[]
							typeOfbiomat=[]
							typeOfsex=[]
							typeOfstrain=[]
							typeOfknocout=[]
							if len(coninfo)>0:
								for c in coninfo:
									subconinfo=c.split('|')
									dataAdded=str(subconinfo[4])+'@'+str(subconinfo[3])+'@'+str(subconinfo[2])+'@'+str(subconinfo[0])+'@'+str(subconinfo[1])+'@'+pepseq+'@'+uniprotid
									if 'NA' in subconinfo[6] and str(subconinfo[2]) in tempSampleLLOQInfo:
										if (max(tempMinMaxConDic[str(subconinfo[2])]) < float(tempSampleLLOQInfo[subconinfo[2]].split('(')[0].strip())) and (min(tempMinMaxConDic[str(subconinfo[2])]) < float(tempSampleLLOQInfo[subconinfo[2]].split('(')[0].strip())):
											 subconinfo[6]="<"+str(tempSampleLLOQInfo[subconinfo[2]]).split('(')[0].strip()+"(Sample LLOQ-"+str(subconinfo[2])+")"
										elif (max(tempMinMaxConDic[str(subconinfo[2])]) > float(tempSampleLLOQInfo[subconinfo[2]].split('(')[0].strip())) and (min(tempMinMaxConDic[str(subconinfo[2])]) > float(tempSampleLLOQInfo[subconinfo[2]].split('(')[0].strip())):
											subconinfo[6]= ">"+str(tempULOQInfo[subconinfo[2]]).split('(')[0].strip()+"(ULOQ-"+str(subconinfo[2])+")"
										else:
											subconinfo[6]= "<"+str(tempSampleLLOQInfo[subconinfo[2]]).split('(')[0].strip()+"(Sample LLOQ-"+str(subconinfo[2])+")<br>" + ">"+str(tempULOQInfo[subconinfo[2]]).split('(')[0].strip()+"(ULOQ-"+str(subconinfo[2])+")"

									tempconlist=[subconinfo[6],subconinfo[4],pepseq,uniprotid,str(subconinfo[2]),str(subconinfo[3]),str(subconinfo[0]),str(subconinfo[1])]
									if dataAdded not in addedType:
										typeOfbiomat.append(tempconlist[4])
										typeOfsex.append(tempconlist[1])
										typeOfstrain.append(tempconlist[5])
										typeOfknocout.append(tempconlist[7])
										addedType.append(dataAdded)
										tempdetailslist.append(tempconlist)
							typeOfbiomat=list(set(typeOfbiomat))
							typeOfsex=list(set(typeOfsex))
							typeOfstrain=list(set(typeOfstrain))
							typeOfknocout=list(set(typeOfknocout))
							for b in typeOfbiomat:
								templist=[]
								tempsex=[]
								tempstrain=[]
								tempknockout=[]
								temppanel=[]
								concenVal={}
								ukb=''
								temppepseq=''
								tempUnit=''
								for i in tempdetailslist:
									if b == i[4]:
										tempsex.append(i[1])
										tempstrain.append(i[5])
										tempknockout.append(i[7])
										temppanel.append(i[6])
										if concenVal.has_key(i[4]):
											concenVal[i[4]].append(i[0].split('(')[0].strip())
										else:
											concenVal[i[4]]=[i[0].split('(')[0].strip()]
										if '<' in i[0] or '>' in i[0]:
											tempUnit=''.join(i[0].split('(')[1:-1]).strip()
										else:
											tempUnit=i[0].split('(')[-1].strip()
										ukb=i[3]
										temppepseq=i[2]
								tempQuery='|'.join(list(set(tempsex)))+'@'+'|'.join(list(set(tempstrain)))+'@'+b+'@'+'|'.join(list(set(tempknockout)))+'@'+temppepseq+'@'+ukb
								tempQuery=tempQuery.replace('/','!')
								tempconcenVal='NA'
								tempUnit=tempUnit.replace('fmol target protein/u','fmol target protein/µ')
								tempUnit=tempUnit.replace('fmol target protein/g','fmol target protein/µg')
								countSampleLLOQ=len([mc for mc in concenVal[b] if '<' in mc or '>' in mc])
								if len(concenVal[b]) ==countSampleLLOQ:
									if len(list(set(concenVal[b])))==1:
										if '<' in list(set(concenVal[b]))[0]:
											tempconcenVal=list(set(concenVal[b]))[0]+"(Sample LLOQ-"+str(b)+")"
										else:
											tempconcenVal=list(set(concenVal[b]))[0]+"(ULOQ-"+str(b)+")"
									else:
										tempconcenVal='<br>'.join([ul+"(Sample LLOQ-"+str(b)+")" if '<' in ul else ul+"(ULOQ-"+str(b)+")" for ul in concenVal[b]])
								else:
									tempVal=[float(j) for j in concenVal[b] if '<' not in str(j) and '>' not in str(j)]
									if len(tempVal)>0:
										tempconcenVal=str(mean(tempVal))
								templist=[tempconcenVal,'<br>'.join(list(set(tempsex))),temppepseq,ukb,b,'<br>'.join(list(set(tempstrain))),'<br>'.join(list(set(tempknockout))),tempQuery,tempPlotSampleLLOQ[b],tempPlotULOQ[b]]
								biologicalmatrixdetails.append(templist)
							for s in typeOfsex:
								templist=[]
								tempbiomat=[]
								tempstrain=[]
								tempknockout=[]
								temppanel=[]
								concenVal={}
								ukb=''
								temppepseq=''
								tempUnit=''
								for i in tempdetailslist:
									if s == i[1]:
										tempbiomat.append(i[4])
										tempstrain.append(i[5])
										tempknockout.append(i[7])
										temppanel.append(i[6])
										if concenVal.has_key(i[4]):
											concenVal[i[4]].append(i[0].split('(')[0].strip())
										else:
											concenVal[i[4]]=[i[0].split('(')[0].strip()]
										if '<' in i[0] or '>' in i[0]:
											tempUnit=''.join(i[0].split('(')[1:-1]).strip()
										else:
											tempUnit=i[0].split('(')[-1].strip()
										ukb=i[3]
										temppepseq=i[2]
								tempQuery=s+'@'+'|'.join(list(set(tempstrain)))+'@'+'|'.join(list(set(tempbiomat)))+'@'+'|'.join(list(set(tempknockout)))+'@'+temppepseq+'@'+ukb
								tempQuery=tempQuery.replace('/','!')
								for tbm in list(set(tempbiomat)):
									tempconcenVal='NA'
									tempUnit=tempUnit.replace('fmol target protein/u','fmol target protein/µ')
									tempUnit=tempUnit.replace('fmol target protein/g','fmol target protein/µg')
									countSampleLLOQ=len([mc for mc in concenVal[tbm] if '<' in mc or '>' in mc])

									if len(concenVal[tbm]) ==countSampleLLOQ:
										if len(list(set(concenVal[tbm])))==1:
											if '<' in list(set(concenVal[tbm]))[0]:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(Sample LLOQ-"+str(tbm)+")"
											else:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(ULOQ-"+str(tbm)+")"
										else:
											tempconcenVal='<br>'.join([ul+"(Sample LLOQ-"+str(tbm)+")" if '<' in ul else ul+"(ULOQ-"+str(tbm)+")" for ul in concenVal[tbm]])
									else:
										tempVal=[float(j) for j in concenVal[tbm] if '<' not in str(j) and '>' not in str(j)]
										if len(tempVal)>0:
											tempconcenVal=str(mean(tempVal))

									templist=[tempconcenVal,s,temppepseq,ukb,tbm,'<br>'.join(list(set(tempstrain))),'<br>'.join(list(set(tempknockout))),tempQuery,tempPlotSampleLLOQ[tbm],tempPlotULOQ[tbm]]
									sexdetails.append(templist)
							for st in typeOfstrain:
								templist=[]
								tempbiomat=[]
								tempsex=[]
								tempknockout=[]
								temppanel=[]
								concenVal={}
								ukb=''
								temppepseq=''
								tempUnit=''
								for i in tempdetailslist:
									if st == i[5]:
										tempbiomat.append(i[4])
										tempsex.append(i[1])
										tempknockout.append(i[7])
										temppanel.append(i[6])
										if concenVal.has_key(i[4]):
											concenVal[i[4]].append(i[0].split('(')[0].strip())
										else:
											concenVal[i[4]]=[i[0].split('(')[0].strip()]
										if '<' in i[0] or '>' in i[0]:
											tempUnit=''.join(i[0].split('(')[1:-1]).strip()
										else:
											tempUnit=i[0].split('(')[-1].strip()
										ukb=i[3]
										temppepseq=i[2]
								tempQuery='|'.join(list(set(tempsex)))+'@'+st+'@'+'|'.join(list(set(tempbiomat)))+'@'+'|'.join(list(set(tempknockout)))+'@'+temppepseq+'@'+ukb
								tempQuery=tempQuery.replace('/','!')
								for tbm in list(set(tempbiomat)):
									tempconcenVal='NA'
									tempUnit=tempUnit.replace('fmol target protein/u','fmol target protein/µ')
									tempUnit=tempUnit.replace('fmol target protein/g','fmol target protein/µg')
									countSampleLLOQ=len([mc for mc in concenVal[tbm] if '<' in mc or '>' in mc])
									if len(concenVal[tbm]) ==countSampleLLOQ:
										if len(list(set(concenVal[tbm])))==1:
											if '<' in list(set(concenVal[tbm]))[0]:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(Sample LLOQ-"+str(tbm)+")"
											else:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(ULOQ-"+str(tbm)+")"
										else:
											tempconcenVal='<br>'.join([ul+"(Sample LLOQ-"+str(tbm)+")" if '<' in ul else ul+"(ULOQ-"+str(tbm)+")" for ul in concenVal[tbm]])
									else:
										tempVal=[float(j) for j in concenVal[tbm] if '<' not in str(j) and '>' not in str(j)]
										if len(tempVal)>0:
											tempconcenVal=str(mean(tempVal))
									templist=[tempconcenVal,'<br>'.join(list(set(tempsex))),temppepseq,ukb,tbm,st,'<br>'.join(list(set(tempknockout))),tempQuery,tempPlotSampleLLOQ[tbm],tempPlotULOQ[tbm]]
									straindetails.append(templist)
							for k in typeOfknocout:
								templist=[]
								tempbiomat=[]
								tempsex=[]
								tempstrain=[]
								temppanel=[]
								concenVal={}
								ukb=''
								temppepseq=''
								tempUnit=''
								for i in tempdetailslist:
									if k == i[7]:
										tempbiomat.append(i[4])
										tempsex.append(i[1])
										tempstrain.append(i[5])
										temppanel.append(i[6])
										if concenVal.has_key(i[4]):
											concenVal[i[4]].append(i[0].split('(')[0].strip())
										else:
											concenVal[i[4]]=[i[0].split('(')[0].strip()]
										if '<' in i[0] or '>' in i[0]:
											tempUnit=''.join(i[0].split('(')[1:-1]).strip()
										else:
											tempUnit=i[0].split('(')[-1].strip()
										ukb=i[3]
										temppepseq=i[2]
								tempQuery='|'.join(list(set(tempsex)))+'@'+'|'.join(list(set(tempstrain)))+'@'+'|'.join(list(set(tempbiomat)))+'@'+k+'@'+temppepseq+'@'+ukb
								tempQuery=tempQuery.replace('/','!')
								for tbm in list(set(tempbiomat)):
									tempconcenVal='NA'
									tempUnit=tempUnit.replace('fmol target protein/u','fmol target protein/µ')
									tempUnit=tempUnit.replace('fmol target protein/g','fmol target protein/µg')
									countSampleLLOQ=len([mc for mc in concenVal[tbm] if '<' in mc or '>' in mc])
									if len(concenVal[tbm]) ==countSampleLLOQ:
										if len(list(set(concenVal[tbm])))==1:
											if '<' in list(set(concenVal[tbm]))[0]:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(Sample LLOQ-"+str(tbm)+")"
											else:
												tempconcenVal=list(set(concenVal[tbm]))[0]+"(ULOQ-"+str(tbm)+")"
										else:
											tempconcenVal='<br>'.join([ul+"(Sample LLOQ-"+str(tbm)+")" if '<' in ul else ul+"(ULOQ-"+str(tbm)+")" for ul in concenVal[tbm]])
									else:
										tempVal=[float(j) for j in concenVal[tbm] if '<' not in str(j) and '>' not in str(j)]
										if len(tempVal)>0:
											tempconcenVal=str(mean(tempVal))
									templist=[tempconcenVal,'<br>'.join(list(set(tempsex))),temppepseq,ukb,tbm,'<br>'.join(list(set(tempstrain))),k,tempQuery,tempPlotSampleLLOQ[tbm],tempPlotULOQ[tbm]]
									knockoutdetails.append(templist)

						tempconcendata.append(jd['Summary Concentration Range Data'])
					except KeyError:
						tempconcendata.append('NA')
					subpepinfodic.pop('Peptide ID', None)
					try:
						tempmean=[]
						tempMin=[]
						tempMax=[]
						if len(concenView)>0:
							for c in concenView:
								if "<" not in concenView[c]:
									tmean=c+':'+str(round(mean(concenView[c]),2))+unitDic[c]
									tmean=tmean.encode('ascii','ignore')
									tempmean.append(tmean)
									
									tmin=c+':'+str(round(min(concenView[c]),2))+unitDic[c]
									tmin=tmin.encode('ascii','ignore')
									tempMin.append(tmin)

									tmax=c+':'+str(round(max(concenView[c]),2))+unitDic[c]
									tmax=tmax.encode('ascii','ignore')
									tempMax.append(tmax)
								else:
									concenView[c]=concenView[c].replace('fmol target protein/u','fmol target protein/µ')
									concenView[c]=concenView[c].replace('fmol target protein/g','fmol target protein/µg')
									tempmean.append(concenView[c])
									tempMin.append(concenView[c])
									tempMax.append(concenView[c])
						subpepinfodic["Concentration View"]='<br/>'.join(tempmean)+'|'+'<br/>'.join(tempMin)+'|'+'<br/>'.join(tempMax)
						subpepinfodic["Concentration View"]=subpepinfodic["Concentration View"].replace('(fmol target protein/µg extracted protein)','')
						tempconcenlist.append(subpepinfodic["Concentration View"])
					except KeyError:
						tempconcenlist.append('NA')
					if len(tempdiffcol) >0:
						tempupdatedUniDic={key: jd[key] for key in tempdiffcol}
			tempassaydic['concenQuery']=concenQuery
			tempassaydic['Assay Information']=tempassaydinfo
			tempgradients=list(set(tempgradients))
			tempassaydic['Gradients']=tempgradients
			temptransition=list(set(temptransition))
			tempassaydic['Transitions']=temptransition
			tempassaydic['Transitions']=temptransition
			tempconcendata=list(set(tempconcendata))
			tempassaydic['Summary Concentration Range Data']=tempconcendata
			tempconcenlist=list(set(tempconcenlist))
			if len(tempconcenlist)>1:
				tempconcenlist.remove('NA')
			try:
				tempassaydic['Concentration View']=tempconcenlist[0]
				tempassaydic['Concentration View']=tempassaydic['Concentration View'].replace('(fmol target protein/µg extracted protein)','')
				tempassaydic['Concentration View']=tempassaydic['Concentration View'].replace('(fmol target protein/ug extracted protein)','')
			except IndexError:
				tempassaydic['Concentration View']='NA'
			peptidebasedinfo.append(tempassaydic)
		biologicalmatrix=[x for i in biologicalmatrix for x in i.split('<br/>')]
		biologicalmatrix=list(set(biologicalmatrix))
		if len(biologicalmatrix) >0:
			if 'NA' in biologicalmatrix:
				biologicalmatrix.remove('NA')

		biologicalmatrix='<br/>'.join(biologicalmatrix)
		try:
			tempupdatedUniDic["Biological Matrix"]=biologicalmatrix
		except IndexError:
			tempupdatedUniDic["Biological Matrix"]='NA'

		pepSeqPresence=list(set(pepSeqPresence))
		if len(pepSeqPresence) >1:
			if 'No' in pepSeqPresence:
				pepSeqPresence.remove('No')
		tempmatchingpepseq=list(set(tempepepseqlist))

		tempupdatedUniDic['Concentration Range']=tempupdatedUniDic['Concentration Range'].replace('(fmol target protein/µg extracted protein)','')
		tempupdatedUniDic['Concentration Range']=tempupdatedUniDic['Concentration Range'].replace('Mean Conc.:','')
		if ':' in tempupdatedUniDic['Concentration Range']:
			tempConcRange=tempupdatedUniDic['Concentration Range'].split('<br/>')
			tempConcRange=[str(fI).strip() for fI in tempConcRange if len(str(fI).strip())>0]
			tempConcRangeDic={}
			for cR in tempConcRange:
				crInfo=cR.split(':')
				tempConcRangeDic[crInfo[0]]=crInfo[1]
			newtempConcRange=[]
			for fK in tempConcRangeDic:
				newtempConcRange.append(fK+':'+tempConcRangeDic[fK])
			tempupdatedUniDic['Concentration Range']='<br/>'.join(newtempConcRange)

		tempupdatedUniDic['Peptide Sequence']='<br>'.join(map(str,tempmatchingpepseq))
		tempupdatedUniDic['Peptide Based Info']=peptidebasedinfo
		tempupdatedUniDic['Gene Expression Data']=geneExpData
		tempupdatedUniDic['All Concentration Range Data']=concendataAll
		tempupdatedUniDic['All Concentration Range Data-Sample LLOQ Based']=concendataALLSampleLLOQ
		tempupdatedUniDic['Assay Info']=','.join(map(str, peptidebasedinfo))
		tempupdatedUniDic['Assay Info']=tempupdatedUniDic['Assay Info'].replace('Peptide ID','Assay ID')
		biologicalmatrixdetails=[list(tupl) for tupl in {tuple(item) for item in biologicalmatrixdetails}]
		tempupdatedUniDic['Biological Matrix Details']=biologicalmatrixdetails

		sexdetails=[list(tupl) for tupl in {tuple(item) for item in sexdetails}]
		tempupdatedUniDic['Sex Details']=sexdetails

		straindetails=[list(tupl) for tupl in {tuple(item) for item in straindetails}]
		tempupdatedUniDic['Strain Details']=straindetails
		knockoutdetails=[list(tupl) for tupl in {tuple(item) for item in knockoutdetails}]
		tempupdatedUniDic['Knockout Details']=knockoutdetails
		tempupdatedUniDic['Present in human ortholog']=pepSeqPresence


		tempupdatedUniDic['Sex']=tempupdatedUniDic['Sex'].replace('|','<br>')
		tempupdatedUniDic['Sex']=tempupdatedUniDic['Sex'].replace('<br/>','<br>')
		tempupdatedUniDic['Strain']=tempupdatedUniDic['Strain'].replace('|','<br>')
		tempupdatedUniDic['Strain']=tempupdatedUniDic['Strain'].replace('<br/>','<br>')
		tempupdatedUniDic['Biological Matrix']=tempupdatedUniDic['Biological Matrix'].replace('|','<br>')
		tempupdatedUniDic['Biological Matrix']=tempupdatedUniDic['Biological Matrix'].replace('<br/>','<br>')

		if '<br>' in tempupdatedUniDic['Sex']:
			sexData.append(tempupdatedUniDic['Sex'].split('<br>'))
		else:
			sexData.append(tempupdatedUniDic['Sex'])

		if '<br>' in tempupdatedUniDic['Strain']:
			strainData.append(tempupdatedUniDic['Strain'].split('<br>'))
		else:
			strainData.append(tempupdatedUniDic['Strain'])

		if '<br>' in tempupdatedUniDic['Biological Matrix']:
			biomatrixData.append(tempupdatedUniDic['Biological Matrix'].split('<br>'))
		else:
			biomatrixData.append(tempupdatedUniDic['Biological Matrix'])

		updatedUniInfo.append(tempupdatedUniDic)

		if len(querybiomatrix) >0:
			if querybiomatrix in str(tempupdatedUniDic["Biological Matrix"]).lower():
				biomatrixContainUniId.append(tempupdatedUniDic["UniProtKB Accession"])
	foldChangeQueryData={
		'Biological Matrix':sorted(list(set(flatten(biomatrixData)))),
		'Sex':sorted(list(set(flatten(sexData)))),
		'Strain':sorted(list(set(flatten(strainData))))
	}
	if len(sorted(list(set(flatten(biomatrixData)))))>1:
		foldchangeData['Biological Matrix']=sorted(list(set(flatten(biomatrixData))))
	if len(sorted(list(set(flatten(sexData)))))>1:
		foldchangeData['Sex']=sorted(list(set(flatten(sexData))))
	if len(sorted(list(set(flatten(strainData)))))>1:
		foldchangeData['Strain']=sorted(list(set(flatten(strainData))))

	foldchangeData['foldChangeQueryData']=foldChangeQueryData
		
	finalupdatedUniInfo["data"]=updatedUniInfo[:10000]
	return finalupdatedUniInfo,biomatrixContainUniId,foldchangeData


# function to generate peptidebased info into nested json format
def pepbasedInfoRESTAPI(updatedresult,uniprotpepinfo):
	restApiColname=['Mouse UniProtKB accession','Mouse Protein name','Mouse Gene','Organism','Subcellular localization',\
	'Strain','Mutant','Biological Matrix','UniProtKB accession of human ortholog','Human ortholog','Human Gene',\
	'Available assays in human ortholog','Molecular pathway(s) Mouse','Molecular pathway(s) Human',\
	'Involvement in disease-Human(UniProt)','Involvement in disease-Human(DisGeNET)',\
	'GO Mouse','GO Human','Drug associations-Human','Gene Expression Data']

	pepetidebasedinfoCol=['Assay ID','Peptide sequence','Summary Concentration Range Data',\
	'All Concentration Range Data-Sample LLOQ Based','Labeled Residues','Molecular Weight',\
	'GRAVY Score','Transitions','Retention Time','Percent Organic Solution',\
	'Gradients','LLOQ','ULOQ','Sample LLOQ','Unique in protein','Present in isoforms']
	updatedpepinfocol=['Peptide sequence',"Unique in protein",'Present in isoforms',\
	'Present in human ortholog','Unique in human protein','Present in human isoforms',\
	"Peptide unique in user's database", "Peptide in user's database","Panel"]
	assaydinfocol=['Molecular Weight','GRAVY Score','LLOQ','ULOQ','Sample LLOQ']
	updatedUniInfo=[]

	for uniprotid in uniprotpepinfo:
		tempupdatedUniDic={}
		peptidebasedinfo=[]
		tempmatchingpepseq=''
		tempepepseqlist=[]
		biologicalmatrix=[]
		for pepseq in list(set(uniprotpepinfo[uniprotid])):
			tempassaydic={}
			tempconcenlist=[]
			tempassaydinfo=[]
			tempgradients=[]
			tempAnalytInfo=[]
			tempRetTimeInfo=[]
			temptransition=[]
			sumtempconcendata=[]
			alltempconcendata=[]
			alltempconcendataSampleLLOQ=[]

			for jd in updatedresult:
				if uniprotid in jd['Mouse UniProtKB accession'] and pepseq in jd['Peptide sequence']:
					biologicalmatrix.append(jd["Biological Matrix"])
					tempepepseqlist.append(jd['Peptide sequence'])
					tempjfinalkeys=jd.keys()
					subpepinfodic={}
					for i in pepetidebasedinfoCol:
						try:
							subpepinfodic[i]=jd[i]
						except KeyError:
							subpepinfodic[i]='NA'
					for j in updatedpepinfocol:
						try:
							tempassaydic[j]=jd[j]
						except KeyError:
							tempassaydic[j]='NA'
					try:
						tempassaydinfo.append({a:jd[a] for a in assaydinfocol})
					except KeyError:
						pass

					try:
						tempgradients.append(jd['Gradients'])
					except KeyError:
						tempgradients.append('NA')

					try:
						tempAnalytInfo.append(jd['Analytical inofrmation'])
					except KeyError:
						tempAnalytInfo.append('NA')

					try:
						tempRetTimeInfo.append(jd['Retention Time'])
					except KeyError:
						tempRetTimeInfo.append('NA')

					try:
						temptransition.append(jd['Transitions'])
					except KeyError:
						temptransition.append('NA')

					try:
						sumtempconcendata.append(jd['Summary Concentration Range Data'])
					except KeyError:
						sumtempconcendata.append('NA')
					try:
						alltempconcendata.append(jd['All Concentration Range Data'])
					except KeyError:
						alltempconcendata.append('NA')
					try:
						alltempconcendataSampleLLOQ.append(jd['All Concentration Range Data-Sample LLOQ Based'])
					except KeyError:
						alltempconcendataSampleLLOQ.append('NA')
					subpepinfodic.pop('Peptide ID', None)

					if len(restApiColname) >0:
						tempupdatedUniDic={key: jd[key] for key in restApiColname}

			tempassaydic['Assay Information']=tempassaydinfo
			tempgradients=list(set(tempgradients))
			tempAnalytInfo=list(set(tempAnalytInfo))
			tempassaydic['Gradients']=tempgradients
			tempassaydic['Analytical inofrmation']=tempAnalytInfo
			tempRetTimeInfo=list(set(tempRetTimeInfo))
			tempassaydic['Retention Time']=tempRetTimeInfo
			temptransition=list(set(temptransition))
			temptransition=[x for item in temptransition for x in item.split(';')]
			tempassaydic['Transitions']=temptransition
			sumtempconcendata=list(set(sumtempconcendata))
			sumtempconcendata=['|'.join(x.split('|')[1:]) for item in sumtempconcendata for x in item.split(';')]
			alltempconcendata=list(set(alltempconcendata))
			alltempconcendata=['|'.join(x.split('|')[1:]) for item in alltempconcendata for x in item.split(';')]
			alltempconcendataSampleLLOQ=list(set(alltempconcendataSampleLLOQ))
			alltempconcendataSampleLLOQ=['|'.join(x.split('|')[1:]) for item in alltempconcendataSampleLLOQ for x in item.split(';')]
			tempassaydic['Summary Concentration Range Data']=sumtempconcendata
			#tempassaydic['All Concentration Range Data']=alltempconcendata
			tempassaydic['All Concentration Range Data-Sample LLOQ Based']=alltempconcendataSampleLLOQ
			tempconcenlist=list(set(tempconcenlist))
			peptidebasedinfo.append(tempassaydic)

		biologicalmatrix=[x for i in biologicalmatrix for x in i.split('<br/>')]
		biologicalmatrix=list(set(biologicalmatrix))
		if len(biologicalmatrix) >0:
			if 'NA' in biologicalmatrix:
				biologicalmatrix.remove('NA')
		try:
			tempupdatedUniDic["Biological Matrix"]=biologicalmatrix[0]
		except IndexError:
			tempupdatedUniDic["Biological Matrix"]='NA'

		tempupdatedUniDic['Peptide Assay']=peptidebasedinfo
		updatedUniInfo.append(tempupdatedUniDic)
	return updatedUniInfo
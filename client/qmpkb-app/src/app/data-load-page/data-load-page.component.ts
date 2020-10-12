import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';

@Component({
  selector: 'app-data-load-page',
  templateUrl: './data-load-page.component.html',
  styleUrls: ['./data-load-page.component.css']
})
export class DataLoadPageComponent implements OnInit {

  loadQuery:string;
  errorStr:Boolean;
  public alertIsVisible:boolean= false;
  constructor(
	private route: ActivatedRoute,
	private router: Router,
	private spinner: NgxSpinnerService,
	private location: Location,
	private _qmpkb:QmpkbService
  ) { }
  
  ngOnInit() {
	this.spinner.show();
	this.route.params.subscribe(params=>{
		this.loadQuery =params['slug']
		if (this.loadQuery.includes('biomat_')) {
			this.location.go('/results/');
			let biomatArray=this.loadQuery.split('_');
			let updatedBiomatQuery=biomatArray[1]+'_mus'
			this._qmpkb.receiveDataFromBackendSearch('/resultsapi/?searchterm=' + updatedBiomatQuery).subscribe((response: any)=>{
				if (response.filename_proteincentric != null){
		            this._qmpkb.queryStorage={
		              searchterm: biomatArray[1],
		              filepath: response.filename_proteincentric,
		              totallist: response.totallist,
		              unqisostat: response.unqisostat,
		              subcell:response.subcell,
		              updatedgo:response.updatedgo,
		              querystrainData:response.querystrainData,
		              querybioMatData:response.querybioMatData,
		              querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
		              querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,		              
		              keggchart:response.keggchart,
		              foundHits:response.foundHits
		            }
		            this.router.navigate(['/results/']);
				} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
				}
			}, error=>{
				this.errorStr = error;
			})
		} else if (this.loadQuery.includes('concentration_')) {
			this.location.go('/concentration/')
			let concentrationArray=this.loadQuery.split('concentration_');
			this._qmpkb.receiveDataFromBackendSearch('/concentrationapi/?query=' + concentrationArray[1]).subscribe((response: any)=>{
				let conclist= response.conclist
				let protList= response.protList
				let foundHits=response.foundHits
				let concUnit = response.concUnit
				let lenOfConcData= response.lenOfConcData
				if (foundHits > 0){
		            this._qmpkb.queryStorage={
					  protList: protList,
					  conclist: conclist,
					  foundHits:foundHits,
					  concUnit: concUnit,
					  lenOfConcData: lenOfConcData
		            }
		            this.router.navigate(['/concentration/']);
				} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
				}
			}, error=>{
				this.errorStr = error;
			})
		} else if (this.loadQuery.includes('userpepseq_')) {
			this.location.go('/peptideuniqueness/')
			let userpepseqArray=this.loadQuery.split('_');
			let filename = userpepseqArray.slice(3).join("_"); 
			this._qmpkb.receiveDataFromBackendSearch('/peptideuniquenessapi/?Uniprotkb=' + userpepseqArray[1]+
				'&pepseq='+ userpepseqArray[2]+
				'&fastafile='+ filename
				).subscribe((response: any)=>{
				let pepunqdata= response.pepunqdata
				let reachable= response.reachable
				if (reachable != false) {
		            this._qmpkb.queryStorage={
						pepunqdata:pepunqdata,
						reachable :reachable
		            }
		            this.router.navigate(['/peptideuniqueness/']);
				} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
				}
			}, error=>{
				this.errorStr = error;
			})
		} else if (this.loadQuery.includes('advanceSearchData_')) {
			/*this.location.go('/results/')*/
			let advanceSearchDataArray=this.loadQuery.split('_');
			let advancedFormData={
				queryformData:
					{optionGroups:
						[
							{selectInput:"gene",whereInput:advanceSearchDataArray[1]}
						]
					}
			}
	        this._qmpkb.receiveDataFromBackendSearch('/advanceresultsapi/?advancedFormData=' + JSON.stringify(advancedFormData)).subscribe((response: any)=>{
	        	if (response.filename_proteincentric != null){
		        	this._qmpkb.queryStorage={
		              searchterm: response.query,
		              filepath: response.filename_proteincentric,
		              totallist: response.totallist,
		              unqisostat: response.unqisostat,
		              subcell:response.subcell,
		              querystrainData:response.querystrainData,
		              querybioMatData:response.querybioMatData,
		              querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
		              querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,		            
		              updatedgo:response.updatedgo,
		              keggchart:response.keggchart,
		              foundHits:response.foundHits,
		              fastafilename:response.fastafilename
		            }
		            this.router.navigate(['/results/']);
	        	
	        	} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
	        	}
	      	}, error=>{
	        this.errorStr = error;
	      	})

		}  else if (this.loadQuery.includes('googleChartData_')) {
			/*this.location.go('/results/')*/
			let googleChartDataArray=this.loadQuery.split('_');
			let advancedFormData:any={};
			let tempinputArrayArray=[];
			if (googleChartDataArray[2]=='strain' || googleChartDataArray[2]=='biologicalMatrix'){
				tempinputArrayArray.push(googleChartDataArray[1]);
				advancedFormData={
					queryformData:
						{optionGroups:
							[
								{selectInput:googleChartDataArray[2],whereInput:tempinputArrayArray}
							]
						}
				}

			} else {
				advancedFormData={
					queryformData:
						{optionGroups:
							[
								{selectInput:googleChartDataArray[2],whereInput:googleChartDataArray[1]}
							]
						}
				}
			}

	        this._qmpkb.receiveDataFromBackendSearch('/advanceresultsapi/?advancedFormData=' + JSON.stringify(advancedFormData)).subscribe((response: any)=>{
	        	if (response.filename_proteincentric != null){
		        	this._qmpkb.queryStorage={
		              searchterm: response.query,
		              filepath: response.filename_proteincentric,
		              totallist: response.totallist,
		              unqisostat: response.unqisostat,
		              subcell:response.subcell,
		              querystrainData:response.querystrainData,
		              querybioMatData:response.querybioMatData,
		              querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
		              querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,	
		              updatedgo:response.updatedgo,
		              keggchart:response.keggchart,
		              foundHits:response.foundHits,
		              fastafilename:response.fastafilename
		            }
		            this.router.navigate(['/results/']);
	        	
	        	} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
	        	}
	      	}, error=>{
	        this.errorStr = error;
	      	})

		} else if (this.loadQuery.includes('detailinformation_')) {
			this.location.go('/detailinformation/')
			let userQuery=this.loadQuery.split('_');
			let resFile=userQuery.slice(3,).join('_');
			this._qmpkb.receiveDataFromBackendSearch('/detailinformationapi/?uniProtKb=' + userQuery[2]+
				'&fileName='+ resFile +'&fastafilename='+userQuery[1]
				).subscribe((response: any)=>{
				let resultFilePath= response.resultFilePath;
				let proteinName=response.proteinName;
		    	let geneName=response.geneName;
		    	let uniprotkb=response.uniprotkb;
		    	let foundHits=response.foundHits;
				let orthologData=response.orthologData;
				let subcell=response.subcell;
				let humanDiseaseUniProt = response.humanDiseaseUniProt;
				let humanDiseaseDisGeNet = response.humanDiseaseDisGeNet;
				let drugBankData = response.drugBankData;
				let fastafilename = response.fastafilename;
				let orgID = response.orgID;

				if (foundHits > 0){ 
		            this._qmpkb.queryStorage={
		            	resultFilePath:resultFilePath,
						proteinName:proteinName,
						geneName:geneName,
						uniprotkb:uniprotkb,
						foundHits:foundHits,
						orthologData:orthologData,
						subcell:subcell,
						humanDiseaseUniProt:humanDiseaseUniProt,
						humanDiseaseDisGeNet:humanDiseaseDisGeNet,
						drugBankData:drugBankData,
						fastafilename:fastafilename,
						orgID:orgID
		            }
		            this.router.navigate(['/detailinformation/']);
				} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
				}
			}, error=>{
				this.errorStr = error;
			})
		}  else if (this.loadQuery.includes('pathwayview_')) {
			this.location.go('/pathwayview/')
			let pathwayviewArray=this.loadQuery.split('_');
			this._qmpkb.receiveDataFromBackendSearch('/pathwayviewapi/?Uniprotkb=' + pathwayviewArray[1]+
				'&organismid='+ pathwayviewArray[3]+
				'&pathwayid='+ pathwayviewArray[2]+
				'&pathwayname='+ pathwayviewArray[4]
				).subscribe((response: any)=>{
				let uniprotid= response.uniprotid
				let uniprotname= response.uniprotname
				let keggimagedict=response.keggimagedict
				let otherkeggcolor = response.otherkeggcolor
				let notpresentkeggcolor = response.notpresentkeggcolor
				let reachable = response.reachable
				if (reachable != false) {
		            this._qmpkb.queryStorage={
						uniprotid:uniprotid,
						uniprotname:uniprotname,
						keggimagedict:keggimagedict,
						otherkeggcolor:otherkeggcolor,
						notpresentkeggcolor:notpresentkeggcolor,
						reachable :reachable
		            }
		            this.router.navigate(['/pathwayview/']);
				} else {
			        this.spinner.hide();
			        if(this.alertIsVisible){
			          return;
			        }
			        this.alertIsVisible=true;
			        setTimeout(()=>{
			          this.alertIsVisible=false;
			           this.router.navigate(['/']);
			        },2000);
				}
			}, error=>{
				this.errorStr = error;
			})
		}

	})
  }

}
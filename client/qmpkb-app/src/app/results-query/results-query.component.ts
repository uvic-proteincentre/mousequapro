import { Component, OnInit, Input, Renderer } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import { NgxSpinnerService } from 'ngx-spinner';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-results-query',
  templateUrl: './results-query.component.html',
  styleUrls: ['./results-query.component.css']
})
export class ResultsQueryComponent implements OnInit {

  loadQuery:any;
  @Input()
  inputQuery:any;
  inputQueryStatus=0;
  inputFastaQuery:any;
  inputFastaQueryStatus=0;
  errorStr:Boolean;
  public alertIsVisible:boolean= false;
  public alertIsVisibleValidQuery:boolean=false;
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private renderer: Renderer,
    private _qmpkb:QmpkbService,
    private spinner: NgxSpinnerService
  ) { }

  async  getQuery(){
    await this.route.queryParams.subscribe(params=>{
      this.loadQuery =params;
      if (Object.keys(this.loadQuery).length > 0){
        this.spinner.show();
        setTimeout(() => {
          this.getProteinData(this.loadQuery);
        }, 100); 
      } else {
        this.spinner.hide();
        if(this.alertIsVisible){
          return;
        }
        this.alertIsVisible=true;
        setTimeout(()=>{
          this.alertIsVisible=false;
          this.router.navigate(['/']);
        },5000);
      }
    })
  }
  getProteinData(queryData:any){
    const queryParameters=Object.keys(this.loadQuery);
    if (queryParameters[0]=='searchterm' && Object.keys(queryParameters).length) {
      if (this.loadQuery.searchterm.trim().length >0 ){
        this._qmpkb.receiveDataFromBackendSearch('/resultsapi/?searchterm=' +this.loadQuery.searchterm).subscribe((response: any)=>{
            if (response.filename_proteincentric != null){
                this.inputQuery={
                  searchterm: this.loadQuery.searchterm,
                  filepath: response.filename_proteincentric,
                  totallist: response.totallist,
                  unqisostat: response.unqisostat,
                  subcell:response.subcell,
                  humandisease:response.humandisease,
                  updatedgo:response.updatedgo,
                  querystrainData:response.querystrainData,
                  querybioMatData:response.querybioMatData,
                  querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
                  querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,
                  keggchart:response.keggchart,
                  foundHits:response.foundHits
                };
                this.inputQueryStatus=1;
            } else {
              this.spinner.hide();
              if(this.alertIsVisible){
                return;
              }
              this.alertIsVisible=true;
              setTimeout(()=>{
                this.alertIsVisible=false;
                this.router.navigate(['/']);
              },5000);
            }
          }, error=>{
            this.errorStr = error;
          })
        } else{
            this.spinner.hide();
            if(this.alertIsVisibleValidQuery){
              return;
            }
            this.alertIsVisibleValidQuery=true;
            setTimeout(()=>{
              this.alertIsVisibleValidQuery=false;
              this.router.navigate(['/']);
            },5000); 
        }
      } else {
       let buildAdvancedFormData=[];
       const advanceQueryParmsArray=['uniProtKBAccession','protein','gene','pepSeq','panel','strain','mutant','sex','biologicalMatrix','subCellLoc','keggPathway','disCausMut','goId','goTerm','goAspects','drugId','fastaFileName'];
       const userAdvanceQuery=Object.keys(this.loadQuery);
       for(let i=0; i<Object.keys(userAdvanceQuery).length;i++){
           if (advanceQueryParmsArray.includes(userAdvanceQuery[i]) && this.loadQuery[userAdvanceQuery[i]].trim().length>0){
              if (userAdvanceQuery[i]=='panel' || userAdvanceQuery[i]=='strain' ||userAdvanceQuery[i]=='mutant' || userAdvanceQuery[i]=='sex' || userAdvanceQuery[i]=='biologicalMatrix'){
                buildAdvancedFormData.push({selectInput:userAdvanceQuery[i],whereInput:this.loadQuery[userAdvanceQuery[i]].split('|')});
              } else{
                if (userAdvanceQuery[i] =='fastaFileName'){
                  if(this.loadQuery[userAdvanceQuery[i]] !== undefined){
                    buildAdvancedFormData.push({selectInput:userAdvanceQuery[i],whereInput:this.loadQuery[userAdvanceQuery[i]]});
                  }
                } else{
                  buildAdvancedFormData.push({selectInput:userAdvanceQuery[i],whereInput:this.loadQuery[userAdvanceQuery[i]]});
                }
              }
           }
       }
       let advancedFormData={
          queryformData:
            {optionGroups:buildAdvancedFormData
            }
        }
        if (Object.keys(buildAdvancedFormData).length>0){
          this._qmpkb.receiveDataFromBackendSearch('/advanceresultsapi/?advancedFormData=' + JSON.stringify(advancedFormData)).subscribe((response: any)=>{
            if (response.filename_proteincentric != null){
              if (response.unqfastaseqlen >0 ){
                this.inputFastaQuery={
                  searchterm: response.query,
                  filepath: response.filename_proteincentric,
                  totallist: response.totallist,
                  unqisostat: response.unqisostat,
                  subcell:response.subcell,
                  humandisease:response.humandisease,
                  updatedgo:response.updatedgo,
                  querystrainData:response.querystrainData,
                  querybioMatData:response.querybioMatData,
                  querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
                  querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,            
                  keggchart:response.keggchart,
                  foundHits:response.foundHits,
                  fastafilename:response.fastafilename
                };
                this.inputFastaQueryStatus=1;
              } else {
                this.inputQuery={
                  searchterm: response.query,
                  filepath: response.filename_proteincentric,
                  totallist: response.totallist,
                  unqisostat: response.unqisostat,
                  subcell:response.subcell,
                  humandisease:response.humandisease,
                  updatedgo:response.updatedgo,
                  querystrainData:response.querystrainData,
                  querybioMatData:response.querybioMatData,
                  querynoOfDiseaseAssProt:response.querynoOfDiseaseAssProt,
                  querynoOfHumanOrtholog:response.querynoOfHumanOrtholog,
                  keggchart:response.keggchart,
                  foundHits:response.foundHits
                };
                this.inputQueryStatus=1;
              }
            } else {
              this.spinner.hide();
              if(this.alertIsVisible){
                return;
              }
              this.alertIsVisible=true;
              setTimeout(()=>{
                this.alertIsVisible=false;
                 this.router.navigate(['/']);
              },5000);
            }
      }, error=>{
        this.errorStr = error;
        })
      } else{
          this.spinner.hide();
          if(this.alertIsVisibleValidQuery){
            return;
          }
          this.alertIsVisibleValidQuery=true;
          setTimeout(()=>{
            this.alertIsVisibleValidQuery=false;
            this.router.navigate(['/']);
          },5000);
      }
    }
  }
  ngOnInit() {
    this.getQuery();
  }

}

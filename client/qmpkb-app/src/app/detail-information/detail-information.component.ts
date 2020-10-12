import { Component, OnInit, OnDestroy, ViewChild, Renderer, HostListener} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";
declare var jquery: any;

@Component({
  selector: 'app-detail-information',
  templateUrl: './detail-information.component.html',
  styleUrls: ['./detail-information.component.css']
})
export class DetailInformationComponent implements OnInit {
  loadQuery:any;
  dtOptionsortholog:any ={};
  dtOptionsSubCell: any = {};
  dtOptionsDisease: any = {};
  dtOptionsDrugBank: any = {};
  diseaseQuery:any;
  errorStr:Boolean;
  proteinName:any;
  geneName:any;
  uniprotkb:any;
  foundHits:number;
  orthologData:any;
  subcell:any;
  subcellArray:any;
  subCellQuery:any;
  humanDiseaseUniProt:any;
  humanDiseaseDisGeNet:any;
  drugBankData:any;
  drugbankQuery:any;
  drugBankDataArray:any;
  queryData:any;
  plotlyData:any=[];
  screenWidth:any;
  lenOfGeneExpData:any;
  goUniProtKB:any;
  geneExpUniProtKB:any;
  protVistaUniProtKB:any;
  assayQuery:any;
  concenQuery:any;
  resultFilePath:any;
  fastafilename:any;
  pathwayQueryTerm:any;
  orgID:any;
  filterredDrugBankData:any;
  filterredSubcell:any;
  filterDrugBankDataStatus=false;
  filterSubCellStatus=false;
  qsideBar:string;
  sideBarLink:string;
  strainStat:number;
  bioMatStat:number;
  assayStat:number;
  availableOtherAssayStatus=0;

  public alertIsVisible:boolean= false;

  @ViewChild(DataTableDirective)
  datatableElement: DataTableDirective;


  @HostListener('window.resize', ['$event'])

  getScreenSize(event?){
    this.screenWidth=(window.innerWidth-50)+"px";
  }

  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService,
    private renderer: Renderer,
    ) { 
      this.getScreenSize();
  }

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
    let qUniProtKB='NA';
    let qresultID='NA';
    let qseqID='NA';
    for(let i=0; i< queryParameters.length ;i++){
      if (queryParameters[i]=='uniProtKb'){
        qUniProtKB=queryData[queryParameters[i]];
      } else if (queryParameters[i]=='resultID'){
        qresultID=queryData[queryParameters[i]];
      } else if (queryParameters[i]=='seqID'){
        qseqID=queryData[queryParameters[i]];
      }
    }
    if (this.router.url.includes('#')){
      this.qsideBar=this.router.url.split('#')[1];
      this.sideBarLink=this.router.url.split('#')[0].split('?')[1];
    } else{
      this.qsideBar='NA';
      this.sideBarLink=this.router.url.split('?')[1];
    }
    if (qUniProtKB.trim().length <6 || qUniProtKB.trim() =='NA'){
        this.spinner.hide();
        if(this.alertIsVisible){
          return;
        }
        this.alertIsVisible=true;
        setTimeout(()=>{
          this.alertIsVisible=false;
           this.router.navigate(['/']);
        },5000);
    } else {
      this._qmpkb.receiveDataFromBackendSearch('/detailinformationapi/?uniProtKb=' + qUniProtKB+'&fileName='+ qresultID +'&fastafilename='+qseqID).subscribe((response: any)=>{
        this.queryData=response;
        this.foundHits=this.queryData.foundHits;
        if (this.foundHits > 0){
            this.resultFilePath=this.queryData.resultFilePath;
            this.proteinName=this.queryData.proteinName;
            this.geneName=this.queryData.geneName;
            this.uniprotkb=this.queryData.uniprotkb;
            this.orthologData=this.queryData.orthologData;
            this.subcellArray=this.queryData.subcell;
            this.subcell=this.queryData.subcell.join("; ");
            this.subCellQuery={
              subcell:this.subcell,
              subcellArray:this.subcellArray
            }
            this.humanDiseaseUniProt=this.queryData.humanDiseaseUniProt;
            this.humanDiseaseDisGeNet=this.queryData.humanDiseaseDisGeNet;
            this.drugBankDataArray=this.queryData.drugBankData;
            this.drugBankData=this.queryData.drugBankData.join("; ");
            this.drugbankQuery={
              drugBankDataArray:this.drugBankDataArray,
              drugBankData:this.drugBankData
            }
            this.fastafilename=this.queryData.fastafilename;
            this.goUniProtKB=this.uniprotkb;
            this.geneExpUniProtKB=this.uniprotkb;
            this.protVistaUniProtKB=this.uniprotkb;
            this.orgID=this.queryData.orgID;
            this.assayQuery=this.uniprotkb+'|'+this.resultFilePath+'|'+this.fastafilename;
            this.concenQuery=this.uniprotkb+'|'+this.resultFilePath;
            this.pathwayQueryTerm=this.uniprotkb;
            this.diseaseQuery={
              humanDiseaseUniProt:this.humanDiseaseUniProt,
              humanDiseaseDisGeNet:this.humanDiseaseDisGeNet

            }
            if(this.orthologData[0].pepPresentInHumanortholog == 'No' && this.orthologData[0].availableAssayInHumanortholog !='NA') {
              this.availableOtherAssayStatus=1;
            }
            this.assayStat=this.queryData.assayStat;
            this.bioMatStat=this.queryData.bioMatStat;
            this.strainStat=this.queryData.strainStat;
            let datatableElement = this.datatableElement;
            this.dtOptionsortholog = {
               searching: false,
               info: false,
               ordering: false,
               paging: false,
               autoWidth:true 
            };
            if (!this.router.url.includes('#')){
              this.spinner.hide();
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
      });
    }
  }
  ngOnInit() {
    this.getQuery();
    if (this.router.url.includes('#')){
      const link=this.router.url.split('#')[1];
      if (link.length >0){
          this.preCSS(link);
      }
    }
  }


 preCSS(hashLink:any):void {
    var self= this;
    setTimeout(()=>{
      if ($('#'+hashLink).length){
        $('#'+hashLink).css({'padding-top':'51px'});
        location.href=self.router.url;
        this.spinner.hide();
      }

    },2000);
/*    if (hashLink=='subcell' || hashLink=='pathway' || hashLink=='go' || hashLink=='disease' || hashLink=='drug'){
      setTimeout(()=>{
        if ($('#'+hashLink).length){
          $('#'+hashLink).css({'padding-top':'51px'});
          location.href=self.router.url;
          this.spinner.hide();
        }

      },5000);

    } else{
      setTimeout(()=>{
        if ($('#'+hashLink).length){
          $('#'+hashLink).css({'padding-top':'51px'});
          location.href=self.router.url;
          this.spinner.hide();
        }

      },2000);
    }*/
 }

  gethref(evt, linkName) {
      const hrefIDArray=['protein','assay','concentration','genExp','protvista','subcell','pathway','go','disease','drug']
      $('#'+linkName).css({'padding-top':'51px'});
      for(let i=0; i<hrefIDArray.length;i++){
        if(hrefIDArray[i] !==linkName){
          $('#'+hrefIDArray[i]).css({'padding-top':''});
        }
      }
  }
}

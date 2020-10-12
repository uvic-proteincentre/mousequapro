import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var jquery: any;


@Component({
  selector: 'app-pathwayview',
  templateUrl: './pathwayview.component.html',
  styleUrls: ['./pathwayview.component.css']
})
export class PathwayviewComponent implements OnInit {

  errorStr:Boolean;
  uniprotid:any;
  uniprotname:any;
  keggimagedict:any;
  keggimagedictlen:number;
  keggurl:any;
  reachable:Boolean;
  queryData:any;
  screenWidth:any;
  loadQuery:any;
  public alertIsVisible:boolean= false;

  @HostListener('window.resize', ['$event'])

  getScreenSize(event?){
    this.screenWidth=Math.round(window.innerWidth-50)+"px";
  }
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { 
        this.getScreenSize();
  }

  async  getQuery(){
    await this.route.queryParams.subscribe(params=>{
      this.loadQuery =params;
      if (Object.keys(this.loadQuery).length > 0){
        this.spinner.show();
        setTimeout(() => {
          this.getPathwayData(this.loadQuery);
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

  getPathwayData(queryData:any){
    const queryParameters=Object.keys(this.loadQuery);
    let qUniProtKB='NA';
    let qOrgID='NA';
    let qPathWayID='NA';
    let qPathWayName='NA';
    for(let i=0; i< queryParameters.length ;i++){
      if (queryParameters[i]=='Uniprotkb'){
        qUniProtKB=queryData[queryParameters[i]];
      } else if (queryParameters[i]=='organismid'){
        qOrgID=queryData[queryParameters[i]];
      } else if (queryParameters[i]=='pathwayid'){
        qPathWayID=queryData[queryParameters[i]];
      } else if (queryParameters[i]=='pathwayname'){
        qPathWayName=queryData[queryParameters[i]];
      }
    }
    if (qUniProtKB.trim().length <6 || qUniProtKB.trim() =='NA' || qOrgID.trim() !=='10090' || qOrgID.trim() =='NA' || !qPathWayID.includes('mmu')){
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
      this._qmpkb.receiveDataFromBackendSearch('/pathwayviewapi/?Uniprotkb=' + qUniProtKB+
        '&organismid='+ qOrgID+
        '&pathwayid='+ qPathWayID+
        '&pathwayname='+ qPathWayName
        ).subscribe((response: any)=>{
        this.queryData=response;
        this.reachable =this.queryData.reachable;
        if (this.reachable != false){
          this.uniprotid=this.queryData.uniprotid;
          this.uniprotname=this.queryData.uniprotname;
          this.keggimagedict=this.queryData.keggimagedict;
          this.keggurl= this.queryData.keggurl;
          this.keggimagedictlen=Object.keys(this.keggimagedict).length;
          this.spinner.hide();
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
  }

}
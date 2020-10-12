import { Component, OnInit, OnDestroy, HostListener, ViewChild,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var require: any
declare var jquery: any;

@Component({
  selector: 'app-protvista-view',
  templateUrl: './protvista-view.component.html',
  styleUrls: ['./protvista-view.component.css']
})
export class ProtvistaViewComponent implements OnInit,OnDestroy  {
  private routeSub:any;
  dtOptionsProtVista: any = {};
  mousePepStart:number;
  humanPepStart:number;
  mousePepEnd:number;
  humanPepEnd:number;
  mouseUniprotKB:any;
  humanUniprotKB:any;
  pepseq:any;
  protname:any;
  errorStr:Boolean;
  queryData:any;
  queryProtVistaUniProtKB:any;
  pepSeqMatchList:any;
  humanProtvistaQueryData:any;
  protVistaDataStatus=false;
  @Input() public href: string | undefined;
  @HostListener('click', ['$event']) public onClick(event: Event): void{
    if (!this.href || this.href === '#' || (this.href && this.href.length ===0)){
      event.preventDefault();
    }
  }
  @ViewChild(DataTableDirective)
  datatableElement: DataTableDirective;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

    @Input()
    set protVistatermQuery(protVistaUniProtKB:any){
      this.queryProtVistaUniProtKB=protVistaUniProtKB;

    }

  async  getProtVistaData(){

    await this._qmpkb.receiveDataFromBackendSearch('/seqfeaturesapi/?uniProtKb='+ this.queryProtVistaUniProtKB).subscribe((response: any)=>{
        
        this.queryData=response;
        this.pepseq=this.queryData.pepseq;
        this.mouseUniprotKB=this.queryProtVistaUniProtKB;
        this.humanUniprotKB=this.queryData.humanUniprotKB;
        this.mousePepStart=this.queryData.seqStart;
        this.humanPepStart=this.queryData.humanPepStart;
        this.mousePepEnd=this.queryData.seqEnd;
        this.humanPepEnd=this.queryData.humanPepEnd;
        this.protname= this.queryData.protname;
        this.pepSeqMatchList=this.queryData.pepSeqMatchList;
        this.humanProtvistaQueryData={
          humanUniprotKB:this.humanUniprotKB,
          humanPepStart:this.humanPepStart,
          humanPepEnd:this.humanPepEnd

        }
        this.dtOptionsProtVista = {
              searching: false,
              info: false,
              ordering: false,
              paging: false,
              autoWidth:true  
        };
        if (this.mousePepEnd > 0){
           setTimeout(() => {this.plotProtVistaMouseFunc(this.mouseUniprotKB,this.mousePepStart,this.mousePepEnd)}, 100); 
       };
       this.protVistaDataStatus=true;
      }, error=>{
        this.errorStr = error;
      })
  }

  ngOnInit() {
    this.getProtVistaData();
  }


  plotProtVistaMouseFunc(protvistaMouseUni:string,mousePreSelectStart:number,mousePreSelectEnd:number): void {
      if (mousePreSelectStart >0){
        var mouseDiv = document.getElementById('mouseDiv');
        var ProtVistaMouse = require('ProtVista');

        var mouseinstance = new ProtVistaMouse({
          el: mouseDiv,
          uniprotacc: protvistaMouseUni,
          defaultSources: true,
          //These categories will **not** be rendered at all
          exclusions: ['SEQUENCE_INFORMATION', 'STRUCTURAL', 'TOPOLOGY', 'MOLECULE_PROCESSING', 'ANTIGEN'],
          //Your data sources are defined here
          customDataSource: {
            url: 'fileapi/resultFile/jsonData/protvistadataJson/mouse/externalLabeledFeatures_',
            source: 'MouseQuaPro',
            useExtension: true
          },
          categoryOrder: ['TARGETED_PROTEOMICS_ASSAY_MOUSE', 'PROTEOMICS', 'DOMAINS_AND_SITES', 'PTM', 'MUTAGENESIS'],
          //This feature will be preselected
          selectedFeature: {
          begin: mousePreSelectStart,
          end: mousePreSelectEnd,
          type: 'MRM'
          }
        });
      }
  }
  ngOnDestroy(){
      this.routeSub.unsubscribe()
  }
}


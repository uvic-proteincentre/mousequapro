import { Component, OnInit, OnDestroy,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-assay',
  templateUrl: './assay.component.html',
  styleUrls: ['./assay.component.css']
})
export class AssayComponent implements OnInit {
  dtOptionsSummary: any = {};
  dtOptionsGrad: any = {};
  dtOptionsTrans:any ={};
  dtOptionsLOQ:any ={};
  errorStr:Boolean;
  transdic: any;
  transdiclen: number;
  gradientlist:any;
  gradientlistlen:number;
  gradinfoheader:any;
  loquantinfo:any;
  foundHits:number;
  protinfo:any
  queryData:any;
  assayInputData:any;
  assayDataStatus=false;
  userFastaStatus:number;
  fastafilename:any;
  assayuniProtKb:any;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set assaytermQuery(assayQuery:any){
      this.assayInputData=assayQuery;

  }

  ngOnInit() {
      let assayQueryArray=this.assayInputData.split('|');
      this._qmpkb.receiveDataFromBackendSearch('/assaydetailsapi/?resultFilePath=' + assayQueryArray[1]+'&uniProtKb='+ assayQueryArray[0]+'&fastafilename='+assayQueryArray[2]).subscribe((response: any)=>{
        this.queryData=response;
        this.transdic=this.queryData.transdic;
        this.gradientlist=this.queryData.gradientlist;
        this.gradinfoheader=this.queryData.gradinfoheader;
        this.loquantinfo=this.queryData.loquantinfo;
        this.foundHits=this.queryData.foundHits;
        this.userFastaStatus=this.queryData.userFastaStatus;
        this.protinfo=this.queryData.protinfo;
        this.fastafilename=this.queryData.fastafilename;
        this.transdiclen=Object.keys(this.transdic).length;
        this.gradientlistlen=Object.keys(this.gradientlist).length;
        this.assayuniProtKb=assayQueryArray[0];
        this.assayDataStatus=true;
        this.dtOptionsSummary = {
          orderCellsTop: true,
          fixedHeader: true,
          pageLength: 10,
          pagingType: 'full_numbers',
          scrollX:true,
          scrollY:'650px',
          scrollCollapse:true,
          autoWidth:true,
          dom: 'lBfrtip',
          buttons: [
              {
                extend:'csv',
                filename: 'PeptideInformationMouseQuaPro',
                text:'Download all(CSV)'
              },
              {
                extend:'excel',
                filename: 'PeptideInformationMouseQuaPro',
                text:'Download all(Excel)'
              }
          ]

        };
        this.dtOptionsGrad = {
          orderCellsTop: true,
          fixedHeader: true,
          pageLength: 10,
          pagingType: 'full_numbers',
          scrollX:true,
          scrollY:'650px',
          scrollCollapse:true,
          autoWidth:true,
          dom: 'lBfrtip',
          buttons: [
              {
                extend:'csv',
                filename: 'GradientsMouseQuaPro',
                text:'Download all(CSV)'
              },
              {
                extend:'excel',
                filename: 'GradientsMouseQuaPro',
                text:'Download all(Excel)'
              }
          ],
/*          columnDefs:[{
            type: 'na',
            targets: 3
          }]*/

        };
        this.dtOptionsLOQ = {
          orderCellsTop: true,
          fixedHeader: true,
          pageLength: 10,
          pagingType: 'full_numbers',
          scrollX:true,
          scrollY:'650px',
          scrollCollapse:true,
          autoWidth:true,
          dom: 'lBfrtip',
          buttons: [
              {
                extend:'csv',
                filename: 'LimitofquantificationMouseQuaPro',
                text:'Download all(CSV)'
              },
              {
                extend:'excel',
                filename: 'LimitofquantificationMouseQuaPro',
                text:'Download all(Excel)'
              }
          ]

        };
        this.dtOptionsTrans = {
          orderCellsTop: true,
          fixedHeader: true,
          pageLength: 10,
          pagingType: 'full_numbers',
          scrollX:true,
          scrollY:'650px',
          scrollCollapse:true,
          autoWidth:true,
          dom: 'lBfrtip',
          buttons: [
              {
                extend:'csv',
                filename: 'TransitionMouseQuaPro',
                text:'Download all(CSV)'
              },
              {
                extend:'excel',
                filename: 'TransitionMouseQuaPro',
                text:'Download all(Excel)'
              }
          ]

        };

      }, error=>{
        this.errorStr = error;
      })

  }

  private openTabsAssay(evt, tabName) {
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontentassay");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablinksassay");
      for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";
  }
}

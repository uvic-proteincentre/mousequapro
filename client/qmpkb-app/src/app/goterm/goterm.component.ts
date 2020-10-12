import { Component, OnInit, OnDestroy,Input,ViewChildren, QueryList, ElementRef} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { Subject } from 'rxjs';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";
declare var jquery: any;

@Component({
  selector: 'app-goterm',
  templateUrl: './goterm.component.html',
  styleUrls: ['./goterm.component.css']
})
export class GotermComponent implements OnInit {

  dtOptions: any = {};
  errorStr:Boolean;
  foundHits:number;
  contextgoterminfo:any
  contextgoterminfolen:number;
  goStat:any;
  queryGoUniProtKB:any;
  goDataStatus=false;
  queryData:any;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set gotermQuery(goUniProtKB:any){
      this.queryGoUniProtKB=goUniProtKB;

  }
  ngOnInit() {
  }

  ngAfterViewInit(): void {
    this._qmpkb.receiveDataFromBackendSearch('/gotermapi/?uniProtKb='+ this.queryGoUniProtKB).subscribe((response: any)=>{
      this.goDataStatus=true;
      this.queryData=response;
      this.foundHits=this.queryData.foundHits;
      this.contextgoterminfo=this.queryData.contextgoterminfo;
      this.contextgoterminfolen=Object.keys(this.contextgoterminfo).length;
      this.goStat=this.queryData.goStat;
      this.dtOptions = {
        processing: true,
        serverSide: false,
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 10,
        pagingType: 'full_numbers',
        scrollX:true,
        scrollY:'650px',
        scrollCollapse:true,
        // Declare the use of the extension in the dom parameter
        dom: 'lBfrtip',
        buttons: [
            {
              extend:'csv',
              filename: 'GeneOntologyMouseQuaPro',
              text:'Download all(CSV)'
            },
            {
              extend:'excel',
              filename: 'GeneOntologyMouseQuaPro',
              text:'Download all(Excel)'
            }
        ],
        autoWidth:true  
       };
    }, error=>{
      this.errorStr = error;
    })

  }
}

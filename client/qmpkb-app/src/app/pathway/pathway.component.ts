import { Component, OnInit, OnDestroy,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

@Component({
  selector: 'app-pathway',
  templateUrl: './pathway.component.html',
  styleUrls: ['./pathway.component.css']
})
export class PathwayComponent implements OnInit {
  dtOptions: any = {};
  errorStr:Boolean;
  keggData:any;
  keggDatalen:number;
  pathwayInputData:any;
  pathwayDataStatus=false;
  queryData:any;

  pathViewUniprotid:any;
  pathViewUniprotname:any;
  keggimagedict:any;
  keggimagedictlen:number;
  otherkeggcolor:any;
  notpresentkeggcolor:any;
  screenWidth:any;

  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set pathwaytermQuery(pathQuery:any){
      this.pathwayInputData=pathQuery;

  }

  ngOnInit() {

    this._qmpkb.receiveDataFromBackendSearch('/pathwayapi/?uniProtKb='+ this.pathwayInputData).subscribe((response: any)=>{
        this.queryData=response;
        this.keggData=this.queryData.pathWayList;
        this.keggDatalen=Object.keys(this.keggData).length;
        this.pathwayDataStatus=true;
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
                filename: 'PathwayMouseQuaPro',
                text:'Download all(CSV)'
              },
              {
                extend:'excel',
                filename: 'PathwayMouseQuaPro',
                text:'Download all(Excel)'
              }
          ],
          autoWidth:true  
         };
    }, error=>{
        this.errorStr = error;
    });
  }
  
}




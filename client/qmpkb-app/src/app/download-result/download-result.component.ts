import { Component, OnInit, OnDestroy,Input,Renderer} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

@Component({
  selector: 'app-download-result',
  templateUrl: './download-result.component.html',
  styleUrls: ['./download-result.component.css']
})
export class DownloadResultComponent implements OnInit {

  downloadResultJsonPath:any;
  downloadResultStatus=false;
  downloadPathLink:any;
  queryData:any;
  errorStr:Boolean;

  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private _qmpkb:QmpkbService,
    private renderer: Renderer,
    ) { 
  }

  @Input()
  set downloadTermQuery(dQuery:any){
      this.downloadResultJsonPath=dQuery;

  }

  async  getDownloadFileLink(){
    await this._qmpkb.receiveDataFromBackendSearch('/downloadapi/?jsonfile=' + this.downloadResultJsonPath).subscribe((response: any)=>{
      
      this.queryData=response;
      this.downloadPathLink='fileapi/resultFile/downloadResult/search/'+this.queryData.downloadFileName;

       this.downloadResultStatus=true;
    }, error=>{
      this.errorStr = error;
    })

  }
  ngOnInit() {
  	this.getDownloadFileLink();
  }

}

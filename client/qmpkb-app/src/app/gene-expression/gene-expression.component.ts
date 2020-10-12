import { Component, OnInit, OnDestroy, ViewChild, Renderer, HostListener,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as Plotly from 'plotly.js';
import { Subject } from 'rxjs';
import * as $ from "jquery";
declare var jquery: any;

@Component({
  selector: 'app-gene-expression',
  templateUrl: './gene-expression.component.html',
  styleUrls: ['./gene-expression.component.css']
})
export class GeneExpressionComponent  implements OnInit {

  dtOptions: any = {};
  errorStr:Boolean;
  geneExplist:any;
  geneExplistlen:number;
  foundHits:number;
  protList:any
  queryData:any;
  plotlyData:any=[];
  screenWidth:any;
  lenOfGeneExpData:any;
  queryGeneExpUniProtKB:any;
  geneExpDataStatus=false;
  @ViewChild(DataTableDirective)
  datatableElement: DataTableDirective;

  plotDataOptions=[
       {num:0, name:'Concentration Data'},
       {num:1, name:'Log2(Concentration Data)'},
       {num:2, name:'Log10(Concentration Data)'},
  ];
  selectedLevel=this.plotDataOptions[0];

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

  @Input()
  set geneexptermQuery(geneExpUniProtKB:any){
      this.queryGeneExpUniProtKB=geneExpUniProtKB;

  }
  async  generateTable(){
    await this._qmpkb.receiveDataFromBackendSearch('/geneexpapi/?uniProtKb=' + this.queryGeneExpUniProtKB).subscribe((response: any)=>{
      
      this.queryData=response;
      this.geneExplist=this.queryData.geneExplist;
      this.geneExplistlen=Object.keys(this.geneExplist).length
      this.foundHits=this.queryData.foundHits;
      this.protList=this.queryData.protList;
      this.lenOfGeneExpData= this.queryData.lenOfGeneExpData;
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
        columnDefs:[
          {
            targets: 0,
            data: null,
            defaultContent: '',
            orderable: false,
            className: 'select-checkbox',
            searchable:false
          },
          {
            targets: 1,
            searchable:false,
            visible:false
          },
          {
            targets: 2,
            searchable:false,
            visible:false
          }
        ],
        select:{
          style:'multi'
        },
        // Declare the use of the extension in the dom parameter
        dom: 'lBfrtip',
        buttons: [
            {
              extend:'csv',
              filename: 'GeneExpressionMouseQuaPro',
              text:'Download all(CSV)',
              exportOptions:{
                columns:[1,2,3,4]
              }
            },
            {
              extend:'excel',
              filename: 'GeneExpressionQMPKB',
              text:'Download all(Excel)',
              exportOptions:{
                columns:[1,2,3,4]
              }
            },
            'selectAll',
            'selectNone'
        ],
        order: [],
        autoWidth:true
      };
      if (this.lenOfGeneExpData > 0){
           setTimeout(() => {this.dataTableGenerated()}, 100); 
       }
       this.geneExpDataStatus=true;
    }, error=>{
      this.errorStr = error;
    })

  }
  ngOnInit() {
     this.generateTable();
  }

  dataTableGenerated(): void {
    const self = this;
    self.datatableElement.dtInstance.then((dtInstance:any) => {
      
      dtInstance.rows(function(idx,data){
        const plotName=data[3];
        const plotData=data[4];
        const tempPlotArray=[plotName,plotData];
        self.plotlyData.push(tempPlotArray.join(';'));
        return idx >=0;
      }).select();
      self.barplot(self.plotlyData);
    });
     self.datatableElement.dtInstance.then(table => {
      $('#dataTables-wrkld-geneExp').on('select.dt', function (e,dt,type,indexes) {
        if (self.lenOfGeneExpData == indexes.length){
           self.plotlyData=[];
           for(let j=0; j< indexes.length;j++){
              const plotName=dt.row(indexes[j]).data()[3];
              const plotData=dt.row(indexes[j]).data()[4];
              const tempPlotArray=[plotName,plotData];
              self.plotlyData.push(tempPlotArray.join(';'));
           }
           self.barplot(self.plotlyData);

        } else {
          const plotName=dt.row(indexes[0]).data()[3];
          const plotData=dt.row(indexes[0]).data()[4];
          const tempPlotArray=[plotName,plotData];
          self.plotlyData.push(tempPlotArray.join(';'));
          self.barplot(self.plotlyData);          
        }

        
      });
      $('#dataTables-wrkld-geneExp').on('deselect.dt', function (e,dt,type,indexes) {
        if (self.lenOfGeneExpData == indexes.length || indexes.length>1 || self.plotlyData == indexes.length){
            self.plotlyData=[];
            self.barplot(self.plotlyData);
        } else {
          const plotName=dt.row(indexes[0]).data()[3];
          const plotData=dt.row(indexes[0]).data()[4];
          const tempPlotArray=[plotName,plotData];
          const indexOfplotlyData=self.plotlyData.indexOf(tempPlotArray.join(';'));
          self.plotlyData.splice(indexOfplotlyData,1);
          self.barplot(self.plotlyData);          
        }

      });
    });


  }

  barplot(dataToPlot:any):void {
      let defaultPlotlyConfiguration:any={};
      defaultPlotlyConfiguration ={
        scrollZoom: true, // lets us scroll to zoom in and out - works
        showTips:true,
        modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d','toImage','pan', 'pan2d','zoom2d','toggleSpikelines'],
        //modeBarButtonsToAdd: ['lasso2d'],
        displayLogo: false, // this one also seems to not work
      };
      let xAxisData=[];
      let yAxisData=[];
      for(let i=0; i< dataToPlot.length;i++){
        const tempPlotDataArray=dataToPlot[i].split(';');
        xAxisData.push(tempPlotDataArray[0])
        yAxisData.push(tempPlotDataArray[1])
      }
    let expPlotData=[];
    const expTraceData={
      x:xAxisData,
      y:yAxisData,
      type:'bar',
      marker:{
        color:'rgb(142,124,195)'
      }
    }
    expPlotData=[expTraceData];
    const layout={
      title:'Gene Expression',
      font:{
        family:'Raleway, sans-serif'
      },
      showlegend:false,
      xaxis:{
        tickangle:-45
      },
      yaxis:{
        title:'Mean RPKM',
        zeroline:false,
        gridwidth:2
      },
      bargap:0.05
    }


    Plotly.newPlot('myDivGeneExp',expPlotData,layout,defaultPlotlyConfiguration);

    if (dataToPlot.length==0){
      Plotly.purge('myDivGeneExp')
    }
  }
}

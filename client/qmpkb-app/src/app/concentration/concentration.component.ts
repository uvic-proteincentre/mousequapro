import { Component, OnInit, OnDestroy, ViewChild, Renderer, HostListener} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as Plotly from 'plotly.js';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-concentration',
  templateUrl: './concentration.component.html',
  styleUrls: ['./concentration.component.css']
})
export class ConcentrationComponent implements OnInit {
  dtOptions: any = {};
  errorStr:Boolean;
  conclist:any;
  conclistlen:number;
  foundHits:number;
  sampleConcUnit:string;
  protList:any
  queryData:any;
  plotlyData:any=[];
  lenOfConcData:any;
  screenWidth:any;
  finalPlotData:any={};
  wildObj={
    'Wild type':'WT'
  };
  sexObj={
    'Male':'M',
    'Female':'F'
  };
  @ViewChild(DataTableDirective)
  datatableElement: DataTableDirective;

  plotDataOptions=[
       {num:0, name:'Concentration Data'},
       {num:1, name:'Log2(Concentration Data)'},
       {num:2, name:'Log10(Concentration Data)'},
  ];
/*  this.selectedLevel=this.plotDataOptions[0];*/
   selected=this.plotDataOptions[2];

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

  ngOnInit() {
    this.spinner.show();

    this.queryData=this._qmpkb.queryStorage;
    this.conclist=this.queryData.conclist;
    this.conclistlen=Object.keys(this.conclist).length
    this.foundHits=this.queryData.foundHits;
    this.protList=this.queryData.protList;
    this.sampleConcUnit=this.queryData.concUnit;
    this.lenOfConcData= this.queryData.lenOfConcData;
    jQuery.extend( jQuery.fn.dataTable.ext.oSort, {
        "na-asc": function (str1, str2) {
            if(str1 == "NA")
                return 1;
            else if(str2 == "NA")
                return -1;
            else{
               var fstr1 = parseFloat(str1);
               var fstr2 = parseFloat(str2);
               return ((fstr1 < str2) ? -1 : ((fstr1 > fstr2) ? 1 : 0));
            }
           
        },
     
        "na-desc": function (str1, str2) {
            if(str1 == "NA")
                return 1;
            else if(str2 == "NA")
                return -1;
            else {
              var fstr1 = parseFloat(str1);
              var fstr2 = parseFloat(str2);
              return ((fstr1 < fstr2) ? 1 : ((fstr1 > fstr2) ? -1 : 0));
            }
            
        }
    } );
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
        },
        {
          targets: 3,
          searchable:false,
          visible:false
        },
        {
          targets: 13,
          searchable:false,
          visible:false
        },
        {
          targets: 14,
          searchable:false,
          visible:false
        },
        {
          targets: 15,
          searchable:false,
          visible:false
        },        
        {
          targets: 16,
          searchable:false,
          visible:false
        },
        {
          targets: 17,
          searchable:false,
          visible:false
        },
        {type: 'na', targets: [8,9,10,11]} // define 'name' column as na type
      ],
      select:{
        style:'multi'
      },
      // Declare the use of the extension in the dom parameter
      dom: 'lBfrtip',
      buttons: [
          {
            extend:'csv',
            filename: 'ConcentrationMouseQuaPro',
            text:'Download all(CSV)',
            exportOptions:{
              columns:[1,2,3,4,5,6,7,8,9,10,11,12,15,16,17]
            }
          },
          {
            extend:'excel',
            filename: 'ConcentrationMouseQuaPro',
            text:'Download all(Excel)',
            exportOptions:{
              columns:[1,2,3,4,5,6,7,8,9,10,11,12,15,16,17]
            }
          },
          'selectAll',
          'selectNone'
      ],
      order: [],
      autoWidth:true
    };
    this.spinner.hide();
  }


  ngAfterViewInit(): void {      
    const self = this;
    self.datatableElement.dtInstance.then((dtInstance:any) => {
      
      dtInstance.rows(function(idx,data){
        const plotName=data[13].split('|');
        //plotName[0]=self.wildObj[plotName[0]];
        plotName[2]=self.sexObj[plotName[2]];
        const plotData=data[14];
        const plotDataSampleLLOQ=data[15];
        const sampleLLOQ=data[16];
        const ULOQ=data[17];
        const tempPlotArray=[plotName.join('|'),plotData,plotDataSampleLLOQ,sampleLLOQ,ULOQ];
        self.plotlyData.push(tempPlotArray.join(';'));
        return idx >=0;
      }).select();
      self.prepareDatatoPlot(self.plotlyData);
    });
     self.datatableElement.dtInstance.then(table => {
      $('#dataTables-wrkld-concentration').on('select.dt', function (e,dt,type,indexes) {
        if (self.lenOfConcData == indexes.length){
           self.plotlyData=[];
           for(let j=0; j< indexes.length;j++){
              const plotName=dt.row(indexes[j]).data()[13].split('|');
              //plotName[0]=self.wildObj[plotName[0]];
              plotName[2]=self.sexObj[plotName[2]];
              const plotData=dt.row(indexes[j]).data()[14];
              const plotDataSampleLLOQ=dt.row(indexes[j]).data()[15];
              const sampleLLOQ=dt.row(indexes[j]).data()[16];
              const ULOQ=dt.row(indexes[j]).data()[17];
              const tempPlotArray=[plotName.join('|'),plotData,plotDataSampleLLOQ,sampleLLOQ,ULOQ];
              self.plotlyData.push(tempPlotArray.join(';'));
              self.selected=self.plotDataOptions[0];
           }
           self.prepareDatatoPlot(self.plotlyData);

        } else {
          const plotName=dt.row(indexes[0]).data()[13].split('|');
          //plotName[0]=self.wildObj[plotName[0]];
          plotName[2]=self.sexObj[plotName[2]];
          const plotData=dt.row(indexes[0]).data()[14];
          const plotDataSampleLLOQ=dt.row(indexes[0]).data()[15];
          const sampleLLOQ=dt.row(indexes[0]).data()[16];
          const ULOQ=dt.row(indexes[0]).data()[17];
          const tempPlotArray=[plotName.join('|'),plotData,plotDataSampleLLOQ,sampleLLOQ,ULOQ];
          self.plotlyData.push(tempPlotArray.join(';'));
          self.prepareDatatoPlot(self.plotlyData); 
          self.selected=self.plotDataOptions[0];       
        }

        
      });
      $('#dataTables-wrkld-concentration').on('deselect.dt', function (e,dt,type,indexes) {
        if (self.lenOfConcData == indexes.length || indexes.length>1 || self.plotlyData == indexes.length){
            self.plotlyData=[];
            self.prepareDatatoPlot(self.plotlyData);
        } else {
          const plotName=dt.row(indexes[0]).data()[13].split('|');
          //plotName[0]=self.wildObj[plotName[0]];
          plotName[2]=self.sexObj[plotName[2]];
          const plotData=dt.row(indexes[0]).data()[14];
          const plotDataSampleLLOQ=dt.row(indexes[0]).data()[15];
          const sampleLLOQ=dt.row(indexes[0]).data()[16];
          const ULOQ=dt.row(indexes[0]).data()[17];
          const tempPlotArray=[plotName.join('|'),plotData,plotDataSampleLLOQ,sampleLLOQ,ULOQ];
          const indexOfplotlyData=self.plotlyData.indexOf(tempPlotArray.join(';'));
          self.plotlyData.splice(indexOfplotlyData,1);
          self.prepareDatatoPlot(self.plotlyData);
          self.selected=self.plotDataOptions[0];        
        }

      });
    });

  }


    prepareDatatoPlot(rawData:any) {
      const tissueColor= {
        "Brain":"cyan",
        "Brown Adipose":"olive",
        "Epididymis":"slategray",
        "Eye":"rosybrown", 
        "Heart":"darksalmon",
        "Kidney":"lightcoral",
        "Liver Caudate and Right Lobe":"sandybrown",
        "Liver Left Lobe":"deepskyblue",
        "Lung":"tan",
        "Pancreas":"cadetblue",
        "Plasma":"greenyellow",
        "Ovary":"goldenrod",
        "RBCs":"seagreen",
        "Salivary Gland":"chocolate",
        "Seminal Vesicles":"khaki",
        "Skeletal Muscle":"indigo",
        "Skin":"thistle",
        "Spleen":"violet",
        "Testes":"lightpink",
        "White Adipose":"plum"
      };

      let prepareDatatoPlotDataArray=[];
      let prepareDatatoPlotDataArrayLog2=[];
      let prepareDatatoPlotDataArrayLog10=[];
      const yAxisTile='Concentration<br>(fmol target protein/µg extracted protein)';
      let layout={
        yaxis:{
        title:yAxisTile,
        zeroline:false,
        showlegend: true,
        legend :{
          x:rawData.length+1
        }
       },
       xaxis:{
         automargin: true
       }
      };

      let layout2={
        yaxis:{
        title:'Concentration<br>in Log2 Scale',
        zeroline:false,
        showlegend: true,
        legend :{
          x:rawData.length+1
        }
       },
       xaxis:{
         automargin: true
       }
      };

      let layout10={
        yaxis:{
        title:'Concentration<br>in Log10 Scale',
        zeroline:false,
        showlegend: true,
        legend :{
          x:rawData.length+1
        }
       },
       xaxis:{
         automargin: true
       }
      };
      const d3colors = Plotly.d3.scale.category10();


      for(let i=0; i< rawData.length;i++){
        const tempPlotDataArray=rawData[i].split(';');
        const plotDataArray=[];
        const plotDataArrayLog2=[];
        const plotDataArrayLog10=[];
        let tempArray=tempPlotDataArray[2].split('|');
        if (tempPlotDataArray[2] === 'NA' || tempPlotDataArray[2].trim().length == 0){
          tempArray=tempPlotDataArray[1].split('|');
        }
        for(let j=0; j< tempArray.length;j++){
           plotDataArray.push(parseFloat(tempArray[j]));
           plotDataArrayLog2.push(Math.log2(parseFloat(tempArray[j])));
           plotDataArrayLog10.push(Math.log10(parseFloat(tempArray[j])));
        }
        let prepareDatatoPlotData={};
        let prepareDatatoPlotDataLog2={};
        let prepareDatatoPlotDataLog10={};

        let boxSamLLOQData={};
        let boxSamLLOQDataLog2={};
        let boxSamLLOQDataLog10={};

        let boxULOQData={};
        let boxULOQDataLog2={};
        let boxULOQDataLog10={};

        let tempplotDataArray=plotDataArray.filter(value=> !Number.isNaN(value));
        if (tempPlotDataArray[2] === 'NA' || tempPlotDataArray[2].trim().length == 0){
          if (tempplotDataArray.length > 0){
            prepareDatatoPlotData={
              y:plotDataArray,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              type:'box',
              marker:{
                color:'black'
              },
              fillcolor:'rgba(0,0,0,0)',
              line:{
                color:'rgba(0,0,0,0)'
              },
              hoverinfo:'skip'
            };
            prepareDatatoPlotDataLog2={
              y:plotDataArrayLog2,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              type:'box',
              marker:{
                color:'black'
              },
              fillcolor:'rgba(0,0,0,0)',
              line:{
                color:'rgba(0,0,0,0)'
              },
              hoverinfo:'skip'
            };
            prepareDatatoPlotDataLog10={
              y:plotDataArrayLog10,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              type:'box',
              marker:{
                color:'black'
              },
              fillcolor:'rgba(0,0,0,0)',
              line:{
                color:'rgba(0,0,0,0)'
              },
              hoverinfo:'skip'
            };
          }

        } else {
          if (tempplotDataArray.length > 0){
            const tempColor=tissueColor[tempPlotDataArray[0].split('|')[0]];
            prepareDatatoPlotData={
              y:plotDataArray,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              boxmean:true,
              marker:{
                color:tempColor
              },
              type:'box'
            };
            prepareDatatoPlotDataLog2={
              y:plotDataArrayLog2,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              boxmean:true,
              marker:{
                color:tempColor
              },
              type:'box'
            };
            prepareDatatoPlotDataLog10={
              y:plotDataArrayLog10,
              name: tempPlotDataArray[0],
              boxpoints: 'all',
              jitter: 0,
              pointpos: 0,
              boxmean:true,
              marker:{
                color:tempColor
              },
              type:'box'
            };
          }
        }

        if (tempplotDataArray.length > 0){
            boxSamLLOQData={
              x:[tempPlotDataArray[0]],
              y:[parseFloat(tempPlotDataArray[3])],
              text: 'Sample LLOQ',
              marker:{
                color:'red',
                symbol:'triangle-up',
                size:8
              },
              showlegend:false
            };


            boxSamLLOQDataLog2={
              x:[tempPlotDataArray[0]],
              y:[Math.log2(parseFloat(tempPlotDataArray[3]))],
              text: 'Sample LLOQ',
              marker:{
                color:'red',
                symbol:'triangle-up',
                size:8
              },
              showlegend:false
            };

            boxSamLLOQDataLog10={
              x:[tempPlotDataArray[0]],
              y:[Math.log10(parseFloat(tempPlotDataArray[3]))],
              text: 'Sample LLOQ',
              marker:{
                color:'red',
                symbol:'triangle-up',
                size:8
              },
              showlegend:false
            };

            boxULOQData={
              x:[tempPlotDataArray[0]],
              y:[parseFloat(tempPlotDataArray[4])],
              text: 'ULOQ',
              marker:{
                color:'red',
                symbol:'triangle-down',
                size:8
              },
              showlegend:false
            };


            boxULOQDataLog2={
              x:[tempPlotDataArray[0]],
              y:[Math.log2(parseFloat(tempPlotDataArray[4]))],
              text: 'ULOQ',
              marker:{
                color:'red',
                symbol:'triangle-down',
                size:8
              },
              showlegend:false
            };

            boxULOQDataLog10={
              x:[tempPlotDataArray[0]],
              y:[Math.log10(parseFloat(tempPlotDataArray[4]))],
              text: 'ULOQ',
              marker:{
                color:'red',
                symbol:'triangle-down',
                size:8
              },
              showlegend:false
            };

          prepareDatatoPlotDataArray.push(prepareDatatoPlotData);
          prepareDatatoPlotDataArray.push(boxSamLLOQData);
          prepareDatatoPlotDataArray.push(boxULOQData);
          prepareDatatoPlotDataArrayLog2.push(prepareDatatoPlotDataLog2);
          prepareDatatoPlotDataArrayLog2.push(boxSamLLOQDataLog2);
          prepareDatatoPlotDataArrayLog2.push(boxULOQDataLog2);
          prepareDatatoPlotDataArrayLog10.push(prepareDatatoPlotDataLog10);
          prepareDatatoPlotDataArrayLog10.push(boxSamLLOQDataLog10);
          prepareDatatoPlotDataArrayLog10.push(boxULOQDataLog10);
        }
      }

     let finalprepareDatatoPlotDataArray={
       0:prepareDatatoPlotDataArray,
       1:prepareDatatoPlotDataArrayLog2,
       2:prepareDatatoPlotDataArrayLog10
     }

      let defaultPlotlyConfiguration={};
      defaultPlotlyConfiguration ={
        responsive: true,
        scrollZoom: true,
        showTips:true,
        modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d','toImage','pan', 'pan2d','zoom2d','toggleSpikelines'],
        displayLogo: false
      };

      this.finalPlotData={
        'plotData':finalprepareDatatoPlotDataArray,
        'plotLayout':[layout,layout2,layout10],
        'config':defaultPlotlyConfiguration
      };
      Plotly.newPlot('myDivConc',finalprepareDatatoPlotDataArray[2],layout10,defaultPlotlyConfiguration);

      if (rawData.length==0){
        Plotly.purge('myDivConc')
      }
    }
  onOptionsSelected(event){
      if(event.target){
        let tempPlotData=this.finalPlotData['plotData'];
        let tempPlotLayout=this.finalPlotData['plotLayout'];
        let tempConfig=this.finalPlotData['config'];
        if (this.selected.name == 'Concentration Data'){
          Plotly.purge('myDivConc')
          Plotly.newPlot('myDivConc',tempPlotData[0],tempPlotLayout[0],tempConfig)
        }

        if (this.selected.name == 'Log2(Concentration Data)'){
          Plotly.purge('myDivConc')
          Plotly.newPlot('myDivConc',tempPlotData[1],tempPlotLayout[1],tempConfig)
        }

        if (this.selected.name == 'Log10(Concentration Data)'){
          Plotly.purge('myDivConc')
          Plotly.newPlot('myDivConc',tempPlotData[2],tempPlotLayout[2],tempConfig)
        }
        
      }
    }

}

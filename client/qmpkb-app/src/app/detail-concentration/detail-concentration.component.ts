
import { Component, OnInit, OnDestroy, ViewChild, Renderer, HostListener,Input} from '@angular/core';
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
  selector: 'app-detail-concentration',
  templateUrl: './detail-concentration.component.html',
  styleUrls: ['./detail-concentration.component.css']
})
export class DetailConcentrationComponent implements OnInit {

  dtOptions: any = {};
  dtOptionsOther: any = {};
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
  queryConcen:any;
  strainData:any;
  knockoutData:any;
  bioMatData:any;
  sexData:any;
  allConcSamLLOQ:any;
  allConc:any;
  concenPlotlyData:any=[];
  concenPlotDataUnit: string;
  bioMatDataTableData:any=[];
  bioMatDataLen=0;
  strainDataTableData:any=[];
  strainDataLen=0;
  sexDataTableData:any=[];
  sexDataLen=0;
  knockoutDataTableData:any=[];
  knockoutDataLen=0;
  concenDataStatus=false;
/*  cocenDataTypeObj={
    'biomat':[this.bioMatData,0],
    'str':['strainData',1],
    'knock':['knockoutData',1],
    'sex':['sexData',1]

  }*/
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

  @Input()
  set concentermQuery(concenQuery:any){
      this.queryConcen=concenQuery;

  }
  async getConcenData(){
  	let queryConcenArray=this.queryConcen.split('|');
    await this._qmpkb.receiveDataFromBackendSearch('/detailConcentrationapi/?uniProtKb=' + queryConcenArray[0]+ '&resultFilePath=' + queryConcenArray[1]).subscribe((response: any)=>{
      
      this.queryData=response;
      this.conclist=this.queryData.conclist;
      this.strainData=this.queryData.strainData;
      this.knockoutData=this.queryData.knockoutData;
      this.bioMatData=this.queryData.bioMatData;
      this.sexData=this.queryData.sexData;
      this.allConcSamLLOQ=this.queryData.allConcSamLLOQ;
      this.allConc=this.queryData.allConc;
      this.conclistlen=Object.keys(this.conclist).length
      this.foundHits=this.queryData.foundHits;
      this.sampleConcUnit=this.queryData.concUnit;
      this.lenOfConcData= this.queryData.lenOfConcData;

      jQuery.extend( jQuery.fn.dataTable.ext.oSort, {
          "na-asc": function (str1, str2) {
              if(str1 == "NA" || str1.includes('Sample'))
                  return 1;
              else if(str2 == "NA" || str2.includes('Sample') )
                  return -1;
              else{
                 var fstr1 = parseFloat(str1);
                 var fstr2 = parseFloat(str2);
                 return ((fstr1 < str2) ? -1 : ((fstr1 > fstr2) ? 1 : 0));
              }
             
          },
       
          "na-desc": function (str1, str2) {
              if(str1 == "NA" || str1.includes('Sample'))
                  return 1;
              else if(str2 == "NA" || str2.includes('Sample'))
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
/*          {
            targets: 3,
            searchable:false,
            visible:false
          },*/
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
      this.dtOptionsOther = {
        orderCellsTop: true,
        fixedHeader: true,
        pageLength: 10,
        pagingType: 'full_numbers',
        scrollX:true,
        scrollY:'650px',
        scrollCollapse:true,
        autoWidth:true,
        columnDefs:[{
          type: 'na', 
          targets: 4
        }]
      };
      if (this.lenOfConcData > 0){
           setTimeout(() => {this.dataTableGenerated()}, 100);
       }
       this.concenDataStatus=true;
    }, error=>{
      this.errorStr = error;
    })

  }

  ngOnInit() {
  	this.getConcenData()
  }

  dataTableGenerated(): void {      
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
      Plotly.newPlot('myDivConcAll',finalprepareDatatoPlotDataArray[2],layout10,defaultPlotlyConfiguration);

      if (rawData.length==0){
        Plotly.purge('myDivConcAll')
      }
  }

  prepareDataToCocenComb(concenTabName:any){
    let concQuery=[];
     if (concenTabName == "biomat") {
        let tempUnit=[];
        if (this.bioMatData.length >0 ){
          this.bioMatDataLen=1;
          for(let y = 0; y <this.bioMatData.length; y++){
            let biomatrixifo = this.bioMatData[y];
            let tempconcQuery=[];
            let tempSampLLOQ=biomatrixifo[8];
            let tempULOQ=biomatrixifo[9];
            tempconcQuery.push(biomatrixifo[4].trim());
            tempconcQuery.push(biomatrixifo[2].trim());
            concQuery.push([tempconcQuery.join('|'),tempSampLLOQ,tempULOQ]);
            let tempView='<a target="_blank"  routerLinkActive="active" href="/dataload/concentration_'+biomatrixifo[7].trim()+'" >' + 'View' + '</a>';
            let tempBiomatTableData=[biomatrixifo[4].trim(), biomatrixifo[1].trim(), biomatrixifo[5].trim(), biomatrixifo[6].trim(), biomatrixifo[0].trim(), tempView,biomatrixifo[2].trim()];
            this.bioMatDataTableData.push(tempBiomatTableData);
          }
          for (let m = 0; m <concQuery.length; m++){
            const tconcQuery = concQuery[m][0].trim().split('|');
                  const plotName=concQuery[m][0].trim();
                  const sampleLLOQ=concQuery[m][1].trim();
                  const ULOQ=concQuery[m][2].trim();
                  const plotData=[];
                  const plotDataSampleLLOQ=[];
                  
            for(let x = 0; x <this.allConcSamLLOQ.length; x++){
              const tempConcAllSamLLOQ=this.allConcSamLLOQ[x][1].trim().split(';');
              if ('NA' != Array.from(new Set(tempConcAllSamLLOQ)).join('')){
                for(let i = 0; i <tempConcAllSamLLOQ.length; i++){
                  const subConcAllSamLLOQ=tempConcAllSamLLOQ[i].trim().split('|');
                  if(subConcAllSamLLOQ[2] == tconcQuery[0] && this.allConcSamLLOQ[x][0] == tconcQuery[1]){
                    plotDataSampleLLOQ.push(subConcAllSamLLOQ.slice(-3)[0].split('(')[0].trim())
                      
                  }
                }

              }
            }
            //Group-1|Wild type|Plasma|1|C57BL6NCrl_Perfused|Female
            for(let z = 0; z <this.allConc.length; z++){
              const tempConcAll=this.allConc[z][1].trim().split(';')
              for(let j = 0; j <tempConcAll.length; j++){
                const subConcAll=tempConcAll[j].trim().split('|');
                if(subConcAll[2] == tconcQuery[0] && this.allConc[z][0] == tconcQuery[1]){
                  plotData.push(subConcAll.slice(-3)[0].split('(')[0].trim())
                  tempUnit.push('('+subConcAll.slice(-3)[0].split('(')[1].trim());
                    
                }
              }
            }
            const tempPlotArray=[plotName,plotData.join('|'),plotDataSampleLLOQ.join('|'),sampleLLOQ,ULOQ];
            this.concenPlotlyData.push(tempPlotArray.join(';'));
                  
          }
          this.concenPlotDataUnit ='Concentration '+Array.from(new Set(tempUnit)).join('&');
          //var plotLyHTML='<div id="myDivConc"></div>';
                  
          this.boxplot(this.concenPlotlyData,this.concenPlotDataUnit,0,concenTabName);

        }
      } else if (concenTabName == "str") {
        let tempUnit=[];
        if (this.strainData.length >0 ){
          this.strainDataLen=1;
          for(let y = 0; y <this.strainData.length; y++){
            let strainifo = this.strainData[y];
            let tempconcQuery=[];
            let tempSampLLOQ=strainifo[8];
            let tempULOQ=strainifo[9];
            tempconcQuery.push(strainifo[5].trim());
            tempconcQuery.push(strainifo[4].trim());
            tempconcQuery.push(strainifo[2].trim());
            concQuery.push([tempconcQuery.join('|'),tempSampLLOQ,tempULOQ]);
            let tempView='<a target="_blank"  routerLinkActive="active" href="/dataload/concentration_'+strainifo[7].trim()+'" >' + 'View' + '</a>';
            let tempStrainTableData=[ strainifo[5].trim(),strainifo[4].trim(), strainifo[1].trim(), strainifo[6].trim(), strainifo[0].trim(), tempView,strainifo[2].trim()];
            this.strainDataTableData.push(tempStrainTableData);
          }
          for (let m = 0; m <concQuery.length; m++){
            const tconcQuery = concQuery[m][0].trim().split('|');
                  const plotName=concQuery[m][0].trim();
                  const sampleLLOQ=concQuery[m][1].trim();
                  const ULOQ=concQuery[m][2].trim();
                  const plotData=[];
                  const plotDataSampleLLOQ=[];
                  
            for(let x = 0; x <this.allConcSamLLOQ.length; x++){
              const tempConcAllSamLLOQ=this.allConcSamLLOQ[x][1].trim().split(';');
              if ('NA' != Array.from(new Set(tempConcAllSamLLOQ)).join('')){
                for(let i = 0; i <tempConcAllSamLLOQ.length; i++){
                  const subConcAllSamLLOQ=tempConcAllSamLLOQ[i].trim().split('|');
                  if(subConcAllSamLLOQ[4] == tconcQuery[0] && subConcAllSamLLOQ[2] == tconcQuery[1] && this.allConcSamLLOQ[x][0] == tconcQuery[2]){
                    plotDataSampleLLOQ.push(subConcAllSamLLOQ.slice(-3)[0].split('(')[0].trim())
                      
                  }
                }

              }
            }
            //Group-1|Wild type|Plasma|1|C57BL6NCrl_Perfused|Female
            for(let z = 0; z <this.allConc.length; z++){
              const tempConcAll=this.allConc[z][1].trim().split(';')
              for(let j = 0; j <tempConcAll.length; j++){
                const subConcAll=tempConcAll[j].trim().split('|');
                if(subConcAll[4] == tconcQuery[0] && subConcAll[2] == tconcQuery[1] && this.allConc[z][0] == tconcQuery[2]){
                  plotData.push(subConcAll.slice(-3)[0].split('(')[0].trim())
                  tempUnit.push('('+subConcAll.slice(-3)[0].split('(')[1].trim());
                    
                }
              }
            }
            const tempPlotArray=[plotName,plotData.join('|'),plotDataSampleLLOQ.join('|'),sampleLLOQ,ULOQ];
            this.concenPlotlyData.push(tempPlotArray.join(';'));
                  
          }

          this.concenPlotDataUnit ='Concentration '+Array.from(new Set(tempUnit)).join('&');
          //var plotLyHTML='<div id="myDivConc"></div>';
                  
          this.boxplot(this.concenPlotlyData,this.concenPlotDataUnit,1,concenTabName);

        }
      } else if (concenTabName == "knock") {
        let tempUnit=[];
        if (this.knockoutData.length >0 ){
          this.knockoutDataLen=1;
          for(let y = 0; y <this.knockoutData.length; y++){
            let knockoutifo = this.knockoutData[y];
            let tempSampLLOQ=knockoutifo[8];
            let tempULOQ=knockoutifo[9];
            let tempconcQuery=[];
            tempconcQuery.push(knockoutifo[6].trim());
            tempconcQuery.push(knockoutifo[4].trim());
            tempconcQuery.push(knockoutifo[2].trim());
            concQuery.push([tempconcQuery.join('|'),tempSampLLOQ,tempULOQ]);
            let tempView='<a target="_blank"  routerLinkActive="active" href="/dataload/concentration_'+knockoutifo[7].trim()+'" >' + 'View' + '</a>';
            let tempKnockoutTableData=[knockoutifo[6].trim(),knockoutifo[4].trim(), knockoutifo[1].trim(), knockoutifo[5].trim(), knockoutifo[0].trim(), tempView,knockoutifo[2].trim()];
            this.knockoutDataTableData.push(tempKnockoutTableData);

          }
          for (let m = 0; m <concQuery.length; m++){
            const tconcQuery = concQuery[m][0].trim().split('|');
                  const plotName=concQuery[m][0].trim();
                  const sampleLLOQ=concQuery[m][1].trim();
                  const ULOQ=concQuery[m][2].trim();
                  const plotData=[];
                  const plotDataSampleLLOQ=[];
                  
            for(let x = 0; x <this.allConcSamLLOQ.length; x++){
              const tempConcAllSamLLOQ=this.allConcSamLLOQ[x][1].trim().split(';');
              if ('NA' != Array.from(new Set(tempConcAllSamLLOQ)).join('')){
                for(let i = 0; i <tempConcAllSamLLOQ.length; i++){
                  const subConcAllSamLLOQ=tempConcAllSamLLOQ[i].trim().split('|');
                  if(subConcAllSamLLOQ[1] == tconcQuery[0] && subConcAllSamLLOQ[2] == tconcQuery[1] && this.allConcSamLLOQ[x][0] == tconcQuery[2]){
                    plotDataSampleLLOQ.push(subConcAllSamLLOQ.slice(-3)[0].split('(')[0].trim())
                      
                  }
                }

              }
            }
            //Group-1|Wild type|Plasma|1|C57BL6NCrl_Perfused|Female
            for(let z = 0; z <this.allConc.length; z++){
              const tempConcAll=this.allConc[z][1].trim().split(';')
              for(let j = 0; j <tempConcAll.length; j++){
                const subConcAll=tempConcAll[j].trim().split('|');
                if(subConcAll[1] == tconcQuery[0] && subConcAll[2] == tconcQuery[1] && this.allConc[z][0] == tconcQuery[2]){
                  plotData.push(subConcAll.slice(-3)[0].split('(')[0].trim())
                  tempUnit.push('('+subConcAll.slice(-3)[0].split('(')[1].trim());
                    
                }
              }
            }
            const tempPlotArray=[plotName,plotData.join('|'),plotDataSampleLLOQ.join('|'),sampleLLOQ,ULOQ];
            this.concenPlotlyData.push(tempPlotArray.join(';'));
                  
          }

          this.concenPlotDataUnit ='Concentration '+Array.from(new Set(tempUnit)).join('&');
          //var plotLyHTML='<div id="myDivConc"></div>';
                  
          this.boxplot(this.concenPlotlyData,this.concenPlotDataUnit,1,concenTabName);
        }
      } else if (concenTabName == "sex") {
        let strs='';
        let tempUnit=[];
        if (this.sexData.length >0 ){
          this.sexDataLen=1;
          for(let y = 0; y <this.sexData.length; y++){
            let sexifo = this.sexData[y];
            let tempSampLLOQ=sexifo[8];
            let tempULOQ=sexifo[9];
            let tempconcQuery=[];
            tempconcQuery.push(sexifo[1].trim());
            tempconcQuery.push(sexifo[4].trim());
            tempconcQuery.push(sexifo[2].trim());
            concQuery.push([tempconcQuery.join('|'),tempSampLLOQ,tempULOQ]);
            let tempView='<a target="_blank"  routerLinkActive="active" href="/dataload/concentration_'+sexifo[7].trim()+'" >' + 'View' + '</a>';
            let tempSexTableData=[sexifo[1].trim(),sexifo[4].trim(), sexifo[5].trim(), sexifo[6].trim(), sexifo[0].trim(), tempView,sexifo[2].trim()];
            this.sexDataTableData.push(tempSexTableData);
          }
          for (let m = 0; m <concQuery.length; m++){
            const tconcQuery = concQuery[m][0].trim().split('|');
                  const plotName=concQuery[m][0].trim();
                  const sampleLLOQ=concQuery[m][1].trim();
                  const ULOQ=concQuery[m][2].trim();
                  const plotData=[];
                  const plotDataSampleLLOQ=[];
                  
            for(let x = 0; x <this.allConcSamLLOQ.length; x++){
              const tempConcAllSamLLOQ=this.allConcSamLLOQ[x][1].trim().split(';');
              if ('NA' != Array.from(new Set(tempConcAllSamLLOQ)).join('')){
                for(let i = 0; i <tempConcAllSamLLOQ.length; i++){
                  const subConcAllSamLLOQ=tempConcAllSamLLOQ[i].trim().split('|');
                  if(subConcAllSamLLOQ[5] == tconcQuery[0] && subConcAllSamLLOQ[2] == tconcQuery[1] && this.allConcSamLLOQ[x][0] == tconcQuery[2]){
                    plotDataSampleLLOQ.push(subConcAllSamLLOQ.slice(-3)[0].split('(')[0].trim())
                      
                  }
                }

              }
            }
            //Group-1|Wild type|Plasma|1|C57BL6NCrl_Perfused|Female
            for(let z = 0; z <this.allConc.length; z++){
              const tempConcAll=this.allConc[z][1].trim().split(';')
              for(let j = 0; j <tempConcAll.length; j++){
                const subConcAll=tempConcAll[j].trim().split('|');
                if(subConcAll[5] == tconcQuery[0] && subConcAll[2] == tconcQuery[1] && this.allConc[z][0] == tconcQuery[2]){
                  plotData.push(subConcAll.slice(-3)[0].split('(')[0].trim())
                  tempUnit.push('('+subConcAll.slice(-3)[0].split('(')[1].trim());
                    
                }
              }
            }
            const tempPlotArray=[plotName,plotData.join('|'),plotDataSampleLLOQ.join('|'),sampleLLOQ,ULOQ];
            this.concenPlotlyData.push(tempPlotArray.join(';'));
                  
          }

          this.concenPlotDataUnit ='Concentration '+Array.from(new Set(tempUnit)).join('&');
          //var plotLyHTML='<div id="myDivConc"></div>';
                  
          this.boxplot(this.concenPlotlyData,this.concenPlotDataUnit,1,concenTabName);
        }
      }
    //this.boxplot(this.concenPlotlyData,this.concenPlotDataUnit,1);

  }

  boxplot(dataToPlot:any,yAxisTile:any,tisPos:any, clickedTabName:any):void {
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
      let boxPlotDataArray=[];
      let boxPlotDataArrayLog2=[];
      let boxPlotDataArrayLog10=[];
      yAxisTile='Concentration<br>(fmol target protein/µg extracted protein)';
      let layout={
        yaxis:{
        title:yAxisTile,
        zeroline:false,
        showlegend: true,
        legend :{
          x:dataToPlot.length+1
        }
       },
       xaxis:{
         automargin: true,
         showticklabels:false
       }
      };

      let layout2={
        yaxis:{
        title:'Concentration<br>(fmol target protein/µg extracted protein)<br> in Log2 Scale',
        zeroline:false,
        showlegend: true,
        legend :{
          x:dataToPlot.length+1
        }
       },
       xaxis:{
         automargin: true,
         showticklabels:false
       }
      };

      let layout10={
        yaxis:{
        title:'Concentration<br>(fmol target protein/µg extracted protein)<br> in Log10 Scale',
        zeroline:false,
        showlegend: true,
        legend :{
          x:dataToPlot.length+1
        }
       },
       xaxis:{
         automargin: true,
         showticklabels:false
       }
      };
      const d3colors = Plotly.d3.scale.category10();
      let defaultPlotlyConfiguration={};
      defaultPlotlyConfiguration ={
        responsive: true,
        scrollZoom: true,
        showTips:true,
        modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d','toImage','pan', 'pan2d','zoom2d','toggleSpikelines'],
        displayLogo: false
      };

      for(let i=0; i< dataToPlot.length;i++){
        const tempPlotDataArray=dataToPlot[i].split(';');
        const plotDataArray=[];
        const plotDataArrayLog2=[];
        const plotDataArrayLog10=[];
        let tempArray=tempPlotDataArray[2].split('|');
        if (tempPlotDataArray[2] === 'NA' || tempPlotDataArray[2].trim().length == 0){
          tempArray=tempPlotDataArray[1].split('|');
        }
        for(let j=0; j< tempArray.length;j++){
           if (parseFloat(tempArray[j]) >0){
             plotDataArray.push(parseFloat(tempArray[j]));
             plotDataArrayLog2.push(Math.log2(parseFloat(tempArray[j])));
             plotDataArrayLog10.push(Math.log10(parseFloat(tempArray[j])));
           }
        }
        let boxPlotData={};
        let boxPlotDataLog2={};
        let boxPlotDataLog10={};

        let boxSamLLOQData={};
        let boxSamLLOQDataLog2={};
        let boxSamLLOQDataLog10={};

        let boxULOQData={};
        let boxULOQDataLog2={};
        let boxULOQDataLog10={};

        let tempplotDataArray=plotDataArray.filter(value=> !Number.isNaN(value));

        if (tempPlotDataArray[2] === 'NA' || tempPlotDataArray[2].trim().length == 0){
          if (tempplotDataArray.length > 0){
            boxPlotData={
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
            boxPlotDataLog2={
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
            boxPlotDataLog10={
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
            const tempColor=tissueColor[tempPlotDataArray[0].split('|')[tisPos]];
              boxPlotData={
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
              boxPlotDataLog2={
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
              boxPlotDataLog10={
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

            boxPlotDataArray.push(boxPlotData);
            boxPlotDataArray.push(boxSamLLOQData);
            boxPlotDataArray.push(boxULOQData);
            boxPlotDataArrayLog2.push(boxPlotDataLog2);
            boxPlotDataArrayLog2.push(boxSamLLOQDataLog2);
            boxPlotDataArrayLog2.push(boxULOQDataLog2);
            boxPlotDataArrayLog10.push(boxPlotDataLog10);
            boxPlotDataArrayLog10.push(boxSamLLOQDataLog10);
            boxPlotDataArrayLog10.push(boxULOQDataLog10);

        }
      }

     let finalBoxPlotDataArray={
       0:boxPlotDataArray,
       1:boxPlotDataArrayLog2,
       2:boxPlotDataArrayLog10
     }
     let plotlyWidth=$(window).width();
     plotlyWidth=plotlyWidth-320;
     const updatedDimension={
       width:plotlyWidth
     }
     if (clickedTabName=='str'){
       if(document.getElementById('myDivConcStrain')){
      /* Plotly.newPlot('myDivConcStrain',finalBoxPlotDataArray[0],layout,defaultPlotlyConfiguration);      
          Plotly.newPlot('myDivConcStrain',finalBoxPlotDataArray[1],layout2,defaultPlotlyConfiguration);*/
          Plotly.newPlot('myDivConcStrain',finalBoxPlotDataArray[2],layout10,defaultPlotlyConfiguration);
          Plotly.relayout('myDivConcStrain',updatedDimension);
          Plotly.purge('myDivConcSex');
          Plotly.purge('myDivConcKnockout');
          Plotly.purge('myDivConcBioMat');
      }
        if (dataToPlot.length==0){
          if(document.getElementById('myDivConcStrain')){
            Plotly.purge('myDivConcStrain')
          }
        }
     } else if (clickedTabName=='sex'){
       if(document.getElementById('myDivConcSex')){
      /* Plotly.newPlot('myDivConcSex',finalBoxPlotDataArray[0],layout,defaultPlotlyConfiguration);      
          Plotly.newPlot('myDivConcSex',finalBoxPlotDataArray[1],layout2,defaultPlotlyConfiguration);*/
          Plotly.newPlot('myDivConcSex',finalBoxPlotDataArray[2],layout10,defaultPlotlyConfiguration);
          Plotly.relayout('myDivConcSex',updatedDimension);
          Plotly.purge('myDivConcStrain');
          Plotly.purge('myDivConcKnockout');
          Plotly.purge('myDivConcBioMat');
      }
        if (dataToPlot.length==0){
          if(document.getElementById('myDivConcSex')){
            Plotly.purge('myDivConcSex')
          }
        }
     } else if (clickedTabName=='knock'){
       if(document.getElementById('myDivConcKnockout')){
      /* Plotly.newPlot('myDivConcKnockout',finalBoxPlotDataArray[0],layout,defaultPlotlyConfiguration);      
          Plotly.newPlot('myDivConcKnockout',finalBoxPlotDataArray[1],layout2,defaultPlotlyConfiguration);*/
          Plotly.newPlot('myDivConcKnockout',finalBoxPlotDataArray[2],layout10,defaultPlotlyConfiguration);
          Plotly.relayout('myDivConcKnockout',updatedDimension);
          Plotly.purge('myDivConcStrain');
          Plotly.purge('myDivConcSex');
          Plotly.purge('myDivConcBioMat');
      }
        if (dataToPlot.length==0){
          if(document.getElementById('myDivConcKnockout')){
            Plotly.purge('myDivConcKnockout')
          }
        }
     } else if (clickedTabName=='biomat'){
       if(document.getElementById('myDivConcBioMat')){
      /* Plotly.newPlot('myDivConcBioMat',finalBoxPlotDataArray[0],layout,defaultPlotlyConfiguration);      
          Plotly.newPlot('myDivConcBioMat',finalBoxPlotDataArray[1],layout2,defaultPlotlyConfiguration);*/
          Plotly.newPlot('myDivConcBioMat',finalBoxPlotDataArray[2],layout10,defaultPlotlyConfiguration);
          Plotly.relayout('myDivConcBioMat',updatedDimension);
          Plotly.purge('myDivConcStrain');
          Plotly.purge('myDivConcSex');
          Plotly.purge('myDivConcKnockout');
      }
        if (dataToPlot.length==0){
          if(document.getElementById('myDivConcBioMat')){
            Plotly.purge('myDivConcBioMat')
          }
        }
     }
    }

  onOptionsSelected(event){
      if(event.target){
        let tempPlotData=this.finalPlotData['plotData'];
        let tempPlotLayout=this.finalPlotData['plotLayout'];
        let tempConfig=this.finalPlotData['config'];
        if (this.selected.name == 'Concentration Data'){
          Plotly.purge('myDivConcAll')
          Plotly.newPlot('myDivConcAll',tempPlotData[0],tempPlotLayout[0],tempConfig)
        }

        if (this.selected.name == 'Log2(Concentration Data)'){
          Plotly.purge('myDivConcAll')
          Plotly.newPlot('myDivConcAll',tempPlotData[1],tempPlotLayout[1],tempConfig)
        }

        if (this.selected.name == 'Log10(Concentration Data)'){
          Plotly.purge('myDivConcAll')
          Plotly.newPlot('myDivConcAll',tempPlotData[2],tempPlotLayout[2],tempConfig)
        }
        
      }
    }

  private openTabsConcen(evt, tabName) {
      this.prepareDataToCocenComb(tabName);
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontentconcen");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablinksconcen");
      for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";
  }
}

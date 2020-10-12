import { Component, OnInit, OnDestroy, HostListener, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, Observer } from 'rxjs';
import { share } from 'rxjs/operators';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as Plotly from 'plotly.js';
import { NgxSpinnerService } from 'ngx-spinner';
import * as $ from "jquery";

declare var jquery: any;


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit,OnDestroy {
  private queryRes:any;
  private advReq:any;
  unqProteins;
  unqpeptides;
  unqassays;
  pepSeqPresenceHumanOrtholog;
  pepSeqPresenceHumanOrthologUniId;
  screenWidth:any;
  plotlyData:any=[];
  allBioMat:any;
  allStrain:any;
  interval:any;
  autoPlotStatus:boolean= false;
  plotIndex:number=0;
  progress:number=0;
  finalPlotData:any={};
  public show:boolean = false;
  public buttonName:any = 'Advanced search';

  public number: number = 0;
  public observable: Observable<boolean>;
  private observer: Observer<boolean>;
  qmpkbLogoImage ='static/ang/assets/images/logo/logo.png'
  isCollapsed:boolean=true;

  plotDataOptions=[
       {num:0, name:'Brain'},
       {num:1, name:'Brown Adipose'},
       {num:2, name:'Epididymis'},
       {num:3, name:'Eye'},
       {num:4, name:'Heart'},
       {num:5, name:'Kidney'},
       {num:6, name:'Liver Caudate and Right Lobe'},
       {num:7, name:'Liver Left Lobe'},
       {num:8, name:'Lung'},
       {num:9, name:'Ovary'},
       {num:10, name:'Pancreas'},
       {num:11, name:'Plasma'},
       {num:12, name:'RBCs'},
       {num:13, name:'Salivary Gland'},
       {num:14, name:'Seminal Vesicles'},
       {num:15, name:'Skeletal Muscle'},
       {num:16, name:'Skin'},
       {num:17, name:'Spleen'},
       {num:18, name:'Testes'},
       {num:19, name:'White Adipose'}

  ];

  unitDic={
        'Brain':' (fmol target protein/µg extracted protein)',
        'Brown Adipose': ' (fmol target protein/µg extracted protein)',
        'Eye':' (fmol target protein/µg extracted protein)',
        'Epididymis':' (fmol target protein/µg extracted protein)',
        'Heart':' (fmol target protein/µg extracted protein)',
        'Kidney': ' (fmol target protein/µg extracted protein)',
        'Liver Caudate and Right Lobe':' (fmol target protein/µg extracted protein)',
        'Liver Left Lobe':' (fmol target protein/µg extracted protein)',
        'Lung':' (fmol target protein/µg extracted protein)',
        'Ovary': ' (fmol target protein/µg extracted protein)',
        'Pancreas':' (fmol target protein/µg extracted protein)',
        'Plasma':' (fmol target protein/µg extracted protein)',
        'RBCs':' (fmol target protein/µg extracted protein)',
        'Salivary Gland': ' (fmol target protein/µg extracted protein)',
        'Seminal Vesicles':' (fmol target protein/µg extracted protein)',
        'Skeletal Muscle':' (fmol target protein/µg extracted protein)',
        'Skin':' (fmol target protein/µg extracted protein)',
        'Spleen':' (fmol target protein/µg extracted protein)',
        'Testes':' (fmol target protein/µg extracted protein)',
        'White Adipose': ' (fmol target protein/µg extracted protein)'
    };

  defaultPlotlyConfiguration ={
      responsive: true,
      scrollZoom: true,
      showTips:true,
      modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d','toImage','pan', 'pan2d','zoom2d','toggleSpikelines'],
      displayLogo: false
  };

  selected=this.plotDataOptions[0];

  @HostListener('window.resize', ['$event'])

  getScreenSize(event?){
    this.screenWidth=Math.round(window.innerWidth/2)+"px";
  }

  constructor(private router:Router, private http:HttpClient,private _qmpkb:QmpkbService,private spinner: NgxSpinnerService, private cdRef:ChangeDetectorRef) { 
        this.observable = new Observable<boolean>((observer: any) => this.observer = observer);
        this.getScreenSize();

        // For auto mode
        //setTimeout(() => this.number += this.number, 5000); // Update on 5 seconds
  }

  ngOnInit() {
  this.spinner.show();
  this.queryRes=this.http.get('/fileapi/resultFile/jsonData/preLoadData/preloadHomeData.json')
    .subscribe((resp:any) => {
      this.allBioMat=resp.data[1]["BioMat"].split('|');
      this.allStrain=resp.data[2]["Strain"].split('|');
      this.unqassays=resp.data[0]["uniqueAssays"];
      this.unqProteins=resp.data[0]["uniqueProtein"];
      this.unqpeptides=resp.data[0]["uniquePeptide"];
      this.pepSeqPresenceHumanOrtholog=resp.data[0]["pepSeqPresenceHumanOrtholog"];
      this.pepSeqPresenceHumanOrthologUniId=resp.data[0]["pepSeqPresenceHumanOrthologUniId"];
      this.plotlyData.push(resp.data[1]);
      this.plotlyData.push(resp.data[3]);
      this.plotlyData.push(resp.data[2]);

      let rawData = resp.data[4];
      let bioMatData = resp.data[5];
      let finalData:any={};
      for (let x in this.allBioMat){
         finalData[this.allBioMat[x]]=[];
      }
      let bioMatKey=Object.keys(bioMatData).sort();
      for (let z in bioMatKey){
        let plotDataArrayTrace:any={};
        plotDataArrayTrace={
          y:bioMatData[bioMatKey[z]]['MeanConcData'].split('|'),
          x:bioMatData[bioMatKey[z]]['MeanProtein'].split('|'),
          name:'Mean Concentration',
          type:'Scatter',
          mode:'markers',
          marker:{
            size:6,
            symbol:Array(bioMatData[bioMatKey[z]]['MeanProtein'].length).fill("diamond-open-dot"),
          },
          //text:bioMatData[bioMatKey[z]]['MeanProtein'].split('|') //name of Uniprot ID and Gene
        };
        finalData[bioMatKey[z]].push(plotDataArrayTrace);
      }
      let number=0;
      let tempKey=Object.keys(rawData).sort()
      for (let i in tempKey){
        number++;
        for (let j=0; j<rawData[tempKey[i]].length; j++){
          let tempBioMat=rawData[tempKey[i]][j];
          let tempBioMatKey=(Object.keys(tempBioMat))[0];
          let tempBioMatVal=(Object.values(tempBioMat))[0];
          let plotDataArrayMaleTrace:any={};
          let plotDataArrayFemaleTrace:any={};
          try{
            plotDataArrayMaleTrace={
              y:tempBioMatVal['Male']['MeanConcData'].split('|'),
              x:tempBioMatVal['Male']['MeanProtein'].split('|'),
              name:'Male '+tempKey[i],
              type:'Scatter',
              mode:'markers',
              marker:{
                size:6,
                symbol:Array(tempBioMatVal['Male']['MeanProtein'].length).fill("circle-open-dot"),
              },
              //text:tempBioMatVal['Male']['MeanProtein'].split('|') //name of Uniprot ID and Gene
            };
            finalData[tempBioMatKey].push(plotDataArrayMaleTrace);
          } catch (e){

          }
          try{
            plotDataArrayFemaleTrace={
              y:tempBioMatVal['Female']['MeanConcData'].split('|'),
              x:tempBioMatVal['Female']['MeanProtein'].split('|'),
              name:'Female '+tempKey[i],
              type:'Scatter',
              mode:'markers',
              marker:{
                size:6,
                symbol:Array(tempBioMatVal['Female']['MeanProtein'].length).fill("square-open-dot"),
              },
              //text:tempBioMatVal['Female']['MeanProtein'].split('|') //name of Uniprot ID and Gene
            };
            finalData[tempBioMatKey].push(plotDataArrayFemaleTrace);
          } catch (e){

          }

        }
      }
      let finalLayout:any=[]
      //this.cdRef.detectChanges();
      for (let y in bioMatKey){
        let layout={
          title:{text:'Protein concentration ranges in '+bioMatKey[y],font:{size:14}},
          xaxis: {showticklabels:false,title:'Protein',font:{size:14}},
          yaxis: {title:this.unitDic[bioMatKey[y]]+'<br>in Log10 Scale',font:{size:14}},
        };
        finalLayout.push(layout);
      }

      this.finalPlotData={
          'plotData':finalData,
          'plotLayout':finalLayout,
          'config':this.defaultPlotlyConfiguration
      };


      this.barplot(this.plotlyData);
      this.preparerawData(this.autoPlotStatus);
    });
    this.advReq=this.http.get('/fileapi/resultFile/jsonData/preLoadData/advanceSearchOptions.json')
      .subscribe((resp:any) => {
        this._qmpkb.dropDownStorage=resp.data;
    });
  }


  preparerawData(plotStatus:any){
    let tempTissueList=[
       'Brain',
       'Brown Adipose',
       'Epididymis',
       'Eye',
       'Heart',
       'Kidney',
       'Liver Caudate and Right Lobe',
       'Liver Left Lobe',
       'Lung',
       'Ovary',
       'Pancreas',
       'Plasma',
       'RBCs',
       'Salivary Gland',
       'Seminal Vesicles',
       'Skeletal Muscle',
       'Skin',
       'Spleen',
       'Testes',
       'White Adipose'

  ];
    let tempPlotDataInitial=this.finalPlotData['plotData'];
    let tempPlotLayoutInitial=this.finalPlotData['plotLayout'];
    let tempConfigInitial=this.finalPlotData['config'];

    if(document.getElementById('myDivHome')){
      Plotly.newPlot('myDivHome',tempPlotDataInitial['Brain'],tempPlotLayoutInitial[0],tempConfigInitial);
    }
    
    const self =this;
    let timeleft=3;
    if ( !plotStatus){
      this.interval = setInterval(() => {
        if(this.progress>= 3){
          this.plotIndex++;
          if(this.plotIndex==20){
             this.plotIndex=0;
          }
          this.selected=this.plotDataOptions[this.plotIndex];
          if(document.getElementById('myDivHome')){
            Plotly.newPlot('myDivHome',tempPlotDataInitial[tempTissueList[this.plotIndex]],tempPlotLayoutInitial[this.plotIndex],tempConfigInitial);
          }
          
          this.progress=0;
        } else{
           this.progress++;
        }
      }, 1000);
    }
     $('#myDivHome').hover(function(ev){
         $("#progressBar").hide();
         self.progress=0;
         clearInterval(self.interval);
      }, function(ev){
        self.interval = setInterval(() => {
          $("#progressBar").show();
          if(self.progress>= 3){
            self.plotIndex++;
            if(self.plotIndex==20){
               self.plotIndex=0;
            }
            self.selected=self.plotDataOptions[self.plotIndex];
            if(document.getElementById('myDivHome')){
              Plotly.newPlot('myDivHome',tempPlotDataInitial[tempTissueList[self.plotIndex]],tempPlotLayoutInitial[self.plotIndex],tempConfigInitial);
            }
            self.progress=0;
          } else{
             self.progress++;
          }
          },1000);
      });

    this.spinner.hide();
  }


  barplot(rawData:any):void {
    let layout:any={};
    layout = {
      xaxis: {domain: [0, 0.25]},
      xaxis2: {domain: [0.35, .60]},
      xaxis3: {domain: [.70, 1.0]},
      yaxis: {domain: [0, .9]},
      yaxis2: {anchor: 'x2',domain: [0, .9]},
      yaxis3: {anchor: 'x3',domain: [0, .9]},
      annotations: [
        {
          text: "Biological Matrix",
          font: {
            size: 16
          },
          showarrow: false,
          align: 'center',
          x: 0.13,
          y: 1,
          xref: 'paper',
          yref: 'paper',
        },
        {
          text: "Sex",
          font: {
            size: 16
          },
          showarrow: false,
          align: 'center',
          x: 0.48,
          y: 1,
          xref: 'paper',
          yref: 'paper',
         },
        {
          text: "Strain",
          font: {
            size: 16
          },
          showarrow: false,
          align: 'center',
          x: 0.85,
          y: 1,
          xref: 'paper',
          yref: 'paper',
         }
      ],
      showlegend: false
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

    let plotDataArrayMatTrace1:any={};
    let plotDataArrayMatTrace2:any={};
    plotDataArrayMatTrace1={
      y:rawData[0]["BioMat"].split('|'),
      x:rawData[0]["PeptideSeq"].split('|'),
      name:'Assays',
      type:'bar',
      orientation:'h'
    };
    plotDataArrayMatTrace2={
      y:rawData[0]["BioMat"].split('|'),
      x:rawData[0]["Protein"].split('|'),
      name:'Protein',
      type:'bar',
      orientation:'h'
    };

    let plotDataArraySexTrace1:any={};
    let plotDataArraySexTrace2:any={};
    plotDataArraySexTrace1={
      y:rawData[1]["Sex"].split('|'),
      x:rawData[1]["PeptideSeq"].split('|'),
      xaxis:'x2',
      yaxis:'y2',
      name:'Assays',
      type:'bar',
      orientation:'h'
    };
    plotDataArraySexTrace2={
      y:rawData[1]["Sex"].split('|'),
      x:rawData[1]["Protein"].split('|'),
      xaxis:'x2',
      yaxis:'y2',
      name:'Protein',
      type:'bar',
      orientation:'h'
    };

    let plotDataArrayStrainTrace1:any={};
    let plotDataArrayStrainTrace2:any={};
    plotDataArrayStrainTrace1={
      y:rawData[2]["Strain"].split('|'),
      x:rawData[2]["PeptideSeq"].split('|'),
      xaxis:'x3',
      yaxis:'y3',
      name:'Assays',
      type:'bar',
      orientation:'h'
    };
    plotDataArrayStrainTrace2={
      y:rawData[2]["Strain"].split('|'),
      x:rawData[2]["Protein"].split('|'),
      xaxis:'x3',
      yaxis:'y3',
      name:'Protein',
      type:'bar',
      orientation:'h'
    };

    const finalData=[plotDataArrayMatTrace1,plotDataArrayMatTrace2,plotDataArraySexTrace1,plotDataArraySexTrace2,plotDataArrayStrainTrace1,plotDataArrayStrainTrace2];


    //Plotly.newPlot('myDiv',finalData,layout,defaultPlotlyConfiguration);      
  }


  onOptionsSelected(event){
      if(event.target){
        $("#progressBar").hide();
        let tempPlotData=this.finalPlotData['plotData'];
        let tempPlotLayout=this.finalPlotData['plotLayout'];
        let tempConfig=this.finalPlotData['config'];
        this.autoPlotStatus = true;
        this.preparerawData(this.autoPlotStatus);
        clearInterval(this.interval);
        if(document.getElementById('myDivHome')){
          Plotly.purge('myDivHome');
          Plotly.newPlot('myDivHome',tempPlotData[this.selected.name],tempPlotLayout[this.selected.num],tempConfig);
        }
      }
    }


  toggle() {
    this.show = !this.show;

    // CHANGE THE NAME OF THE BUTTON.
    if(this.show)  
      this.buttonName = "Basic search";
    else
      this.buttonName = "Advanced search";
  }

  ngOnDestroy(){
    this.queryRes.unsubscribe();
    this.advReq.unsubscribe();
  }

}


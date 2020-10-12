
import { Component, OnInit, Input,ViewChildren, QueryList, ElementRef } from '@angular/core';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { Subject } from 'rxjs';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as Plotly from 'plotly.js';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-fold-change',
  templateUrl: './fold-change.component.html',
  styleUrls: ['./fold-change.component.css']
})
export class FoldChangeComponent implements OnInit {

  	queryData:any;
    foldChangeQueryData:any;
  	errorStr:Boolean;
  	foldChangeStatus:Boolean;
  	plotStatus=true;
  	dataStatus=true;
  	foldchangeDataChecked:any=[];
  	selected:any='';
  	checkedValues:any;
  	filteredFoldData:any;
  	checkIfTwoAreSeleected=false;
    resetButton=true;
  	downloadFile:string;
  	plotDataLength=0;

    fieldArray: Array<number> = [0, 1];
    selectedOptions = new Set<string>();
  	@ViewChildren("selectValue") selectValue: QueryList<ElementRef<HTMLSelectElement>>;

  	constructor(
		private http: HttpClient,
		private _qmpkb:QmpkbService,
  	) { }

    @Input()
    set foldChangeResult(foldData:any){
    	let tempQueryData=foldData;
    	this.downloadFile=tempQueryData['DownloadPath'];
    	delete tempQueryData['DownloadPath'];
      this.foldChangeQueryData=tempQueryData['foldChangeQueryData'];
      delete tempQueryData['foldChangeQueryData'];
  		this.queryData=tempQueryData;
    }

    ngOnInit() {

    }


    onOptionsSelected(event){
      if(event.target){
        this.foldchangeDataChecked=[];
        this.checkIfTwoAreSeleected=false;
        this.resetButton=true;
        this.dataStatus=true;
        this.plotDataLength=0;
        this.selectedOptions.clear();
        this.scatterplot({},0,0,0);
      }
    }

   changed() {
      this.selectedOptions.clear();
      this.foldchangeDataChecked=[];
      this.selectValue.forEach(j => {
        const selectedVal = j.nativeElement.value;
        if (selectedVal && selectedVal !== "undefined"){ 
          this.selectedOptions.add(selectedVal);
          this.foldchangeDataChecked.push(selectedVal);
        }
      });

      if (this.foldchangeDataChecked.length==2 && this.foldchangeDataChecked[0] !=="undefined" && this.foldchangeDataChecked[1] !=="undefined") {
        this.checkIfTwoAreSeleected=true;
        this.resetButton=false;
        this.plotStatus=false;
        this.plotDataLength=1;
        this._qmpkb.receiveDataFromBackendSearch('/foldChangeapi/?dropDownTerm='  +this.selected.key +'&checkBoxTerm='+ this.foldchangeDataChecked.join() +'&fileName='+ this.downloadFile +'&queryData='+ JSON.stringify(this.foldChangeQueryData)).subscribe((response: any)=>{
          this.filteredFoldData=response;
          this.foldChangeStatus=response.foldChangeStatus;
          if (this.foldChangeStatus == true){
            this.scatterplot(this.filteredFoldData.log2FoldData,this.filteredFoldData.maxAbsValLog2,this.filteredFoldData.hLine,this.filteredFoldData.maxValPval);
          } else{
            this.plotStatus=true;
            this.dataStatus=false;
          }
        }, error=>{
          this.errorStr = error;
        })
      }
    }


    isSelected(opt: string) {
      return this.selectedOptions.has(opt);
    }

    scatterplot(plotData:any,maxAbsValLog2:any,hLine:any,maxValPval:any):void {

      let defaultPlotlyConfiguration={};
      defaultPlotlyConfiguration ={
        responsive: true,
        scrollZoom: true,
        showTips:true,
        modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d','toImage','pan', 'pan2d','zoom2d','toggleSpikelines'],
        displayLogo: false
      };


    	const plotDataArray=[];
    	for(let key in plotData){
    		if (plotData[key][0].length >0 ){
    			let trace={}
    			if (key == 'Yes'){
					trace = {
					  x: plotData[key][0],
					  y: plotData[key][1],
					  mode: 'markers',
					  type: 'scatter',
					  text: plotData[key][2],
					  marker: { size: 5,color:'red', opacity:0.5 },
					  hoverinfo:'x+y+text',
	          		  showlegend:false
					};
    			} else{
					trace = {
					  x: plotData[key][0],
					  y: plotData[key][1],
					  mode: 'markers',
					  type: 'scatter',
					  text: plotData[key][2],
					  marker: { size: 5,color:'blue', opacity:0.5 },
					  hoverinfo:'x+y+text',
	          		  showlegend:false
					};
    			}
				plotDataArray.push(trace);
    		}
    	}

    	let verLine1={
		  x: [-1,-1],
		  y: [0,maxValPval],
		  mode: 'lines',
		  line:{
		  		color: 'red',
		  		dash:'dot',
		  		width:1.5
		  },
          showlegend:false,
          hoverinfo:'skip'
    	};
    	let verLine2={
		  x: [1,1],
		  y: [0,maxValPval],
		  mode: 'lines',
		  line:{
		  		color: 'red',
		  		dash:'dot',
		  		width:1.5
		  },
          showlegend:false,
          hoverinfo:'skip'
    	};
    	let horZLine={
		  x: [-maxAbsValLog2-1, maxAbsValLog2+1],
		  y: [hLine,hLine],
		  mode: 'lines',
		  line:{
		  		color: 'red',
		  		dash:'dot',
		  		width:1.5
		  },
          showlegend:false,
          hoverinfo:'skip'
    	}
    	plotDataArray.push(verLine1);
    	plotDataArray.push(verLine2);
    	plotDataArray.push(horZLine);
		let layout = {
			title:{text:'Note: Blue and red circle represents dataset size greater than 1 and equal to 1 respectively.<br>When dataset size is one, we replaced p-value with 1.',font:{size:12}},
			xaxis: {range: [ -maxAbsValLog2-1, maxAbsValLog2+1 ],title: 'Log2 Fold Change'},
  		yaxis: {title:'-Log10(adjusted p-value using BH)'},
      autosize:false,
      width:600,
      height:350,
      margin:{
        l:100,
        r:100,
        b:40,
        t:90
      }
		};
		
		if (Object.keys(plotData).length >0){
			this.plotStatus=true;
      this.checkIfTwoAreSeleected=false;
		}

		Plotly.newPlot('myDiv', plotDataArray, layout, defaultPlotlyConfiguration);
		if (this.plotDataLength==0){
			this.dataStatus=true;
      this.checkIfTwoAreSeleected=false;
			Plotly.purge('myDiv')
		}
    }

}
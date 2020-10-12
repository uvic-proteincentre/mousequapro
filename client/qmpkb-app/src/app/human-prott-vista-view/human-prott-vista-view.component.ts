import { Component, OnInit, Input} from '@angular/core';
import * as $ from "jquery";

declare var require: any
declare var jquery: any;

@Component({
  selector: 'app-human-prott-vista-view',
  templateUrl: './human-prott-vista-view.component.html',
  styleUrls: ['./human-prott-vista-view.component.css']
})
export class HumanProttVistaViewComponent implements OnInit  {

  humanPepStart:number;
  humanPepEnd:number;
  humanUniprotKB:any;
  queryHuamanProtVistaInfo:any;
  humanProtvistaQueryData:any;
  constructor(
    ) { }

    @Input()
    set humanProtVistamQuery(humanProtvistaQueryInfo:any){
      this.queryHuamanProtVistaInfo=humanProtvistaQueryInfo;

    }

  ngOnInit() {
    this.humanUniprotKB=this.queryHuamanProtVistaInfo.humanUniprotKB;
    this.humanPepStart=this.queryHuamanProtVistaInfo.humanPepStart;
    this.humanPepEnd=this.queryHuamanProtVistaInfo.humanPepEnd;
    if (this.humanPepEnd > 0){
       setTimeout(() => {this.plotProtVistaHumanFunc(this.humanUniprotKB,this.humanPepStart,this.humanPepEnd)}, 100); 
   };

  }

  plotProtVistaHumanFunc(protvistaHumanUni:string,humanPreSelectStart:number,humanPreSelectEnd:number): void {

    if (humanPreSelectStart >0){
        var humanDiv = document.getElementById('humanDiv');
        var ProtVistaHuman = require('ProtVista');
        var humaninstance = new ProtVistaHuman({
          el: humanDiv,
          uniprotacc: protvistaHumanUni,
          defaultSources: true,
          //These categories will **not** be rendered at all
          exclusions: ['SEQUENCE_INFORMATION', 'STRUCTURAL', 'TOPOLOGY', 'MOLECULE_PROCESSING', 'ANTIGEN'],
          //Your data sources are defined here
          customDataSource: {
            url: 'fileapi/resultFile/jsonData/protvistadataJson/human/externalLabeledFeatures_',
            source: 'MouseQuaPro',
            useExtension: true
          },
          categoryOrder: ['TARGETED_PROTEOMICS_ASSAY_HUMAN', 'PROTEOMICS', 'DOMAINS_AND_SITES', 'PTM', 'MUTAGENESIS'],
          //This feature will be preselected
          selectedFeature: {
          begin: humanPreSelectStart,
          end: humanPreSelectEnd,
          type: 'MRM'
          },
        });
    }
  }

}

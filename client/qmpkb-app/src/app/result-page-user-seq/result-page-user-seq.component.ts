import { Component, OnInit, OnDestroy, ViewChild, Renderer,HostListener,Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { DataTableDirective } from 'angular-datatables';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { Subject } from 'rxjs';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import { NgxSpinnerService } from 'ngx-spinner';
import * as Plotly from 'plotly.js';
import * as $ from "jquery";

declare var jquery: any;
declare let google: any;

@Component({
  selector: 'app-result-page-user-seq',
  templateUrl: './result-page-user-seq.component.html',
  styleUrls: ['./result-page-user-seq.component.css']
})
export class ResultPageUserSeqComponent implements OnInit,OnDestroy {
  dtOptions: any = {};
  dtOptionssummarystatUnq:any={};
  dtOptionsOther:any={};
  queryResPath: string;
  private routeSub:any;
  private req:any;
  errorStr:Boolean;
  uniprotacc:string;
  fileDownloadUrl;
  totallist:any;
  unqisostat:any;
  subcell:any;
  humandisease:any;
  querystrainData:any;
  querybioMatData:any;
  querynoOfDiseaseAssProt:any;
  querynoOfHumanOrtholog:any;
  updatedgo:any;
  keggchart:any;
  foundHits:number;
  fastafilename:any;
  queryData:any;

  mProtVal:any;
  mGenVal:any;
  mUKBVal:any;
  mPepassVal:any;
  mStrVal:any;
  mKoutVal:any;
  mBioTisVal:any;
  mGenderVal:any;
  mGenExpVal:any;
  hProtVal:any;
  hUKBVal:any;
  hPresPepVal:any;
  mSCellVal:any;
  mPathVal:any;
  hDisVal:any;
  mGOVal:any;
  hDrugVal:any;

  query: string;

  screenWidth:any;
  plotlyData:any=[];
  plotDataUnit: string;
  userQueryFastaResult:any;
  downloadResultQuery:any;

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
  private renderer: Renderer,
  private router: Router,
  private _qmpkb:QmpkbService,
  private spinner: NgxSpinnerService,
  ){ 
      this.getScreenSize();
  }
  @Input()
  set resultFastaTermQuery(resultFastaQuery:any){
      this.userQueryFastaResult=resultFastaQuery;

  }
  ngOnInit() {
    this.spinner.show();
    //this.location.go('/resultsseq/')
    this.queryData=this.userQueryFastaResult;
    this.query = this.queryData.searchterm;
    this.queryResPath=this.queryData.filepath;
    this.totallist=this.queryData.totallist;
    this.unqisostat=this.queryData.unqisostat;
    this.subcell=this.queryData.subcell;
    this.humandisease=this.queryData.humandisease;
    this.querystrainData=this.queryData.querystrainData;
    this.querybioMatData=this.queryData.querybioMatData;
    this.querynoOfDiseaseAssProt=this.queryData.querynoOfDiseaseAssProt;
    this.querynoOfHumanOrtholog=this.queryData.querynoOfHumanOrtholog;
    this.updatedgo=this.queryData.updatedgo;
    this.keggchart=this.queryData.keggchart;
    this.foundHits=this.queryData.foundHits;
    this.fastafilename=this.queryData.fastafilename;
    this.downloadResultQuery=this.queryResPath+'|Fasta';

    this.barplot(this.querybioMatData,this.querystrainData,this.subcell,this.updatedgo,this.humandisease);

    let destPath='fileapi/resultFile/jsonData/resultJson/'+this.queryResPath;
    let queryfastafilename=this.fastafilename;
    //let destPath='assets/'+this.queryResPath
    let detailResFile=this.queryResPath.split('/')[2].split('_search')[0];
    let datatableElement = this.datatableElement;
    this.dtOptions = {
      processing: true,
      serverSide: false,
      orderCellsTop: true,
      fixedHeader: true,
      pageLength: 10,
      pagingType: 'full_numbers',
      ajax: destPath,
      columns: [
        { 
          title: 'Protein',
          render: function (data, type, row) {
            if ((row["Protein"].trim()).length > 0){
              return row["Protein"].trim();
            } else {
              return 'NA';
            }
          }
        },
        { 
          title: 'Gene',
          data: 'Gene'
        },
        { 
          title: 'UniProtKB accession',
          render: function (data, type, row) {
            return '<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#protein">' + row["UniProtKB Accession"].trim() + '</a>';
          }
        },
        { 
          title: 'Peptide assay',
          className: 'details-control-pep',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data: any, type: any, row: any, meta) {
            if (row["Peptide Sequence"].trim().length > 0 ){
              const tempPepseq=row["Peptide Sequence"].trim();
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#assay"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const temprowdata=[tempPepseq,tempURL];
              return temprowdata.join("<br>");
            } else {
              ('<font color="black">No</font>');
            }
          },
          width:"15px"
        },
        { 
          title: 'Strain',
          className: 'details-control-strainCol',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data, type, row) {
            if ((row["Strain"].trim()).length > 0 && (row["Strain"].trim()) != "NA"){
              const array =(row["Strain"].trim()).split('|');
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#concentration"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const temprowdata=[array.join("<br>"),tempURL];
              return temprowdata.join("<br>");
            } else {
              return ('<font color="black">NA</font>');
            }
          },
          width:"15px"
        },
        { 
          title: 'Mutant',
          className: 'details-control-knockoutCol',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data, type, row) {
            if ((row["Knockout"].trim()).length > 0 && (row["Knockout"].trim()) != "NA"){
              const array =(row["Knockout"].trim()).split(';');
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#concentration"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const temprowdata=[array.join("<br>"),tempURL];
              return temprowdata.join("<br>");
            } else {
              return ('<font color="black">NA</font>');
            }
          },
          width:"15px"
        },
        { 
          title: 'Biological matrix',
          className: 'details-control-biomatrix',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data: any, type: any, row: any, meta) {
            if (row["Biological Matrix"].trim() != "NA" ){
               const tempbiomat=row["Biological Matrix"].trim();
               const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#concentration"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
               const temprowdata=[tempbiomat,tempURL];
               return temprowdata.join("<br>");
            } else {
              return ('<font color="black">NA</font>');
            }
          },
           width:"15px"
        },
        { 
          title: 'Sex',
          className: 'details-control-sexCol',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data, type, row) {
            if ((row["Sex"].trim()).length > 0 && (row["Sex"].trim()) != "NA"){
              const array =(row["Sex"].trim()).split('|');
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#concentration"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const temprowdata=[array.join("<br>"),tempURL];
              return temprowdata.join("<br>");
            } else {
              return ('<font color="black">NA</font>');
            }
          },
          width:"15px"
        },
        { 
          title: 'Gene expression',
          className: 'details-control-expCol',
          orderable: true,
          data: null,
          defaultContent: '',
          render: function (data, type, row) {
            if ((row["Gene Expression View"].trim()).length > 0 && (row["Gene Expression View"].trim()) != "No"){
                const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#genExp">....more</a>';
                const tempdata=row["Gene Expression View"].trim();
                //const temprowdata=[tempdata,tempURL];
                const temprowdata=[tempURL];
                return temprowdata.join("<br>");
            } else {
              return 'No';
            }
          },
          width:"15px"
        },
        { 
          title: 'Human ortholog',
          render: function (data, type, row) {
            if ((row["Human ProteinName"].trim()).length > 0 && (row["Human ProteinName"].trim()) != "NA"){
              const array =(row["Human ProteinName"].trim()).split('|');
              return array.join("<br>");
            } else {
              return 'NA';
            }
          }
        },
        { 
          title: 'UniProtKB accession human ortholog',
          render: function (data, type, row) {
            if ((row["Human UniProtKB Accession"].trim()).length > 0 && (row["Human UniProtKB Accession"].trim()) != "NA"){
              const array =(row["Human UniProtKB Accession"].trim()).split(',');
              array.forEach(function(element, index) {
              array[index] = '<a target="_blank" routerLinkActive="active" href="https://www.uniprot.org/uniprot/' + element+'">'+element+ '</a>';
              });
              return array.join("<br>");
            } else {
              return 'NA';
            }
          }
        },
        { 
          title: 'Peptide present in human ortholog',
          render: function (data, type, row) {
            return row["Present in human ortholog"];
          }
        },
        { 
          title: 'Subcellular localization',
          render: function (data, type, row) {
            if ((row["SubCellular"].trim()).length > 0){
              return (row["SubCellular"].trim()).split('|').join("<br>");
            } else {
              return 'NA';
            }
          }
        },
        { 
          title: 'Involvement in pathways',
          render: function (data, type, row) {
            if ((row["Mouse Kegg Pathway Name"].trim()).length > 0 && (row["Mouse Kegg Pathway Name"].trim()) != "NA"){
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#pathway"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const tempdata=(row["Mouse Kegg Pathway Name"].trim()).split("|").slice(0, 3).join("<br>");
              const temprowdata=[tempdata,tempURL];
              return temprowdata.join("<br>");
            } else {
              return 'NA';
            }
            
          }
        },
        { 
          title: 'Go term associations',
          render: function (data, type, row) {
            if ((row["Mouse Go Name"].trim()).length > 0 && (row["Mouse Go Name"].trim()) != "NA"){
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#go"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const tempdata=(row["Mouse Go Name"].trim()).split("|").slice(0, 3).join("<br>");
              const temprowdata=[tempdata,tempURL];
              return temprowdata.join("<br>");
            } else {
              return 'NA';
            }

          }
        },
        { 
          title: 'Involvement in disease',
          render: function (data, type, row) {
            if ((row["Human Disease Name"].trim()).length > 0 && (row["Human Disease Name"].trim()) != "NA"){
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#disease"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';
              const tempdata=(row["Human Disease Name"].trim()).split("|").slice(0, 3).join("<br>");
              const temprowdata=[tempdata,tempURL];
              return temprowdata.join("<br>");
            } else {
              return 'NA';
            }
            
          }
        }, 
        { 
          title: 'Drug associations',
          render: function (data, type, row) {
            if ((row["Human Drug Bank"].trim()).length > 0 && (row["Human Drug Bank"].trim()) != "NA"){
              const tempURL ='<a target="_blank" routerLinkActive="active" href="/detailinformation?uniProtKb=' + row["UniProtKB Accession"].trim() + '&resultID=' + detailResFile +'&seqID=' + queryfastafilename +'#drug"><i class="fa fa-plus-square" aria-hidden="true"></i></a>';              
              const tempdata=(row["Human Drug Bank"].trim()).split('|').slice(0, 3).join("<br>");
              const temprowdata=[tempdata,tempURL];
              return temprowdata.join("<br>");

            }else {
              return 'NA';
            }
          }
        },
        { 
          title: 'Search Pathway(s) Mouse',
          className: 'noVis',
          render: function (data, type, row) {
            if ((row["Mouse Kegg Pathway Name"].trim()).length > 0 && (row["Mouse Kegg Pathway Name"].trim()) != "NA"){
              const tempdata=(row["Mouse Kegg Pathway Name"].trim()).split("|").join("<br>");
              return tempdata;
            } else {
              return 'NA';
            }
            
          },
          visible:false
          
        },
        { 
          title: 'Search Go Term Name-Mouse',
          className: 'noVis',
          render: function (data, type, row) {
            if ((row["Mouse Go Name"].trim()).length > 0 && (row["Mouse Go Name"].trim()) != "NA"){
              const tempdata=(row["Mouse Go Name"].trim()).split("|").join("<br>");
              return tempdata;
            } else {
              return 'NA';
            }

          },
          visible:false
        },
        { 
          title: 'Search Involvement in disease-ortholog',
          className: 'noVis',
          render: function (data, type, row) {
            if ((row["Human Disease Name"].trim()).length > 0 && (row["Human Disease Name"].trim()) != "NA"){
              const tempdata=(row["Human Disease Name"].trim()).split("|").join("<br>");
              return tempdata;
            } else {
              return 'NA';
            }
            
          },
          visible:false
        },              
        { 
          title: 'Search Drug Bank-ortholog',
          className: 'noVis',
          render: function (data, type, row) {
            if ((row["Human Drug Bank"].trim()).length > 0 && (row["Human Drug Bank"].trim()) != "NA"){
              const tempdata=(row["Human Drug Bank"].trim()).split('|').join("<br>");
              return tempdata;
            }else {
              return 'NA';
            }
          },
          visible:false
        }      
      ], 
      scrollX:true,
      scrollY:'650px',
      scrollCollapse:true,
      // Declare the use of the extension in the dom parameter
      dom: 'lBrtip',
      // Configure the buttons
      buttons: [
        {
          extend:'colvis',
          columns:':not(.noVis)'
        }
      ],
      autoWidth:true
    };
    if (Object.keys(this.keggchart).length >0 ){
      this.drawChart(this.keggchart);
    }
    this.dtOptionssummarystatUnq = {
        searching: false,
        info: false,
        ordering: false,
        paging: false,
        autoWidth:true  
    };
    this.dtOptionsOther = {
      order:[[1,'desc']],
      autoWidth:true
    };
    this.spinner.hide();

  }

    ngAfterViewInit(): void {

    const self = this;
    this.datatableElement.dtInstance.then((dtInstance: DataTables.Api) => {
      dtInstance.columns().every(function () {
      const that = this;
      $( 'table thead'  ).on( 'keyup', ".column_search",function () {
        let colIndex:any;
        colIndex=$(this).parent().index();
        console.log(colIndex,this['value']);
        if (colIndex == 13){
            self.datatableElement['dt'].columns( 17 ).search(this['value']).draw();
        } else if (colIndex == 14){
            self.datatableElement['dt'].columns( 18 ).search(this['value']).draw();
        } else if (colIndex == 15){
            self.datatableElement['dt'].columns( 19 ).search(this['value']).draw();
        } else if (colIndex == 16){
            self.datatableElement['dt'].columns( 20 ).search(this['value']).draw();
        } else {
            self.datatableElement['dt'].columns( colIndex ).search(this['value']).draw();
        } 
      });
      });
    });

  }

    drawChart(keggchart) {
      const self = this;
      google.charts.load('current', {packages: ['corechart', 'bar']});
      google.charts.setOnLoadCallback(drawKeggChart);

      function drawKeggChart() {
         var tempdatakegg=keggchart;
           var dataPlot = google.visualization.arrayToDataTable(tempdatakegg);
           const options = {
              'height':400,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                title: 'No. of proteins covered',
                 minValue: 0,
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              axes: {
                  x: {
                    0: { side: 'top'}
                  }
              },
              vAxis: {
                title: 'KEGG pathway',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
            };
            const chart = new google.charts.Bar(document.getElementById('chart_div_pathway'));
            const container = document.getElementById('chart_div_pathway');
            var axislabels:any=[];
            google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
            
            function uselessHandler() {
              $('#chart_div_pathway path').css('cursor','pointer')
              $('#chart_div_pathway text').css('cursor','pointer')
             }
            
              google.visualization.events.addListener(chart, 'select', selectHandler);
              google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
              google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
       
             // use the 'ready' event to modify the chart once it has been drawn
            google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
             });
       
       
             function selectHandler(e) {
              var selection = chart.getSelection();
                if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempGoogleDataURL='/dataload/googleChartData_'+mydataSelect+'_keggPathway';
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  //window.open(tempGoogleDataURL,'_blank');
                  self.mPathVal=mydataSelect;
                  self.datatableElement['dt'].columns( 17 ).search(mydataSelect).draw();               
                  chart.setSelection([])
               }
             }        
            
             function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOver) {
                      axislabels[i].setAttribute('font-weight', 'bold');
                    }
                  }
              }
             }
          
             function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOut) {
                      axislabels[i].removeAttribute('font-weight', 'bold');
                    }
                  }
              }
             }
          
            container.addEventListener('click', clickHandlerLabel);
            container.addEventListener("mouseover", mouseOverLabel);
            container.addEventListener("mouseout", mouseOutrLabel);
         
            function mouseOverLabel(propertiesLabel) {
             if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                        axislabels[i].setAttribute('font-weight', 'bold');
                        const findArray =tempdatakegg.filter(p => p[0] == propertiesLabel.target.textContent);
                        var textY=propertiesLabel.target.getAttribute("y");
                        var textX=propertiesLabel.target.getAttribute("x");
                        var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdatakegg[0][1]+':'+'<br>'+findArray[0][1];                        
                        var bars = container.getElementsByTagName('path');
                        for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip);  
                          }
                        }
                    }
              }
          }
             }
            function mouseOutrLabel(propertiesOutLabel) {
             if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                       axislabels[i].removeAttribute('font-weight', 'bold');
                       var bars = container.getElementsByTagName('path');
                       for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesOutLabel.target.textContent){
                            bars[j].setAttribute('fill','#4285f4');
                            $('.tooltiptextLabel').html('');
                            $('.tooltiptextLabel').css('visibility','hidden');
                            $('.tooltiptextLabel').css('top',0);
                            $('.tooltiptextLabel').css('left',0);

                          }
                       }
                    }
                
                  }
            }
         }  
      
           function clickHandlerLabel(e) {
            if (e.target.tagName === 'text') {
              const findArray =tempdatakegg.filter(p => p[0] == e.target.textContent);
              if (typeof findArray[0] != "undefined"){
                if (tempdatakegg.indexOf(findArray[0])){
                    var tempGoogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_keggPathway';
                    $('tfoot input').val('');
                    self.datatableElement['dt'].columns().search('').draw();
                    self.datatableElement['dt'].search('').draw();                    
                    self.mPathVal=e.target.textContentt;
                    self.datatableElement['dt'].columns( 17 ).search(e.target.textContent).draw();                  
                      //window.open(tempGoogleDataURL,'_blank');

                }
              }
            }
           }
             chart.draw(dataPlot, google.charts.Bar.convertOptions(options));
          }
          $(document).ready(function() {
            $(window).resize(function() {
              drawKeggChart();
            })
          })

    }

    barplot(matrixData:any,mouseStrainData:any,subCellData:any,goData:any,humanDiseaseData:any):void {
      const self = this;

      google.charts.load('current', {packages: ['bar']});
      google.charts.setOnLoadCallback(drawMatrixChart);
      google.charts.setOnLoadCallback(drawStrainChart);
      google.charts.setOnLoadCallback(drawSubCellChart);
      google.charts.setOnLoadCallback(drawGOChart);
      google.charts.setOnLoadCallback(drawDisChart);

      function drawMatrixChart() {
         var tempdatamatrix=matrixData;
         var dataPlot = google.visualization.arrayToDataTable(tempdatamatrix);
         const options = {
              'height':400,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                title: 'No. of assays',
                 minValue: 0,
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              vAxis: {
                title: 'Biological Matrix',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
           };
           const chart = new google.charts.Bar(document.getElementById('chart_div_matrix'));
            
             const container = document.getElementById('chart_div_matrix');
             var axislabels:any=[];
             google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
            
             function uselessHandler() {
              $('#chart_div_matrix path').css('cursor','pointer')
              $('#chart_div_matrix text').css('cursor','pointer')
            }
            
             google.visualization.events.addListener(chart, 'select', selectHandler);
             google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
             google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
       
            // use the 'ready' event to modify the chart once it has been drawn
           google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
            });
       
       
            function selectHandler(e) {
              var selection = chart.getSelection();
                if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempGoogleDataURL='/dataload/googleChartData_'+mydataSelect+'_biologicalMatrix';
                  //window.open(tempGoogleDataURL,'_blank');
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  self.mBioTisVal=mydataSelect;
                  self.datatableElement['dt'].columns( 6 ).search(mydataSelect).draw();                 
                  chart.setSelection([]);
               }
            }        
            
            function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOver) {
                      axislabels[i].setAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
            function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOut) {
                      axislabels[i].removeAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
           container.addEventListener('click', clickHandlerLabel);
           container.addEventListener("mouseover", mouseOverLabel);
           container.addEventListener("mouseout", mouseOutrLabel);
         
           function mouseOverLabel(propertiesLabel) {
             if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                        axislabels[i].setAttribute('font-weight', 'bold');
                        const findArray =tempdatamatrix.filter(p => p[0] == propertiesLabel.target.textContent);
                        var textY=propertiesLabel.target.getAttribute("y");
                        var textX=propertiesLabel.target.getAttribute("x");
                        var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdatamatrix[0][1]+':'+'<br>'+findArray[0][1]+'<br>'+tempdatamatrix[0][2]+':'+'<br>'+findArray[0][2];                    
                        var bars = container.getElementsByTagName('path');
                        for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip);                              
                          }
                        }
                        //this block of code for proteins and peptide              
/*                        for(var j = 0; j<bars.length; j+=2){
                          if(dataPlot.getValue(j/2,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            bars[j+1].setAttribute('fill','#ba3a2f');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip); 
                          }
                        } */                       
                    }
              }
          }
            }
           function mouseOutrLabel(propertiesOutLabel) {
             if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                       axislabels[i].removeAttribute('font-weight', 'bold');
                       var bars = container.getElementsByTagName('path');
                       for(var j = 0; j<bars.length; j++){
                         if(dataPlot.getValue(j,0) == propertiesOutLabel.target.textContent){
                           bars[j].setAttribute('fill','#4285f4');
                           $('.tooltiptextLabel').html('');
                           $('.tooltiptextLabel').css('visibility','hidden');
                           $('.tooltiptextLabel').css('top',0);
                           $('.tooltiptextLabel').css('left',0);      

                         }
                       }
                       //this block of code for proteins and peptide                        
/*                       for(var j = 0; j<bars.length; j+=2){
                          if(dataPlot.getValue(j/2,0) == propertiesOutLabel.target.textContent){
                            bars[j].setAttribute('fill','#4285f4');
                            bars[j+1].setAttribute('fill','#db4437');
                            $('.tooltiptextLabel').html('');
                            $('.tooltiptextLabel').css('visibility','hidden');
                            $('.tooltiptextLabel').css('top',0);
                            $('.tooltiptextLabel').css('left',0);

                          }
                       }  */                     
                    }
                
                  }
            }
        }  
      
          function clickHandlerLabel(e) {
            if (e.target.tagName === 'text') {
              const findArray =tempdatamatrix.filter(p => p[0] == e.target.textContent);
              if (typeof findArray[0] != "undefined"){
                if (tempdatamatrix.indexOf(findArray[0])){
                    var tempGoogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_biologicalMatrix';
                    $('tfoot input').val('');
                    self.datatableElement['dt'].columns().search('').draw();
                    self.datatableElement['dt'].search('').draw();                    
                    self.mBioTisVal=e.target.textContent;
                    self.datatableElement['dt'].columns( 6 ).search(e.target.textContent).draw();                     
                      //window.open(tempGoogleDataURL,'_blank');

                }
              }
            }
          }
          chart.draw(dataPlot, google.charts.Bar.convertOptions(options));

      }

      function drawStrainChart() {
         var tempdatastrain=mouseStrainData;
           var dataPlot = google.visualization.arrayToDataTable(tempdatastrain);
         const options = {
              'height':400,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                title: 'No. of assays',
                 minValue: 0,
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },      
              vAxis: {
                title: 'Strain',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
           };
           const chart = new google.charts.Bar(document.getElementById('chart_div_strain'));
             const container = document.getElementById('chart_div_strain');
             var axislabels:any=[];
             google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
            
             function uselessHandler() {
              $('#chart_div_strain path').css('cursor','pointer')
              $('#chart_div_strain text').css('cursor','pointer')
            }
            
             google.visualization.events.addListener(chart, 'select', selectHandler);
             google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
             google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
       
            // use the 'ready' event to modify the chart once it has been drawn
           google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
            });
       
       
            function selectHandler(e) {
              var selection = chart.getSelection();
                if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempGoogleDataURL='/dataload/googleChartData_'+mydataSelect+'_strain';
                  //window.open(tempGoogleDataURL,'_blank');
                  chart.setSelection([])
               }
            }        
            
            function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOver) {
                      axislabels[i].setAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
            function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOut) {
                      axislabels[i].removeAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
           container.addEventListener('click', clickHandlerLabel);
           container.addEventListener("mouseover", mouseOverLabel);
           container.addEventListener("mouseout", mouseOutrLabel);
         
           function mouseOverLabel(propertiesLabel) {
             if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                        axislabels[i].setAttribute('font-weight', 'bold');
                        const findArray =tempdatastrain.filter(p => p[0] == propertiesLabel.target.textContent);
                        var textY=propertiesLabel.target.getAttribute("y");
                        var textX=propertiesLabel.target.getAttribute("x");
                        var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdatastrain[0][1]+':'+'<br>'+findArray[0][1]+'<br>'+tempdatastrain[0][2]+':'+'<br>'+findArray[0][2];                    
                        var bars = container.getElementsByTagName('path');
                        for(var j = 0; j<bars.length; j+=2){
                          if(dataPlot.getValue(j/2,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            bars[j+1].setAttribute('fill','#ba3a2f');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip); 
                          }
                        }                        
                    }
              }
          }
            }
           function mouseOutrLabel(propertiesOutLabel) {
             if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                       axislabels[i].removeAttribute('font-weight', 'bold');
                       var bars = container.getElementsByTagName('path');
                       for(var j = 0; j<bars.length; j+=2){
                          if(dataPlot.getValue(j/2,0) == propertiesOutLabel.target.textContent){
                            bars[j].setAttribute('fill','#4285f4');
                            bars[j+1].setAttribute('fill','#db4437');
                            $('.tooltiptextLabel').html('');
                            $('.tooltiptextLabel').css('visibility','hidden');
                            $('.tooltiptextLabel').css('top',0);
                            $('.tooltiptextLabel').css('left',0);

                          }
                       }                        
                    }
                
                  }
            }
        }  
      
          function clickHandlerLabel(e) {
            if (e.target.tagName === 'text') {
              const findArray =tempdatastrain.filter(p => p[0] == e.target.textContent);
              if (typeof findArray[0] != "undefined"){
                if (tempdatastrain.indexOf(findArray[0])){
                    var tempGoogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_strain';
                    //window.open(tempGoogleDataURL,'_blank');

                }
              }
            }
          }
          chart.draw(dataPlot, google.charts.Bar.convertOptions(options));
      }

      function drawSubCellChart() {
         var tempdatasubCell=subCellData;
           var dataPlot = google.visualization.arrayToDataTable(tempdatasubCell);
         const options = {
              'height':300,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                title: 'No. of proteins covered',
                 minValue: 0,
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              vAxis: {
                title: 'SubCellular localization',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
           };
           const chart = new google.charts.Bar(document.getElementById('chart_div_subcell'));
             const container = document.getElementById('chart_div_subcell');
             var axislabels:any=[];
             google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
            
             function uselessHandler() {
              $('#chart_div_subcell path').css('cursor','pointer')
              $('#chart_div_subcell text').css('cursor','pointer')
            }
            
             google.visualization.events.addListener(chart, 'select', selectHandler);
             google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
             google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
       
            // use the 'ready' event to modify the chart once it has been drawn
           google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
            });
       
       
            function selectHandler(e) {
              var selection = chart.getSelection();
                if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempGoogleDataURL='/dataload/googleChartData_'+mydataSelect+'_subCellLoc';
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  self.mSCellVal=mydataSelect;
                  self.datatableElement['dt'].columns( 12 ).search(mydataSelect).draw();                 
                  //window.open(tempGoogleDataURL,'_blank');
                  chart.setSelection([])
               }
            }        
            
            function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOver) {
                      axislabels[i].setAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
            function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOut) {
                      axislabels[i].removeAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
           container.addEventListener('click', clickHandlerLabel);
           container.addEventListener("mouseover", mouseOverLabel);
           container.addEventListener("mouseout", mouseOutrLabel);
         
           function mouseOverLabel(propertiesLabel) {
             if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                        axislabels[i].setAttribute('font-weight', 'bold');
                        const findArray =tempdatasubCell.filter(p => p[0] == propertiesLabel.target.textContent);
                        var textY=propertiesLabel.target.getAttribute("y");
                        var textX=propertiesLabel.target.getAttribute("x");
                        var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdatasubCell[0][1]+':'+'<br>'+findArray[0][1];
                        var bars = container.getElementsByTagName('path');
                        for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip); 
                          }
                        }                        
                    }
              }
          }
            }
           function mouseOutrLabel(propertiesOutLabel) {
             if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                       axislabels[i].removeAttribute('font-weight', 'bold');
                       var bars = container.getElementsByTagName('path');
                       for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesOutLabel.target.textContent){
                            bars[j].setAttribute('fill','#4285f4');
                            $('.tooltiptextLabel').html('');
                            $('.tooltiptextLabel').css('visibility','hidden');
                            $('.tooltiptextLabel').css('top',0);
                            $('.tooltiptextLabel').css('left',0);

                          }
                       }                        
                    }
                
                  }
            }
        }  
      
          function clickHandlerLabel(e) {
            if (e.target.tagName === 'text') {
              const findArray =tempdatasubCell.filter(p => p[0] == e.target.textContent);
              if (typeof findArray[0] != "undefined"){
                if (tempdatasubCell.indexOf(findArray[0])){
                  var tempGoogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_subCellLoc';
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  self.mSCellVal=e.target.textContent;
                  self.datatableElement['dt'].columns( 12 ).search(e.target.textContent).draw();                  
                  //window.open(tempGoogleDataURL,'_blank');

                }
              }
            }      
          }
          chart.draw(dataPlot, google.charts.Bar.convertOptions(options));
      }

      function drawGOChart() {
         var tempdataGO=goData;
           var dataPlot = google.visualization.arrayToDataTable(tempdataGO);
         const options = {
              'height':300,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                title: 'No. of proteins covered',
                 minValue: 0,
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              vAxis: {
                title: 'GO Term Name',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
           };
           const chart = new google.charts.Bar(document.getElementById('chart_div_GO'));
             const container = document.getElementById('chart_div_GO');
             var axislabels:any=[];
             google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
            
             function uselessHandler() {
              $('#chart_div_GO path').css('cursor','pointer')
              $('#chart_div_GO text').css('cursor','pointer')
            }
            
             google.visualization.events.addListener(chart, 'select', selectHandler);
             google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
             google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
       
            // use the 'ready' event to modify the chart once it has been drawn
           google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
            });
       
       
            function selectHandler(e) {
              var selection = chart.getSelection();
                if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempGoogleDataURL='/dataload/googleChartData_'+mydataSelect+'_goTermName';
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  self.mGOVal=mydataSelect;
                  self.datatableElement['dt'].columns( 18 ).search(mydataSelect).draw();                  
                  //window.open(tempGoogleDataURL,'_blank');
                  chart.setSelection([])
               }
            }        
            
            function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOver) {
                      axislabels[i].setAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
            function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == mydataOut) {
                      axislabels[i].removeAttribute('font-weight', 'bold');
                    }
                  }
              }
            }
          
           container.addEventListener('click', clickHandlerLabel);
           container.addEventListener("mouseover", mouseOverLabel);
           container.addEventListener("mouseout", mouseOutrLabel);
         
           function mouseOverLabel(propertiesLabel) {
             if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                        axislabels[i].setAttribute('font-weight', 'bold');
                        const findArray =tempdataGO.filter(p => p[0] == propertiesLabel.target.textContent);
                        var textY=propertiesLabel.target.getAttribute("y");
                        var textX=propertiesLabel.target.getAttribute("x");
                        var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdataGO[0][1]+':'+'<br>'+findArray[0][1];
                        var bars = container.getElementsByTagName('path');
                        for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesLabel.target.textContent){
                            bars[j].setAttribute('fill','#3871cf');
                            $('.tooltiptextLabel').css('visibility','visible');
                            $('.tooltiptextLabel').css('position', 'absolute');
                            $('.tooltiptextLabel').css('top',textY+'px');
                            $('.tooltiptextLabel').css('left',textX+'px');
                            $('.tooltiptextLabel').html(customTextToolTip); 
                          }
                        }                        
                    }
              }
          }
            }
           function mouseOutrLabel(propertiesOutLabel) {
             if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                    if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                       axislabels[i].removeAttribute('font-weight', 'bold');
                       var bars = container.getElementsByTagName('path');
                       for(var j = 0; j<bars.length; j++){
                          if(dataPlot.getValue(j,0) == propertiesOutLabel.target.textContent){
                            bars[j].setAttribute('fill','#4285f4');
                            $('.tooltiptextLabel').html('');
                            $('.tooltiptextLabel').css('visibility','hidden');
                            $('.tooltiptextLabel').css('top',0);
                            $('.tooltiptextLabel').css('left',0);

                          }
                       }                        
                    }
                
                  }
            }
        }  
      
          function clickHandlerLabel(e) {
            if (e.target.tagName === 'text') {
              const findArray =tempdataGO.filter(p => p[0] == e.target.textContent);
              if (typeof findArray[0] != "undefined"){
                if (tempdataGO.indexOf(findArray[0])){
                  var tempGoogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_goTermName';
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();                  
                  self.mGOVal=e.target.textContent;
                  self.datatableElement['dt'].columns( 18 ).search(e.target.textContent).draw();                  
                  //window.open(tempGoogleDataURL,'_blank');

                }
              }
            } 
          }
          chart.draw(dataPlot, google.charts.Bar.convertOptions(options));
      }

      function drawDisChart() {
          var tempdataDis=humanDiseaseData;
          var dataPlot = google.visualization.arrayToDataTable(tempdataDis);
          const options = {
              'height':400,
              bar: {groupWidth: "100%"},
              legend: {position: 'none'},
              hAxis: {
                  title: 'No. of proteins associated',
                   minValue: 0,
                    textStyle : {
                        fontSize: 16 // or the number you want
                    },
              },
              vAxis: {
                title: 'Disease Name',
                  textStyle : {
                      fontSize: 16 // or the number you want
                  },
              },
              bars: 'horizontal'
          };
          const chart = new google.charts.Bar(document.getElementById('chart_div_disease'));
          const container = document.getElementById('chart_div_disease');
          var axislabels:any=[];
          google.visualization.events.addListener(chart, 'onmouseover', uselessHandler);
          
          function uselessHandler() {
              $('#chart_div_disease path').css('cursor','pointer')
              $('#chart_div_disease text').css('cursor','pointer')
          }
          
          google.visualization.events.addListener(chart, 'select', selectHandler);
          google.visualization.events.addListener(chart, 'onmouseover', onmouseoverHandler);
          google.visualization.events.addListener(chart, 'onmouseout', onmouseoutHandler);
     
          // use the 'ready' event to modify the chart once it has been drawn
          google.visualization.events.addListener(chart, 'ready', function () {
              axislabels = container.getElementsByTagName('text');
          });
     
     
          function selectHandler(e) {
              var selection = chart.getSelection();
              if (selection.length > 0) {
                  var colLabelSelect = dataPlot.getColumnLabel(selection[0].column);
                  var mydataSelect= dataPlot.getValue(selection[0].row,0);
                  var tempDisogleDataURL='/dataload/googleChartData_'+mydataSelect+'_disTermName';
                  //window.open(tempDisogleDataURL,'_blank');
                  $('tfoot input').val('');
                  self.datatableElement['dt'].columns().search('').draw();
                  self.datatableElement['dt'].search('').draw();
                  self.hDisVal=mydataSelect;
                  self.datatableElement['dt'].columns( 19 ).search(mydataSelect).draw();
                  chart.setSelection([])
              }
          }        
          
          function onmouseoverHandler(propertiesOver) {
              var hooverOverSelection= propertiesOver;
              if (Object.keys(hooverOverSelection).length > 0 && typeof hooverOverSelection.column !== "undefined") {
                  var colLabelOver=dataPlot.getColumnLabel(hooverOverSelection.column);
                  var mydataOver =dataPlot.getValue(hooverOverSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                      if (axislabels[i].textContent == mydataOver) {
                          axislabels[i].setAttribute('font-weight', 'bold');
                      }
                  }
              }
          }
        
          function onmouseoutHandler(propertiesOut) {
              var hooverOutSelection= propertiesOut;
              if (Object.keys(hooverOutSelection).length > 0 && typeof hooverOutSelection.column !== "undefined") {
                  var mydataOut =dataPlot.getValue(hooverOutSelection.row,0);
                  for (var i = 0; i < axislabels.length; i++) {
                      if (axislabels[i].textContent == mydataOut) {
                          axislabels[i].removeAttribute('font-weight', 'bold');
                      }
                  }
              }
          }
        
          container.addEventListener('click', clickHandlerLabel);
          container.addEventListener("mouseover", mouseOverLabel);
          container.addEventListener("mouseout", mouseOutrLabel);
       
          function mouseOverLabel(propertiesLabel) {
              if (propertiesLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                      if (axislabels[i].textContent == propertiesLabel.target.textContent) {
                          axislabels[i].setAttribute('font-weight', 'bold');
                          const findArray =tempdataDis.filter(p => p[0] == propertiesLabel.target.textContent);
                          var textY=propertiesLabel.target.getAttribute("y");
                          var textX=propertiesLabel.target.getAttribute("x");
                          var customTextToolTip='<b>'+propertiesLabel.target.textContent+'</b>'+'<br>'+tempdataDis[0][1]+':'+'<br>'+findArray[0][1];
                          var bars = container.getElementsByTagName('path');
                          for(var j = 0; j<bars.length; j++){
                            if(dataPlot.getValue(j,0) == propertiesLabel.target.textContent){
                              bars[j].setAttribute('fill','#3871cf');
                              $('.tooltiptextLabel').css('visibility','visible');
                              $('.tooltiptextLabel').css('position', 'absolute');
                              $('.tooltiptextLabel').css('top',textY+'px');
                              $('.tooltiptextLabel').css('left',textX+'px');
                              $('.tooltiptextLabel').html(customTextToolTip); 
                            }
                          }
                      }
                      const findArray =tempdataDis.filter(p => p[0] == propertiesLabel.target.textContent);
                  }
              }
          }
          function mouseOutrLabel(propertiesOutLabel) {
              if (propertiesOutLabel.target.tagName === 'text') {
                  for (var i = 0; i < axislabels.length; i++) {
                      if (axislabels[i].textContent == propertiesOutLabel.target.textContent) {
                          axislabels[i].removeAttribute('font-weight', 'bold');
                          var bars = container.getElementsByTagName('path');
                          for(var j = 0; j<bars.length; j++){
                             if(dataPlot.getValue(j,0) == propertiesOutLabel.target.textContent){
                               bars[j].setAttribute('fill','#4285f4');
                               $('.tooltiptextLabel').html('');
                               $('.tooltiptextLabel').css('visibility','hidden');
                               $('.tooltiptextLabel').css('top',0);
                               $('.tooltiptextLabel').css('left',0);      

                             }
                          }                       
                      }
              
                  }
              }
          }  
    
          function clickHandlerLabel(e) {
              if (e.target.tagName === 'text') {
                const findArray =tempdataDis.filter(p => p[0] == e.target.textContent);
                if (typeof findArray[0] != "undefined"){
                  if (tempdataDis.indexOf(findArray[0])){
                    var tempDisogleDataURL='/dataload/googleChartData_'+e.target.textContent+'_disTermName';
                    $('tfoot input').val('');
                    self.datatableElement['dt'].columns().search('').draw();
                    self.datatableElement['dt'].search('').draw();
                    self.hDisVal=e.target.textContent;
                    self.datatableElement['dt'].columns( 19 ).search(e.target.textContent).draw();
                    //window.open(tempGoogleDataURL,'_blank');

                  }
                }
              } 
          }
        chart.draw(dataPlot, google.charts.Bar.convertOptions(options));
      }
        $(document).ready(function() {
          $(window).resize(function() {
            drawMatrixChart();
            drawStrainChart();
            drawSubCellChart();
            drawGOChart();
            drawDisChart();
          })
        })
      }

  toggleAccordian(event) {
      var element = event.target;
      element.classList.toggle("active");     
      var panel = element.nextElementSibling;
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
      } else {
        panel.style.maxHeight = panel.scrollHeight + "px";
      }
 }
  clearFilterSearch(){
    $('tfoot input').val('');
    this.mProtVal='';
    this.mGenVal='';
    this.mUKBVal='';
    this.mPepassVal='';
    this.mStrVal='';
    this.mKoutVal='';
    this.mBioTisVal='';
    this.mGenderVal='';
    this.mGenExpVal='';
    this.hProtVal='';
    this.hUKBVal='';
    this.hPresPepVal='';
    this.mSCellVal='';
    this.mPathVal='';
    this.hDisVal='';
    this.mGOVal='';
    this.hDrugVal='';
    this.datatableElement['dt'].columns().search('').draw();
    this.datatableElement['dt'].search('').draw();
  }
  ngOnDestroy(){
    this.routeSub.unsubscribe();
  }
}

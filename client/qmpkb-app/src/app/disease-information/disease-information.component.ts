import { Component, OnInit, OnDestroy,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-disease-information',
  templateUrl: './disease-information.component.html',
  styleUrls: ['./disease-information.component.css']
})
export class DiseaseInformationComponent implements OnInit {
  disDataStatus=false;
  humanDiseaseUniProt:any;
  humanDiseaseDisGeNet:any;
  humanDiseaseUniProtArray:any;
  humanDiseaseDisGeNetArray:any;
  diseaseInputData:any;
  filterredHumanDiseaseUniProt:any;
  filterredHumanDiseaseDisGeNet:any;
  filterHumanDiseaseUniProtStatus=false;
  filterHumanDiseaseDisGeNetStatus=false;

  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set diseasetermQuery(disQuery:any){
      this.diseaseInputData=disQuery;

  }

  ngOnInit() {
  	this.disDataStatus=true;
    this.humanDiseaseUniProtArray=this.diseaseInputData.humanDiseaseUniProt;
  	this.humanDiseaseUniProt=this.diseaseInputData.humanDiseaseUniProt.join('; ');
    this.humanDiseaseDisGeNetArray=this.diseaseInputData.humanDiseaseDisGeNet;
  	this.humanDiseaseDisGeNet=this.diseaseInputData.humanDiseaseDisGeNet.join('; ');
  }

  ngAfterViewInit(): void {
      var self= this;
      $("#myInputUniProt").on("keyup", function() {
        const valueUniProt = $(this).val().toString().toLowerCase();
        if (valueUniProt.trim().length > 0){
          self.filterHumanDiseaseUniProtStatus=true;
          const textArrayUniProt=self.humanDiseaseUniProtArray;
          let textContentUniProt=[];
          for(let i=0; i < textArrayUniProt.length; i++){
              const strUniProt = textArrayUniProt[i];
              const divUniProt=document.createElement('div');
              divUniProt.innerHTML=strUniProt;
              if (textArrayUniProt[i] == 'NA'){
                textContentUniProt.push(textArrayUniProt[i]);
              } else{
               textContentUniProt.push(divUniProt.children[0].textContent);
              }
          }
          const filterredUniProt=textContentUniProt.filter(function (elem) {
             return elem.toString().toLowerCase().indexOf(valueUniProt) > -1;
          });
          if (filterredUniProt.length >0){
              const tempData=[];
              for(let j=0; j < filterredUniProt.length; j++){
                tempData.push(textArrayUniProt[textContentUniProt.indexOf(filterredUniProt[j])])
              }
              self.filterredHumanDiseaseUniProt=tempData.join('; '); 
          } else{
             self.filterredHumanDiseaseUniProt='Oopps. No result matched with your search criteria!'; 
          }      
        } 
        if (valueUniProt.trim().length == 0){
          self.filterHumanDiseaseUniProtStatus=false;
        }
      });

      $("#myInputDisGenNet").on("keyup", function() {
        const valueDisGenNet = $(this).val().toString().toLowerCase();
        if (valueDisGenNet.trim().length > 0){
          self.filterHumanDiseaseDisGeNetStatus=true;
          const textArrayDisGeNet=self.humanDiseaseDisGeNetArray;
          let textContentDisGeNet=[];
          for(let i=0; i < textArrayDisGeNet.length; i++){
              const strDisGeNet = textArrayDisGeNet[i];
              const divDisGeNet=document.createElement('div');
              divDisGeNet.innerHTML=strDisGeNet;
              if (textArrayDisGeNet[i] == 'NA'){
                textContentDisGeNet.push(textArrayDisGeNet[i]);
              } else{
                textContentDisGeNet.push(divDisGeNet.children[0].textContent);
              }
              
          }
          const filterredDisGeNet=textContentDisGeNet.filter(function (elem) {
             return elem.toString().toLowerCase().indexOf(valueDisGenNet) > -1;
          });
          if (filterredDisGeNet.length >0){
              const tempData=[];
              for(let j=0; j < filterredDisGeNet.length; j++){
                tempData.push(textArrayDisGeNet[textContentDisGeNet.indexOf(filterredDisGeNet[j])])
              }
              self.filterredHumanDiseaseDisGeNet=tempData.join('; '); 
          } else{
             self.filterredHumanDiseaseDisGeNet='Oopps. No result matched with your search criteria!'; 
          }      
        } 
        if (valueDisGenNet.trim().length == 0){
          self.filterHumanDiseaseDisGeNetStatus=false;
        }
      });

  }
  openTabsDis(evt, tabName) {
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontentdisease");
      for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablinksdisease");
      for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
      }
      document.getElementById(tabName).style.display = "block";
      evt.currentTarget.className += " active";
  }

}

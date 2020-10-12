import { Component, OnInit, OnDestroy,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-drug-bank',
  templateUrl: './drug-bank.component.html',
  styleUrls: ['./drug-bank.component.css']
})
export class DrugBankComponent implements OnInit {

  drugDataStatus=false;
  drugBankQueryData:any;
  drugBankInputData:any;
  drugBankInputDataArray:any;

  filterredDrugBankData:any;
  filterDrugBankDataStatus=false;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set drugBanktermQuery(drugQuery:any){
      this.drugBankQueryData=drugQuery;

  }

  ngOnInit() {
  	this.drugDataStatus=true;
    this.drugBankInputDataArray=this.drugBankQueryData.drugBankDataArray;
  	this.drugBankInputData=this.drugBankQueryData.drugBankData;
  }

  ngAfterViewInit(): void {
      var self= this;
      $("#myInputDrug").on("keyup", function() {
        const valueDrug = $(this).val().toString().toLowerCase();
        if (valueDrug.trim().length > 0){
          self.filterDrugBankDataStatus=true;
          const textArrayDrug=self.drugBankInputDataArray;
          let textContentDrug=[];
          for(let i=0; i < textArrayDrug.length; i++){
              const strDrug = textArrayDrug[i];
              const divDrug=document.createElement('div');
              divDrug.innerHTML=strDrug;
              if (textArrayDrug[i] == 'NA'){
              	textContentDrug.push(textArrayDrug[i]);
              } else{
              	textContentDrug.push(divDrug.children[0].textContent);
              }
              
          }
          const filterredDrug=textContentDrug.filter(function (elem) {
             return elem.toString().toLowerCase().indexOf(valueDrug) > -1;
          });
          if (filterredDrug.length >0){
              const tempData=[];
              for(let j=0; j < filterredDrug.length; j++){
                tempData.push(textArrayDrug[textContentDrug.indexOf(filterredDrug[j])])
              }
              self.filterredDrugBankData=tempData.join('; '); 
          } else{
             self.filterredDrugBankData='Oopps. No result matched with your search criteria!'; 
          }      
        } 
        if (valueDrug.trim().length == 0){
          self.filterDrugBankDataStatus=false;
        }
      });
  }

}

import { Component, OnInit, OnDestroy,Input} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-subcell-location',
  templateUrl: './subcell-location.component.html',
  styleUrls: ['./subcell-location.component.css']
})
export class SubcellLocationComponent implements OnInit {

  subCellDataStatus=false;
  subCellQueryData:any;
  subcellInputData:any;
  subcellInputDataArray:any;


  filterredSubcell:any;
  filterSubCellStatus=false;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private _qmpkb:QmpkbService
    ) { }

  @Input()
  set subCelltermQuery(subcellLocalQuery:any){
      this.subCellQueryData=subcellLocalQuery;

  }

  ngOnInit() {
  	this.subCellDataStatus=true;
    this.subcellInputDataArray=this.subCellQueryData.subcellArray;
  	this.subcellInputData=this.subCellQueryData.subcell;
  }

  ngAfterViewInit(): void {
     var self= this;

      $("#myInputSubCell").on("keyup", function() {
        const valueSubCell = $(this).val().toString().toLowerCase();
        if (valueSubCell.trim().length > 0){
          self.filterSubCellStatus=true;
          const textArraySubCell=self.subcellInputDataArray;        
          const filterredSubCell=textArraySubCell.filter(function (elem) {
                return elem.toString().toLowerCase().indexOf(valueSubCell) > -1;
          });
          if (filterredSubCell.length >0){
              self.filterredSubcell=filterredSubCell.join('; '); 
          } else{
             self.filterredSubcell='Oopps. No result matched with your search criteria!'; 
          }      
        } 
        if (valueSubCell.trim().length == 0){
          self.filterSubCellStatus=false;
        }
      });
  }

}

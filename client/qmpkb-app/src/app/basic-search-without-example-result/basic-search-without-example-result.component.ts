import { Component, OnInit, Input, Renderer } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, FormControl, Validators, FormArray } from '@angular/forms';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-basic-search-without-example-result',
  templateUrl: './basic-search-without-example-result.component.html',
  styleUrls: ['./basic-search-without-example-result.component.css']
})
export class BasicSearchWithoutExampleResultComponent implements OnInit {
  searchQuery: string;
  baseUrl;
  @Input()
  passedQuery: string;
  errorStr:Boolean;
  public alertIsVisible:boolean= false;

  constructor(
    private router: Router,
    private http: HttpClient,
    private renderer: Renderer,
    private _qmpkb:QmpkbService,
    private spinner: NgxSpinnerService
  ) { }


  ngOnInit() {
  }

  submitSearch(event,formData){

  	let searchedQuery = formData.value['searchterm']
    if (searchedQuery){
      this.spinner.show();
      let tempURL=window.location.origin+'/results/?searchterm='+searchedQuery;

      //window.open(tempURL,'_blank');
      //window.focus();
      location.assign(tempURL);

    }

  }

  moveAdv(){
    location.assign('/');
  }

}
import { Component, OnInit, Input, HostListener, Renderer } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, FormControl, Validators, FormArray } from '@angular/forms';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-basic-search-without-example',
  templateUrl: './basic-search-without-example.component.html',
  styleUrls: ['./basic-search-without-example.component.css']
})
export class BasicSearchWithoutExampleComponent implements OnInit {
  searchQuery: string;
  baseUrl;
  @Input()
  passedQuery: string;
  errorStr:Boolean;
  public alertIsVisible:boolean= false;
/*  @Input() public href: string | undefined;
  @HostListener('click', ['$event']) public onClick(event: Event): void{
    if (!this.href || this.href === '#' || (this.href && this.href.length ===0)){
      event.preventDefault();
    }
  }*/

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
      this.router.navigate(['/results'],{queryParams:{searchterm:searchedQuery}});

    }

  }
  moveAdv(){
    location.assign('/');
  }

}
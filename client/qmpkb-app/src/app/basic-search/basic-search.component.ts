import { Component, OnInit, Input, Renderer } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, FormControl, Validators, FormArray } from '@angular/forms';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import { NgxSpinnerService } from 'ngx-spinner';
import * as $ from "jquery";

declare var jquery: any;

@Component({
  selector: 'app-basic-search',
  templateUrl: './basic-search.component.html',
  styleUrls: ['./basic-search.component.css']
})
export class BasicSearchComponent implements OnInit {
	searchQuery: string;
  baseUrl;
  @Input()
  passedQuery: string;
  selectedExampleValue: string;
  selectedExampleName: string;
  errorStr:Boolean;
  public alertIsVisible:boolean= false;
  submitButtonClickStatus:boolean = false;

  public fields: any[] = [
      [
        {
          name:'Protein name',
          value:'Vinculin'
        },
        {
          name:'Gene',
          value:'Vcl'
        },
        {
          name:'UniProtKB accession',
          value:'Q64727'
        }
      ],[
        {
          name:'Peptide sequence',
          value:'ALASQLQDSLK'
        },
        {
          name:'Strain',
          value:'NODSCID'
        },
        {
          name:'Mutant',
          value:'Wild'
        }
      ],[
        {
          name:'Sex',
          value:'Male'
        },
        {
          name:'Biological matrix',
          value:'Plasma'
        },
        {
          name:'Subcellular localization',
          value:'Secreted'
        }
      ],[
        {
          name:'Molecular pathway(s)',
          value:'Complement and coagulation cascades'
        },
        {
          name:'Involvement in disease',
          value:'Adiponectin deficiency(ADPND)'
        },
        {
          name:'GO ID',
          value:'GO:0008015'
        }
      ],[
        {
          name:'GO Term',
          value:'blood circulation'
        },
        {
          name:'GO Aspects',
          value:'Biological Process'
        },
        {
          name:'Drug associations ID',
          value:'DB05202'
        }
      ]
    ];

  constructor(
    private router: Router,
    private http: HttpClient,
    private renderer: Renderer,
    private _qmpkb:QmpkbService,
    private spinner: NgxSpinnerService
  ) { }


  ngOnInit() {
    this.spinner.show();
    this.fields;
    this.selectedExampleName='';
    this.selectedExampleValue='';
    this.spinner.hide();
  }

  ngAfterViewInit(): void {


/*    window.onclick = function(event) {
      if (!event.target.matches('#bt')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
          var openDropdown = dropdowns[i];
          if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show');
          }
        }
      }
    }*/
  }
  getValue(item : any) {
    this.selectedExampleName=item.name;
    this.selectedExampleValue=item.value;
  }

   exampleFunction() {
      document.getElementById("myDropdown").classList.toggle("show");
  }
  exampleDisplay(){
    document.getElementById("myDropdown").classList.toggle("show");
  }
  submitFunction(){
    this.submitButtonClickStatus=true;
  }
  submitSearch(event,formData){

  	let searchedQuery = formData.value['searchterm']
    if (searchedQuery){
      if (this.submitButtonClickStatus){
        this.spinner.show();
        this.router.navigate(['/results'],{queryParams:{searchterm:searchedQuery}});
      }
    }

  }

}
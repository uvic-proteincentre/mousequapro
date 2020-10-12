import { Component, OnInit, Input, ElementRef, ViewChild, NgModule, Renderer, HostListener } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { FormGroup, FormBuilder, FormControl, Validators, FormArray } from '@angular/forms';
import {DropdownService} from '../dropdown-service/dropdown.service';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import {saveAs} from 'file-saver';


@Component({
  selector: 'app-advance-search',
  templateUrl: './advance-search.component.html',
  styleUrls: ['./advance-search.component.css']
})
export class AdvanceSearchComponent implements OnInit {
	selects: any[];
	@Input()
	wheres;
	formIndex:number = 1;
	fastaFileContext:any;
	fastaFileName:any;
	savedfastaFileName:any;
	parts = {};
	errorStr:Boolean;
	dropdownSettings = {};
	dropdownList = [];
	selectedItems = [];
	public alertIsVisible:boolean= false;
	

  fields ={
	protein: 'Protein',
	gene: 'Gene',
	uniProtKBAccession:'UniProtKB accession',
	pepSeq:'Peptide sequence',
	panel:'Panel',
	strain:'Strain',
	mutant : 'Mutant',
	sex:'Sex',
	biologicalMatrix : 'Biological matrix',
	subCellLoc:'Subcellular localization',
	keggPathway:'Molecular pathway(s)',
	disCausMut:'Involvement in disease',
	goId:'GO ID',
	goTerm:'GO term',
	goAspects:'GO aspects',
	drugId:'Drug associations ID',
	fastaFile: 'Own protein sequences in FASTA format'

  };

	public queryForm: FormGroup;
	@ViewChild('fileInput') fileInput: ElementRef;
	

	ngOnInit(){}

	public addOptionGroup(){
		const fa = this.queryForm.controls["optionGroups"] as FormArray;
		fa.push(this.newOptionGroup());
		this.formIndex ++;
	}

	public removeOptionGroup(index: number){
		const fa = this.queryForm.controls["optionGroups"] as FormArray;
		fa.removeAt(index);
		this.formIndex --;
	}


	public savequeryForm() {
		this.spinner.show();
		let advancedFormData={};
		for(let i=0; i<Object.keys(this.queryForm.value.optionGroups).length;i++){
			const temQParm=this.queryForm.value.optionGroups[i].selectInput;
			const temQVal=this.queryForm.value.optionGroups[i].whereInput;
			if (temQParm=='panel' || temQParm=='strain' ||temQParm=='mutant' || temQParm=='sex' || temQParm=='biologicalMatrix'){
				advancedFormData[temQParm]=temQVal.join('|');
			} else{
				if (temQParm !=='fastaFile'){
					advancedFormData[temQParm]=temQVal;
				}
			}
		}
		advancedFormData['fastaFileName']=this.savedfastaFileName;
	    this.router.navigate(['/results'],{queryParams:advancedFormData});
	  	this.queryForm.reset();


	}

	openFile(event:any, selectInput: string , formIndex : number) {
		if (event.target.files && event.target.files[0]) {
			let fileReader = new FileReader();
			fileReader.onload = (e) => {
				// this 'text' is the content of the file
				this.fastaFileContext = fileReader.result;
				this.fastaFileName = event.target.files[0].name;
				if (this.fastaFileName.length >0){
					this._qmpkb.receiveDataFromBackendSearch('/fastafileapi/?fastaFileContext=' + JSON.stringify(this.fastaFileContext)).subscribe((response: any)=>{
						this.savedfastaFileName=response.nameFile;
					}, error=>{
					this.errorStr = error;
					})					
				}

			}
			fileReader.readAsText(event.target.files[0]);
		};
	}

	constructor(
		private router: Router, 
		public dropdownservice: DropdownService , 
		private fb : FormBuilder,
		private _qmpkb:QmpkbService,
		private spinner: NgxSpinnerService,
		private http: HttpClient
		) {
		this.queryForm = this.fb.group({
				optionGroups : this.fb.array([
					this.fb.group({
						selectInput : ['', Validators.required],
						whereInput : ['', Validators.required],
						}),
				]),
		});
		this.selects = this.dropdownservice.getSelect();
		this.wheres=[];
	}



	private newOptionGroup() {
		return new FormGroup({
				selectInput: new FormControl(""),
				whereInput: new FormControl(""),
		});
	}

	onSelectSelect(selectInput: string , formIndex : number) : void{

		this.dropdownSettings = {
		  singleSelection: false,
		  idField: 'id',
		  textField: 'name',
		  enableCheckAll:false,
		  allowSearchFilter: true
		};
		this.wheres[selectInput] = this.dropdownservice.getWhere().filter((item)=> item.selectid == selectInput);
		this.parts[formIndex]=selectInput;
		let keys = Object.keys(this.parts);
		let values = keys.map(k => this.parts[k]);
		this.dropdownList =	this.wheres[selectInput];
		if (values.length > 1){
			let countDuplicate=0;
			for(let v of values){
				if (selectInput == v){
					countDuplicate++;
				}
				if (countDuplicate > 1){
					alert(this.fields[selectInput]+' already selected.');
					this.queryForm.get('optionGroups')['controls'][formIndex].patchValue({ selectInput: '', whereInput: ''});
					countDuplicate=0;
				} else {
					this.queryForm.get('optionGroups')['controls'][formIndex].patchValue({ selectInput: selectInput, whereInput: ''});
				}
		}
		}
		
	}
/*	log(event) {
		console.log(event);
	}
*/
}
import { Component, OnInit, HostListener } from '@angular/core';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';

@Component({
  selector: 'app-data-submission-form',
  templateUrl: './data-submission-form.component.html',
  styleUrls: ['./data-submission-form.component.css']
})
export class DataSubmissionFormComponent implements OnInit {

	submissionForm: FormGroup;
	disabledSubmitButton: boolean = true;
	optionsSelect: Array<any>;

	@HostListener('input') oninput() {
		if (this.submissionForm.valid) {
			this.disabledSubmitButton = false;
		}
	}
	constructor(
		private http: HttpClient,
		private fb: FormBuilder
		) {
		this.submissionForm = fb.group({
			'submissionFormName': ['', Validators.required],
			'submissionFormEmail': ['', Validators.compose([Validators.required, Validators.email])],
			'submissionFormLaboratory': ['', Validators.required],
			'submissionFormExperiment': ['', Validators.required],
			'submissionFormPublication': [''],
			'submissionFormDataRepository': ['', Validators.required],
			'submissionFormDataAcessionNumber': ['', Validators.required],
			'submissionFormRepositoryPassword': [''],
			'submissionFormMessage': ['', Validators.required],
			'submissionFormCopy': [''],
		});
	}



  ngOnInit() {
  }

	onSubmit() {
		if (this.submissionForm.valid) {
			alert('We have received your data.');
			this.http.get('/submissionapi/?submissiondetails=' + JSON.stringify(this.submissionForm.value)).subscribe(response => {},errors => {console.log(errors)});
			this.submissionForm.reset();
			this.disabledSubmitButton = true;
		}
	}
}

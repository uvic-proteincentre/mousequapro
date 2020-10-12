import { Component, OnInit, HostListener } from '@angular/core';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit {
	contactForm: FormGroup;
	disabledSubmitButton: boolean = true;
	optionsSelect: Array<any>;

	@HostListener('input') oninput() {
		if (this.contactForm.valid) {
			this.disabledSubmitButton = false;
		}
	}
	constructor(
		private http: HttpClient,
		private fb: FormBuilder
		) {
		this.contactForm = fb.group({
			'contactFormName': ['', Validators.required],
			'contactFormEmail': ['', Validators.compose([Validators.required, Validators.email])],
			'contactFormMessage': ['', Validators.required],
			'contactFormCopy': [''],
		});
	}

	ngOnInit() { }

	onSubmit() {
		if (this.contactForm.valid) {
			alert('Your message has been sent.');
			this.http.get('/contactapi/?contactdetails=' + JSON.stringify(this.contactForm.value)).subscribe(response => {},errors => {console.log(errors)});
			this.contactForm.reset();
			this.disabledSubmitButton = true;
		}
	}

}
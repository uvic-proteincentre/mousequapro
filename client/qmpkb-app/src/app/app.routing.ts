import {NgModule} from '@angular/core';
import { RouterModule, Routes} from '@angular/router';

import { HomeComponent } from './home/home.component';
import { ResultPageComponent } from './result-page/result-page.component';
import { ResultPageUserSeqComponent } from './result-page-user-seq/result-page-user-seq.component';
import { ResultsQueryComponent } from './results-query/results-query.component';
import { HelpComponent } from './help/help.component';
import { ContactComponent } from './contact/contact.component';
import { ConcentrationComponent } from './concentration/concentration.component';
import { PathwayviewComponent } from './pathwayview/pathwayview.component';
import { PeptideuniquenessComponent } from './peptideuniqueness/peptideuniqueness.component';
import { DataLoadPageComponent } from './data-load-page/data-load-page.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { DetailInformationComponent } from './detail-information/detail-information.component';
import { ProtocolComponent } from './protocol/protocol.component';
import { DataSubmissionFormComponent } from './data-submission-form/data-submission-form.component';



const appRoutes: Routes =[
	{
		path:"",
		component:HomeComponent,
		pathMatch:'full',
	},
	{
		path:"results",
		component:ResultsQueryComponent,
	},
	{
		path:"resultsseq",
		component:ResultPageUserSeqComponent,
	},
	{
		path:"protocol",
		component:ProtocolComponent,
	},
	{
		path:"help",
		component:HelpComponent,
	},
	{
		path:"contact",
		component:ContactComponent,
	},
	{
		path:"concentration",
		component:ConcentrationComponent,
	},
	{
		path:"peptideuniqueness",
		component:PeptideuniquenessComponent,
	},
	{
		path:"detailinformation",
		component:DetailInformationComponent,
	},
	{
		path:"viewpathway",
		component:PathwayviewComponent,
	},
	{
		path:"submission",
		component:DataSubmissionFormComponent,
	},
	{
		path:"dataload/:slug",
		component:DataLoadPageComponent,
	},
	{
		path:"**",
		component:NotFoundComponent,
	}
]



@NgModule({
	imports:[
		RouterModule.forRoot(
			appRoutes
		)
	],
	exports:[
		RouterModule
	]
})

export class AppRoutingModule{}
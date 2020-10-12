import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule }    from '@angular/common/http';
import { FormsModule,ReactiveFormsModule } from '@angular/forms';

// third party imports
import { Ng2OdometerModule } from 'ng2-odometer';
import { DataTablesModule } from 'angular-datatables';
import { NgxSpinnerModule } from 'ngx-spinner';
import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown';
import { CollapseModule } from 'ngx-bootstrap/collapse';
import * as $ from "jquery";
//service
import {DropdownService} from './dropdown-service/dropdown.service';
import {QmpkbService} from './qmpkb-service/qmpkb.service';

import { AppRoutingModule } from './app.routing';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { HelpComponent } from './help/help.component';
import { ContactComponent } from './contact/contact.component';
import { BasicSearchComponent } from './basic-search/basic-search.component';
import { BasicSearchWithoutExampleComponent } from './basic-search-without-example/basic-search-without-example.component';
import { BasicSearchWithoutExampleResultComponent } from './basic-search-without-example-result/basic-search-without-example-result.component';
import { AdvanceSearchComponent } from './advance-search/advance-search.component';
import { ProtvistaViewComponent } from './protvista-view/protvista-view.component';
import { ResultPageComponent } from './result-page/result-page.component';
import { ResultPageUserSeqComponent } from './result-page-user-seq/result-page-user-seq.component';
import { AssayComponent } from './assay/assay.component';
import { ConcentrationComponent } from './concentration/concentration.component';
import { PathwayComponent } from './pathway/pathway.component';
import { PathwayviewComponent } from './pathwayview/pathwayview.component';
import { GotermComponent } from './goterm/goterm.component';
import { PeptideuniquenessComponent } from './peptideuniqueness/peptideuniqueness.component';
import { MouseAnatomyComponent } from './mouse-anatomy/mouse-anatomy.component';
import { DataLoadPageComponent } from './data-load-page/data-load-page.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { GeneExpressionComponent } from './gene-expression/gene-expression.component';
import { FoldChangeComponent } from './fold-change/fold-change.component';
import { DetailInformationComponent } from './detail-information/detail-information.component';
import { DetailConcentrationComponent } from './detail-concentration/detail-concentration.component';
import { DiseaseInformationComponent } from './disease-information/disease-information.component';
import { DrugBankComponent } from './drug-bank/drug-bank.component';
import { SubcellLocationComponent } from './subcell-location/subcell-location.component';
import { ResultsQueryComponent } from './results-query/results-query.component';
import { ProtocolComponent } from './protocol/protocol.component';
import { HumanProttVistaViewComponent } from './human-prott-vista-view/human-prott-vista-view.component';
import { Navbar1Component } from './navbar1/navbar1.component';
import { Navbar2Component } from './navbar2/navbar2.component';
import { Navbar3Component } from './navbar3/navbar3.component';
import { DataSubmissionFormComponent } from './data-submission-form/data-submission-form.component';
import { DownloadResultComponent } from './download-result/download-result.component';



@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    HelpComponent,
    ContactComponent,
    BasicSearchComponent,
    BasicSearchWithoutExampleComponent,
    BasicSearchWithoutExampleResultComponent,
    ProtvistaViewComponent,
    ResultPageComponent,
    ResultPageUserSeqComponent,
    AdvanceSearchComponent,
    AssayComponent,
    ConcentrationComponent,
    PathwayComponent,
    PathwayviewComponent,
    GotermComponent,
    PeptideuniquenessComponent,
    MouseAnatomyComponent,
    DataLoadPageComponent,
    NotFoundComponent,
    GeneExpressionComponent,
    FoldChangeComponent,
    DetailInformationComponent,
    DetailConcentrationComponent,
    DiseaseInformationComponent,
    DrugBankComponent,
    SubcellLocationComponent,
    ResultsQueryComponent,
    ProtocolComponent,
    HumanProttVistaViewComponent,
    Navbar1Component,
    Navbar2Component,
    Navbar3Component,
    DataSubmissionFormComponent,
    DownloadResultComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    Ng2OdometerModule.forRoot(),
    NgMultiSelectDropDownModule.forRoot(),
    DataTablesModule,
    NgxSpinnerModule,
    CollapseModule.forRoot()
  ],
  providers: [
  DropdownService,
  QmpkbService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

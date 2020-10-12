import { Component, OnInit, OnDestroy, ViewChild} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { NgxSpinnerService } from 'ngx-spinner';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';
import * as $ from "jquery";

declare var require: any
declare var jquery: any;


@Component({
  selector: 'app-peptideuniqueness',
  templateUrl: './peptideuniqueness.component.html',
  styleUrls: ['./peptideuniqueness.component.css']
})
export class PeptideuniquenessComponent implements OnInit  {
  private routeSub:any;
  dtOptions: any = {};
  pepunqdata:any;
  errorStr:Boolean;
  reachable:Boolean;
  queryData:any;
  @ViewChild(DataTableDirective)
  datatableElement: DataTableDirective;
  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private _qmpkb:QmpkbService
    ) { }

  ngOnInit() {
    this.spinner.show();
    this.location.go('/peptideuniqueness/')
    this.queryData=this._qmpkb.queryStorage;
    this.pepunqdata=JSON.parse(this.queryData.pepunqdata)
    this.reachable=this.queryData.reachable
    this.dtOptions = {
      data: this.pepunqdata.data,
      columns: [
         {   title: 'Show Highlighted Peptide Sequence',
             className: 'details-control',
             orderable: false,
             data: null,
             defaultContent: '',
             render: function () {
                 return '<i class="fa fa-plus-square" aria-hidden="true"></i>';
             },
             width:"15px"
         },
         { 
           title: 'Protein ID',
           data: "proteinID" 
         },
         { 
           title: 'Peptide Sequence',
           data: "peptideSequence" 
         },
         {
           title: 'Start',
           data: "start"
         },
         {
           title: 'End',
           data: "end"
         },
         {
           title: 'Sequence Length',
           data: "seqlen"
         },
         { 
           title: 'Peptide unique in protein',
           data: "peptideuniqueinprotein"
         },
         {
           title: 'Data source',
           data: "datasource"
         }
      ],
      autoWidth:true
    };
    this.spinner.hide();
  }

  private format(d){     
   // `d` is the original data object for the row
   return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
       '<tr>' +
           '<td>Fasta:</td>' +
           '<td>' + d.highlightedpepseq + '</td>' +
       '</tr>' +
   '</table>';  
  }

  ngAfterViewInit(): void {

    const self = this;
    this.datatableElement.dtInstance.then(table => {
       // Add event listener for opening and closing details
       $('#pepUnqness tbody').on('click', 'td.details-control', function () {
           var tr = $(this).closest('tr');
           var tdi = tr.find("i.fa");
           var row = table.row(tr);

           if (row.child.isShown()) {
               // This row is already open - close it
               row.child.hide();
               tr.removeClass('shown');
               tdi.first().removeClass('fa-minus-square');
               tdi.first().addClass('fa-plus-square');
           }
           else {
               // Open this row
               row.child(self.format(row.data())).show();
               tr.addClass('shown');
               tdi.first().removeClass('fa-plus-square');
               tdi.first().addClass('fa-minus-square');
           }
       });

       table.on("user-select", function (e, dt, type, cell, originalEvent) {
           if ($(cell.node()).hasClass("details-control")) {
               e.preventDefault();
           }
       });
    }); 
   
  }


}




import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import * as $ from "jquery";
declare var jquery: any;


@Component({
  selector: 'app-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {
  baseUrl;
  constructor(
  	  private router: Router
  ) { }

  ngOnInit() {
  	this.baseUrl = window.location.origin;
    if (this.router.url.includes('#')){
      const link=this.router.url.split('#')[1];
      this.preCSS(link);
    }
  }

 preCSS(hashLink:any):void {
    var self= this;
/*    $('#'+hashLink).trigger('click');*/
    $('#'+hashLink).css({'padding-top':'51px'});

 }
  gethref(evt, linkName) {
      const hrefIDArray=['searching','update','cite','result','submission','implementation'];
      $('#'+linkName).css({'padding-top':'51px'});
      for(let i=0; i<hrefIDArray.length;i++){
        if(hrefIDArray[i] !==linkName){
          $('#'+hrefIDArray[i]).css({'padding-top':''});
        }
      }
  }
}
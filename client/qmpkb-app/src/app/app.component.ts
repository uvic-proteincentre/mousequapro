import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'MouseQuaPro';
  todayDate;
  qmpkbLogoImage ='static/ang/assets/images/logo/logo.png'
  private routeSub:any;
  isCollapsed:boolean=true;

  constructor(
    private route: ActivatedRoute,
    private router: Router
    ) { }
  
  ngOnInit() {
  	this.todayDate = new Date()
  }


}

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar2',
  templateUrl: './navbar2.component.html',
  styleUrls: ['./navbar2.component.css']
})
export class Navbar2Component implements OnInit {
  qmpkbLogoImage ='static/ang/assets/images/logo/logo.png'
  isCollapsed:boolean=true;
  constructor() { }

  ngOnInit() {
  }

}

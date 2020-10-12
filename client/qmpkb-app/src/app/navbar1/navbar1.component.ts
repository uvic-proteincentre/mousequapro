import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar1',
  templateUrl: './navbar1.component.html',
  styleUrls: ['./navbar1.component.css']
})
export class Navbar1Component implements OnInit {
  qmpkbLogoImage ='static/ang/assets/images/logo/logo.png'
  isCollapsed:boolean=true;
  constructor() { }

  ngOnInit() {
  }

}

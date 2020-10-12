import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar3',
  templateUrl: './navbar3.component.html',
  styleUrls: ['./navbar3.component.css']
})
export class Navbar3Component implements OnInit {
  qmpkbLogoImage ='static/ang/assets/images/logo/logo.png'
  isCollapsed:boolean=true;
  constructor() { }

  ngOnInit() {
  }

}

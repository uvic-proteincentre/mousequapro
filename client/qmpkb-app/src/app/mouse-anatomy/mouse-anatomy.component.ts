import { Component, OnInit, HostListener } from '@angular/core';

@Component({
  selector: 'app-mouse-anatomy',
  templateUrl: './mouse-anatomy.component.html',
  styleUrls: ['./mouse-anatomy.component.css']
})
export class MouseAnatomyComponent implements OnInit {
  
  screenWidth:any;
  screenHeight:any;
  @HostListener('window.resize', ['$event'])

  getScreenSize(event?){
    this.screenWidth=Math.round(window.innerWidth/4)+"px";
    this.screenHeight=Math.round(window.innerWidth/2)+"px";
  }
  constructor() {
    this.getScreenSize();
  }

  ngOnInit() {
  }

}

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-reports-page',
  //templateUrl: '../../../../res/report.html',
  templateUrl: './reports-page.component.html',
  //styleUrls: ['./reports-page.component.css']
})


export class ReportsPageComponent implements OnInit {

async delay(ms: number) {
    await new Promise(resolve => setTimeout(()=>resolve(), ms)).then(()=>console.log("fired"));
}

  constructor() { }

  ngOnInit() {this.delay(3000);}




}
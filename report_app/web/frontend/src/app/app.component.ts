import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { FormControl, FormGroup, FormBuilder } from '@angular/forms';
import { ReportData, FormWrapper } from './models/contact-request';
import {Router,RouterModule} from "@angular/router";
import 'rxjs/add/operator/toPromise';
import 'rxjs/add/operator/map';
import {API_URL, GET_REPORT_URL} from './env';
import {MyTestApiService} from './mytest/mytest.service';
import { Observable } from 'rxjs/Observable';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [MyTestApiService]
})

export class AppComponent implements OnInit {
  contactForm: FormGroup;
  result:string;

  title = 'app';
  results = '';
  api = API_URL;
  finalres = '';

  // Step 1
  createFormGroup() {
    
    return new FormGroup({
      ReportData: new FormGroup({
        ReportStartDate: new FormControl(),
        ReportFinishDate: new FormControl(),
        ReportName: new FormControl()
      
      }),
      requestType: new FormControl(),
      text: new FormControl()
    });
  }
  
  constructor
  (public http: HttpClient, private router: Router , private formBuilder: FormBuilder, private apiService: MyTestApiService)
  {
   this.contactForm = this.createFormGroup();
  console.log(this.contactForm);
  }



revert() {
    // Resets to blank object
    this.contactForm.reset();

    // Resets to provided model
    this.contactForm.reset({ personalData: new ReportData(), requestType: '', text: '' });
  }

refresh_int(res) {
  console.log(res);
  console.log(this.api);
  this.http.get((this.api + '/refresh_json'),{params:res}).subscribe(data => { console.log(data) });    
  }

async getReportAsync(params) {
    
    this.finalres = await this.apiService.getReportPromise(params);

    //console.log("LOGGED IN STATUS: " + this.loginStatus);

    // if (this.loginStatus == true){
     //   return true;
    // }
    //setTimeout(() => 
    //{
    //this.router.navigate(['/']);
    //},
    //5000);
    // not logged in so redirect to login page with the return url

    this.router.navigate(['get_report_ang']);    
}

onSubmit() {
    
    // Make sure to create a deep copy of the form-model

    const result: FormWrapper = Object.assign({}, this.contactForm.value);
    result.ReportData = Object.assign({}, result.ReportData);

    result.ReportData['Fname'] = 'Okta';
    result.ReportData['Debug'] = 'False'
    result.ReportData['LastDayToday'] = 'False'
    result.ReportData['EnableDisplay'] = 'False'

    console.log(result.ReportData)

    this.getReportAsync(result.ReportData)
  
  }


   ngOnInit(): void {
    
   }

}
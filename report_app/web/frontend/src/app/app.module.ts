import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { RouterModule, Routes,ActivatedRouteSnapshot,RouterStateSnapshot} from '@angular/router';
import {API_URL, GET_REPORT_URL} from './env';
import { ReportsPageComponent } from './reports-page/reports-page.component';

const appRoutes: Routes = [
{path: 'get_report_ang', component: ReportsPageComponent},


{ path: '', 
component: AppComponent, 
pathMatch: 'full',
},

{
path: 'get_report_ang', 
component: ReportsPageComponent
},

{ 
path: 'get_report', 
component: AppComponent, 
resolve: {
         url: 'externalUrlRedirectResolver'
         },
      
data: 
{
externalUrl: GET_REPORT_URL + '/get_report'
}
}

];



@NgModule({
  declarations: [
    AppComponent,
    ReportsPageComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule,
    RouterModule.forRoot(
    appRoutes,
    {enableTracing: true}
    )
  ],
     providers: [
        {
            provide: 'externalUrlRedirectResolver',
            useValue: (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) =>
            {
                window.location.href = (route.data as any).externalUrl;
            }
        }
    ],
  bootstrap: [AppComponent],
   exports: [RouterModule]
})

export class AppModule { }
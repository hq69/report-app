import {Injectable, EventEmitter} from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import {Observable} from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import {API_URL} from '../env';
import {MyTest} from './mytest.model';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/toPromise';

@Injectable()

export class MyTestApiService {
  constructor(private http: HttpClient) { }

  configUrl = 'assets/config.json';

  public getReport(params): Observable<any> {

        return this.http.get((API_URL + '/refresh_json'),{params:params}).map((res: Response) => res.json())

    }
  public async getReportPromise(params): Promise<any>{
     
     const response = await this.http.get((API_URL + '/refresh_json'),{params:params}).toPromise();
     return response;
  }
}


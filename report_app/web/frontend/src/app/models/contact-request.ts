import { Moment } from 'moment';


export class FormWrapper {
  ReportData: ReportData;
  requestType: any = '';
  text: string = '';
}

export class ReportData {

  ReportStartDate: Moment;
  ReportFinishDate: Moment;
  ReportName: string;
  LastDayToday:string;

}
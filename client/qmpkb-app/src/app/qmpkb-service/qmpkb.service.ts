import { Injectable, OnDestroy } from '@angular/core';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { map, catchError,takeUntil } from 'rxjs/operators';
import { BehaviorSubject,Subject,Observable, throwError } from 'rxjs';

const endpoint = 'http://127.0.0.1:8000'

@Injectable({
  providedIn: 'root'
})
export class QmpkbService implements OnDestroy {
  public queryStorage:any;
  public dropDownStorage:any;
  private destroy$ = new Subject();
  constructor(
  	private http: HttpClient
  ) { }

  receiveDataFromBackendSearch(url){
    return this.http.get(url)
        .pipe(
            takeUntil(this.destroy$),
            map(responce=>responce),
            catchError(this.handleError)
        )

  }

  private handleError(error:any, caught:any): any{
      //console.log(error, caught)
      if(error.status == 404){
        alert("Oopps. Not found!");
      } else {
        alert("Something went wrong. Please try again.");
      }
  }

  ngOnDestroy(): void{
    this.destroy$.next(); // trigger the unsubscribe
    this.destroy$.complete(); // finalize and clean up the subject stream
  }
}
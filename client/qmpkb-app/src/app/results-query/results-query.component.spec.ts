import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultsQueryComponent } from './results-query.component';

describe('ResultsQueryComponent', () => {
  let component: ResultsQueryComponent;
  let fixture: ComponentFixture<ResultsQueryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ResultsQueryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ResultsQueryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DataSubmissionFormComponent } from './data-submission-form.component';

describe('DataSubmissionFormComponent', () => {
  let component: DataSubmissionFormComponent;
  let fixture: ComponentFixture<DataSubmissionFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DataSubmissionFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DataSubmissionFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

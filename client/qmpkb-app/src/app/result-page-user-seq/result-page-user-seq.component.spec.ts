import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultPageUserSeqComponent } from './result-page-user-seq.component';

describe('ResultPageUserSeqComponent', () => {
  let component: ResultPageUserSeqComponent;
  let fixture: ComponentFixture<ResultPageUserSeqComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ResultPageUserSeqComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ResultPageUserSeqComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

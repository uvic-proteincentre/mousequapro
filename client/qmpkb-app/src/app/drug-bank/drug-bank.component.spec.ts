import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DrugBankComponent } from './drug-bank.component';

describe('DrugBankComponent', () => {
  let component: DrugBankComponent;
  let fixture: ComponentFixture<DrugBankComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DrugBankComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DrugBankComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

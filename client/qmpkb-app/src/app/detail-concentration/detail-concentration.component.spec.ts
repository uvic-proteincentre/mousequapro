import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailConcentrationComponent } from './detail-concentration.component';

describe('DetailConcentrationComponent', () => {
  let component: DetailConcentrationComponent;
  let fixture: ComponentFixture<DetailConcentrationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DetailConcentrationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DetailConcentrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

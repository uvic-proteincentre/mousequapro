import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DiseaseInformationComponent } from './disease-information.component';

describe('DiseaseInformationComponent', () => {
  let component: DiseaseInformationComponent;
  let fixture: ComponentFixture<DiseaseInformationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DiseaseInformationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DiseaseInformationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

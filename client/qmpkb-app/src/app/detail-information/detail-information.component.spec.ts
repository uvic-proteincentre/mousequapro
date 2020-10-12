import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailInformationComponent } from './detail-information.component';

describe('DetailInformationComponent', () => {
  let component: DetailInformationComponent;
  let fixture: ComponentFixture<DetailInformationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DetailInformationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DetailInformationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

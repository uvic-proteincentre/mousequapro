import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HumanProttVistaViewComponent } from './human-prott-vista-view.component';

describe('HumanProttVistaViewComponent', () => {
  let component: HumanProttVistaViewComponent;
  let fixture: ComponentFixture<HumanProttVistaViewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HumanProttVistaViewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HumanProttVistaViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

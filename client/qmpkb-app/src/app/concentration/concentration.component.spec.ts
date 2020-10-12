import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConcentrationComponent } from './concentration.component';

describe('ConcentrationComponent', () => {
  let component: ConcentrationComponent;
  let fixture: ComponentFixture<ConcentrationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConcentrationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConcentrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

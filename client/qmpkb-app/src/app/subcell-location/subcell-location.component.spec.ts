import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SubcellLocationComponent } from './subcell-location.component';

describe('SubcellLocationComponent', () => {
  let component: SubcellLocationComponent;
  let fixture: ComponentFixture<SubcellLocationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SubcellLocationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SubcellLocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

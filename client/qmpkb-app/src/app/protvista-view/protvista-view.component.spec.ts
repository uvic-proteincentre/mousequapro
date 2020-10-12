import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtvistaViewComponent } from './protvista-view.component';

describe('ProtvistaViewComponent', () => {
  let component: ProtvistaViewComponent;
  let fixture: ComponentFixture<ProtvistaViewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtvistaViewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtvistaViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

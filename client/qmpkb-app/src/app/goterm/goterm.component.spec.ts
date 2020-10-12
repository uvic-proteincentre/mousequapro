import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GotermComponent } from './goterm.component';

describe('GotermComponent', () => {
  let component: GotermComponent;
  let fixture: ComponentFixture<GotermComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GotermComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GotermComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

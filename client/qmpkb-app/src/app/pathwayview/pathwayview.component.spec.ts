import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PathwayviewComponent } from './pathwayview.component';

describe('PathwayviewComponent', () => {
  let component: PathwayviewComponent;
  let fixture: ComponentFixture<PathwayviewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PathwayviewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PathwayviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

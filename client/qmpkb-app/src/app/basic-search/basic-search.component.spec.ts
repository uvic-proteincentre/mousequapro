import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BasicSearchComponent } from './basic-search.component';

describe('BasicSearchComponent', () => {
  let component: BasicSearchComponent;
  let fixture: ComponentFixture<BasicSearchComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BasicSearchComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

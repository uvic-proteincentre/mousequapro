import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DataLoadPageComponent } from './data-load-page.component';

describe('DataLoadPageComponent', () => {
  let component: DataLoadPageComponent;
  let fixture: ComponentFixture<DataLoadPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DataLoadPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DataLoadPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

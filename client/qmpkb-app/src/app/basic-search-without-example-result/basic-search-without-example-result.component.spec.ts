import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BasicSearchWithoutExampleResultComponent } from './basic-search-without-example-result.component';

describe('BasicSearchWithoutExampleResultComponent', () => {
  let component: BasicSearchWithoutExampleResultComponent;
  let fixture: ComponentFixture<BasicSearchWithoutExampleResultComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BasicSearchWithoutExampleResultComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicSearchWithoutExampleResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BasicSearchWithoutExampleComponent } from './basic-search-without-example.component';

describe('BasicSearchWithoutExampleComponent', () => {
  let component: BasicSearchWithoutExampleComponent;
  let fixture: ComponentFixture<BasicSearchWithoutExampleComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BasicSearchWithoutExampleComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicSearchWithoutExampleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

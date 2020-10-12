import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MouseAnatomyComponent } from './mouse-anatomy.component';

describe('MouseAnatomyComponent', () => {
  let component: MouseAnatomyComponent;
  let fixture: ComponentFixture<MouseAnatomyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MouseAnatomyComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MouseAnatomyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

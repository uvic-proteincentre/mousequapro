import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FoldChangeComponent } from './fold-change.component';

describe('FoldChangeComponent', () => {
  let component: FoldChangeComponent;
  let fixture: ComponentFixture<FoldChangeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FoldChangeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FoldChangeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

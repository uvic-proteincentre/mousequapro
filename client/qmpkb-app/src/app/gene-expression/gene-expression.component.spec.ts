import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneExpressionComponent } from './gene-expression.component';

describe('GeneExpressionComponent', () => {
  let component: GeneExpressionComponent;
  let fixture: ComponentFixture<GeneExpressionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GeneExpressionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GeneExpressionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

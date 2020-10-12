import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PeptideuniquenessComponent } from './peptideuniqueness.component';

describe('PeptideuniquenessComponent', () => {
  let component: PeptideuniquenessComponent;
  let fixture: ComponentFixture<PeptideuniquenessComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PeptideuniquenessComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PeptideuniquenessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

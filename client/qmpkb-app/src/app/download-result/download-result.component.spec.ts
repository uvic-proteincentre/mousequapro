import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DownloadResultComponent } from './download-result.component';

describe('DownloadResultComponent', () => {
  let component: DownloadResultComponent;
  let fixture: ComponentFixture<DownloadResultComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DownloadResultComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DownloadResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

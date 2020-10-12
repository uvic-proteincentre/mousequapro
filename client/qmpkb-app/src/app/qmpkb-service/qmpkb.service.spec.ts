import { TestBed } from '@angular/core/testing';

import { QmpkbService } from './qmpkb.service';

describe('QmpkbService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: QmpkbService = TestBed.get(QmpkbService);
    expect(service).toBeTruthy();
  });
});

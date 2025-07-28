import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StockData } from './stock-data';

describe('StockData', () => {
  let component: StockData;
  let fixture: ComponentFixture<StockData>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [StockData]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StockData);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

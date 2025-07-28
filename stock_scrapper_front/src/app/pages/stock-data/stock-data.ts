import { Component } from '@angular/core';
import { StockDataService } from '../../services/stock-data.service';

@Component({
  selector: 'app-stock-data',
  standalone: false,
  templateUrl: './stock-data.html',
  styleUrl: './stock-data.scss'
})
export class StockData {
  ticker: string = 'PETR4';
  years: number = 5;
  months: number = 60;

  companyDetails: any = null;
  yearlyDividends: any[] = [];
  monthlyDividends: any[] = [];
  accumulatedYearly: number | null = null;
  accumulatedMonthly: number | null = null;

  loading: boolean = false;
  error: string | null = null;

  constructor(private stockDataService: StockDataService) { }

  fetchDetails(): void {
    this.loading = true;
    this.error = null;
    this.stockDataService.getCompanyDetails(this.ticker).subscribe({
      next: (data) => {
        this.companyDetails = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }

  fetchYearlyDividends(): void {
    this.loading = true;
    this.error = null;
    this.stockDataService.getYearlyDividends(this.ticker).subscribe({
      next: (data) => {
        this.yearlyDividends = data.data; // A API retorna { "ticker": "...", "data": [...] }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }

  fetchMonthlyDividends(): void {
    this.loading = true;
    this.error = null;
    this.stockDataService.getMonthlyDividends(this.ticker).subscribe({
      next: (data) => {
        this.monthlyDividends = data.data; // A API retorna { "ticker": "...", "data": [...] }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }

  fetchAccumulatedYearly(): void {
    this.loading = true;
    this.error = null;
    this.accumulatedYearly = null;
    this.stockDataService.getAccumulatedYearlyDividends(this.ticker, this.years).subscribe({
      next: (data) => {
        this.accumulatedYearly = data.accumulated_dividends;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }

  fetchAccumulatedMonthly(): void {
    this.loading = true;
    this.error = null;
    this.accumulatedMonthly = null;
    this.stockDataService.getAccumulatedMonthlyDividends(this.ticker, this.months).subscribe({
      next: (data) => {
        this.accumulatedMonthly = data.accumulated_dividends;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }
}

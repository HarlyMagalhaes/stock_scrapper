import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StockDataService {
  private apiUrl = 'http://localhost:8000/api'; // URL base da sua API Django

  constructor(private http: HttpClient) { }

  getCompanyDetails(ticker: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/details/${ticker}/`).pipe(
      catchError(this.handleError)
    );
  }

  getYearlyDividends(ticker: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/yearly_dividends/${ticker}/`).pipe(
      catchError(this.handleError)
    );
  }

  getMonthlyDividends(ticker: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/monthly_dividends/${ticker}/`).pipe(
      catchError(this.handleError)
    );
  }

  getAccumulatedYearlyDividends(ticker: string, years: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/accumulated_yearly_dividends/${ticker}/${years}/`).pipe(
      catchError(this.handleError)
    );
  }

  getAccumulatedMonthlyDividends(ticker: string, months: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/accumulated_monthly_dividends/${ticker}/${months}/`).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any): Observable<never> {
    let errorMessage = 'Ocorreu um erro desconhecido!';
    if (error.error instanceof ErrorEvent) {
      // Erro no lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else {
      // Erro no lado do servidor
      errorMessage = `Código do Erro: ${error.status}\nMensagem: ${error.message}`;
      if (error.error && error.error.error) {
        errorMessage = `Código do Erro: ${error.status}\nMensagem da API: ${error.error.error}`;
      }
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}

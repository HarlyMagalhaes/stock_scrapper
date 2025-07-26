from .errors import DataParsingError
from datetime import datetime
import calendar

# --- Novo Serviço de Cálculos de Dividendos ---
class DividendCalculator:
    """
    Classe responsável por calcular somas de dividendos a partir de dados brutos.
    """
    def calculate_accumulated_yearly(self, yearly_data: list[dict], num_years: int) -> float:
        """
        Calcula a soma dos dividendos anuais de uma lista de dados brutos.
        """
        if not isinstance(yearly_data, list):
            raise TypeError("yearly_data deve ser uma lista de dicionários.")
        
        total_accumulated_dividends = 0.0
        current_year = datetime.now().year
        cut_off_year = current_year - num_years

        for entry in yearly_data:
            try:
                year = entry['Ano']
                value = entry['Valor']
                if year >= cut_off_year and year <= current_year:
                    total_accumulated_dividends += value
            except KeyError as e:
                raise DataParsingError(f"Formato de dados anual inválido: chave ausente {e}")
            except (TypeError, ValueError) as e:
                raise DataParsingError(f"Erro de tipo/valor ao processar dados anuais: {e}")
        return total_accumulated_dividends

    def calculate_accumulated_monthly(self, monthly_data: list[dict], num_months: int) -> float:
        """
        Calcula a soma dos dividendos mensais de uma lista de dados brutos para um período de meses.
        """
        if not isinstance(monthly_data, list):
            raise TypeError("monthly_data deve ser uma lista de dicionários.")
        
        total_accumulated_dividends = 0.0
        today = datetime.now()
        
        # Calculate the cut-off date: today's day, N months ago.
        year_n_months_ago = today.year - (num_months // 12)
        month_n_months_ago = today.month - (num_months % 12)
        if month_n_months_ago <= 0:
            year_n_months_ago -= 1
            month_n_months_ago += 12
        
        try:
            # Try to create the date with the current day.
            # If the day doesn't exist in the month (e.g., 31st of Feb), get the last day of the month.
            cut_off_date = datetime(year_n_months_ago, month_n_months_ago, today.day)
        except ValueError:
            last_day_of_month = calendar.monthrange(year_n_months_ago, month_n_months_ago)[1]
            cut_off_date = datetime(year_n_months_ago, month_n_months_ago, last_day_of_month)

        for entry in monthly_data:
            try:
                # Ensure 'Data' is in 'YYYY-MM-DD' format if it came from the scraper already processed,
                # or handle 'DD/MM/YYYY' if you decide to keep it raw from the scraper.
                # Here, we assume the scraper returns 'YYYY-MM-DD' for 'Data'.
                ex_date = datetime.strptime(entry['Data'], '%Y-%m-%d')
                value = entry['Valor']
                
                if ex_date >= cut_off_date and ex_date <= today:
                    total_accumulated_dividends += value
            except KeyError as e:
                raise DataParsingError(f"Formato de dados mensal inválido: chave ausente {e}")
            except (TypeError, ValueError) as e:
                raise DataParsingError(f"Erro de tipo/valor ao processar dados mensais: {e}")
        return total_accumulated_dividends
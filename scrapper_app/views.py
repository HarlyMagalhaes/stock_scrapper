from django.shortcuts import render

from django.http import JsonResponse
from .scrapper import FundamentusScraper
from .calculator import DividendCalculator
from .errors import ScrapingError, TickerNotFoundError, TableNotFoundError, ColumnNotFoundError, DataParsingError

# Instancie suas classes de serviço
scraper = FundamentusScraper()
calculator = DividendCalculator()

def get_details_view(request, ticker):
    """
    View para obter os detalhes de uma empresa do Fundamentus.
    Exemplo: /details/PETR4
    """
    try:
        details = scraper.get_company_details(ticker)
        return JsonResponse(details, status=200)
    except TickerNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except TableNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except ScrapingError as e:
        return JsonResponse({"error": f"Erro inesperado no scraping: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ocorreu um erro interno: {e}"}, status=500)

def get_yearly_dividends_view(request, ticker):
    """
    View para obter os dados brutos de dividendos anuais de uma empresa do Fundamentus.
    Exemplo: /yearly_dividends/PETR4
    """
    try:
        yearly_data = scraper.get_yearly_dividends(ticker)
        return JsonResponse({"ticker": ticker, "data": yearly_data}, status=200)
    except TickerNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except TableNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except ColumnNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except ScrapingError as e:
        return JsonResponse({"error": f"Erro inesperado no scraping: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ocorreu um erro interno: {e}"}, status=500)

def get_monthly_dividends_view(request, ticker):
    """
    View para obter os dados brutos de dividendos mensais de uma empresa do Fundamentus.
    Exemplo: /monthly_dividends/PETR4
    """
    try:
        monthly_data = scraper.get_monthly_dividends(ticker)
        return JsonResponse({"ticker": ticker, "data": monthly_data}, status=200)
    except TickerNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except TableNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
    except ColumnNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except ScrapingError as e:
        return JsonResponse({"error": f"Erro inesperado no scraping: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ocorreu um erro interno: {e}"}, status=500)

def get_accumulated_yearly_dividends_view(request, ticker, years):
    """
    View para obter o dividendo anual acumulado de uma empresa do Fundamentus.
    Primeiro busca os dados brutos, depois calcula a soma.
    Exemplo: /accumulated_yearly_dividends/PETR4/5
    """
    try:
        yearly_data = scraper.get_yearly_dividends(ticker)
        accumulated_dividends = calculator.calculate_accumulated_yearly(yearly_data, years)
        return JsonResponse({"ticker": ticker, "years": years, "accumulated_dividends": round(accumulated_dividends, 2)}, status=200)
    except ScrapingError as e:
        status_code = 404 if isinstance(e, (TickerNotFoundError, TableNotFoundError)) else 500
        return JsonResponse({"error": str(e)}, status=status_code)
    except DataParsingError as e:
        return JsonResponse({"error": f"Erro ao calcular proventos anuais: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ocorreu um erro interno: {e}"}, status=500)

def get_accumulated_monthly_dividends_view(request, ticker, months):
    """
    View para obter o dividendo mensal acumulado de uma empresa do Fundamentus.
    Primeiro busca os dados brutos, depois calcula a soma.
    Exemplo: /accumulated_monthly_dividends/ITUB4/60
    """
    try:
        monthly_data = scraper.get_monthly_dividends(ticker)
        accumulated_dividends = calculator.calculate_accumulated_monthly(monthly_data, months)
        return JsonResponse({"ticker": ticker, "months": months, "accumulated_dividends": round(accumulated_dividends, 2)}, status=200)
    except ScrapingError as e:
        status_code = 404 if isinstance(e, (TickerNotFoundError, TableNotFoundError)) else 500
        return JsonResponse({"error": str(e)}, status=status_code)
    except DataParsingError as e:
        return JsonResponse({"error": f"Erro ao calcular proventos mensais: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ocorreu um erro interno: {e}"}, status=500)
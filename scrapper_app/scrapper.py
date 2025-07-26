import requests
from .errors import ScrapingError, TickerNotFoundError, TableNotFoundError, ColumnNotFoundError, DataParsingError
from bs4 import BeautifulSoup
from datetime import datetime
from abc import ABC, abstractmethod
import re # Para expressões regulares, útil para limpar strings

# --- Interface Genérica para Web Scrapers ---
class GenericWebScraper(ABC):
    """
    Interface (Classe Abstrata) para web scrapers genéricos.
    Define os métodos que qualquer scraper específico de site deve implementar.
    """
    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers if headers is not None else {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/555.36'
        }

    def _fetch_html(self, path: str) -> BeautifulSoup:
        """
        Método auxiliar para fazer a requisição HTTP e parsear o HTML.
        Levanta requests.exceptions.RequestException em caso de erro na requisição.
        """
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise ScrapingError(f"Erro ao acessar a URL {url}: {e}") from e

    @abstractmethod
    def get_company_details(self, ticker: str) -> dict:
        """
        Método abstrato para extrair detalhes de uma empresa.
        Deve ser implementado por classes concretas.
        """
        pass

    @abstractmethod
    def get_yearly_dividends(self, ticker: str) -> list[dict]:
        """
        Método abstrato para extrair dados de dividendos anuais.
        Deve ser implementado por classes concretas.
        """
        pass

    @abstractmethod
    def get_monthly_dividends(self, ticker: str) -> list[dict]:
        """
        Método abstrato para extrair dados de dividendos mensais (detalhados).
        Deve ser implementado por classes concretas.
        """
        pass

# --- Implementação do FundamentusScraper (Herda da Interface Genérica) ---
class FundamentusScraper(GenericWebScraper):
    """
    Classe para realizar o scraping de dados do site Fundamentus.
    Encapsula a lógica para extrair detalhes de empresas e proventos anuais/mensais.
    """
    def __init__(self, ignorable_classes: list = None):
        self.ignorable_classes = ignorable_classes if ignorable_classes is not None else ['nivel1', 'nivel2', 'oscil']
        super().__init__(base_url="http://fundamentus.com.br/")

    def get_company_details(self, ticker: str) -> dict:
        """
        Extrai todos os dados de "label" e "data" da página de detalhes de uma empresa
        no Fundamentus e os retorna como um dicionário.
        Lida com múltiplas colunas label-data por linha e ignora linhas com classe 'nivel'.
        """
        path = f"detalhes.php?papel={ticker.upper()}"
        try:
            soup = self._fetch_html(path)
        except ScrapingError as e:
            raise TickerNotFoundError(f"Não foi possível acessar a página para o ticker '{ticker}'.") from e

        company_details = {}
        all_tables = soup.find_all('table')
        if not all_tables:
            raise TableNotFoundError(f"Nenhuma tabela encontrada na página de detalhes para '{ticker}'.")

        for table in all_tables:
            for row in table.find_all('tr'):
                if 'class' in row.attrs and 'nivel' in row['class']:
                    continue

                cols = row.find_all('td')
                for i in range(0, len(cols), 2):
                    if i + 1 < len(cols):
                        first_col = cols[i]
                        second_col = cols[i + 1]

                        if self._has_ignorable_class(first_col) or self._has_ignorable_class(second_col):
                            continue
                        
                        label_raw = first_col.get_text(strip=True)
                        data_raw = second_col.get_text(strip=True)

                        label = re.sub(r'[^\w\sÀ-ÿ]', '', label_raw).strip()
                        label = re.sub(r'\s+', '_', label).upper() 

                        if label:
                            company_details[label] = data_raw
        
        if not company_details:
            raise TableNotFoundError(f"Nenhum dado no padrão 'label' e 'data' encontrado para '{ticker}'.")

        return company_details

    # Check if first_col or second_col or any of their children have ignorable classes
    def _has_ignorable_class(self, tag):
        if not tag:
            return False
        # Check the tag itself
        if 'class' in tag.attrs and any(cls in self.ignorable_classes for cls in tag['class']):
            return True
        # Check all descendants
        for descendant in tag.descendants:
            if hasattr(descendant, 'attrs') and 'class' in descendant.attrs:
                if any(cls in self.ignorable_classes for cls in descendant['class']):
                    return True
        return False

    def get_yearly_dividends(self, ticker: str) -> list[dict]:
        """
        Busca os dados de proventos anuais de uma empresa no Fundamentus.
        Retorna uma lista de dicionários com 'Ano' e 'Valor'.
        """
        path = f"proventos.php?papel={ticker.upper()}"
        try:
            soup = self._fetch_html(path)
        except ScrapingError as e:
            raise TickerNotFoundError(f"Não foi possível acessar a página de proventos para o ticker '{ticker}'.") from e

        dividends_table = soup.find('table', id='resultado-anual')
        if not dividends_table:
            raise TableNotFoundError(f"Não foi possível encontrar a tabela de proventos anual (id='resultado-anual') para '{ticker}'.")

        header_row = dividends_table.find('thead')
        if not header_row:
            raise ColumnNotFoundError(f"Não foi possível encontrar o cabeçalho da tabela de proventos anual para '{ticker}'.")
        
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        try:
            ano_col_idx = headers.index('Ano')
            valor_col_idx = headers.index('Valor')
        except ValueError as e:
            raise ColumnNotFoundError(f"Colunas 'Ano' ou 'Valor' não encontradas no cabeçalho da tabela de proventos anual para '{ticker}'.") from e

        yearly_data = []
        for row in dividends_table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > max(ano_col_idx, valor_col_idx):
                ano_str = cols[ano_col_idx].get_text(strip=True)
                valor_str = cols[valor_col_idx].get_text(strip=True)
                try:
                    year = int(ano_str)
                    value = float(valor_str.replace('.', '').replace(',', '.'))
                    yearly_data.append({"Ano": year, "Valor": value})
                except (ValueError, IndexError) as e:
                    print(f"Aviso: Não foi possível processar a linha anual de provento: {e} - Ano: '{ano_str}', Valor: '{valor_str}'")
                    continue
        return yearly_data

    def get_monthly_dividends(self, ticker: str) -> list[dict]:
        """
        Busca os dados de proventos mensais (detalhados) de uma empresa no Fundamentus.
        Retorna uma lista de dicionários com 'Data', 'Valor', 'Tipo', etc.
        """
        path = f"proventos.php?papel={ticker.upper()}"
        try:
            soup = self._fetch_html(path)
        except ScrapingError as e:
            raise TickerNotFoundError(f"Não foi possível acessar a página de proventos para o ticker '{ticker}'.") from e

        dividends_table = soup.find('table', id='resultado') # The detailed table
        if not dividends_table:
            raise TableNotFoundError(f"Não foi possível encontrar a tabela de proventos detalhada (id='resultado') para '{ticker}'.")

        header_row = dividends_table.find('thead')
        if not header_row:
            raise ColumnNotFoundError(f"Não foi possível encontrar o cabeçalho da tabela de proventos detalhada para '{ticker}'.")
        
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # Mapping headers to their column indices dynamically
        header_map = {h: i for i, h in enumerate(headers)}
        
        required_cols = ['Data', 'Valor', 'Tipo', 'Data de Pagamento', 'Por quantas ações']
        for col in required_cols:
            if col not in header_map:
                raise ColumnNotFoundError(f"Coluna '{col}' não encontrada no cabeçalho da tabela de proventos detalhada para '{ticker}'.")

        monthly_data = []
        for row in dividends_table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= len(required_cols): # Ensure enough columns
                try:
                    data_str = cols[header_map['Data']].get_text(strip=True)
                    valor_str = cols[header_map['Valor']].get_text(strip=True)
                    tipo = cols[header_map['Tipo']].get_text(strip=True)
                    data_pagamento_str = cols[header_map['Data de Pagamento']].get_text(strip=True)
                    por_acoes_str = cols[header_map['Por quantas ações']].get_text(strip=True)

                    value = float(valor_str.replace('.', '').replace(',', '.'))
                    
                    # Handle date parsing for 'Data' (Ex-Date)
                    try:
                        ex_date = datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                    except ValueError:
                        ex_date = None # Or raise DataParsingError

                    # Handle date parsing for 'Data de Pagamento'
                    try:
                        payment_date = datetime.strptime(data_pagamento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                    except ValueError:
                        payment_date = None # Or raise DataParsingError if critical

                    shares_per_action = int(por_acoes_str)

                    monthly_data.append({
                        "Data": ex_date,
                        "Valor": value,
                        "Tipo": tipo,
                        "Data de Pagamento": payment_date,
                        "Por quantas ações": shares_per_action
                    })
                except (ValueError, IndexError) as e:
                    print(f"Aviso: Não foi possível processar a linha mensal de provento: {e} - Data: '{data_str}', Valor: '{valor_str}'")
                    continue
        return monthly_data

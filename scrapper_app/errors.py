# --- Exceções Personalizadas ---
class ScrapingError(Exception):
    """Exceção base para erros de scraping."""
    pass

class TickerNotFoundError(ScrapingError):
    """Exceção levantada quando o ticker não é encontrado ou a página não existe."""
    pass

class TableNotFoundError(ScrapingError):
    """Exceção levantada quando uma tabela esperada não é encontrada na página."""
    pass

class ColumnNotFoundError(ScrapingError):
    """Exceção levantada quando uma coluna esperada não é encontrada no cabeçalho da tabela."""
    pass

class DataParsingError(ScrapingError):
    """Exceção levantada quando há um erro ao parsear dados (ex: valor, data)."""
    pass
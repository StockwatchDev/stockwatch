"""Runtime data used for scraping the DeGiro site."""
from stockwatch.use_cases import degiro

_SCRAPE_THREAD = degiro.ScrapeThread()


def get_thread() -> degiro.ScrapeThread:
    """Get the singleton scrape thread."""
    return _SCRAPE_THREAD

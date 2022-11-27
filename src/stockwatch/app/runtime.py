"""Runtime data used for displaying the Stockwatch site."""
from stockwatch.use_cases import degiro

_SCRAPE_THREAD = degiro.ScrapeThread()


def get_scrape_thread() -> degiro.ScrapeThread:
    """Get the singleton scrape thread."""
    return _SCRAPE_THREAD

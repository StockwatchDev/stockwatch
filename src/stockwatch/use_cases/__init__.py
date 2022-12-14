"""This module contains the application logic for holding a stock portfolio with DeGiro.

This package has a clean architecture. Hence, this module should only depend on the
entities module (apart from plain Python).
"""

from . import degiro, importing, stockdir
from .importing import (
    get_portfolios_index_positions,
    process_index_prices,
    process_indices,
    process_portfolios,
    process_transactions,
)

__all__ = [
    "get_portfolios_index_positions",
    "process_index_prices",
    "process_indices",
    "process_portfolios",
    "process_transactions",
]

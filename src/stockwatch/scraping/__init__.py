""" Module for scraping data from the DeGiro website.

Can be run as an executable (see: python3 -m run.py --help),
or as a module py using the `process_date` method.
"""
from .run import process_date

__all__ = [
    "process_date",
]

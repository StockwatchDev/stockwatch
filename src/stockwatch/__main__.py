"""Analysis application for stock data obtain from DeGiro."""
import argparse

from .app import run_blocking
from .use_cases import stockdir

parser = argparse.ArgumentParser(description=__doc__, prog="python -m stockwatch")
stockdir.add_stockdir_argument(parser)


args = parser.parse_args()

stockdir.set_stockdir(args.dir)
print(f"Parsing the porfolio files in directory: '{stockdir.get_stockdir()}'")

run_blocking()

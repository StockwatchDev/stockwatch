"""Analysis application for stock data obtain from DeGiro."""
import argparse
import sys

from . import run
from .use_cases import stockdir

parser = argparse.ArgumentParser(description=__doc__, prog="python -m stockwatch")
parser.add_argument(
    "-n",
    "--no-dash",
    default=False,
    action="store_true",
    help="Don't run with the Dash webapp.",
)
stockdir.add_stockdir_argument(parser)


args = parser.parse_args()

stockdir.set_stockdir(args.dir)
print(f"Parsing the porfolio files in directory: '{stockdir.get_stockdir()}'")

sys.exit(run.main(args.no_dash))

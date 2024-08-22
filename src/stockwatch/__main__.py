"""Analysis application for stock data obtain from DeGiro."""

import argparse
import sys

from .app import run_blocking
from .use_cases import stockdir


def main() -> int:
    """Get command line arguments and start the server"""
    parser = argparse.ArgumentParser(description=__doc__, prog="stockwatch")
    stockdir.add_stockdir_argument(parser)

    args = parser.parse_args()

    stockdir.set_stockdir(args.dir)
    print(f"Parsing the porfolio files in directory: '{stockdir.get_stockdir()}'")

    run_blocking()

    return 0


if __name__ == "__main__":
    sys.exit(main())

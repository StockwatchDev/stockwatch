"""Analysis application for stock data obtain from DeGiro."""
import argparse
import os
import sys
from pathlib import Path

import stockwatch.run

STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"

parser = argparse.ArgumentParser(description=__doc__, prog="python -m stockwatch")
parser.add_argument(
    "-n",
    "--no-dash",
    default=False,
    action="store_true",
    help="Don't run with the Dash webapp.",
)

args = parser.parse_args()

# Let's try to read from the environment variables.
if not (folder_str := os.environ.get(STOCKWATCH_ENV_VAR, None)):
    parser.error(
        f"Please define the {STOCKWATCH_ENV_VAR} environment variable to specify "
        f"where the stockdata can be saved."
    )
    # This is not reached as parser.error already throws, but is used for mypy
    sys.exit(-1)

folder = Path(folder_str)
folder.mkdir(exist_ok=True)

print(f"Parsing the porfolio files in directory: '{folder}'")
run_func = stockwatch.run.main if args.no_dash else stockwatch.run.dash
sys.exit(run_func(folder))

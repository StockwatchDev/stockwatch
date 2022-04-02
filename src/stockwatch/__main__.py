"""Analysis application for stock data obtain from DeGiro."""
import argparse
import os
import sys
from pathlib import Path

import stockwatch.run

STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"

parser = argparse.ArgumentParser(description=__doc__, prog="python -m stockwatch")
parser.add_argument(
    "dir",
    nargs="?",
    default=None,
    type=Path,
    help="Directory where the portfolio files are installed, if not defined the "
    f"environment variable '{STOCKWATCH_ENV_VAR}' is used",
)
parser.add_argument(
    "-d",
    "--dash",
    default=False,
    action="store_true",
    help="Run a webserver with the stockwatch analysis.",
)

args = parser.parse_args()
folder: Path | None = args.dir

if not folder or not folder.is_dir():
    # Let's try to read from the environment variables.
    if env_path := os.environ.get(STOCKWATCH_ENV_VAR, ""):
        folder = Path(env_path)

if folder is None or not folder.is_dir():  # not folder or not folder.is_dir():
    parser.error(
        f"Folder: '{folder}' does not exist, please pass as commandline argument, or "
        f"define the '{STOCKWATCH_ENV_VAR}' environment variable."
    )
    # This is not reached as parser.error already throws, but is used for mypy
    sys.exit(-1)

print(f"Parsing the porfolio files in directory: '{folder}'")
run_func = stockwatch.run.dash if args.dash else stockwatch.run.main
sys.exit(run_func(folder))

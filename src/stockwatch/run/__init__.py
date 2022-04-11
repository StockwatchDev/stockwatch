"""Here all the different ways of running the Stockwatch application are defined."""
from pathlib import Path

from . import console, dash


def main(no_dash: bool, stockdir: Path) -> int:
    """Main run function."""
    return console.run(stockdir) if no_dash else dash.run(stockdir)

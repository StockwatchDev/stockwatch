"""Run module for starting stockwatch using a Dash interface in the browser."""
from pathlib import Path

from ..app import run_blocking


def run(folder: Path) -> int:
    """Wrapper method to the stockwatch.app.run_blocking method."""
    run_blocking(folder)
    return 0

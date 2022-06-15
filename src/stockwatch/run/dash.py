"""Run module for starting stockwatch using a Dash interface in the browser."""
from stockwatch.app import run_blocking


def run() -> int:
    """Wrapper method to the stockwatch.app.run_blocking method."""
    run_blocking()
    return 0

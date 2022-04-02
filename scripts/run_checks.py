#!/usr/bin/env python3
import pathlib
import subprocess
import sys


def _run_checker(cmdline: list[str]) -> subprocess.CompletedProcess[bytes]:
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    return subprocess.run(
        cmdline, cwd=root_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )


def run() -> int:
    """Run the defined checker on the source code."""
    checkers = {
        "mypy": ["mypy", "src"],
        "black": ["python3", "-m", "black", "--check", "src"],
        "pylint": ["pylint", "--recursive=y", "--enable-all-extensions", "./src"],
    }
    failed_checkers = []

    for checker, cmdline in checkers.items():
        print(f"Running: {checker}.")
        output = _run_checker(cmdline)

        if output.returncode != 0:
            failed_checkers.append(checker)
            print(output.stdout.decode())

    if failed_checkers:
        print(f"The failed checkers are: {failed_checkers}")
        return 1
    print("All checks successfull")
    return 0


if __name__ == "__main__":
    sys.exit(run())

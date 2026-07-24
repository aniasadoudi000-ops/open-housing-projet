"""CLI entrypoint for the Open Housing MVP package.

Usage examples:
    python -m open_housing_mvp
    python -m open_housing_mvp train
    python -m open_housing_mvp etl
"""

from __future__ import annotations

import argparse

from .etl import run_etl
from .train import train_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Open Housing MVP command runner")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["train", "etl"],
        default="train",
        help="Command to execute (default: train)",
    )
    args = parser.parse_args()

    if args.command == "etl":
        run_etl()
    else:
        train_model()


if __name__ == "__main__":
    main()

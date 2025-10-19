#!/usr/bin/env python
"""Utility script to download or prepare DocVQA dataset slices."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from docvqa.utils.logging import configure_logging, get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a local DocVQA dataset slice.")
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the raw DocVQA dataset (extracted).",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        required=True,
        help="Directory to store the curated subset for the pipeline.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of files to copy into the subset.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging("INFO")
    logger = get_logger(__name__)

    if not args.source.exists():
        raise SystemExit(f"Source path does not exist: {args.source}")

    args.destination.mkdir(parents=True, exist_ok=True)

    copied = 0
    supported_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
    for document in sorted(args.source.iterdir()):
        if document.suffix.lower() not in supported_suffixes:
            continue
        target = args.destination / document.name
        shutil.copy2(document, target)
        copied += 1
        if copied >= args.limit:
            break

    logger.info("dataset_prepared", copied=copied, destination=str(args.destination))


if __name__ == "__main__":
    main()

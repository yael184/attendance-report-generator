"""Command-line entry point.

A thin adapter over :class:`~attendance_report.container.Container`: it parses
arguments, configures logging and delegates to the pipeline.  It does **not**
know how any service is constructed.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import List, Optional, Sequence

from .container import AppConfig, Container
from .domain.exceptions import AttendanceError
from .infrastructure.logging_config import configure_logging

logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the fully-described argument parser."""
    parser = argparse.ArgumentParser(
        prog="attendance-report",
        description=(
            "Read a scanned PDF attendance report, apply deterministic "
            "variations to the working hours and render a new PDF."
        ),
        epilog="Omit INPUT to batch-process every PDF in the input directory.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        metavar="INPUT",
        help="Path to a single input PDF. If omitted, batch-process --input-dir.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        metavar="DIR",
        default="data/output",
        help="Directory for output PDF(s) (default: data/output).",
    )
    parser.add_argument(
        "-i", "--input-dir",
        metavar="DIR",
        default="data/input",
        help="Directory scanned in batch mode (default: data/input).",
    )
    parser.add_argument(
        "--template-dir",
        metavar="DIR",
        default="templates",
        help="Directory holding the Jinja2 HTML templates (default: templates).",
    )
    parser.add_argument(
        "--tesseract-path",
        metavar="PATH",
        default=None,
        help="Explicit path to the tesseract binary (if not on PATH).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG logging on the console.",
    )
    return parser


def _process_single(container: Container, input_path: str, output_dir: str) -> None:
    filename = os.path.basename(input_path)
    out_file = os.path.join(output_dir, f"modified_{filename}")
    container.pipeline().process_file(input_path, out_file)


def _process_batch(container: Container, input_dir: str, output_dir: str) -> int:
    os.makedirs(input_dir, exist_ok=True)
    pdfs = sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".pdf"))
    if not pdfs:
        logger.warning("No PDF files found in %s", input_dir)
        return 0
    logger.info("Found %d PDF file(s)", len(pdfs))
    for filename in pdfs:
        _process_single(container, os.path.join(input_dir, filename), output_dir)
    return len(pdfs)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    args = build_arg_parser().parse_args(argv)
    configure_logging(level=logging.DEBUG if args.verbose else logging.INFO)

    os.makedirs(args.output_dir, exist_ok=True)
    container = Container(
        AppConfig(
            template_dir=args.template_dir,
            tesseract_path=args.tesseract_path,
        )
    )

    logger.info("=" * 60)
    logger.info("Attendance Report Generator")
    logger.info("=" * 60)

    try:
        if args.input:
            if not os.path.isfile(args.input):
                logger.error("Input file not found: %s", args.input)
                return 1
            _process_single(container, args.input, args.output_dir)
        else:
            _process_batch(container, args.input_dir, args.output_dir)
    except AttendanceError as exc:
        logger.error("Processing failed: %s", exc)
        return 1

    logger.info("All files processed")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

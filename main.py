import argparse
import hashlib
import os
import sys

from logger_config import get_logger
from processors.eagle_strategy import EagleReportStrategy
from processors.monthly_strategy import MonthlyCardStrategy
from processors.type_a_strategy import TypeATransformationStrategy
from processors.type_b_strategy import TypeBTransformationStrategy
from processors.validating_decorator import ValidatingStrategyDecorator
from services.ocr_service import OCRService
from services.pdf_generator import PDFGenerator
from services.transformation_service import TransformationService

logger = get_logger(__name__)


def _make_seed(filename: str) -> int:
    return int(hashlib.md5(filename.encode()).hexdigest(), 16) % 100


def build_transformation_service() -> TransformationService:
    registry = {
        "TYPE_A": ValidatingStrategyDecorator(TypeATransformationStrategy()),
        "TYPE_B": ValidatingStrategyDecorator(TypeBTransformationStrategy()),
    }
    return TransformationService(strategy_registry=registry)


class AttendanceAutomationApp:

    def __init__(self):
        self.ocr_service = OCRService()
        self.pdf_generator = PDFGenerator(template_dir="templates")
        self.transformation_service = build_transformation_service()
        self.parsers = [EagleReportStrategy(), MonthlyCardStrategy()]

    def _select_parser(self, raw_text: str):
        for parser in self.parsers:
            if parser.identify(raw_text):
                return parser
        return None

    def process_file(self, input_path: str, output_path: str):
        try:
            filename = os.path.basename(input_path)
            logger.info(f"Processing: {filename}")

            logger.info("[1/4] OCR — extracting text from PDF")
            raw_text = self.ocr_service.get_text_from_pdf(input_path)

            logger.info("[2/4] Identifying report type and parsing rows")
            parser = self._select_parser(raw_text)
            if not parser:
                raise ValueError(f"Unsupported report format: {filename}")

            logger.info(f"Detected parser: {parser.__class__.__name__} ({parser.report_type})")
            rows = parser.parse(raw_text)
            logger.info(f"Parsed {len(rows)} rows")

            logger.info("[3/4] Applying transformation with validation")
            seed = _make_seed(filename)
            modified_rows = self.transformation_service.transform(parser.report_type, rows, seed)

            logger.info("[4/4] Generating output PDF")
            report_label = f"{parser.__class__.__name__}_{parser.report_type}"
            self.pdf_generator.generate_report(
                rows=modified_rows,
                output_path=output_path,
                report_type=report_label,
            )

            logger.info(f"Done → {output_path}")

        except Exception as exc:
            logger.error(f"Failed to process {input_path}: {exc}", exc_info=True)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Attendance Report Generator — produces a modified PDF from a scanned input"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the input PDF file. Omit to batch-process all PDFs in data/input/",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="data/output",
        help="Directory where the output PDF(s) will be written (default: data/output)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Attendance Report Generator")
    logger.info("=" * 60)

    app = AttendanceAutomationApp()

    if args.input:
        # Single-file mode (used by Docker)
        if not os.path.isfile(args.input):
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)
        filename = os.path.basename(args.input)
        out_file = os.path.join(args.output_dir, f"modified_{filename}")
        app.process_file(args.input, out_file)
    else:
        # Batch mode — process everything in data/input/
        input_dir = "data/input"
        os.makedirs(input_dir, exist_ok=True)
        files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
        if not files:
            logger.warning(f"No PDF files found in {input_dir}")
            return
        logger.info(f"Found {len(files)} PDF file(s)")
        for filename in files:
            in_file = os.path.join(input_dir, filename)
            out_file = os.path.join(args.output_dir, f"modified_{filename}")
            app.process_file(in_file, out_file)

    logger.info("=" * 60)
    logger.info("All files processed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

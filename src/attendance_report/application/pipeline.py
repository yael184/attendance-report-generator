"""The end-to-end use case: PDF in -> transformed PDF out.

The pipeline depends only on *abstractions*: the OCR and PDF ports and the
application-level factories/services.  It has no idea which concrete OCR
engine or PDF renderer is in use — the container wires those in.
"""

from __future__ import annotations

import logging
import os

from ..domain.exceptions import AttendanceError, OutputError
from .interfaces import OCRPort, PDFRendererPort
from .parsing.factory import ParserFactory
from .service import TransformationService
from .transformation.seed import seed_from_text

logger = logging.getLogger(__name__)


class AttendancePipeline:
    """Coordinates OCR, parsing, transformation and PDF rendering."""

    def __init__(
        self,
        ocr: OCRPort,
        renderer: PDFRendererPort,
        transformation_service: TransformationService,
    ) -> None:
        self._ocr = ocr
        self._renderer = renderer
        self._transformer = transformation_service

    def process_file(self, input_path: str, output_path: str) -> None:
        """Run the full pipeline for a single input PDF."""
        filename = os.path.basename(input_path)
        logger.info("Processing: %s", filename)

        try:
            logger.info("[1/4] OCR — extracting text")
            raw_text = self._ocr.get_text_from_pdf(input_path)

            logger.info("[2/4] Identifying report type and parsing")
            parser = ParserFactory.create_for(raw_text)
            rows = parser.parse(raw_text)
            logger.info("Parsed %d row(s) as %s", len(rows), parser.report_type)

            logger.info("[3/4] Transforming with validation")
            base_seed = seed_from_text(filename)
            modified = self._transformer.transform(parser.report_type, rows, base_seed)

            logger.info("[4/4] Rendering output PDF")
            try:
                self._renderer.generate_report(
                    rows=modified,
                    output_path=output_path,
                    report_type=parser.report_type,
                )
            except Exception as exc:  # noqa: BLE001 - normalise to OutputError
                raise OutputError(f"Failed to render {output_path}: {exc}") from exc

            logger.info("Done -> %s", output_path)

        except AttendanceError:
            logger.error("Failed to process %s", filename, exc_info=True)
            raise

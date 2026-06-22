"""OCR adapter — Tesseract + pdf2image (implements :class:`OCRPort`)."""

from __future__ import annotations

import logging
import os
from typing import Optional

from ..domain.exceptions import OCRError

logger = logging.getLogger(__name__)


class OCRService:
    """Extracts text from scanned PDFs using Tesseract OCR.

    Requires the *poppler* and *tesseract-ocr* system packages (provided by
    the Docker image).  Imports of the heavy OCR libraries are deferred to
    construction time so the rest of the app can be imported/tested without
    them installed.
    """

    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        dpi: int = 300,
        lang: str = "heb+eng",
    ) -> None:
        try:
            import pytesseract
            from pdf2image import convert_from_path
        except ImportError as exc:  # pragma: no cover - environment specific
            raise OCRError(f"OCR dependencies not available: {exc}") from exc

        self._pytesseract = pytesseract
        self._convert_from_path = convert_from_path
        self._dpi = dpi
        self._lang = lang
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def get_text_from_pdf(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            raise OCRError(f"PDF file not found: {pdf_path}")

        logger.info("Starting OCR for: %s", os.path.basename(pdf_path))
        try:
            pages = self._convert_from_path(pdf_path, dpi=self._dpi)
            logger.info("Converted PDF to %d page(s)", len(pages))

            chunks = []
            for idx, page in enumerate(pages, 1):
                grayscale = page.convert("L")
                text = self._pytesseract.image_to_string(
                    grayscale, lang=self._lang, config="--psm 6"
                )
                logger.debug("Page %d: %d chars", idx, len(text))
                chunks.append(f"\n--- PAGE {idx} ---\n{text}")

            full_text = "".join(chunks)
            logger.info("OCR complete: %d chars", len(full_text))
            return full_text
        except OCRError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalise to domain error
            raise OCRError(f"OCR failed for {pdf_path}: {exc}") from exc

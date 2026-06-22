"""Composition root — the one place that knows *how* to build the app.

A small hand-rolled DI container.  Nothing else in the codebase constructs
its own collaborators: the CLI asks the container for a ready-to-use
``AttendancePipeline`` and runs it.  Swapping an implementation (e.g. a fake
OCR engine in tests) is a single change here.

Dependencies are created lazily and cached so the (expensive) OCR/PDF
adapters are only built when first needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .application.interfaces import OCRPort, PDFRendererPort
from .application.observers import LoggingObserver, TransformationObserver
from .application.pipeline import AttendancePipeline
from .application.service import TransformationService
from .application.transformation.factory import StrategyFactory

# Importing these packages triggers self-registration of parsers/strategies.
from .application import parsing as _parsing  # noqa: F401
from .application import transformation as _transformation  # noqa: F401


@dataclass(frozen=True, slots=True)
class AppConfig:
    """User-tunable settings resolved at the composition root."""

    template_dir: str = "templates"
    tesseract_path: Optional[str] = None
    ocr_dpi: int = 300
    ocr_lang: str = "heb+eng"


class Container:
    """Builds and wires the application's object graph."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        *,
        ocr: Optional[OCRPort] = None,
        renderer: Optional[PDFRendererPort] = None,
        observers: Optional[list[TransformationObserver]] = None,
    ) -> None:
        self._config = config or AppConfig()
        # Optional overrides let tests inject fakes without touching anything else.
        self._ocr = ocr
        self._renderer = renderer
        self._observers = observers
        self._transformation_service: Optional[TransformationService] = None

    # ----- providers ------------------------------------------------------
    def ocr_service(self) -> OCRPort:
        if self._ocr is None:
            from .infrastructure.ocr_service import OCRService

            self._ocr = OCRService(
                tesseract_path=self._config.tesseract_path,
                dpi=self._config.ocr_dpi,
                lang=self._config.ocr_lang,
            )
        return self._ocr

    def pdf_renderer(self) -> PDFRendererPort:
        if self._renderer is None:
            from .infrastructure.pdf_generator import PDFGenerator

            self._renderer = PDFGenerator(template_dir=self._config.template_dir)
        return self._renderer

    def observers(self) -> list[TransformationObserver]:
        if self._observers is None:
            self._observers = [LoggingObserver()]
        return self._observers

    def transformation_service(self) -> TransformationService:
        if self._transformation_service is None:
            self._transformation_service = TransformationService(
                strategy_registry=StrategyFactory.build_registry(validated=True),
                observers=self.observers(),
            )
        return self._transformation_service

    def pipeline(self) -> AttendancePipeline:
        return AttendancePipeline(
            ocr=self.ocr_service(),
            renderer=self.pdf_renderer(),
            transformation_service=self.transformation_service(),
        )

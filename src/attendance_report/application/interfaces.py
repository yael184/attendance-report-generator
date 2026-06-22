"""Ports (interfaces) the application depends on.

These are declared in the application layer; the *infrastructure* layer
provides concrete adapters.  Because they are :class:`typing.Protocol`
classes, infrastructure does not even need to import them — dependencies
keep flowing inwards.
"""

from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from ..domain.models import AttendanceRow


@runtime_checkable
class OCRPort(Protocol):
    """Extracts raw text from a (scanned) PDF file."""

    def get_text_from_pdf(self, pdf_path: str) -> str: ...


@runtime_checkable
class PDFRendererPort(Protocol):
    """Renders transformed rows into an output PDF document."""

    def generate_report(
        self, rows: List[AttendanceRow], output_path: str, report_type: str
    ) -> None: ...

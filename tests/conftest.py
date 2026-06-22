"""Shared fixtures and test doubles."""

from __future__ import annotations

from typing import List

import pytest

from attendance_report.application.interfaces import OCRPort, PDFRendererPort
from attendance_report.domain.models import AttendanceRow

# Representative OCR output for an Eagle (TYPE_A) report.
EAGLE_TEXT = """
נ.ע. הנשר כח אדם בע"מ  גליליון
תאריך כניסה יציאה
01/05/2024 08:00 17:00
02/05/2024 08:30 16:45
03/05/2024 07:45 16:30
""".strip()

# Representative OCR output for a Monthly Card (TYPE_B) report.
MONTHLY_TEXT = """
כרטיס נוכחות חודשי - ימי עבודה
תאריך כניסה יציאה סה"כ
01/05 08:00 17:00 540
02/05 08:30 16:30 480
""".strip()


@pytest.fixture
def eagle_text() -> str:
    return EAGLE_TEXT


@pytest.fixture
def monthly_text() -> str:
    return MONTHLY_TEXT


@pytest.fixture
def sample_row() -> AttendanceRow:
    return AttendanceRow(
        date="01/05/2024",
        day_of_week="",
        entry_time="08:00",
        exit_time="17:00",
        total_hours=9.0,
    )


class FakeOCR:
    """An OCR port that returns canned text, ignoring the file path."""

    def __init__(self, text: str) -> None:
        self._text = text
        self.calls: List[str] = []

    def get_text_from_pdf(self, pdf_path: str) -> str:
        self.calls.append(pdf_path)
        return self._text


class FakeRenderer:
    """A PDF renderer port that records what it was asked to render."""

    def __init__(self) -> None:
        self.rows: List[AttendanceRow] = []
        self.output_path: str | None = None
        self.report_type: str | None = None

    def generate_report(
        self, rows: List[AttendanceRow], output_path: str, report_type: str
    ) -> None:
        self.rows = list(rows)
        self.output_path = output_path
        self.report_type = report_type


@pytest.fixture
def fake_ocr_factory():
    def _make(text: str) -> OCRPort:
        return FakeOCR(text)

    return _make


@pytest.fixture
def fake_renderer() -> PDFRendererPort:
    return FakeRenderer()

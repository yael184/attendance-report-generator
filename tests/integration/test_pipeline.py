"""End-to-end pipeline tests.

These exercise the whole flow (OCR -> parse -> transform -> render) wired
through the real :class:`Container`, but with the OCR and PDF *ports* replaced
by in-memory fakes so the test needs no tesseract/wkhtmltopdf installed.
"""

from __future__ import annotations

import pytest

from attendance_report.container import Container
from attendance_report.domain.exceptions import UnsupportedReportError

from tests.conftest import FakeOCR, FakeRenderer

pytestmark = pytest.mark.integration


def _run(text: str, input_name: str = "report.pdf"):
    renderer = FakeRenderer()
    container = Container(ocr=FakeOCR(text), renderer=renderer)
    container.pipeline().process_file(input_name, f"out_{input_name}")
    return renderer


def test_pipeline_eagle(eagle_text: str) -> None:
    renderer = _run(eagle_text, "eagle.pdf")
    assert renderer.report_type == "TYPE_A"
    assert len(renderer.rows) == 3
    assert renderer.output_path == "out_eagle.pdf"


def test_pipeline_monthly(monthly_text: str) -> None:
    renderer = _run(monthly_text, "monthly.pdf")
    assert renderer.report_type == "TYPE_B"
    assert len(renderer.rows) == 2


def test_pipeline_is_deterministic(eagle_text: str) -> None:
    first = _run(eagle_text, "eagle.pdf").rows
    second = _run(eagle_text, "eagle.pdf").rows
    assert first == second


def test_pipeline_rejects_unknown_report() -> None:
    container = Container(ocr=FakeOCR("nothing recognisable"), renderer=FakeRenderer())
    with pytest.raises(UnsupportedReportError):
        container.pipeline().process_file("x.pdf", "out.pdf")

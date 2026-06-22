"""Real end-to-end test using actual OCR + PDF rendering.

Skipped automatically when the Python OCR/PDF libraries or the underlying
system binaries (tesseract, poppler, wkhtmltopdf) are not available, so the
fast test suite still runs anywhere.  Where the tools *are* installed this
proves the whole project works against real sample PDFs.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

pytest.importorskip("pytesseract")
pytest.importorskip("pdf2image")
pytest.importorskip("pdfkit")

_TOOLS_PRESENT = all(
    shutil.which(tool) for tool in ("tesseract", "pdftoppm", "wkhtmltopdf")
) or Path(r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe").is_file()

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _TOOLS_PRESENT, reason="OCR/PDF system tools not installed"),
]

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_INPUT_DIR = _PROJECT_ROOT / "data" / "input"
_SAMPLE_PDFS = sorted(_INPUT_DIR.glob("*.pdf"))


@pytest.mark.skipif(not _SAMPLE_PDFS, reason="no sample PDFs in data/input")
def test_real_pipeline_produces_pdf(tmp_path: Path) -> None:
    from attendance_report.container import AppConfig, Container

    container = Container(
        AppConfig(template_dir=str(_PROJECT_ROOT / "templates"))
    )
    sample = _SAMPLE_PDFS[0]
    out_file = tmp_path / f"modified_{sample.name}"

    container.pipeline().process_file(str(sample), str(out_file))

    assert out_file.is_file()
    assert out_file.stat().st_size > 0

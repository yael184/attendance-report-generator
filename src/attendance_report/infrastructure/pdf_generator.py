"""PDF rendering adapter — Jinja2 + wkhtmltopdf (implements PDFRendererPort)."""

from __future__ import annotations

import logging
import os
import shutil
from datetime import date
from typing import List

from ..domain.exceptions import OutputError
from ..domain.models import AttendanceRow

logger = logging.getLogger(__name__)

_TEMPLATES = {
    "TYPE_A": "eagle_template.html",
    "TYPE_B": "monthly_template.html",
}
_DEFAULT_TEMPLATE = "monthly_template.html"


def _find_wkhtmltopdf() -> str:
    """Locate the wkhtmltopdf binary across env / PATH / Windows default."""
    env_path = os.environ.get("WKHTMLTOPDF_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    found = shutil.which("wkhtmltopdf")
    if found:
        return found

    windows_default = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.isfile(windows_default):
        return windows_default

    raise OutputError(
        "wkhtmltopdf not found. Install it or set WKHTMLTOPDF_PATH env variable."
    )


class PDFGenerator:
    """Renders attendance rows to a PDF using an HTML template."""

    def __init__(self, template_dir: str = "templates") -> None:
        try:
            import pdfkit
            from jinja2 import Environment, FileSystemLoader
        except ImportError as exc:  # pragma: no cover - environment specific
            raise OutputError(f"PDF dependencies not available: {exc}") from exc

        self._pdfkit = pdfkit
        self._env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def generate_report(
        self, rows: List[AttendanceRow], output_path: str, report_type: str
    ) -> None:
        logger.info("Generating PDF for %s -> %s", report_type, output_path)

        template_name = _TEMPLATES.get(report_type, _DEFAULT_TEMPLATE)
        template = self._env.get_template(template_name)
        html = template.render(
            rows=rows,
            report_title=report_type,
            report_type=report_type,
            generation_date=date.today().strftime("%d/%m/%Y"),
        )

        try:
            config = self._pdfkit.configuration(wkhtmltopdf=_find_wkhtmltopdf())
            options = {"encoding": "UTF-8", "enable-local-file-access": None}
            self._pdfkit.from_string(html, output_path, configuration=config, options=options)
        except OutputError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalise to domain error
            raise OutputError(f"Failed to generate {output_path}: {exc}") from exc

        logger.info("PDF generated: %s", output_path)

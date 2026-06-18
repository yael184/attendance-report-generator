import os
import shutil
from datetime import date
from typing import List

import pdfkit
from jinja2 import Environment, FileSystemLoader

from core.models import AttendanceRow
from logger_config import get_logger

logger = get_logger(__name__)


def _find_wkhtmltopdf() -> str:
    # Honour explicit env override first (useful in Docker or CI)
    env_path = os.environ.get("WKHTMLTOPDF_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # Try PATH (works on Linux/Mac and Windows when installed globally)
    found = shutil.which("wkhtmltopdf")
    if found:
        return found

    # Fallback for default Windows install location
    windows_default = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.isfile(windows_default):
        return windows_default

    raise FileNotFoundError(
        "wkhtmltopdf not found. Install it or set WKHTMLTOPDF_PATH env variable."
    )


class PDFGenerator:

    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_report(
        self, rows: List[AttendanceRow], output_path: str, report_type: str
    ):
        logger.info(f"Generating PDF report: {report_type}")

        wkhtmltopdf_path = _find_wkhtmltopdf()
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        template_name = (
            "eagle_template.html" if "Eagle" in report_type or "TYPE_A" in report_type
            else "monthly_template.html"
        )
        logger.debug(f"Using template: {template_name}")

        template = self.env.get_template(template_name)
        html_content = template.render(
            rows=rows,
            report_title=report_type,
            generation_date=date.today().strftime("%d/%m/%Y"),
        )

        options = {"encoding": "UTF-8", "enable-local-file-access": None}
        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
        logger.info(f"PDF generated: {output_path}")

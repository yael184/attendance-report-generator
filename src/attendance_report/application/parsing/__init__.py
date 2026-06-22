"""Report parsing — Strategy + Template Method + Factory/Registry.

Importing this package registers the built-in parsers with
:class:`~attendance_report.application.parsing.factory.ParserFactory`.
"""

from . import eagle_parser, monthly_parser  # noqa: F401  (registers parsers)
from .base_parser import BaseReportParser
from .factory import ParserFactory

__all__ = ["BaseReportParser", "ParserFactory"]

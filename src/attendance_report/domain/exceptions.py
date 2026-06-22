"""Custom exception hierarchy for the attendance pipeline.

A single base class (:class:`AttendanceError`) lets callers catch *any*
application error with one ``except``, while the concrete subclasses make it
possible to react to a specific failure stage.  Every exception carries
human-readable context in its message.

    AttendanceError
    ├── ConfigurationError   - invalid / missing configuration or rules
    ├── OCRError             - text extraction from the PDF failed
    ├── ParseError           - raw OCR text could not be understood
    │   └── UnsupportedReportError - no parser recognised the report
    ├── ValidationError      - a transformed row broke a business rule
    └── OutputError          - the result PDF could not be produced
"""

from __future__ import annotations


class AttendanceError(Exception):
    """Base class for every error raised by the application."""


class ConfigurationError(AttendanceError):
    """Raised when configuration or business rules are missing/invalid."""


class OCRError(AttendanceError):
    """Raised when OCR text extraction from a PDF fails."""


class ParseError(AttendanceError):
    """Raised when OCR text cannot be parsed into attendance rows."""


class UnsupportedReportError(ParseError):
    """Raised when no registered parser recognises the report format."""


class ValidationError(AttendanceError):
    """Raised when a transformed row violates a business rule."""


class OutputError(AttendanceError):
    """Raised when the output PDF cannot be generated."""

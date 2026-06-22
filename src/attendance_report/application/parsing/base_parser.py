"""Template-Method base class for all report parsers.

:meth:`BaseReportParser.parse` defines the *invariant skeleton* of parsing —
split the OCR text into lines, walk them while carrying a small mutable
``state`` dict, and collect rows — while delegating the variant-specific
"how do I read one line" decision to the abstract :meth:`_parse_line`.

Concrete parsers therefore only implement two things:

* :attr:`report_type` — the variant id they produce, and
* :meth:`matches` / :meth:`_parse_line` — the variant-specific logic.

Adding a brand-new report type means writing one subclass; the skeleton in
:meth:`parse` never changes (Open/Closed).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ...domain.models import AttendanceRow

logger = logging.getLogger(__name__)


class BaseReportParser(ABC):
    """Abstract parser. Subclasses fill in the variant-specific hooks."""

    #: Variant identifier produced by this parser (e.g. ``"TYPE_A"``).
    report_type: str = ""

    @abstractmethod
    def matches(self, raw_text: str) -> bool:
        """Return ``True`` if this parser recognises *raw_text*."""
        raise NotImplementedError

    @abstractmethod
    def _parse_line(
        self, line: str, state: Dict[str, object]
    ) -> Optional[AttendanceRow]:
        """Parse a single line, optionally using/updating *state*.

        Return an :class:`AttendanceRow` when the line completes a record, or
        ``None`` when it does not (yet) yield a row.
        """
        raise NotImplementedError

    # ----- Template method (do not override) -----------------------------
    def parse(self, raw_text: str) -> List[AttendanceRow]:
        """The fixed parsing algorithm shared by every variant."""
        logger.info("Parsing report as %s", self.report_type)
        state: Dict[str, object] = {}
        rows: List[AttendanceRow] = []

        for line_no, line in enumerate(raw_text.split("\n")):
            try:
                row = self._parse_line(line, state)
            except Exception:  # noqa: BLE001 - a bad line must not kill parsing
                logger.debug("Skipping unparseable line %d", line_no, exc_info=True)
                continue
            if row is not None:
                rows.append(row)

        logger.info("%s produced %d row(s)", self.report_type, len(rows))
        return rows

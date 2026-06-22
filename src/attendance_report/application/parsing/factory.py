"""Parser Factory backed by a Registry.

``ParserFactory`` keeps a registry of parser *classes* (not instances) keyed
by report type.  Parsers register themselves with the ``@ParserFactory.register``
decorator, so adding a new report variant is a one-line change at the new
class — no edits to the factory or to any existing code (Open/Closed).

The factory *creates* a fresh parser instance for the text it is given; it
never hands out a shared, stateful instance.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Type

from ...domain.exceptions import UnsupportedReportError
from .base_parser import BaseReportParser

logger = logging.getLogger(__name__)


class ParserFactory:
    """Registry-backed factory that builds the right parser for some text."""

    _registry: Dict[str, Type[BaseReportParser]] = {}

    @classmethod
    def register(
        cls, parser_cls: Type[BaseReportParser]
    ) -> Type[BaseReportParser]:
        """Class decorator: add *parser_cls* to the registry by report type."""
        report_type = parser_cls.report_type
        if not report_type:
            raise ValueError(f"{parser_cls.__name__} must define a report_type")
        cls._registry[report_type] = parser_cls
        logger.debug("Registered parser %s for %s", parser_cls.__name__, report_type)
        return parser_cls

    @classmethod
    def available_types(cls) -> List[str]:
        """Return the report types currently registered."""
        return list(cls._registry)

    @classmethod
    def create_for(cls, raw_text: str) -> BaseReportParser:
        """Instantiate the first parser whose ``matches`` accepts *raw_text*.

        Raises :class:`UnsupportedReportError` if none recognise the text.
        """
        for parser_cls in cls._registry.values():
            parser = parser_cls()
            if parser.matches(raw_text):
                logger.info("Selected parser %s", parser_cls.__name__)
                return parser
        raise UnsupportedReportError(
            "No registered parser recognised this report "
            f"(known types: {cls.available_types()})"
        )

    @classmethod
    def create(cls, report_type: str) -> BaseReportParser:
        """Instantiate a parser by explicit report type."""
        parser_cls = cls._registry.get(report_type)
        if parser_cls is None:
            raise UnsupportedReportError(f"No parser registered for '{report_type}'")
        return parser_cls()

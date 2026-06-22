"""Unit tests for parsers and the parser factory/registry."""

from __future__ import annotations

import pytest

from attendance_report.application.parsing import ParserFactory
from attendance_report.application.parsing.eagle_parser import EagleReportParser
from attendance_report.application.parsing.monthly_parser import MonthlyCardParser
from attendance_report.domain.exceptions import UnsupportedReportError


def test_factory_registers_both_types() -> None:
    types = ParserFactory.available_types()
    assert "TYPE_A" in types
    assert "TYPE_B" in types


def test_factory_selects_eagle(eagle_text: str) -> None:
    parser = ParserFactory.create_for(eagle_text)
    assert isinstance(parser, EagleReportParser)
    assert parser.report_type == "TYPE_A"


def test_factory_selects_monthly(monthly_text: str) -> None:
    parser = ParserFactory.create_for(monthly_text)
    assert isinstance(parser, MonthlyCardParser)
    assert parser.report_type == "TYPE_B"


def test_factory_creates_new_instances_each_call(eagle_text: str) -> None:
    a = ParserFactory.create_for(eagle_text)
    b = ParserFactory.create_for(eagle_text)
    assert a is not b  # a factory creates, it does not store/share


def test_factory_unrecognised_raises() -> None:
    with pytest.raises(UnsupportedReportError):
        ParserFactory.create_for("totally unrelated text")


def test_eagle_parses_rows(eagle_text: str) -> None:
    rows = EagleReportParser().parse(eagle_text)
    assert len(rows) == 3
    first = rows[0]
    assert first.date == "01/05/2024"
    assert first.entry_time == "08:00"
    assert first.exit_time == "17:00"
    assert first.location == "גליליון"


def test_monthly_parses_rows(monthly_text: str) -> None:
    rows = MonthlyCardParser().parse(monthly_text)
    assert len(rows) == 2
    assert rows[0].date == "01/05"
    assert rows[0].entry_time == "08:00"
    assert rows[0].exit_time == "17:00"

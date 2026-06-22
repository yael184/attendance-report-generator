"""Unit tests for the CLI adapter (Container is faked)."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from attendance_report import cli


class _FakePipeline:
    def __init__(self, sink: List[str]) -> None:
        self._sink = sink

    def process_file(self, input_path: str, output_path: str) -> None:
        self._sink.append(f"{input_path}->{output_path}")


class _FakeContainer:
    calls: List[str] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self.calls)


@pytest.fixture(autouse=True)
def _patch_container(monkeypatch: pytest.MonkeyPatch) -> None:
    _FakeContainer.calls = []
    monkeypatch.setattr(cli, "Container", _FakeContainer)


def test_arg_parser_help_runs() -> None:
    parser = cli.build_arg_parser()
    assert parser.prog == "attendance-report"


def test_single_file_mode(tmp_path: Path) -> None:
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    out = tmp_path / "out"
    rc = cli.main([str(pdf), "-o", str(out)])
    assert rc == 0
    assert len(_FakeContainer.calls) == 1


def test_missing_file_returns_error(tmp_path: Path) -> None:
    rc = cli.main([str(tmp_path / "nope.pdf"), "-o", str(tmp_path)])
    assert rc == 1


def test_batch_mode(tmp_path: Path) -> None:
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "a.pdf").write_bytes(b"x")
    (in_dir / "b.pdf").write_bytes(b"x")
    rc = cli.main(["-i", str(in_dir), "-o", str(tmp_path / "out")])
    assert rc == 0
    assert len(_FakeContainer.calls) == 2


def test_batch_mode_no_files(tmp_path: Path) -> None:
    rc = cli.main(["-i", str(tmp_path / "empty"), "-o", str(tmp_path / "out")])
    assert rc == 0
    assert _FakeContainer.calls == []

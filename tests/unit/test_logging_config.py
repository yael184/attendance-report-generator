"""Unit test for logging configuration."""

from __future__ import annotations

import logging
from pathlib import Path

from attendance_report.infrastructure import logging_config


def test_configure_logging_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    # Reset the module-level guard so the test is self-contained.
    monkeypatch.setattr(logging_config, "_CONFIGURED", False)
    root = logging.getLogger()
    before = len(root.handlers)

    log_file = tmp_path / "app.log"
    logging_config.configure_logging(level=logging.INFO, log_file=str(log_file))
    after_first = len(root.handlers)
    assert after_first > before

    logging_config.configure_logging(level=logging.INFO, log_file=str(log_file))
    assert len(root.handlers) == after_first  # second call is a no-op

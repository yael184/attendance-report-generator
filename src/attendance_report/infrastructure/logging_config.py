"""Logging configuration (a cross-cutting infrastructure concern).

Call :func:`configure_logging` once from the composition root.  Everywhere
else, modules simply use ``logging.getLogger(__name__)`` and stay decoupled
from how logging is set up.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

_CONFIGURED = False


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = "logs/app.log",
) -> None:
    """Configure root handlers once (idempotent).

    A console handler shows ``level`` and above; an optional file handler
    captures everything at DEBUG for post-mortem analysis.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    root.addHandler(console)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _CONFIGURED = True

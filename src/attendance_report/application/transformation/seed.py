"""Deterministic, *per-row* seeding.

The whole transformation is reproducible: the same input file always yields
the same output.  Crucially the seed is derived **per row** from the row's
date (plus a per-file base), so each day varies independently and a unit test
can assert that "row Y of file X always becomes Z".

    base_seed  -> stable per input file (e.g. hash of the filename)
    row_seed   -> base_seed combined with the row's day/month
"""

from __future__ import annotations

import hashlib
import random
import re

from ...domain.models import AttendanceRow

_DATE_PARTS_RE = re.compile(r"(\d{1,2})\D+(\d{1,2})")


def seed_from_text(text: str) -> int:
    """Stable non-negative integer seed derived from arbitrary text."""
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100_000


def _date_components(date_str: str) -> tuple[int, int]:
    """Best-effort ``(day, month)`` extraction from a noisy date string."""
    match = _DATE_PARTS_RE.search(date_str or "")
    if not match:
        return 0, 0
    day, month = int(match.group(1)), int(match.group(2))
    return day, month


def derive_row_seed(base_seed: int, row: AttendanceRow) -> int:
    """Combine the per-file *base_seed* with the row's date.

    Mirrors the spirit of ``seed = day + month*100`` but folds in the file
    base so different files transform the same calendar date differently.
    """
    day, month = _date_components(row.date)
    return (base_seed * 10_000 + month * 100 + day) % (2**31)


def row_rng(base_seed: int, row: AttendanceRow) -> random.Random:
    """Return a :class:`random.Random` seeded deterministically for *row*."""
    return random.Random(derive_row_seed(base_seed, row))

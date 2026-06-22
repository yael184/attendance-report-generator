"""Unit tests for deterministic per-row seeding."""

from __future__ import annotations

import dataclasses

from attendance_report.application.transformation.seed import (
    derive_row_seed,
    row_rng,
    seed_from_text,
)


def test_seed_from_text_is_stable() -> None:
    assert seed_from_text("a_r_9.pdf") == seed_from_text("a_r_9.pdf")
    assert seed_from_text("a") != seed_from_text("b")


def test_row_seed_depends_on_date(sample_row) -> None:
    other = dataclasses.replace(sample_row, date="15/06/2024")
    assert derive_row_seed(42, sample_row) != derive_row_seed(42, other)


def test_row_seed_depends_on_base(sample_row) -> None:
    assert derive_row_seed(1, sample_row) != derive_row_seed(2, sample_row)


def test_row_rng_is_reproducible(sample_row) -> None:
    a = row_rng(7, sample_row).randint(0, 1000)
    b = row_rng(7, sample_row).randint(0, 1000)
    assert a == b

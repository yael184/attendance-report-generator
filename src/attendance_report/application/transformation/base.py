"""Strategy interface for row transformations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...domain.models import AttendanceRow


class TransformationStrategy(ABC):
    """A pluggable algorithm that turns one row into a transformed row.

    Both concrete strategies *and* the validating decorator implement this
    single interface, which is what lets the decorator wrap any strategy (or
    another decorator) transparently.
    """

    @abstractmethod
    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        """Return a new, transformed copy of *row* (input is never mutated)."""
        raise NotImplementedError

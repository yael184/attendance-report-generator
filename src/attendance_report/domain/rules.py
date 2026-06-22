"""Central, immutable business-rule configuration.

Every threshold, range and per-variant tuning knob lives here — *not* scattered
across decorators and strategies.  Changing a rule (e.g. the latest allowed
entry time) is a one-line edit in this file.

The :data:`RULES_REGISTRY` maps a report variant to its :class:`VariantRules`,
and :func:`get_rules` performs a safe lookup with a sensible fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class VariantRules:
    """Immutable rule-set governing one report variant.

    Attributes
    ----------
    entry_min / entry_max:
        Allowed window for the (post-variation) entry time, ``HH:MM``.
    exit_min / exit_max:
        Allowed window for the (post-variation) exit time, ``HH:MM``.
    break_max_minutes:
        Maximum tolerated break length in minutes.
    standard_daily_hours:
        Hours worked before overtime (125%) starts to accrue.
    overtime_125_cap_hours:
        Maximum hours billable at the 125% rate per day.
    entry_jitter_mod / exit_jitter_mod:
        Moduli used to derive the deterministic per-row time jitter; using
        different values per variant keeps the two report types visually
        distinct while remaining reproducible.
    """

    entry_min: str
    entry_max: str
    exit_min: str
    exit_max: str
    break_max_minutes: int
    standard_daily_hours: float
    overtime_125_cap_hours: float
    entry_jitter_mod: int
    exit_jitter_mod: int


# The single source of truth for per-variant rules.
RULES_REGISTRY: Mapping[str, VariantRules] = {
    "TYPE_A": VariantRules(
        entry_min="05:00",
        entry_max="11:00",
        exit_min="10:00",
        exit_max="23:59",
        break_max_minutes=90,
        standard_daily_hours=9.0,
        overtime_125_cap_hours=2.0,
        entry_jitter_mod=7,
        exit_jitter_mod=4,
    ),
    "TYPE_B": VariantRules(
        entry_min="05:00",
        entry_max="11:00",
        exit_min="10:00",
        exit_max="23:59",
        break_max_minutes=90,
        standard_daily_hours=9.0,
        overtime_125_cap_hours=2.0,
        entry_jitter_mod=5,
        exit_jitter_mod=6,
    ),
}

# Used when a variant has no dedicated entry (keeps the pipeline resilient).
_DEFAULT_RULES = RULES_REGISTRY["TYPE_A"]


def get_rules(variant: str, *, strict: bool = False) -> VariantRules:
    """Return the :class:`VariantRules` for *variant*.

    With ``strict=False`` (default) an unknown variant falls back to the
    default rule-set; with ``strict=True`` it raises
    :class:`ConfigurationError`.
    """
    rules = RULES_REGISTRY.get(variant)
    if rules is None:
        if strict:
            raise ConfigurationError(f"No rules registered for variant '{variant}'")
        return _DEFAULT_RULES
    return rules

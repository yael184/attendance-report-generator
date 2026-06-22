"""Strategy Factory backed by a Registry.

Transformation strategies register themselves by report type with
``@StrategyFactory.register``.  The factory can hand back a bare strategy or,
more usefully, one already wrapped in the
:class:`ValidatingStrategyDecorator` — the standard composition used by the
pipeline.  Adding a new variant means writing one strategy class; no factory
edit required.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Type

from ...domain.exceptions import ConfigurationError
from .base import TransformationStrategy
from .validating_decorator import ValidatingStrategyDecorator

logger = logging.getLogger(__name__)


class StrategyFactory:
    """Registry-backed factory for transformation strategies."""

    _registry: Dict[str, Type[TransformationStrategy]] = {}

    @classmethod
    def register(
        cls, strategy_cls: Type[TransformationStrategy]
    ) -> Type[TransformationStrategy]:
        """Class decorator: register *strategy_cls* by its ``report_type``."""
        report_type = getattr(strategy_cls, "report_type", "")
        if not report_type:
            raise ValueError(f"{strategy_cls.__name__} must define a report_type")
        cls._registry[report_type] = strategy_cls
        logger.debug(
            "Registered strategy %s for %s", strategy_cls.__name__, report_type
        )
        return strategy_cls

    @classmethod
    def available_types(cls) -> List[str]:
        return list(cls._registry)

    @classmethod
    def create(cls, report_type: str) -> TransformationStrategy:
        """Create a bare strategy instance for *report_type*."""
        strategy_cls = cls._registry.get(report_type)
        if strategy_cls is None:
            raise ConfigurationError(
                f"No transformation strategy registered for '{report_type}'"
            )
        return strategy_cls()

    @classmethod
    def create_validated(cls, report_type: str) -> TransformationStrategy:
        """Create a strategy wrapped in the validating decorator."""
        return ValidatingStrategyDecorator(cls.create(report_type), report_type)

    @classmethod
    def build_registry(cls, *, validated: bool = True) -> Dict[str, TransformationStrategy]:
        """Build a ``{report_type: strategy}`` map for every registered type."""
        factory = cls.create_validated if validated else cls.create
        return {rt: factory(rt) for rt in cls._registry}

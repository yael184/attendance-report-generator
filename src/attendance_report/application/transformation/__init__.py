"""Transformation — Strategy + Decorator + Factory/Registry.

Importing this package registers the built-in transformation strategies with
:class:`~attendance_report.application.transformation.factory.StrategyFactory`.
"""

from . import type_a, type_b  # noqa: F401  (registers strategies)
from .base import TransformationStrategy
from .factory import StrategyFactory
from .validating_decorator import ValidatingStrategyDecorator

__all__ = [
    "TransformationStrategy",
    "StrategyFactory",
    "ValidatingStrategyDecorator",
]

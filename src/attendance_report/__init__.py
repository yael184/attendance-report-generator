"""Attendance Report Generator.

A small Clean-Architecture application that reads scanned PDF attendance
reports, applies deterministic per-row variations to the working hours and
renders a new PDF that mirrors the original layout.

Layers (dependencies always flow inwards):

    domain          -> pure business model, rules and value logic (no I/O)
    application     -> use cases, design patterns, ports (depends on domain)
    infrastructure  -> adapters for OCR / PDF / logging (implements ports)
    cli / container -> composition root that wires everything together
"""

__all__ = ["__version__"]

__version__ = "2.0.0"

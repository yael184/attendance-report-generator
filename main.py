"""Convenience launcher: ``python main.py [args]``.

Adds ``src/`` to the import path so the project runs straight from a checkout
without an editable install, then delegates to the real CLI.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from attendance_report.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())

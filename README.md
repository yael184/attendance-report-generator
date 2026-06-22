# Attendance Report Variation System 📊

Process scanned PDF attendance reports, identify the report type via OCR, apply
**deterministic** per-row variations to the working hours, and generate a new
PDF that mirrors the original layout.

Built as a teaching project to demonstrate **Clean Architecture** and a set of
classic **design patterns** working together on a real, end-to-end task.

---

## 🏗️ Architecture

Dependencies always flow **inwards** — the domain knows nothing about OCR, PDF
libraries or the CLI. Infrastructure implements ports declared by the
application; the composition root (`container.py`) is the only place that wires
concrete adapters together.

```text
src/attendance_report/
├── domain/                 # Pure business core (no I/O, no frameworks)
│   ├── models.py           #   frozen dataclasses (the unified model)
│   ├── rules.py            #   frozen VariantRules + RULES_REGISTRY
│   ├── exceptions.py       #   AttendanceError hierarchy
│   └── time_utils.py       #   pure time parsing/normalisation
├── application/            # Use cases + design patterns (depends on domain)
│   ├── interfaces.py       #   ports: OCRPort, PDFRendererPort
│   ├── parsing/            #   Template Method + Strategy + Factory/Registry
│   ├── transformation/     #   Strategy + Decorator + Factory + per-row seed
│   ├── observers.py        #   Observer pattern
│   ├── service.py          #   TransformationService (Observer subject)
│   └── pipeline.py         #   end-to-end use case
├── infrastructure/         # Adapters (implement the ports)
│   ├── ocr_service.py      #   Tesseract + pdf2image
│   ├── pdf_generator.py    #   Jinja2 + wkhtmltopdf
│   └── logging_config.py
├── container.py            # Composition root / DI container
└── cli.py                  # argparse entry point
tests/
├── unit/                   # fast, no system tools required
└── integration/            # pipeline tests (fakes) + 1 real end-to-end test
```

## 🎯 Design patterns used

| Pattern             | Where                                                            |
| ------------------- | --------------------------------------------------------------- |
| **Strategy**        | parsers (`*_parser.py`) and transformations (`type_a/type_b`)   |
| **Template Method** | `BaseReportParser.parse` defines the skeleton; subclasses fill hooks |
| **Factory**         | `ParserFactory`, `StrategyFactory` — *create* by type           |
| **Registry**        | self-registration via `@ParserFactory.register` / `RULES_REGISTRY` |
| **Decorator**       | `ValidatingStrategyDecorator` wraps any strategy (or decorator) |
| **Observer**        | `TransformationService` notifies `LoggingObserver` etc.         |
| **Dependency Injection** | `Container` builds the whole object graph in one place      |

Adding a **third report type** means writing one parser class and one strategy
class — both self-register, and *no existing file changes* (Open/Closed).

## 🔑 Key engineering choices

- **Unified model** — both report formats normalise into the same frozen
  `AttendanceRow`; only the parser and the strategy are variant-specific.
- **Immutability** — every domain object is `frozen=True`; transformations
  return new rows via `dataclasses.replace`, never mutate.
- **Deterministic per-row randomness** — the seed is derived from the filename
  *and* each row's date, so output is reproducible and individually testable.
- **Centralised rules** — all thresholds live in `domain/rules.py`; changing a
  rule is a one-line edit.
- **Typed** — passes `mypy --strict`.

---

## 🛠️ Prerequisites

- **Python 3.10+**
- **Tesseract OCR** (+ Hebrew language pack) — text extraction
- **Poppler** — PDF → image conversion
- **wkhtmltopdf** — HTML → PDF rendering

> With Docker, none of the system tools need to be installed locally — they are
> bundled in the image.

## 💻 Installation

```bash
pip install -r requirements.txt        # runtime only
# or, for development (tests + type checking):
pip install -e ".[dev]"
```

## 🏃 Running

```bash
python main.py                 # batch: process every PDF in data/input/
python main.py report.pdf -o out/   # single file
python -m attendance_report -h      # full help
```

See **[USAGE.md](USAGE.md)** for the complete CLI reference, Docker instructions
and troubleshooting.

## 🐳 Docker

```bash
docker build -t attendance-report .
docker run --rm -v "C:\samples:/data" attendance-report -o /data/output/
```

## ✅ Tests & quality

```bash
pytest --cov          # unit + integration, ~89% coverage
mypy --strict src/attendance_report
```

---

*Developed as a home assignment for a Student Position.*

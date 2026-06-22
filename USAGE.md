# Running the Attendance Report Generator

## Prerequisites

### Local (CLI) run

| Dependency                           | Purpose                |
| ------------------------------------ | ---------------------- |
| Python 3.x                           | Runtime                |
| Tesseract OCR + Hebrew language pack | PDF text extraction    |
| Poppler                              | PDF → image conversion |
| wkhtmltopdf                          | HTML → PDF rendering   |

Install Python packages:

```bash
pip install -r requirements.txt
```

### Docker run

Only Docker Desktop is required — all system dependencies are bundled in the image.

---

## Docker

### 1. Build the image (once)

```bash
docker build -t attendance-report .
```

### 2. Run — single file

**Linux / macOS (bash):**

```bash
docker run --rm -v /path/to/your/samples:/data attendance-report /data/sample.pdf -o /data/
```

**Windows (PowerShell):**

```powershell
docker run --rm -v "C:\samples:/data" attendance-report /data/sample.pdf -o /data/
```

The output file is written to the mounted folder as `modified_sample.pdf`.

> **Note:** Docker volume paths must not contain non-ASCII characters (e.g. Hebrew folder names).
> Copy your PDFs to a plain-ASCII path such as `C:\samples\` before mounting.

### 3. Run — batch mode (process all PDFs in a folder)

Prepare the folder structure on the host:

```text
C:\samples\
  input\
    report1.pdf
    report2.pdf
```

Then run without specifying an input file — the app discovers every `.pdf` in `/data/input/`:

```powershell
docker run --rm -v "C:\samples:/data" attendance-report -o /data/output/
```

Output files appear in `C:\samples\output\` as `modified_<original-name>.pdf`.

---

## CLI (local)

### Single file

```bash
python main.py path/to/report.pdf -o path/to/output/
```

### Batch mode (processes everything in `data/input/`)

```bash
python main.py
```

Output is written to `data/output/` by default.

You can also run it as a module:

```bash
python -m attendance_report            # batch mode
python -m attendance_report report.pdf # single file
```

### Full argument reference

```text
usage: attendance-report [-h] [-o DIR] [-i DIR] [--template-dir DIR]
                         [--tesseract-path PATH] [-v] [INPUT]

positional arguments:
  INPUT                 Path to a single input PDF. If omitted, batch-process --input-dir.

options:
  -o, --output-dir DIR     Directory for output PDF(s) (default: data/output)
  -i, --input-dir DIR      Directory scanned in batch mode (default: data/input)
  --template-dir DIR       Directory holding the Jinja2 templates (default: templates)
  --tesseract-path PATH    Explicit path to the tesseract binary (if not on PATH)
  -v, --verbose            Enable DEBUG logging on the console
  -h, --help               Show this help message and exit
```

---

## Development & testing

```bash
pip install -e ".[dev]"      # install with dev extras (pytest, mypy)
pytest                       # run unit + integration tests
pytest --cov                 # with coverage report
pytest -m "not integration"  # unit tests only (no system tools needed)
mypy --strict src/attendance_report
```

The integration tests use in-memory fakes for OCR/PDF, so they run anywhere.
One real end-to-end test (`tests/integration/test_real_pipeline.py`) exercises
the actual OCR + PDF stack and skips automatically when the system tools are
absent.

---

## Supported Report Types

| Type token | Report format         | Identified by                    |
| ---------- | --------------------- | -------------------------------- |
| `TYPE_A`   | Eagle (נ.ע. הנשר)     | Keywords: הנשר, גליליון          |
| `TYPE_B`   | Monthly Employee Card | Keywords: ימי עבודה, כניסה, שעות |

---

## How It Works

```text
PDF file
  │
  ▼  OCR (Tesseract, 300 DPI, Hebrew + English)
  │
  ▼  Parser — identifies report type, extracts rows into AttendanceRow objects
  │
  ▼  TransformationService — looks up the strategy by type token
  │     └─ ValidatingStrategyDecorator
  │           ├─ TypeAStrategy / TypeBStrategy  ← applies deterministic time adjustments
  │           └─ Validates: exit > entry, times in allowed range, break ≤ 90 min
  │                If validation fails → original row is kept (no silent corruption)
  │
  ▼  PDFGenerator (wkhtmltopdf + Jinja2 template) → modified_<name>.pdf
```

Transformations are **deterministic at the row level**: a per-row seed is
derived from the input filename *and* the row's date, so the same file always
produces the same output and each day varies independently (which is what makes
the transformation unit-testable).

---

## Troubleshooting

| Symptom                                 | Fix                                                                                          |
| --------------------------------------- | -------------------------------------------------------------------------------------------- |
| `wkhtmltopdf not found`                 | Install wkhtmltopdf and ensure it is on PATH, or set `WKHTMLTOPDF_PATH=/path/to/wkhtmltopdf` |
| `TesseractNotFoundError`                | Install Tesseract and add it to PATH                                                         |
| `No PDF files found`                    | Check that input files end with `.pdf` (lowercase)                                           |
| Docker: file not found inside container | Ensure the host path in `-v` uses ASCII characters only                                      |
| Docker: empty output dir                | Check logs — the container prints `INFO`/`ERROR` to stdout                                   |

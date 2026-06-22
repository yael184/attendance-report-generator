# ───────────────────────── Stage 1: build dependencies ─────────────────────
# Python wheels are installed into an isolated prefix so the final image stays
# slim and does not carry build-time tooling.
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ───────────────────────── Stage 2: runtime image ──────────────────────────
FROM python:3.11-slim-bookworm AS runtime

# System dependencies required at runtime:
#   tesseract-ocr / -heb  — OCR engine + Hebrew language pack
#   poppler-utils         — pdf2image (pdftoppm)
#   wkhtmltopdf           — pdfkit HTML→PDF renderer
#   fonts-freefont-ttf    — Unicode/Hebrew glyph coverage for wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-heb \
        poppler-utils \
        wkhtmltopdf \
        fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Bring in the pre-built Python packages from the builder stage.
COPY --from=builder /install /usr/local

WORKDIR /app
COPY src/ ./src/
COPY templates/ ./templates/
COPY main.py pyproject.toml README.md ./

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

# Default I/O directories so the app never crashes on a fresh run.
RUN mkdir -p data/input data/output logs

# No args -> batch-process every PDF in data/input (mount it as a volume).
ENTRYPOINT ["python", "-m", "attendance_report"]

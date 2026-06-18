FROM python:3.11-slim-bullseye

# System dependencies:
#   tesseract-ocr         — OCR engine
#   tesseract-ocr-heb     — Hebrew language pack
#   poppler-utils         — pdf2image (pdftoppm)
#   wkhtmltopdf           — pdfkit HTML→PDF renderer
#   fonts-freefont-ttf    — Unicode/Hebrew font coverage for wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-heb \
        poppler-utils \
        wkhtmltopdf \
        fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requierments.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create default I/O directories so the app doesn't crash on first run
RUN mkdir -p data/input data/output logs

ENTRYPOINT ["python", "main.py"]

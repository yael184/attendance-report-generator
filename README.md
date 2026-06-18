# Attendance Report Variation System 📊

This project was developed as part of a home assignment for a student position. The goal is to process scanned PDF attendance reports, identify the report type, apply deterministic variations to the working hours, and generate a new PDF that preserves the original layout and structure.

## 🚀 Key Features

- **Automatic Report Identification**: Uses OCR and Strategy Design Pattern to distinguish between different report formats.
- **Deterministic Logic**: Applies "human-like" variations to entry/exit times while ensuring logical consistency (Exit > Entry) and consistency across the same file.
- **OCR Integration**: Processes scanned documents using Tesseract OCR and PDF-to-Image conversion.
- **HTML-based PDF Generation**: Utilizes Jinja2 templates to create professional-looking PDFs that mimic the original layout.

## 🏗️ Architecture & Design Patterns

The project follows **Clean Architecture** principles to ensure maintainability and scalability:

- **Strategy Pattern**: Used to encapsulate the parsing logic for different report types. Adding a new report format only requires adding a new strategy class.
- **Layered Architecture**: 
  - `core`: Domain models and business logic (variation engine).
  - `processors`: Strategy implementations and data extraction.
  - `services`: Infrastructure services (OCR, PDF Generation).
  - `templates`: Visual representation (HTML/CSS).

## 📁 Project Structure

```text
attendance_project/
├── main.py                 # Application orchestrator
├── requirements.txt        # Python dependencies
├── core/                   # Logic & Models
│   ├── models.py           # Unified data structures
│   └── variation_logic.py  # Deterministic variation engine
├── processors/             # Parsing Strategies
│   ├── base_strategy.py    # Strategy Interface
│   ├── eagle_strategy.py   # Strategy for "Eagle" reports
│   └── monthly_strategy.py # Strategy for "Monthly Card" reports
├── services/               # Infrastructure
│   ├── ocr_service.py      # Tesseract & PDF processing
│   └── pdf_generator.py    # HTML to PDF conversion
├── templates/              # HTML Templates (Jinja2)
└── data/                   # Input/Output folders
```
## 🛠️ Prerequisites
Before running the project, ensure you have the following system dependencies installed:

- **Tesseract OCR**: Required for text extraction from images.  
- **Poppler**: Required for converting PDF pages to images.  
- **wkhtmltopdf**: Required for converting HTML templates to PDF.  

---

## 💻 Installation & Setup

### Clone the repository:
```bash
git clone <repository-url>
cd attendance_project
```

## 📦 Install Python dependencies

``` bash
pip install -r requirements.txt
```

## ⚙️ Configure Tesseract path (Optional)

If Tesseract is not in your system's PATH, update the path in:

    services/ocr_service.py

## 🏃 How to Run

1.  Place your scanned PDF files in the `data/input/` directory.

2.  Execute the main script:

``` bash
python main.py
```

3.  Find the modified reports in the `data/output/` directory.

## 🧠 The Logic Behind Variations

The system uses a **Hash-based Seeding mechanism**.\
By hashing the filename, the `VariationEngine` generates an offset
(*jitter*) that is:

-   Unique to the file\
-   Consistent across runs for the same file

This ensures:

-   **Reliability** -- Total hours remain within a reasonable
    daily/monthly range\
-   **Validity** -- Exit time is always verified to be later than the
    entry time\
-   **Human Touch** -- Small, non-rounded additions/subtractions to the
    times

------------------------------------------------------------------------

*Developed as a home assignment for a Student Position.*

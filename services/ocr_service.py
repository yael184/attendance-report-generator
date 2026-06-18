import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from logger_config import get_logger

logger = get_logger(__name__)

class OCRService:
    """
    Service to handle Optical Character Recognition for scanned PDFs.
    """

    def __init__(self, tesseract_path: str = None):
        """
        Initializes the OCR service. 
        If Tesseract is not in the system PATH, tesseract_path must be provided.
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Internal helper to enhance image quality before OCR.
        Converts to grayscale to improve character recognition.
        """
        return image.convert('L')

    def get_text_from_pdf(self, pdf_path: str) -> str:
        """
        Converts all PDF pages to images and extracts their text.
        Returns a single string containing the entire report content.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")

        logger.info(f"Starting OCR processing for: {os.path.basename(pdf_path)}")
        full_text = ""
        
        # Convert PDF pages to list of PIL Images
        # Note: 'poppler' must be installed on the machine for this to work.
        try:
            pages = convert_from_path(pdf_path, dpi=300)
            logger.info(f"Converted PDF to {len(pages)} page(s)")
            
            for idx, page_image in enumerate(pages, 1):
                logger.debug(f"Processing page {idx}/{len(pages)}")
                processed_img = self._preprocess_image(page_image)
                
                # 'heb+eng' tells Tesseract to look for both Hebrew and English characters.
                # --psm 6 assumes a single uniform block of text (good for tables).
                page_text = pytesseract.image_to_string(
                    processed_img, 
                    lang='heb+eng', 
                    config='--psm 6'
                )
                
                logger.debug(f"Extracted {len(page_text)} characters from page {idx}")
                full_text += f"\n--- PAGE START ---\n{page_text}"
            
            logger.info(f"OCR completed. Total text extracted: {len(full_text)} characters")
            return full_text

        except Exception as e:
            logger.error(f"Failed to process PDF via OCR: {str(e)}", exc_info=True)
            raise
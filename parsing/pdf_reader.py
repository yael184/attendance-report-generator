from pdf2image import convert_from_path
import pytesseract



def readPDF(path: str) -> str:

    pages = convert_from_path(path, 300) 


    texts = []
    for page in pages:
        texts.append(pytesseract.image_to_string(page, lang='heb+eng'))

    return "\n".join(texts)

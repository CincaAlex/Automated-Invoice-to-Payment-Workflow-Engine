from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"

def file_check(file_path: Path):
    if not file_path.is_file():
        return False, 1
    if file_path.suffix.lower() != '.pdf':
        return False, 2
    return True, 0

def extract_text_from_pdf(pdf_path: Path):
    try:
        images = convert_from_path(str(pdf_path), poppler_path=POPPLER_PATH)
        extracted_text = ""

        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            extracted_text += f"\n--- Page {i+1} ---\n{text}"

        return extracted_text, None

    except Exception as e:
        return None, f"OCR error: {str(e)}"

def process_invoice(file_path: str):
    file_path = Path(file_path)
    success, code = file_check(file_path)

    if not success:
        return None, f"File check failed (code {code})"

    text, error = extract_text_from_pdf(file_path)
    if error:
        return None, error

    return text, None

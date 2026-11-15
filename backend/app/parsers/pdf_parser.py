import io
from typing import BinaryIO, Union
from pypdf import PdfReader
from app.parsers.text_cleaner import clean_text

def extract_text_from_pdf(file_input: Union[bytes, BinaryIO, str]) -> str:
    """Extract clean text content from PDF file bytes or path."""
    try:
        if isinstance(file_input, bytes):
            reader = PdfReader(io.BytesIO(file_input))
        elif isinstance(file_input, str):
            reader = PdfReader(file_input)
        else:
            reader = PdfReader(file_input)

        extracted_pages = []
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)

        full_text = "\n".join(extracted_pages)
        return clean_text(full_text)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

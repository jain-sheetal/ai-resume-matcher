import io
from typing import BinaryIO, Union
from docx import Document
from app.parsers.text_cleaner import clean_text

def extract_text_from_docx(file_input: Union[bytes, BinaryIO, str]) -> str:
    """Extract clean text content from DOCX file bytes or path including tables."""
    try:
        if isinstance(file_input, bytes):
            doc = Document(io.BytesIO(file_input))
        elif isinstance(file_input, str):
            doc = Document(file_input)
        else:
            doc = Document(file_input)

        lines = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                lines.append(paragraph.text)

        # Also extract table cells if any
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    lines.append(" | ".join(row_cells))

        full_text = "\n".join(lines)
        return clean_text(full_text)
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

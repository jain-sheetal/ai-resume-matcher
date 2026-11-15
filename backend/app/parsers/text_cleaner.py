import re
import unicodedata

def clean_text(text: str) -> str:
    """Normalize extracted text from PDF or DOCX."""
    if not text:
        return ""
    # Normalize unicode (ligatures, curly quotes, accents)
    text = unicodedata.normalize("NFKD", text)
    # Replace non-standard bullets and dashes
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u2013\u2014]', ' - ', text)
    # Replace special whitespaces with regular space
    text = re.sub(r'[\t\r\f\v]', ' ', text)
    # Condense multiple horizontal spaces into single space
    text = re.sub(r'[ ]{2,}', ' ', text)
    # Condense 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

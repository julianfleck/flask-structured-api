from io import BytesIO
from PyPDF2 import PdfReader
import docx
from flask_structured_api.extensions.models.files import FileType


def extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF file"""
    pdf = PdfReader(BytesIO(content))
    return "\n".join(page.extract_text() for page in pdf.pages).strip()


def extract_from_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    doc = docx.Document(BytesIO(content))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def extract_from_file(content: bytes, file_type: FileType) -> str:
    """Extract text based on file type"""
    if file_type == FileType.PDF:
        return extract_from_pdf(content)
    elif file_type in (FileType.DOC, FileType.DOCX):
        return extract_from_docx(content)
    elif file_type in (FileType.TXT, FileType.RTF):
        return content.decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

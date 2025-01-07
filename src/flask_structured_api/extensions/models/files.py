from enum import Enum
from typing import Set
import magic


class FileType(str, Enum):
    """Supported file types for processing"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    RTF = "rtf"

    @classmethod
    def extensions(cls) -> Set[str]:
        """Get all supported extensions"""
        return {t.value for t in cls}

    @classmethod
    def mime_types(cls) -> dict:
        """Get supported MIME types mapping"""
        return {
            'application/pdf': cls.PDF,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': cls.DOCX,
            'application/msword': cls.DOC,
            'text/plain': cls.TXT,
            'application/rtf': cls.RTF,
            'text/rtf': cls.RTF
        }


def detect_file_type(file_content: bytes) -> FileType:
    """Detect file type from content using python-magic"""
    mime = magic.from_buffer(file_content, mime=True)
    try:
        return FileType.mime_types()[mime]
    except KeyError:
        raise ValueError(f"Unsupported MIME type: {mime}")

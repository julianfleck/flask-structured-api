from pathlib import Path
import secrets
import shutil
from datetime import datetime, timedelta
import os
import json
from flask_structured_api.extensions.models.files import FileType, detect_file_type
from flask_structured_api.core.enums import WarningCode, WarningSeverity
from flask_structured_api.core.models.responses import ResponseWarning
from flask_structured_api.core.warnings import WarningCollector


class FileStore:
    def __init__(self, base_path="/tmp/stip_uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.token_length = 32
        self.expiry_hours = 87600  # 10 years

    def store_file(self, file, country_code: str) -> tuple[str, FileType]:
        """Store uploaded file and return token with detected type"""
        warning_collector = WarningCollector()

        # Read and validate file type first
        file_content = file.read()
        file_type = detect_file_type(file_content)

        # Check if extension matches actual file type
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext != file_type.value:
            warning_collector.add_warning(
                code=WarningCode.FILE_TYPE_MISMATCH,
                message="File extension '.{}' does not match actual file type '{}'".format(
                    file_ext, file_type.value),
                severity=WarningSeverity.MEDIUM
            )

        # Create storage path
        country_dir = self.base_path / country_code
        country_dir.mkdir(exist_ok=True)
        token = secrets.token_urlsafe(self.token_length)
        file_path = country_dir / token

        # Store file and metadata
        with open(file_path, 'wb') as f:
            f.write(file_content)

        meta_path = file_path.with_suffix('.meta')
        with open(meta_path, 'w') as f:
            meta = {
                'created': datetime.utcnow().isoformat(),
                'type': file_type.value
            }
            json.dump(meta, f)

        return token, file_type

    def get_file(self, token: str, country_code: str) -> bytes:
        """Retrieve file content by token"""
        file_path = self.base_path / country_code / token
        if not file_path.exists():
            raise FileNotFoundError(f"File not found for token: {token}")

        # Check expiry
        meta_path = file_path.with_suffix('.meta')
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
                created = datetime.fromisoformat(meta['created'])
                if datetime.utcnow() - created > timedelta(hours=self.expiry_hours):
                    self._cleanup_file(file_path)
                    raise ValueError("File token expired")

        with open(file_path, 'rb') as f:
            return f.read()

    def cleanup_expired(self) -> None:
        """Remove expired files"""
        now = datetime.utcnow()
        for country_dir in self.base_path.iterdir():
            if not country_dir.is_dir():
                continue

            for meta_path in country_dir.glob('*.meta'):
                with open(meta_path) as f:
                    created = datetime.fromisoformat(f.read())
                    if now - created > timedelta(hours=self.expiry_hours):
                        self._cleanup_file(meta_path.with_suffix(''))

    def _cleanup_file(self, file_path: Path) -> None:
        """Remove file and its metadata"""
        try:
            file_path.unlink(missing_ok=True)
            file_path.with_suffix('.meta').unlink(missing_ok=True)
        except Exception:
            pass  # Best effort cleanup

    def get_file_type(self, token: str, country_code: str) -> FileType:
        """Get file type from metadata"""
        file_path = self.base_path / country_code / token
        meta_path = file_path.with_suffix('.meta')

        if not meta_path.exists():
            raise FileNotFoundError(
                "Metadata not found for token: {} (country_code: {})".format(token, country_code))

        try:
            with open(meta_path) as f:
                meta = json.load(f)
                return FileType(meta['type'])
        except (json.JSONDecodeError, KeyError):
            # Fallback: re-detect file type from content
            with open(file_path, 'rb') as content_file:
                return detect_file_type(content_file.read())

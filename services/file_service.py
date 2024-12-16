from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename


@dataclass
class FileInfo:
    size: int
    created_at: datetime
    mime_type: str


class FileService:
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(self, content: bytes, filename: str) -> Path:
        file_path = self.base_path / secure_filename(filename)
        file_path.write_bytes(content)
        return file_path

    def get_file_info(self, file_path: Path) -> FileInfo:
        stats = file_path.stat()
        mime_type = self._get_mime_type(file_path)
        if hasattr(stats, "st_birthtime"):
            created_at = datetime.fromtimestamp(stats.st_birthtime)
        created_at = datetime.fromtimestamp(stats.st_ctime)
        return FileInfo(
            size=stats.st_size,
            created_at=created_at,
            mime_type=mime_type,
        )

    def _get_mime_type(self, file_path: Path) -> str:
        extension = file_path.suffix.lower()
        mime_types = {
            ".csv": "text/csv",
            ".json": "application/json",
            ".txt": "text/plain",
        }
        return mime_types.get(extension, "application/octet-stream")

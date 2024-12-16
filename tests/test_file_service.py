from pathlib import Path
import pytest
from services.file_service import FileService


class TestFileService:
    """Pruebas unitarias para FileService usando escuela clásica"""

    # Método de fábrica
    @pytest.fixture
    def file_service(self, tmpdir) -> FileService:
        return FileService(Path(tmpdir))

    def test_save_and_retrieve_file(self, file_service: FileService) -> None:
        # Arrange
        content = b"test content"
        filename = "test.txt"

        # Act
        file_path = file_service.save_file(content, filename)
        file_info = file_service.get_file_info(file_path)

        # Assert
        assert file_path.is_file()
        assert file_path.read_bytes() == content
        assert file_info.size == len(content)
        assert file_info.mime_type == "text/plain"
        # Act
        file_path = file_service.save_file(content, filename)
        file_info = file_service.get_file_info(file_path)

        # Assert
        assert file_path.exists()
        assert file_path.read_bytes() == content
        assert file_info.size == len(content)
        assert file_info.mime_type == "text/plain"

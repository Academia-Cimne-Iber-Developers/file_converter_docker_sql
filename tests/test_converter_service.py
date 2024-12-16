import pytest
from pathlib import Path
from unittest.mock import Mock
from services import (
    ConverterService,
    ValidatorService,
    FileService,
    TransformationService,
)


class TestConverterService:

    @pytest.fixture
    def mock_validator_service(self):
        return Mock(spec=ValidatorService)

    @pytest.fixture
    def mock_file_service(self):
        return Mock(spec=FileService)

    @pytest.fixture
    def mock_transformation_service(self):
        return Mock(spec=TransformationService)

    @pytest.fixture
    def converter_service(
        self,
        mock_validator_service,
        mock_file_service,
        mock_transformation_service,
    ):
        return ConverterService(
            mock_validator_service,
            mock_file_service,
            mock_transformation_service,
        )

    def test_csv_to_json(
        self,
        converter_service,
        mock_validator_service,
        mock_transformation_service,
    ):
        mock_validator_service.validate_csv_structure.return_value.is_valid = (
            True
        )
        mock_validator_service.validate_csv_structure.return_value.errors = []
        mock_transformation_service.normalize_csv_data.return_value = [
            {"name": "John Doe", "city": "New York"}
        ]

        file_path = Mock(spec=Path)
        file_path.read_text.return_value = "name,city\nJohn Doe,New York"

        result = converter_service.csv_to_json(file_path)

        assert result == [{"name": "John Doe", "city": "New York"}]
        mock_validator_service.validate_csv_structure.assert_called_once()
        mock_transformation_service.normalize_csv_data.assert_called_once()

    def test_json_to_csv(
        self,
        converter_service,
        mock_validator_service,
        mock_transformation_service,
    ):
        mock_validator_service.validate_json_structure.return_value.is_valid = (
            True
        )
        mock_validator_service.validate_json_structure.return_value.errors = []
        mock_transformation_service.enrich_json_data.return_value = [
            {"name": "John Doe", "city": "New York"}
        ]

        file_path = Mock(spec=Path)
        file_path.read_text.return_value = (
            '[{"name": "John Doe", "city": "New York"}]'
        )

        result = converter_service.json_to_csv(file_path)

        expected_csv = "name,city\r\nJohn Doe,New York\r\n"
        assert result == expected_csv
        mock_validator_service.validate_json_structure.assert_called_once()
        mock_transformation_service.enrich_json_data.assert_called_once()

from services.validator_service import ValidatorService
import pytest


class TestValidatorService:
    """Pruebas unitarias para ValidatorService usando escuela clásica"""

    @pytest.fixture
    def validator(self) -> ValidatorService:
        return ValidatorService()

    def test_validate_valid_csv_structure(
        self, validator: ValidatorService
    ) -> None:
        # Arrange
        valid_csv = "name,age,city\nJohn,30,New York\nMaria,25,Madrid"

        # Act
        result = validator.validate_csv_structure(valid_csv)

        # Assert
        assert result.is_valid is True
        assert not result.errors

    def test_validate_invalid_csv_structure(
        self, validator: ValidatorService
    ) -> None:
        # Arrange
        invalid_csv = "name,age\nJohn,30,New York\nMaria,25"

        # Act
        result = validator.validate_csv_structure(invalid_csv)

        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "columnas" in result.errors[0]

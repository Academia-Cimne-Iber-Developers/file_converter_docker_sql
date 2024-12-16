import pytest
from pathlib import Path
from app import create_app
import json
import io


class TestFlaskApp:
    """Pruebas unitarias para la aplicación Flask"""

    @pytest.fixture
    def app(self, tmpdir):
        """Fixture que proporciona la aplicación Flask configurada para pruebas"""
        config = {"TESTING": True, "UPLOAD_FOLDER": str(tmpdir)}
        app = create_app(config)
        return app

    @pytest.fixture
    def client(self, app):
        """Fixture que proporciona un cliente de prueba"""
        return app.test_client()

    def test_health_check(self, client):
        """Prueba el endpoint de health check"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json == {"status": "healthy"}

    def test_csv_to_json_endpoint(self, client):
        """Prueba el endpoint de conversión CSV a JSON"""
        # Arrange
        csv_content = b"name,age,city\nJohn,30,New York\nMaria,25,Madrid"
        data = {"file": (io.BytesIO(csv_content), "test.csv")}

        # Act
        response = client.post(
            "/api/v1/convert/csv-to-json",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert
        assert response.status_code == 200
        assert "data" in response.json
        assert len(response.json["data"]) == 2
        assert response.json["data"][0]["name"] == "John"

    def test_json_to_csv_endpoint(self, client):
        """Prueba el endpoint de conversión JSON a CSV"""
        # Arrange
        json_content = json.dumps(
            [
                {"name": "John", "age": "30", "city": "New York"},
                {"name": "Maria", "age": "25", "city": "Madrid"},
            ]
        ).encode()
        data = {"file": (io.BytesIO(json_content), "test.json")}

        # Act
        response = client.post(
            "/api/v1/convert/json-to-csv",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["Content-Type"].startswith("text/csv")
        assert "attachment" in response.headers["Content-Disposition"]

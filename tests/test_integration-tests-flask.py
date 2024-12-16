import pytest
from pathlib import Path
import json
import csv
import io
from flask import Flask
from flask.testing import FlaskClient


class TestSystemIntegration:
    """
    Pruebas de integración del sistema completo.
    Estas pruebas verifican la interacción entre múltiples componentes
    y el flujo de datos a través de toda la aplicación.
    """

    @pytest.fixture
    def app(self, tmpdir) -> Flask:
        """Fixture que configura la aplicación con todos sus componentes"""
        config = {
            "TESTING": True,
            "UPLOAD_FOLDER": str(tmpdir),
            "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,
        }
        from app import create_app  # Importamos la factory de la app

        return create_app(config)

    @pytest.fixture
    def client(self, app: Flask) -> FlaskClient:
        return app.test_client()

    def test_complete_conversion_cycle(self, client: FlaskClient) -> None:
        """
        Prueba de integración del ciclo completo de conversión:
        CSV -> JSON -> CSV
        Verifica que los datos se mantienen consistentes a través de múltiples conversiones
        """
        # Arrange
        initial_csv = (
            "name,age,city\n"
            "John Doe,30,NEW YORK\n"
            "Jane Smith,25,LOS ANGELES"
        ).encode("utf-8")

        # Act - Primera conversión: CSV a JSON
        csv_response = client.post(
            "/api/v1/convert/csv-to-json",
            data={"file": (io.BytesIO(initial_csv), "initial.csv")},
            content_type="multipart/form-data",
        )

        # Verificación intermedia
        assert csv_response.status_code == 200
        json_data = csv_response.json["data"]

        # Act - Segunda conversión: JSON a CSV
        json_content = json.dumps(json_data).encode("utf-8")
        csv_conversion = client.post(
            "/api/v1/convert/json-to-csv",
            data={"file": (io.BytesIO(json_content), "converted.json")},
            content_type="multipart/form-data",
        )

        # Assert
        assert csv_conversion.status_code == 200
        final_csv = csv_conversion.data.decode("utf-8").strip()

        # Verificar que los datos se mantienen consistentes
        final_csv_rows = list(csv.DictReader(final_csv.splitlines()))
        assert len(final_csv_rows) == 2
        assert final_csv_rows[0]["name"] == "John Doe"
        assert (
            final_csv_rows[0]["city"] == "New York"
        )  # Verifica normalización
        assert (
            final_csv_rows[1]["city"] == "Los Angeles"
        )  # Verifica normalización

    def test_error_propagation_through_layers(
        self, client: FlaskClient
    ) -> None:
        """
        Prueba cómo los errores se propagan a través de las diferentes capas del sistema:
        API -> Service -> Validation -> Service -> API Response
        """
        # Arrange - CSV con estructura inválida
        invalid_csv = (
            "name,age\n"
            "John,30,extra_column\n"  # Más columnas que headers
            "Jane,25"  # Menos columnas que headers
        ).encode("utf-8")

        # Act
        response = client.post(
            "/api/v1/convert/csv-to-json",
            data={"file": (io.BytesIO(invalid_csv), "invalid.csv")},
            content_type="multipart/form-data",
        )

        # Assert
        assert response.status_code == 400
        assert "error" in response.json
        assert "columnas" in response.json["error"]

    def test_concurrent_file_handling(self, client: FlaskClient) -> None:
        """
        Prueba el manejo concurrente de archivos y recursos del sistema.
        Verifica que múltiples conversiones simultáneas no interfieren entre sí.
        """
        import concurrent.futures

        # Arrange
        test_files = [
            ("name,age\nPerson1,30\n", "file1.csv"),
            ("name,age\nPerson2,25\n", "file2.csv"),
            ("name,age\nPerson3,35\n", "file3.csv"),
        ]

        def make_request(file_data):
            content, filename = file_data
            return client.post(
                "/api/v1/convert/csv-to-json",
                data={"file": (io.BytesIO(content.encode()), filename)},
                content_type="multipart/form-data",
            )

        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            responses = list(executor.map(make_request, test_files))

        # Assert
        for response in responses:
            assert response.status_code == 200
            assert len(response.json["data"]) == 1

    def test_system_resource_cleanup(
        self, client: FlaskClient, app: Flask
    ) -> None:
        """
        Prueba que el sistema limpia correctamente los recursos después de las operaciones.
        Verifica que no quedan archivos temporales después de las conversiones.
        """
        # Arrange
        upload_folder = Path(app.config["UPLOAD_FOLDER"])
        initial_files = set(upload_folder.glob("*"))

        # Act - Realizar una serie de conversiones
        test_data = "name,age\nJohn,30"
        for _ in range(3):
            response = client.post(
                "/api/v1/convert/csv-to-json",
                data={"file": (io.BytesIO(test_data.encode()), "test.csv")},
                content_type="multipart/form-data",
            )
            assert response.status_code == 200

        # Assert
        final_files = set(upload_folder.glob("*"))
        assert (
            final_files == initial_files
        )  # No deben quedar archivos temporales

    def test_data_transformation_consistency(
        self, client: FlaskClient
    ) -> None:
        """
        Prueba la consistencia en las transformaciones de datos a través del sistema.
        Verifica que las normalizaciones y enriquecimientos se aplican correctamente
        en diferentes situaciones.
        """
        # Arrange
        test_cases = [
            # Caso 1: Normalización de ciudades - verificamos nombres y ciudades
            (
                "name,city\nJohn,NEW YORK\nJane,LOS ANGELES",
                ["John", "Jane"],  # Nombres sin normalizar
                ["New York", "Los Angeles"],  # Ciudades normalizadas
            ),
            # Caso 2: Espacios extras - verificamos nombres con espacios normalizados
            (
                "name,age\n John  ,30 \n Jane , 25",
                ["John", "Jane"],
                None,  # No verificamos ciudades
            ),
            # Caso 3: Campos mixtos - verificamos nombres en formato mixto
            (
                "name,city,age\nJOHN DOE,MIAMI,30\nJane Smith,chicago,25",
                ["JOHN DOE", "Jane Smith"],  # Nombres no se normalizan
                ["Miami", "Chicago"],  # Ciudades sí se normalizan
            ),
        ]

        for csv_content, expected_names, expected_cities in test_cases:
            # Act
            response = client.post(
                "/api/v1/convert/csv-to-json",
                data={"file": (io.BytesIO(csv_content.encode()), "test.csv")},
                content_type="multipart/form-data",
            )

            # Assert
            assert response.status_code == 200
            result = response.json["data"]

            # Verificar nombres
            assert [r["name"] for r in result] == expected_names

            # Verificar ciudades si se espera verificarlas
            if expected_cities is not None:
                assert [r["city"] for r in result] == expected_cities

    def test_api_content_negotiation(self, client: FlaskClient) -> None:
        """
        Prueba la negociación de contenido de la API, verificando
        que el sistema maneja correctamente diferentes tipos de contenido
        y produce las respuestas apropiadas.
        """
        # Arrange
        json_data = [{"name": "John", "age": "30"}]

        # Test Case 1: JSON a CSV
        response_csv = client.post(
            "/api/v1/convert/json-to-csv",
            data={
                "file": (
                    io.BytesIO(json.dumps(json_data).encode()),
                    "test.json",
                )
            },
            content_type="multipart/form-data",
        )
        assert response_csv.headers["Content-Type"].startswith("text/csv")
        assert "attachment" in response_csv.headers["Content-Disposition"]

        # Test Case 2: CSV a JSON
        csv_data = "name,age\nJohn,30"
        response_json = client.post(
            "/api/v1/convert/csv-to-json",
            data={"file": (io.BytesIO(csv_data.encode()), "test.csv")},
            content_type="multipart/form-data",
        )
        assert response_json.headers["Content-Type"] == "application/json"

    def test_large_file_processing_integration(
        self, client: FlaskClient
    ) -> None:
        """
        Prueba el procesamiento de archivos grandes a través de todo el sistema,
        verificando el rendimiento y la gestión de memoria.
        """
        # Arrange
        # Generar un CSV grande (1000 registros)
        large_csv = "name,age,city\n" + "\n".join(
            f"Person{i},30,City{i}" for i in range(1000)
        )

        # Act
        response = client.post(
            "/api/v1/convert/csv-to-json",
            data={"file": (io.BytesIO(large_csv.encode()), "large.csv")},
            content_type="multipart/form-data",
        )

        # Assert
        assert response.status_code == 200
        result = response.json["data"]
        assert len(result) == 1000

        # Verificar que la respuesta mantiene la estructura esperada
        first_record = result[0]
        last_record = result[-1]
        assert all(key in first_record for key in ["name", "age", "city"])
        assert first_record["name"] == "Person0"
        assert last_record["name"] == "Person999"


if __name__ == "__main__":
    pytest.main(["-v"])

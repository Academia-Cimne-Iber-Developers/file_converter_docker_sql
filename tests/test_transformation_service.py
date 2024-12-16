import pytest
from datetime import datetime
from services import TransformationService


class TestTransformationService:
    @pytest.fixture
    def sample_data(self):
        return [
            {
                "name": "john doe",
                "city": "new york",
                "country": "usa",
                "state": "ny",
            },
            {
                "name": "jane smith",
                "city": "los angeles",
                "country": "usa",
                "state": "ca",
            },
        ]

    def test_normalize_data(self, sample_data):
        service = TransformationService()
        normalized_data = service.normalize_csv_data(sample_data)

        assert normalized_data == [
            {
                "name": "john doe",
                "city": "New York",
                "country": "Usa",
                "state": "Ny",
            },
            {
                "name": "jane smith",
                "city": "Los Angeles",
                "country": "Usa",
                "state": "Ca",
            },
        ]

    def test_enrich_json_data(self, sample_data):
        service = TransformationService()
        enriched_data = service.enrich_json_data(sample_data)

        assert len(enriched_data) == 2
        assert enriched_data[0]["record_id"] == "REC-0001"
        assert enriched_data[1]["record_id"] == "REC-0002"
        assert "processed_at" in enriched_data[0]
        assert "processed_at" in enriched_data[1]
        assert datetime.fromisoformat(enriched_data[0]["processed_at"])
        assert datetime.fromisoformat(enriched_data[1]["processed_at"])

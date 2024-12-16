from typing import List, Dict
from datetime import datetime


class TransformationService:
    def normalize_csv_data(self, data: List[Dict]) -> List[Dict]:
        normalized = []
        for row in data:
            normalized_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    # Primero guardamos el valor original
                    normalized_value = value.strip()

                    # Solo aplicamos Title() a campos de ubicación
                    if key.lower() in ["city", "country", "state"]:
                        normalized_value = normalized_value.title()
                    # Para nombres, mantenemos el formato original
                    elif key.lower() == "name":
                        normalized_value = normalized_value

                    normalized_row[key] = normalized_value
                else:
                    normalized_row[key] = value
            normalized.append(normalized_row)
        return normalized

    def enrich_json_data(self, data: List[Dict]) -> List[Dict]:
        enriched = []
        for i, row in enumerate(data):
            enriched_row = row.copy()
            enriched_row["record_id"] = f"REC-{i+1:04d}"
            enriched_row["processed_at"] = datetime.now().isoformat()
            enriched.append(enriched_row)
        return enriched

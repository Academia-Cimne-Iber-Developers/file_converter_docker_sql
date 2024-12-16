from dataclasses import dataclass
from typing import List
import csv
import json


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]


class ValidatorService:
    def validate_csv_structure(self, content: str) -> ValidationResult:
        try:
            lines = content.strip().split("\n")
            if not lines:
                return ValidationResult(False, ["Archivo vacío"])

            reader = csv.reader(lines)
            headers = next(reader)
            if not headers:
                return ValidationResult(
                    False, ["No se encontraron encabezados en el CSV"]
                )

            for i, row in enumerate(reader, 1):
                if len(row) != len(headers):
                    return ValidationResult(
                        False,
                        [f"Número inconsistente de columnas en la línea {i}"],
                    )
            return ValidationResult(True, [])
        except Exception as e:
            return ValidationResult(False, [str(e)])

    def validate_json_structure(self, content: str) -> ValidationResult:
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                return ValidationResult(
                    False, ["JSON must be a list of objects"]
                )
            if not data:
                return ValidationResult(False, ["Empty JSON list"])

            if not all(isinstance(item, dict) for item in data):
                return ValidationResult(False, ["All items must be objects"])

            return ValidationResult(True, [])
        except json.JSONDecodeError:
            return ValidationResult(False, ["Invalid JSON format"])

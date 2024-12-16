from pathlib import Path
import csv
import json
import io
from typing import Dict, List
from .validator_service import ValidatorService
from .file_service import FileService
from .transformation_service import TransformationService


class ConverterService:
    def __init__(
        self,
        validator_service: ValidatorService,
        file_service: FileService,
        transformation_service: TransformationService,
    ):
        self.validator_service = validator_service
        self.file_service = file_service
        self.transformation_service = transformation_service

    def csv_to_json(self, file_path: Path) -> List[Dict]:
        content = file_path.read_text()
        validation = self.validator_service.validate_csv_structure(content)
        if not validation.is_valid:
            raise ValueError(validation.errors[0])

        reader = csv.DictReader(content.splitlines())
        data = list(reader)
        return self.transformation_service.normalize_csv_data(data)

    def json_to_csv(self, file_path: Path) -> str:
        content = file_path.read_text()
        validation = self.validator_service.validate_json_structure(content)
        if not validation.is_valid:
            raise ValueError(validation.errors[0])

        data = json.loads(content)
        enriched_data = self.transformation_service.enrich_json_data(data)

        if not enriched_data:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=enriched_data[0].keys())
        writer.writeheader()
        writer.writerows(enriched_data)
        return output.getvalue()

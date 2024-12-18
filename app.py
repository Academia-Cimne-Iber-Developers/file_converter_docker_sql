from pathlib import Path
from flask import Flask, request, jsonify, send_file
import io
import time
from services import (
    FileService,
    ValidatorService,
    TransformationService,
    ConverterService,
    DatabaseService,
)
from config import Config


def create_app(config: dict = None) -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    if config:
        app.config.update(config)

    # Initialize services
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    validator_service = ValidatorService()
    file_service = FileService(upload_path)
    transformation_service = TransformationService()
    database_service = DatabaseService(
        host=app.config["DB_HOST"],
        user=app.config["DB_USER"],
        port=app.config["DB_PORT"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        port=app.config["DB_PORT"],
    )
    converter_service = ConverterService(
        validator_service, file_service, transformation_service
    )

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"})

    @app.route("/api/v1/convert/csv-to-json", methods=["POST"])
    def convert_csv_to_json():
        start_time = time.time()
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.endswith(".csv"):
            return jsonify({"error": "Unsupported file type"}), 400

        try:
            file_content = file.read()
            file_size = len(file_content)
            file_path = file_service.save_file(file_content, file.filename)
            result = converter_service.csv_to_json(file_path)

            processing_time = time.time() - start_time
            database_service.log_conversion(
                ip=request.remote_addr,
                source_format="csv",
                target_format="json",
                file_size=file_size,
                processing_time=processing_time,
                status="success",
                error_message=None,
            )

            return jsonify(
                {"data": result, "message": "Conversion successful"}
            )
        except ValueError as e:
            processing_time = time.time() - start_time
            database_service.log_conversion(
                ip=request.remote_addr,
                source_format="csv",
                target_format="json",
                file_size=file_size if "file_size" in locals() else 0,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )
            return jsonify({"error": str(e)}), 400
        finally:
            if "file_path" in locals():
                file_path.unlink(missing_ok=True)

    @app.route("/api/v1/convert/json-to-csv", methods=["POST"])
    def convert_json_to_csv():
        start_time = time.time()
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "Unsupported file type"}), 400

        try:
            file_content = file.read()
            file_size = len(file_content)
            file_path = file_service.save_file(file_content, file.filename)
            result = converter_service.json_to_csv(file_path)

            processing_time = time.time() - start_time
            database_service.log_conversion(
                ip=request.remote_addr,
                source_format="json",
                target_format="csv",
                file_size=file_size,
                processing_time=processing_time,
                status="success",
                error_message=None,
            )

            output = io.BytesIO(result.encode("utf-8"))
            return send_file(
                output,
                mimetype="text/csv",
                as_attachment=True,
                download_name="converted.csv",
            )

        except ValueError as e:
            processing_time = time.time() - start_time
            database_service.log_conversion(
                ip=request.remote_addr,
                source_format="json",
                target_format="csv",
                file_size=file_size if "file_size" in locals() else 0,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )
            return jsonify({"error": str(e)}), 400
        finally:
            if "file_path" in locals():
                file_path.unlink(missing_ok=True)

    @app.route("/api/v1/conversions/history")
    def get_conversion_history():
        limit = request.args.get("limit", default=100, type=int)
        history = database_service.get_conversion_history(limit=limit)
        return jsonify(
            {
                "data": [
                    {
                        **log,
                        "created_at": (
                            log["created_at"].isoformat()
                            if log["created_at"]
                            else None
                        ),
                    }
                    for log in history
                ]
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

from pathlib import Path
from flask import Flask, request, jsonify, send_file, make_response
from asgiref.wsgi import WsgiToAsgi
import io
from services import (
    FileService,
    ValidatorService,
    TransformationService,
    ConverterService,
)


def create_app(config: dict = None) -> Flask:
    app = Flask(__name__)

    # Default configuration
    app.config.update(
        {
            "UPLOAD_FOLDER": "uploads",
            "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16MB max-limit
        }
    )

    if config:
        app.config.update(config)

    # Initialize services
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    validator_service = ValidatorService()
    file_service = FileService(upload_path)
    transformation_service = TransformationService()
    converter_service = ConverterService(
        validator_service, file_service, transformation_service
    )

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"})

    @app.route("/api/v1/convert/csv-to-json", methods=["POST"])
    def convert_csv_to_json():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.endswith(".csv"):
            return jsonify({"error": "Unsupported file type"}), 400

        try:
            file_path = file_service.save_file(file.read(), file.filename)
            result = converter_service.csv_to_json(file_path)
            return jsonify({"data": result, "message": "Conversion successful"})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        finally:
            if "file_path" in locals():
                file_path.unlink(missing_ok=True)

    @app.route("/api/v1/convert/json-to-csv", methods=["POST"])
    def convert_json_to_csv():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "Unsupported file type"}), 400

        try:
            file_path = file_service.save_file(file.read(), file.filename)
            result = converter_service.json_to_csv(file_path)

            output = io.BytesIO(result.encode("utf-8"))

            return send_file(
                output,
                mimetype="text/csv",
                as_attachment=True,
                download_name="converted.csv",
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        finally:
            if "file_path" in locals():
                file_path.unlink(missing_ok=True)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from flask_structured_api.core.auth import require_auth
from flask_structured_api.core.models.responses import SuccessResponse, ErrorResponse
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.api.custom.decorators import validate_country_code
from flask_structured_api.extensions.models.files import FileType

bp = Blueprint('stip_upload', __name__)


@bp.route('/<country_code>/upload', methods=['POST', 'OPTIONS'])
def upload_file(country_code: str):
    """Upload a file for processing"""
    # Let CORS middleware handle OPTIONS requests
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        if 'file' not in request.files:
            raise ValueError("No file part in the request")

        file = request.files['file']
        if file.filename == '':
            raise ValueError("No selected file")

        # Basic extension check first
        if not file.filename.rsplit('.', 1)[1].lower() in FileType.extensions():
            raise ValueError("File type not allowed. Supported types: {}".format(
                ', '.join(FileType.extensions())))

        if not hasattr(current_app, 'file_store'):
            raise ValueError("File store not initialized")

        # Store and validate file
        token, file_type = current_app.file_store.store_file(file, country_code)

        return jsonify(SuccessResponse(data={
            'file_token': token,
            'filename': secure_filename(file.filename),
            'type': file_type.value
        }).model_dump()), 200

    except ValueError as e:
        return jsonify(ErrorResponse(
            message="Failed to upload file",
            error=ErrorDetail(
                code="FILE_UPLOAD_ERROR",
                details={"error": str(e)}
            ),
            status=400
        ).model_dump()), 400

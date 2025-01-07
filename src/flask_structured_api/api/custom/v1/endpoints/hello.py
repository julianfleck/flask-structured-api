from flask import Blueprint, request, current_app, jsonify
from flask_structured_api.core.models.responses import SuccessResponse, ErrorResponse
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.models.requests.ai import AICompletionRequest, AIMessage
from flask_structured_api.core.middleware.logging import log_ai_request, log_ai_response
from flask_structured_api.core.auth import require_auth
from flask_structured_api.core.config import settings

bp = Blueprint("hello", __name__)


@bp.route("/hello", methods=["POST"])
@require_auth
@log_ai_request
@log_ai_response
async def hello():
    """Async endpoint that uses AI service to generate a greeting"""
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify(ErrorResponse(
            message="Name is required",
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                details={"field": "name", "error": "Missing required field"}
            )
        ).model_dump()), 400

    # Create AI request
    ai_request = AICompletionRequest(
        messages=[
            AIMessage(
                role="system", content="You are a friendly greeter. Generate creative and warm greetings."),
            AIMessage(role="user", content=f"Generate a creative greeting for {name}")
        ],
        temperature=0.7,
        max_tokens=100,
        response_schema={
            "type": "object",
            "properties": {
                "greeting": {"type": "string"}
            },
            "required": ["greeting"]
        }
    )

    # Get response from AI service
    response = await current_app.ai_service.complete(
        request=ai_request,
        response_schema=ai_request.response_schema
    )

    current_app.ai_logger.info(f"AI response: {response}")

    response_data = SuccessResponse(
        data={"greeting": response.content["data"]["greeting"]},
        message=response.content.get("message", "Greeting generated successfully"),
        metadata=response.metadata
    ).model_dump()

    # Convert to a Flask response object to add headers
    flask_response = jsonify(response_data)
    flask_response.headers['X-API-Version'] = settings.API_VERSION
    flask_response.headers['X-Response-Time'] = str(
        response.metadata.get('response_time', ''))

    return flask_response

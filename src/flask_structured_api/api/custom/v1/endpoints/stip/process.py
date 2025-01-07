from flask import Blueprint, current_app, request, jsonify
from flask_structured_api.api.custom.decorators import validate_country_code
from flask_structured_api.core.auth import require_auth
from flask_structured_api.core.middleware.logging import debug_request, debug_response
from flask_structured_api.core.models.errors import ErrorDetail
from flask_structured_api.core.models.responses import ErrorResponse, SuccessResponse
from flask_structured_api.core.storage.decorators import store_api_data
from flask_structured_api.extensions.schemas.stip import InitiativeRequest
from flask_structured_api.extensions.models.stip import ProcessedInitiative

bp = Blueprint("stip_process", __name__)


@bp.route("/<country_code>/process", methods=["POST", "OPTIONS"])
@debug_request
@require_auth
@validate_country_code
@store_api_data(ttl_days=365)
@debug_response
async def process_initiatives(country_code: str):
    try:
        raw_data = request.get_json()
        current_app.logger.info("Processing request")
        current_app.logger.debug("Data: {}".format(raw_data))

        # For file processing, log the input type
        if raw_data.get('input_type') == 'file':
            current_app.logger.info("Processing request with file token: {}".format(
                raw_data.get('content')))

        one_shot = bool(raw_data.pop("one-shot", False))

        # Convert single prompt to list
        if "prompts" in raw_data and isinstance(raw_data["prompts"], str):
            raw_data["prompts"] = [raw_data["prompts"]]

        data = InitiativeRequest(**raw_data)
        processor = current_app.stip_processor

        result = await processor.process_initiative(
            content=data.content,
            initiative_name=data.initiative_name,
            input_type=data.input_type,
            prompts=data.prompts,
            country_code=country_code,
            one_shot=one_shot
        )

        if isinstance(result, ErrorResponse):
            current_app.logger.error(
                "AI processing returned an error",
                extra={
                    "error": result.error.model_dump(),
                    "country_code": country_code,
                    "input_type": data.input_type,
                    "initiative_name": data.initiative_name,
                    "one_shot": one_shot,
                    "success": False
                }
            )
            return result.to_response(status_code=500)

        # Convert SuccessResponse to dict for ProcessedInitiative
        result_dict = {
            "data": result.data,
            "message": result.message,
            "metadata": result.metadata,
            "warnings": result.warnings
        }

        processed = ProcessedInitiative.from_ai_response(
            response=result_dict,  # Pass the dict instead of SuccessResponse object
            url=data.content if data.input_type == "url" else "",
            initiative_name=data.initiative_name,
            country_code=country_code
        )

        processed_dict = processed.model_dump()
        metadata = processed_dict.pop("metadata", {})

        current_app.logger.info(
            "Successfully processed initiative",
            # extra={
            #     "country_code": country_code,
            #     "data": processed_dict,
            #     "input_type": data.input_type,
            #     "initiative_name": data.initiative_name,
            #     "one_shot": one_shot,
            #     "success": True,
            #     "metadata": metadata
            # }
        )

        response = SuccessResponse(
            data=processed_dict,
            message="Successfully processed initiative",
            metadata=metadata
        ).to_response(status_code=200)

        current_app.logger.debug(
            "Final response created",
            extra={
                "response_type": type(response).__name__,
                "headers": dict(response.headers) if hasattr(response, "headers") else {},
                "status_code": getattr(response, "status_code", 200)
            }
        )

        return response

    except Exception as e:
        # Get traceback info
        import traceback
        tb = traceback.format_exc()

        # Log detailed error information
        current_app.logger.error(
            f"Error in process_initiatives: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": tb,
                "input_type": raw_data.get('input_type') if 'raw_data' in locals() else None,
                "content": raw_data.get('content') if 'raw_data' in locals() else None,
                "initiative_name": raw_data.get('initiative_name') if 'raw_data' in locals() else None,
                "country_code": country_code,
                "success": False,
                "request_id": getattr(request, 'request_id', None),
                "user_id": getattr(request, 'user_id', None),
                "endpoint": request.endpoint,
                "method": request.method,
                "path": request.path,
                "headers": dict(request.headers),
            },
            exc_info=True  # This includes the full traceback
        )

        return ErrorResponse(
            message="Failed to process initiative",
            error=ErrorDetail(
                code="STIP_PROCESSING_ERROR",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ),
        ).to_response(status_code=500)

from typing import Dict, Any, Optional, List, Union, get_origin, get_args, Literal, Type
from flask_structured_api.extensions.prompts import STIP_PROMPTS, PromptExcelManager
from flask_structured_api.extensions.prompts.base import STIPPrompt, CombinedSTIPPrompt
from flask_structured_api.core.models.requests.ai import AICompletionRequest
from flask_structured_api.core.models.errors.ai import AIResponseValidationError
from flask_structured_api.core.enums import AIErrorCode, WarningCode, WarningSeverity
from flask_structured_api.core.models.responses import ErrorResponse, SuccessResponse
from flask_structured_api.core.models.errors.base import ErrorDetail
import logging
from flask import current_app
import json
from pydantic import BaseModel
from pydantic.fields import FieldInfo

ai_logger = logging.getLogger("ai")


class AIProcessor:
    """Handles all AI-related processing tasks"""

    def __init__(self, prompt_path: Optional[str] = None):
        self.prompts = self._initialize_prompts(prompt_path)

    def _initialize_prompts(self, prompt_path: Optional[str] = None) -> Dict:
        """Initialize prompts from Excel if available, otherwise use defaults"""
        if prompt_path:
            # Excel loading will be implemented later
            ai_logger.warning(
                "Excel prompt loading not yet implemented, using defaults")
        return STIP_PROMPTS

    async def process_prompt(self, prompt_type: str, text: str, initiative_name: str) -> Union[ErrorResponse, SuccessResponse]:
        """Process a single prompt and return the AI response with metadata"""
        if prompt_type not in self.prompts:
            raise ValueError("Unknown prompt type: {}".format(prompt_type))

        prompt = self.prompts[prompt_type]
        completion_request = prompt.to_completion_request(
            initiative_name=initiative_name,
            # TODO: Remove this once we have a better way to handle long text
            text=text
        )

        ai_request = AICompletionRequest(
            messages=completion_request["messages"],
            temperature=completion_request["temperature"],
            max_tokens=completion_request["max_tokens"],
            response_schema=completion_request["response_schema"]
        )

        response = await current_app.ai_service.complete(
            request=ai_request,
            response_schema=ai_request.response_schema
        )

        if isinstance(response.content["data"], dict) and "$schema" in response.content["data"]:
            ai_logger.warning(
                "Got schema instead of data for {}, requesting again...".format(prompt_type))

            validation_error = AIResponseValidationError(
                code=AIErrorCode.VALIDATION_ERROR,
                validation_errors=[{
                    "error": "AI returned schema instead of data",
                    "field": "data",
                }],
                raw_response=response.content,
                provider="openai",
                confidence=response.content.get("confidence", 0)
            )

            return ErrorResponse(
                message="AI returned schema instead of data",
                error=ErrorDetail(
                    code=validation_error.code,
                    details={
                        "validation_errors": validation_error.validation_errors,
                        "raw_response": response.content,
                        "provider": validation_error.provider,
                        "confidence": validation_error.confidence,
                        "metadata": response.metadata
                    }
                )
            )

        return SuccessResponse(
            data={
                "data": response.content["data"],
                "metadata": {
                    "confidence": response.metadata.get("confidence"),
                    "performance": response.metadata.get("performance"),
                    "usage": response.metadata.get("usage"),
                    # "schema": {
                    #     "used": bool(response.metadata.get("schema")),
                    #     "definition": response.metadata.get("schema")
                    # } if response.metadata.get("schema") else None,
                    # "reference_data": prompt.reference_data
                }
            },
            message=f"Successfully processed {prompt_type} prompt",
            metadata=response.metadata
        )

    async def process_all_prompts(self, text: str, initiative_name: str) -> Union[ErrorResponse, SuccessResponse]:
        """Process text with all available prompts"""
        return await self._process_multiple_prompts(self.prompts.keys(), text, initiative_name)

    async def process_selected_prompts(self, prompt_types: List[str], text: str, initiative_name: str) -> Union[ErrorResponse, SuccessResponse]:
        """Process text with selected prompts"""
        return await self._process_multiple_prompts(prompt_types, text, initiative_name)

    async def _process_multiple_prompts(self, prompt_types: List[str], text: str, initiative_name: str) -> Union[ErrorResponse, SuccessResponse]:
        """Internal method to process multiple prompts and aggregate results"""
        results = {}
        total_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        total_performance = {
            "total_duration": 0,
            "tokens_per_second": 0
        }

        for prompt_type in prompt_types:
            response = await self.process_prompt(prompt_type, text, initiative_name)
            if isinstance(response, ErrorResponse):
                return response

            results[prompt_type] = response.data

            # Sum up usage
            usage = response.metadata.get("usage", {})
            total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total_usage["completion_tokens"] += usage.get("completion_tokens", 0)

            # Sum up performance
            performance = response.metadata.get("performance", {})
            total_performance["total_duration"] += performance.get("total_duration", 0)
            # We'll calculate the average tokens/sec at the end

        # Calculate final values
        total_usage["total_tokens"] = total_usage["prompt_tokens"] + \
            total_usage["completion_tokens"]
        if total_performance["total_duration"] > 0:
            total_performance["tokens_per_second"] = total_usage["total_tokens"] / \
                total_performance["total_duration"]

        total_cost = (
            (total_usage["prompt_tokens"] * 0.0015 / 1000) +
            (total_usage["completion_tokens"] * 0.002 / 1000)
        )

        return SuccessResponse(
            data=results,
            message="Successfully processed prompts",
            metadata={
                "total_cost": total_cost,
                "total_usage": total_usage,
                "total_performance": total_performance
            }
        )

    async def process_one_shot(self, prompt_types: List[str], text: str, initiative_name: str) -> Union[ErrorResponse, SuccessResponse]:
        """Process multiple prompts in a single AI call using CombinedSTIPPrompt"""
        current_app.logger.debug(
            "Starting one-shot processing with text length: {}".format(len(text))
        )
        current_app.logger.debug("Text preview: {}...".format(text[:200]))

        # If no prompts specified, use all available prompts
        if not prompt_types:
            prompt_types = list(self.prompts.keys())

        # Validate prompts and collect them
        dimension_prompts = {}
        for prompt_type in prompt_types:
            if prompt_type not in self.prompts:
                raise ValueError("Unknown prompt type: {}".format(prompt_type))
            dimension_prompts[prompt_type] = self.prompts[prompt_type]

        # Create combined prompt
        combined_prompt = CombinedSTIPPrompt(
            name="one_shot_combined",
            description="Combined analysis of multiple aspects",
            dimensions=dimension_prompts
        )

        # Create and send request
        completion_request = combined_prompt.to_completion_request(
            initiative_name=initiative_name,
            text=text
        )

        ai_request = AICompletionRequest(
            messages=completion_request["messages"],
            temperature=completion_request["temperature"],
            max_tokens=completion_request["max_tokens"],
            response_schema=completion_request["response_schema"]
        )

        response = await current_app.ai_service.complete(
            request=ai_request,
            response_schema=ai_request.response_schema
        )

        # Calculate cost
        usage = response.metadata.get("usage", {})
        total_cost = (
            (usage.get("prompt_tokens", 0) * 0.0015 / 1000) +
            (usage.get("completion_tokens", 0) * 0.002 / 1000)
        )

        return SuccessResponse(
            data=response.content["data"],
            message="Successfully processed one-shot combined prompt",
            metadata={
                "confidence": response.metadata.get("confidence"),
                "usage": response.metadata.get("usage"),
                "performance": response.metadata.get("performance"),
                "total_cost": total_cost,
            }
        )

    def _organize_reference_data(self, prompt_types: List[str]) -> Dict:
        """Organizes reference data by dimension."""
        organized_data = {}
        for prompt_type in prompt_types:
            prompt = self.prompts[prompt_type]
            if prompt.reference_data:
                organized_data[prompt_type] = prompt.reference_data
        return organized_data

    def _add_cross_reference_instructions(self, system_message: str) -> str:
        """Adds cross-reference instructions to the system message."""
        return system_message + """
IMPORTANT:
- Maintain consistency across all analysis dimensions
- Cross-reference related information between dimensions
- If you identify conflicts between dimensions, explicitly note them
- Ensure numerical data (budgets, dates, etc.) is consistent throughout the analysis
"""

    async def _validate_one_shot_response(self, response_data: Dict, prompt_types: List[str]) -> List[Dict]:
        """Validates the one-shot response for consistency."""
        warnings = []

        # Check for consistency across dimensions
        budget_amounts = set()
        dates = set()

        for dimension in response_data:
            if "budget_items" in response_data[dimension]:
                budget_amounts.update(item["amount"]
                                      for item in response_data[dimension]["budget_items"])
            if "start_date" in response_data[dimension]:
                dates.add(response_data[dimension]["start_date"].get("date"))

        if len(budget_amounts) > 1:
            warnings.append({
                "type": "consistency",
                "severity": WarningSeverity.HIGH,
                "message": "Inconsistent budget amounts across dimensions: {}".format(budget_amounts)
            })

        if len(dates) > 1:
            warnings.append({
                "type": "consistency",
                "severity": WarningSeverity.HIGH,
                "message": "Inconsistent dates across dimensions: {}".format(dates)
            })

        return warnings


def _clean_pydantic_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up Pydantic's schema output for OpenAI consumption"""
    if not isinstance(schema, dict):
        return {"type": "string"}  # fallback for non-dict schemas

    keys_to_remove = ['title', 'definitions', '$defs']
    for key in keys_to_remove:
        schema.pop(key, None)

    if schema.get('type') == 'object' and 'properties' in schema:
        schema['required'] = list(schema['properties'].keys())
        schema['additionalProperties'] = False

        for prop_name, prop_schema in schema['properties'].items():
            schema['properties'][prop_name] = _clean_pydantic_schema(prop_schema)

    return schema


def _convert_type_to_schema(field_type) -> Dict[str, Any]:
    """Convert Python type hints to JSON schema"""
    if isinstance(field_type, tuple):
        actual_type, field_info = field_type

        if get_origin(actual_type) is list:
            item_type = get_args(actual_type)[0]
            schema = {
                "type": "array",
                "items": _convert_type_to_schema(item_type),
                "minItems": 1
            }
        elif isinstance(actual_type, type) and issubclass(actual_type, BaseModel):
            schema = _clean_pydantic_schema(actual_type.model_json_schema())
            schema['minProperties'] = 1
        else:
            schema = {"type": "string"}  # fallback for unknown types

        if hasattr(field_info, 'description'):
            schema['description'] = field_info.description

        return schema

    # Handle basic types
    if field_type in (str, int, float, bool):
        return {"type": field_type.__name__.lower()}

    return {"type": "string"}  # fallback for unknown types

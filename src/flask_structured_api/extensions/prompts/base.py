from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field, create_model
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import json

import logging
ai_logger = logging.getLogger("ai")


class STIPPrompt(BaseModel):
    """Base class for all prompts"""
    name: str = Field(..., description="Unique identifier for this prompt type")
    description: str = Field(..., description="Human readable description")
    system_message: str = Field(..., description="Instructions for the AI assistant")
    template: str = Field(...,
                          description="Template with {initiative_name} placeholder")
    version: str = Field(default="1.0", description="Version of this prompt")
    response_fields: Dict[str,
                          Any] = Field(..., description="Response field definitions")
    examples: Optional[list] = None
    reference_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Reference data like policy codes, target groups etc."
    )

    def _format_reference_data(self) -> str:
        """Format reference data into a readable string for the model"""
        if not self.reference_data:
            return ""

        result = []
        for category, items in self.reference_data.items():
            result.append(f"\nAvailable {category}:")
            if isinstance(items, list):
                for item in items:
                    # Format each item's key-value pairs
                    item_str = "\n".join(f"{k}: {v}" for k, v in item.items())
                    result.append(f"\n{item_str}")

        return "\n".join(result)

    def to_completion_request(self, initiative_name: str, text: str = "") -> Dict:
        """Convert prompt to AICompletionRequest format"""
        response_model = self.create_response_model()

        # Create Langchain parser
        parser = PydanticOutputParser(pydantic_object=response_model)
        format_instructions = parser.get_format_instructions()

        # Format reference data and combine with system message
        system_content = "{}\n\n{}\n\n{}".format(
            self.system_message,
            format_instructions,
            self._format_reference_data()
        )

        request = {
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": self.template.format(initiative_name=initiative_name) if not text else
                    "Here is the text to analyze:\n\n{}\n\n{}".format(
                        text,
                        self.template.format(initiative_name=initiative_name)
                )},
            ],
            "response_schema": response_model.model_json_schema(),
            "temperature": 0.1,
            "max_tokens": 4000
        }

        ai_logger.debug("Full completion request for {}: {}".format(
            self.name,
            json.dumps(request, indent=2)
        ))

        return request

    def create_response_model(self) -> Type[BaseModel]:
        """Dynamically create a Pydantic model for the response"""
        fields = {}
        for field_name, (field_type, field_info) in self.response_fields.items():
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                fields[field_name] = (field_type, field_info)
            else:
                fields[field_name] = (field_type, field_info)

        model_name = "{}Response".format(self.name.title())
        return create_model(model_name, **fields)

    def to_excel_format(self) -> Dict:
        """Convert prompt to Excel-friendly format"""
        return {
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "system_message": self.system_message,
            "version": self.version,
            "response_fields": self.response_fields
        }


class CombinedSTIPPrompt(STIPPrompt):
    """Special prompt class for one-shot combined analysis"""
    dimensions: Dict[str, STIPPrompt] = Field(..., description="Prompts by dimension")

    def __init__(self, **data):
        # Set default values for required STIPPrompt fields
        defaults = {
            "system_message": "",  # Will be built dynamically
            "template": "Analyze the provided text for the {initiative_name} initiative across all specified dimensions.",
            "response_fields": {},  # Will be built from dimensions
        }

        # Update with any provided values
        defaults.update(data)

        # Initialize parent class with defaults
        super().__init__(**defaults)

        # Build response fields from dimensions after initialization
        self.response_fields = self._build_combined_response_fields()

    def _build_combined_response_fields(self) -> Dict:
        """Builds combined response fields from all dimensions"""
        combined_fields = {}
        for dim_name, prompt in self.dimensions.items():
            combined_fields[dim_name] = {
                "type": "object",
                "properties": prompt.response_fields,
                "required": list(prompt.response_fields.keys())
            }
        return combined_fields

    def _build_structured_system_message(self, text: str) -> str:
        system_message = """You are a policy analysis expert. You will analyze the following text across multiple dimensions.
        
TEXT TO ANALYZE:
{text}

ANALYSIS DIMENSIONS:
""".format(text=text)

        for dim_name, prompt in self.dimensions.items():
            system_message += """
[{dim_name}]
Purpose: {purpose}
Analysis Instructions: {instructions}
---
""".format(
                dim_name=dim_name.upper(),
                purpose=prompt.description,
                instructions=prompt.system_message
            )

#         system_message += """
# IMPORTANT CROSS-DIMENSIONAL ANALYSIS INSTRUCTIONS:
# - Maintain consistency across all analysis dimensions
# - Cross-reference related information between dimensions
# - If you identify conflicts between dimensions, explicitly note them
# - Ensure numerical data (budgets, dates, etc.) is consistent throughout the analysis
# - When information from one dimension is relevant to another, explicitly mention the connection
# """
        return system_message

    def _organize_reference_data(self) -> Dict:
        """Organizes reference data by dimension"""
        organized_data = {}
        for dim_name, prompt in self.dimensions.items():
            if prompt.reference_data:
                organized_data[dim_name] = prompt.reference_data
        return organized_data

    def _format_reference_data_for_dimension(self, data: Dict) -> str:
        """Format reference data for a specific dimension"""
        result = []
        for category, items in data.items():
            result.append(f"Available {category}:")
            for item in items:
                result.append(f"- {item}")
        return "\n".join(result)

    def to_completion_request(self, initiative_name: str, text: str) -> Dict[str, Any]:
        """Convert prompt to completion request format"""
        # Create response model dynamically
        response_model = self.create_response_model()

        # Build system message with organized reference data
        system_message = self._build_structured_system_message(text)
        reference_data = self._organize_reference_data()

        if reference_data:
            system_message += "\n\nREFERENCE DATA BY DIMENSION:\n"
            for dim_name, data in reference_data.items():
                system_message += f"\n[{dim_name.upper()}]\n"
                system_message += self._format_reference_data_for_dimension(data)

        request = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content":
                    self.template.format(initiative_name=initiative_name)
                 },
            ],
            "response_schema": response_model.model_json_schema(),
            "temperature": 0.1,
            "max_tokens": 4000  # Increased for combined analysis
        }

        ai_logger.debug("Full completion request for {}: {}".format(
            self.name,
            json.dumps(request, indent=2)
        ))

        return request

    def create_response_model(self) -> Type[BaseModel]:
        """Dynamically create a Pydantic model for the combined response"""
        combined_fields = {}
        for dim_name, prompt in self.dimensions.items():
            # Create a nested model for each dimension
            dim_fields = {}
            for field_name, (field_type, field_info) in prompt.response_fields.items():
                if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    dim_fields[field_name] = (field_type, field_info)
                else:
                    dim_fields[field_name] = (field_type, field_info)

            # Create the dimension model
            dim_model_name = f"{dim_name.title()}Response"
            dim_model = create_model(dim_model_name, **dim_fields)
            combined_fields[dim_name] = (
                dim_model, Field(..., description=f"Response for {dim_name} dimension"))

        model_name = "{}Response".format(self.name.title())
        return create_model(model_name, **combined_fields)

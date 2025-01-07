from typing import Dict, List, Optional, Type, Union
from pydantic import BaseModel, ConfigDict, Field

from flask_structured_api.extensions.prompts.stip.budget import BudgetItem
from flask_structured_api.extensions.prompts.stip.evaluation import EvaluationInfo
from flask_structured_api.extensions.prompts.stip.objectives import Objective
from flask_structured_api.extensions.prompts.stip.policy_instruments import PolicyInstrument
from flask_structured_api.extensions.prompts.stip.start_date import StartDateInfo
from flask_structured_api.extensions.prompts.stip.target_groups import TargetGroup
from flask_structured_api.extensions.prompts.stip.themes import ThemeInfo
from flask_structured_api.extensions.models.countries import CountryCode


def create_storage_model(model: Type[BaseModel], name_prefix: str = "Storage") -> Type[BaseModel]:
    """Creates a storage version of a model with disabled length validation"""
    new_fields = {}
    for name, field in model.model_fields.items():
        # Create a new field without max_length constraint
        field_info = field.json_schema_extra or {}
        if 'max_length' in field_info:
            del field_info['max_length']
        new_fields[name] = (field.annotation, Field(
            description=field.description, **field_info))

    return type(
        f"{name_prefix}{model.__name__}",
        (BaseModel,),
        {
            "model_config": ConfigDict(str_max_length=None),
            "__annotations__": {name: field[0] for name, field in new_fields.items()},
            **{name: field[1] for name, field in new_fields.items()}
        }
    )


class ProcessedInitiative(BaseModel):
    """Model for storing processed initiatives."""
    model_config = ConfigDict(str_max_length=None)

    # Base info
    url: Optional[str] = None
    initiative_name: str
    country_code: str
    country_name: str

    # Results from processing
    results: Dict[str, Union[
        Optional[List[create_storage_model(BudgetItem)]],
        Optional[Dict[str, str]],
        Optional[create_storage_model(EvaluationInfo)],
        Optional[Dict[str, Union[int, str]]],
        Optional[List[create_storage_model(Objective)]],
        Optional[List[create_storage_model(PolicyInstrument)]],
        Optional[StartDateInfo],
        Optional[List[create_storage_model(TargetGroup)]],
        Optional[List[create_storage_model(ThemeInfo)]]
    ]] = Field(default_factory=dict)

    metadata: Dict = {}

    @classmethod
    def from_ai_response(cls, response: Dict, url: str | None, initiative_name: str, country_code: str) -> "ProcessedInitiative":
        """Create instance from AI response"""
        data = response["data"]

        country_name = CountryCode[country_code].value if CountryCode.is_valid(
            country_code) else country_code

        metadata = response.pop("metadata", {})
        metadata["counts"] = {
            "budget_items": len(data.get("budget", {}).get("budget_items", [])),
            "objectives": len(data.get("objectives", {}).get("objectives", [])),
            "policy_instruments": len(data.get("policy_instruments", {}).get("instruments", [])),
            "target_groups": len(data.get("target_groups", {}).get("target_groups", [])),
            "themes": len(data.get("themes", {}).get("themes", [])),
            "description": 1 if data.get("description", {}).get("text") else 0,
            "evaluation": 1 if data.get("evaluation", {}).get("evaluation") else 0,
            "identification": 1 if data.get("identification", {}).get("value") is not None else 0,
            "start_date": 1 if data.get("start_date", {}).get("start_date") else 0
        }

        return cls(
            url=url,
            initiative_name=initiative_name,
            country_code=country_code,
            country_name=country_name,
            results={
                "budget_items": data.get("budget", {}).get("budget_items"),
                "description": data.get("description"),
                "evaluation": data.get("evaluation", {}).get("evaluation"),
                "identification": data.get("identification"),
                "objectives": data.get("objectives", {}).get("objectives"),
                "policy_instruments": data.get("policy_instruments", {}).get("instruments"),
                "start_date": data.get("start_date", {}).get("start_date"),
                "target_groups": data.get("target_groups", {}).get("target_groups"),
                "themes": data.get("themes", {}).get("themes"),
            },
            metadata=metadata
        )

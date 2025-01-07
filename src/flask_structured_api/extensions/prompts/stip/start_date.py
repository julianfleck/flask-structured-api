from pydantic import BaseModel, Field
from ..base import STIPPrompt


class StartDateInfo(BaseModel):
    """Start date information for an initiative"""
    date: str = Field(description="The start year of the initiative in YYYY format")
    context: str = Field(description="Context or description of the date")
    reason: str = Field(
        description="Reasoning for why this date was identified as the start date", max_length=200)


start_date_prompt = STIPPrompt(
    name="start_date",
    description="Extract initiative start date",
    system_message="You are a data analyst extracting temporal information.",
    template="""Using the information provided, determine the starting date of the {initiative_name} 
    initiative if mentioned. Structure your response with the date and what it refers to.""",
    response_fields={
        "start_date": (StartDateInfo, Field(description="Start date information"))
    }
)

from typing import List
from pydantic import BaseModel, Field
from ..base import STIPPrompt


class Objective(BaseModel):
    """Single objective with title, description and reasoning"""
    title: str = Field(description="Title or name of the objective")
    text: str = Field(
        description="Detailed explanation of the objective",
        max_length=200)
    reason: str = Field(
        description="Reasoning for why this was identified as an objective",
        max_length=200)


objectives_prompt = STIPPrompt(
    name="objectives",
    description="Extract initiative objectives and their descriptions",
    system_message="""You are a policy expert analyzing initiative objectives.
    Your task is to identify explicit objectives, aims, and intended outcomes.
    Focus on clear statements of what the initiative intends to achieve.
    Do not include activities or implementation details unless they directly relate to goals.""",
    template="""Act as a policy expert and identify the {initiative_name} initiative's objectives. 
    Look for explicit statements about:
    - Goals and aims
    - Intended outcomes
    - Target achievements
    
    For each objective provide:
    1. A clear title
    2. A brief explanation (max 100 words)
    3. Reasoning for why you identified it as an objective
    
    If no clear objectives are found, return an empty list.""",
    response_fields={
        "objectives": (List[Objective], Field(
            description="List of objectives with their descriptions and reasoning",
            default_factory=list
        ))
    }
)

from typing import Optional, List
from pydantic import BaseModel, Field
from ..base import STIPPrompt


class BudgetItem(BaseModel):
    """Single budget item with amount, purpose, year and reasoning"""
    text: str = Field(description="The monetary amount")
    purpose: str = Field(description="What the budget is allocated for")
    year: Optional[str] = Field(
        default=None,
        description="Temporal information about the identified budget item (e.g. '2014', '2024-2034', 'next 10 years', 'from 2014')"
    )
    reason: str = Field(
        description="Reasoning for why this budget information was extracted",
        max_length=200)


budget_prompt = STIPPrompt(
    name="budget",
    description="Extract budget and monetary information",
    system_message="""You are a financial analyst extracting monetary information from policy documents.
    Your task is to identify and extract any budget, funding, or monetary allocations.
    For each item, provide the amount, its purpose, and explain why you identified it as relevant. Extract as many items as possible.""",
    template="""Using the information provided, determine if there is any monetary information 
    such as budget or expenditure related to the {initiative_name} initiative. 
    Include amounts, purposes, and any temporal information if available.
    For each budget item, explain why you consider it relevant to the initiative.
    
    If no monetary information is found, return an empty list.""",
    response_fields={
        "budget_items": (List[BudgetItem], Field(
            description="List of budget items with their amounts, purposes, and reasoning",
            default_factory=list
        ))
    }
)
# template="""Just repeat what's written in the text.""",

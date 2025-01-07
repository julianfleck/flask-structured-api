from pydantic import BaseModel, Field
from ..base import STIPPrompt


class EvaluationInfo(BaseModel):
    """Evaluation information for an initiative"""
    has_evaluation: bool = Field(
        description="Whether an actual evaluation report exists")
    name: str = Field(
        description="Name of the evaluation report, if one exists",
        default="n.a.")
    text: str = Field(
        description="Key findings or conclusions from the evaluation report",
        default="n.a.")
    reason: str = Field(
        description="Reasoning for why this was identified as an evaluation report",
        max_length=200)


evaluation_prompt = STIPPrompt(
    name="evaluation",
    description="Extract evaluation report information",
    system_message="""You are an evaluation expert analyzing policy initiatives.
    Your task is to identify if formal evaluation reports or assessments of the initiative exist.
    Only consider actual evaluation reports, reviews, or assessments that have been conducted 
    AFTER the initiative was implemented. Do not consider strategy documents, plans, or 
    proposals as evaluations.""",
    template="""Using the information provided, determine if the {initiative_name} initiative 
    has been formally evaluated and if evaluation reports exist. Look specifically for:
    - Post-implementation assessments
    - Impact evaluations
    - Progress reviews
    - Performance audits
    
    Include the name of any evaluation reports found and their key findings.
    If no evaluation reports are mentioned, set has_evaluation to false.
    
    Explain your reasoning for identifying something as an evaluation report or not.""",
    response_fields={
        "evaluation": (EvaluationInfo, Field(
            description="Information about evaluation reports"))
    }
)

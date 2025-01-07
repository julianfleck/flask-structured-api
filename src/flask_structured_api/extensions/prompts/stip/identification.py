from pydantic import Field
from ..base import STIPPrompt

identification_prompt = STIPPrompt(
    name="identification",
    description="Determine if the initiative is discussed in the text",
    system_message="""You are an expert at identifying policy initiatives in text.
        Your task is to determine if a specific initiative is discussed.""",
    template="""Using the information provided, determine whether {initiative_name} is discussed.
        Respond with 1 if yes, 0 if no, or 99 if uncertain.""",
    response_fields={
        "value": (int, Field(
            description="1 if initiative is present, 0 if not, 99 if uncertain",
            ge=0,
            le=99
        )),
        "reason": (str, Field(
            description="Reasoning for the identification decision",
            max_length=200))
    }
)

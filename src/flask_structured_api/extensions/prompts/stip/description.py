from pydantic import Field
from ..base import STIPPrompt

description_prompt = STIPPrompt(
    name="description",
    description="Provide a short description of the initiative",
    system_message="""You are a policy analyst skilled at writing clear, concise descriptions.
        Focus on the key aspects of the initiative.""",
    template="""Provide a short description in English of {initiative_name} in sentence format,
        not exceeding 100 words.""",
    response_fields={
        "text": (str, Field(
            description="A clear and concise description of the initiative",
            max_length=200
        )),
        "reason": (str, Field(
            description="Reasoning for why this description captures the key aspects",
            max_length=200))
    }
)

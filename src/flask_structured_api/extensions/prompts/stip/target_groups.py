from typing import List
from pydantic import BaseModel, Field, RootModel
from ..base import STIPPrompt


class TargetGroup(BaseModel):
    """Single target group with ID and reasoning"""
    target_group_id: str = Field(description="ID of the target group")
    label: str = Field(
        description="Label of the target group as provided in the reference data")
    reason: str = Field(
        description="Reasoning for why this target group applies", max_length=200)


REFERENCE_DATA = {
    "target_groups": [
        {
            "id": "TG20",
            "label": "Research and education organisations|Higher education institutes"
        },
        {
            "id": "TG21",
            "label": "Research and education organisations|Public research institutes"
        },
        {
            "id": "TG22",
            "label": "Research and education organisations|Private research and development lab"
        },
        {
            "id": "TG9",
            "label": "Researchers, students and teachers|Established researchers"
        },
        {
            "id": "TG11",
            "label": "Researchers, students and teachers|Postdocs and other early-career researchers"
        },
        {
            "id": "TG41",
            "label": "Researchers, students and teachers|Programme managers and other research support staff"
        },
        {
            "id": "TG10",
            "label": "Researchers, students and teachers|Undergraduate and master students"
        },
        {
            "id": "TG38",
            "label": "Researchers, students and teachers|Secondary education students"
        },
        {
            "id": "TG12",
            "label": "Researchers, students and teachers|PhD students"
        },
        {
            "id": "TG13",
            "label": "Researchers, students and teachers|Teachers"
        },
        {
            "id": "TG29",
            "label": "Firms by size|Firms of any size"
        },
        {
            "id": "TG30",
            "label": "Firms by size|Micro-enterprises"
        },
        {
            "id": "TG31",
            "label": "Firms by size|SMEs"
        },
        {
            "id": "TG32",
            "label": "Firms by size|Large firms"
        },
        {
            "id": "TG33",
            "label": "Firms by size|Multinational enterprises"
        },
        {
            "id": "TG25",
            "label": "Firms by age|Firms of any age"
        },
        {
            "id": "TG26",
            "label": "Firms by age|Nascent firms (0 to less than 1 year old)"
        },
        {
            "id": "TG27",
            "label": "Firms by age|Young firms (1 to 5 years old)"
        },
        {
            "id": "TG28",
            "label": "Firms by age|Established firms (more than 5 years old)"
        },
        {
            "id": "TG34",
            "label": "Intermediaries|Incubators, accelerators, science parks or technoparks"
        },
        {
            "id": "TG35",
            "label": "Intermediaries|Technology transfer offices"
        },
        {
            "id": "TG36",
            "label": "Intermediaries|Industry associations"
        },
        {
            "id": "TG37",
            "label": "Intermediaries|Academic societies / academies"
        },
        {
            "id": "TG42",
            "label": "Intermediaries|Non-governmental organisations (NGOs)"
        },
        {
            "id": "TG40",
            "label": "Governmental entities|International entity"
        },
        {
            "id": "TG23",
            "label": "Governmental entities|National government"
        },
        {
            "id": "TG24",
            "label": "Governmental entities|Subnational government"
        },
        {
            "id": "TG18",
            "label": "Economic actors (individuals)|Entrepreneurs"
        },
        {
            "id": "TG17",
            "label": "Economic actors (individuals)|Private investors"
        },
        {
            "id": "TG19",
            "label": "Economic actors (individuals)|Labour force in general"
        },
        {
            "id": "TG14",
            "label": "Social groups especially emphasised|Women"
        },
        {
            "id": "TG15",
            "label": "Social groups especially emphasised|Disadvantaged and excluded groups"
        },
        {
            "id": "TG16",
            "label": "Social groups especially emphasised|Civil society"
        }
    ]
}


target_groups_prompt = STIPPrompt(
    name="target_groups",
    description="Identify target groups and stakeholders",
    system_message="""You are a policy analyst specializing in target group identification.
    Your task is to identify which groups are affected by or targeted by initiatives.
    Only select groups that are explicitly mentioned or clearly implied in the text.
    Provide clear reasoning for each match. Extract as many groups as possible.""",
    template="""Consider yourself an expert policy analyst. Identify which target group(s) 
    the {initiative_name} initiative affects or targets. Match them to the provided target group definitions 
    and provide reasoning for each match.
    
    If no relevant target groups are found, return an empty list.""",
    response_fields={
        "target_groups": (List[TargetGroup], Field(
            description="List of target groups",
            default_factory=list
        ))
    },
    reference_data=REFERENCE_DATA
)

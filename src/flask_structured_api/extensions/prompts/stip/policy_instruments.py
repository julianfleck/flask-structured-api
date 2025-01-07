from typing import List
from pydantic import BaseModel, Field
from ..base import STIPPrompt


class PolicyInstrument(BaseModel):
    """Single policy instrument with ID and reasoning"""
    instrument_id: str = Field(description="ID of the policy instrument")
    label: str = Field(
        description="Label of the policy instrument as provided in the reference data")
    reason: str = Field(
        description="Reasoning for why this instrument applies", max_length=200)


REFERENCE_DATA = {
    "policy_instruments": [
        {
            "PolicyInstrumentID": "PI024",
            "label": "Governance|Strategies, agendas and plans",
            "definition": "Strategies that articulate the government's vision regarding the contribution of Science technology and innovation to social and economic development."
        },
        {
            "PolicyInstrumentID": "PI030",
            "label": "Governance|Creation or reform of governance structure or public body",
            "definition": "Significant changes in the institutional arrangements concerning STI policy processes."
        },
        {
            "PolicyInstrumentID": "PI031",
            "label": "Governance|Policy intelligence",
            "definition": "Tools for advancing policy learning that aim to improve the design and implementation of policies or that seek to fine-tune STI governance arrangements."
        },
        {
            "PolicyInstrumentID": "PI025",
            "label": "Governance|Formal consultation of stakeholders or experts",
            "definition": "Programmes allowing non-government actors to express their views or provide expert advice that inform policy-making processes."
        },
        {
            "PolicyInstrumentID": "PI026",
            "label": "Governance|Horizontal STI coordination bodies",
            "definition": "Public body ensuring the coherence of STI policy making by setting up mechanisms to co-ordinate different levels of governments."
        },
        {
            "PolicyInstrumentID": "PI033",
            "label": "Governance|Regulatory oversight and ethical advice bodies",
            "definition": "Dedicated authorities or publicly funded boards that assess, monitor and/or advise on the implementation or need for formal regulations soft law or ethical frameworks."
        },
        {
            "PolicyInstrumentID": "PI027",
            "label": "Governance|Standards and certification",
            "definition": "Support provided for the development and adoption of local and international standards, including metrology, inspection, certification, accreditation and conformity assessments."
        },
        {
            "PolicyInstrumentID": "PI028",
            "label": "Governance|Public awareness campaigns",
            "definition": "Instruments promoting the awareness of STI activities and entrepreneurial and innovation culture within non-governmental actors."
        },
        {
            "PolicyInstrumentID": "PI006",
            "label": "Direct financial support|Grants for business R&D and innovation",
            "definition": "Direct funding for business R&D and innovation activities through grants, vouchers, or matching funds."
        }
    ]
}


policy_instruments_prompt = STIPPrompt(
    name="policy_instruments",
    description="Identify policy instruments used in the initiative",
    system_message="""You are a policy analyst specializing in policy instrument classification. 
    Your task is to match initiatives to specific policy instruments based on their definitions.
    Only select instruments that are explicitly mentioned or clearly implied in the text.
    Provide clear reasoning for each match. Extract as many instruments as possible.""",
    template="""Consider yourself an expert policy analyst. Identify which policy instrument(s) 
    the {initiative_name} initiative relates to. Match them to the provided policy instrument definitions 
    and provide reasoning for each match. Select maximum five policy instruments.
    
    If no relevant policy instruments are found, return an empty list.""",
    response_fields={
        "instruments": (List[PolicyInstrument], Field(
            description="List of policy instruments",
            default_factory=list
        ))
    },
    reference_data=REFERENCE_DATA
)

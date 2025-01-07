from .stip.budget import budget_prompt, BudgetItem
from .stip.description import description_prompt
from .stip.evaluation import evaluation_prompt, EvaluationInfo
from .stip.identification import identification_prompt
from .stip.objectives import objectives_prompt, Objective
from .stip.policy_instruments import policy_instruments_prompt, PolicyInstrument
from .stip.start_date import start_date_prompt, StartDateInfo
from .stip.target_groups import target_groups_prompt, TargetGroup
from .stip.themes import themes_prompt, ThemeInfo

from .excel import PromptExcelManager

STIP_PROMPTS = {
    "budget": budget_prompt,
    "description": description_prompt,
    "evaluation": evaluation_prompt,
    "identification": identification_prompt,
    "objectives": objectives_prompt,
    "policy_instruments": policy_instruments_prompt,
    "start_date": start_date_prompt,
    "target_groups": target_groups_prompt,
    "themes": themes_prompt
}

__all__ = [
    # Prompts dictionary
    "STIP_PROMPTS",
    "PromptExcelManager",
    # Models
    "BudgetItem",
    "EvaluationInfo",
    "Objective",
    "PolicyInstrument",
    "StartDateInfo",
    "TargetGroup",
    "ThemeInfo",
    # Individual prompts
    "budget_prompt",
    "description_prompt",
    "evaluation_prompt",
    "identification_prompt",
    "objectives_prompt",
    "policy_instruments_prompt",
    "start_date_prompt",
    "target_groups_prompt",
    "themes_prompt"
]

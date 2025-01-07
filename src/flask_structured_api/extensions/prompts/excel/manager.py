from typing import Dict, Type, List
import pandas as pd
from pathlib import Path
from ..base import STIPPrompt


class PromptExcelManager:
    """Manages Excel import/export of prompts"""

    def export_to_excel(self, prompts: Dict[str, STIPPrompt], path: str) -> None:
        """Export prompts to Excel format"""
        data = []
        for name, prompt in prompts.items():
            data.append(prompt.to_excel_format())

        df = pd.DataFrame(data)
        df.to_excel(path, index=False)

    def import_from_excel(self, path: str) -> Dict[str, STIPPrompt]:
        """Import prompts while preserving schemas"""
        df = pd.read_excel(path)
        prompts = {}

        for _, row in df.iterrows():
            name = row["name"]
            prompts[name] = STIPPrompt(
                name=name,
                description=row["description"],
                template=row["template"],
                system_message=row["system_message"],
                version=row.get("version", "1.0"),
                response_fields=row.get("response_fields", {})
            )
        return prompts

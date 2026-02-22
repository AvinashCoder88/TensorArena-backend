import json
import os
from typing import Any, Dict

from app.services.llm_service import LLMService

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WORKFLOW_DIR = os.path.join(BASE_DIR, "workflows")
PROMPT_DIR = os.path.join(BASE_DIR, "prompts")


class WorkflowRunner:
    def __init__(self):
        self.llm = LLMService()

    def _load_workflow(self, workflow_id: str) -> Dict[str, Any]:
        path = os.path.join(WORKFLOW_DIR, f"{workflow_id}.json")
        if not os.path.exists(path):
            raise ValueError("Workflow not found")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_prompt(self, prompt_path: str) -> str:
        path = os.path.join(PROMPT_DIR, prompt_path)
        if not os.path.exists(path):
            raise ValueError("Prompt not found")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def run(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        workflow = self._load_workflow(workflow_id)
        context: Dict[str, Any] = {"input": payload}

        for step in workflow.get("steps", []):
            step_type = step.get("type")
            step_id = step.get("id")

            if step_type == "llm_text":
                prompt_template = self._load_prompt(step.get("prompt", ""))
                prompt = prompt_template.format(**context)
                result = await self.llm.generate_structured(prompt)
                context[step_id] = result
            else:
                raise ValueError(f"Unsupported step type: {step_type}")

        return context.get(workflow.get("output", ""), context)

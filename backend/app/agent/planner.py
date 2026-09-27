import json
import re
from app.agent.schemas import AgentPlan, PlannedStep
from app.ai.gateway import ai_gateway


class AgentPlanner:
    PLANNER_PROMPT = """You are the EVU Agent Task Planner.
Deconstruct the user's objective into clear sequential steps using ONLY the available tools:
1. `document_search`: query uploaded user documentation.
2. `web_search`: search the web for up-to-date information, news, and technical references.
3. `calculator`: solve arithmetic and numerical formulas.
4. `python_exec`: run python scripts for logic, data transformations, or complex computations.
5. `current_time`: retrieve current UTC time.

Output valid JSON adhering strictly to this schema:
{
  "reasoning": "brief description of strategy",
  "steps": [
    {
      "step_id": 1,
      "tool": "tool_name",
      "description": "why this tool is used",
      "input_parameters": {"query": "..."}
    }
  ]
}
No markdown outside the json block."""

    async def create_plan(
        self,
        message: str,
        provider: str,
        model: str | None = None,
        use_rag: bool = True,
        use_web: bool = True,
        max_steps: int = 4,
    ) -> AgentPlan:
        prompt = f"User Request: {message}\nAvailable flags: use_rag={use_rag}, use_web={use_web}, max_steps={max_steps}"
        messages = [
            {"role": "system", "content": self.PLANNER_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await ai_gateway.generate(messages, provider, model)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            raw_json = match.group(0) if match else response
            data = json.loads(raw_json)

            steps = [
                PlannedStep(
                    step_id=s.get("step_id", idx + 1),
                    tool=s.get("tool"),
                    description=s.get("description", ""),
                    input_parameters=s.get("input_parameters", {}),
                )
                for idx, s in enumerate(data.get("steps", []))
                if s.get("tool")
            ]
            return AgentPlan(
                reasoning=data.get("reasoning", "Plan constructed successfully."),
                steps=steps[:max_steps],
            )
        except Exception:
            # Fallback deterministic planning
            steps = []
            lower = message.lower()
            idx = 1
            if use_rag:
                steps.append(
                    PlannedStep(
                        step_id=idx,
                        tool="document_search",
                        description="Check local uploaded documents",
                        input_parameters={"query": message},
                    )
                )
                idx += 1
            if use_web and any(k in lower for k in ["search", "latest", "what is", "who is"]):
                steps.append(
                    PlannedStep(
                        step_id=idx,
                        tool="web_search",
                        description="Search internet",
                        input_parameters={"query": message},
                    )
                )
                idx += 1
            if any(k in lower for k in ["run", "python", "code", "calculate"]):
                steps.append(
                    PlannedStep(
                        step_id=idx,
                        tool="python_exec",
                        description="Run Python logic",
                        input_parameters={"code": message},
                    )
                )

            return AgentPlan(
                reasoning="Deterministic rule fallback plan.",
                steps=steps[:max_steps],
            )


agent_planner = AgentPlanner()
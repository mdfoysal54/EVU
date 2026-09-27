from typing import Optional
from sqlalchemy.orm import Session

from app.agent.schemas import (
    AgentRequest,
    AgentResponse,
    AgentToolResult,
)
from app.core.config import settings
from app.database.models import User


class EVUAgent:
    """Step 8 agent: tools/RAG first, progressive skills, then intelligent model routing."""

    def __init__(self):
        self._skill_selector = None

    @property
    def skill_selector(self):
        if self._skill_selector is None:
            from app.skills.selector import SkillSelector
            self._skill_selector = SkillSelector()
        return self._skill_selector

    _TIME_WORDS = (
        "time",
        "date",
        "utc",
        "today",
        "current time",
    )

    _MATH_HINTS = (
        "calculate",
        "calculator",
        "solve",
        "what is",
        "how much",
        "sum",
        "multiply",
        "divide",
        "minus",
        "plus",
    )

    _DIAGRAM_HINTS = (
        "diagram",
        "draw",
        "flowchart",
        "architecture",
        "sequence diagram",
        "data flow",
        "timeline",
        "visualize",
        "system design",
    )

    def plan(
        self,
        message: str,
        request: AgentRequest,
    ) -> list[str]:
        from app.agent.tools.calculator import calculator_tool

        text = message.lower()
        tools: list[str] = []

        if request.use_rag:
            tools.append("document_search")

        has_expression = (
            calculator_tool.extract_expression(message) is not None
        )

        if has_expression and any(
            hint in text for hint in self._MATH_HINTS
        ):
            tools.append("calculator")

        if any(
            word in text for word in self._TIME_WORDS
        ):
            tools.append("current_time")

        if any(
            hint in text for hint in self._DIAGRAM_HINTS
        ):
            tools.append("diagram")

        return list(
            dict.fromkeys(tools)
        )[
            : min(
                request.max_steps,
                settings.AGENT_MAX_STEPS,
            )
        ]

    async def run(
        self,
        request: AgentRequest,
        user: User,
        db: Session,
    ) -> AgentResponse:
        from app.agent.tools.calculator import calculator_tool
        from app.agent.tools.current_time import current_time_tool
        from app.agent.tools.diagram_tool import diagram_tool
        from app.agent.tools.document_search import document_search_tool
        from app.ai.orchestrator.engine import evu_orchestrator
        from app.ai.orchestrator.schemas import OrchestrationRequest

        if not settings.AGENT_ENABLED:
            raise ValueError(
                "Agent mode is disabled by server configuration."
            )

        # 1. Progressive Skill Resolution (Lightweight metadata -> Top 2 candidates)
        active_skills = self.skill_selector.resolve_instructions(
            request.message,
            top_k=2,
        )

        planned_tools = self.plan(
            request.message,
            request,
        )

        steps: list[AgentToolResult] = []
        sources = []
        context_blocks: list[str] = []

        # 2. Tool Planning & Execution
        for step_number, tool_name in enumerate(
            planned_tools,
            start=1,
        ):
            if tool_name == "document_search":
                result, tool_sources = (
                    await document_search_tool.run(
                        user.id,
                        request.message,
                        db,
                    )
                )
                sources.extend(tool_sources)

            elif tool_name == "calculator":
                result = calculator_tool.run(
                    request.message
                )

            elif tool_name == "current_time":
                result = current_time_tool.run(
                    request.message
                )

            elif tool_name == "diagram":
                payload = {
                    "title": "Generated Architecture",
                    "diagram_type": "architecture",
                    "nodes": [{"id": "req", "label": "Request"}, {"id": "res", "label": "Response"}],
                    "edges": [{"source": "req", "target": "res", "label": "process"}],
                }
                raw_res = diagram_tool(payload)

                class ToolResultWrapper:
                    def __init__(self, name, user_input, output, success):
                        self.name = name
                        self.input = user_input
                        self.output = output
                        self.success = success

                result = ToolResultWrapper(
                    name="diagram",
                    user_input=request.message,
                    output=raw_res.get("content", raw_res.get("message", "")),
                    success=raw_res.get("status") == "success",
                )

            else:
                continue

            output = str(result.output)[
                : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
            ]

            steps.append(
                AgentToolResult(
                    step=step_number,
                    tool=result.name,
                    input=result.input,
                    output=output,
                    success=result.success,
                )
            )

            if result.success:
                context_blocks.append(
                    f"TOOL: {result.name}\n"
                    f"INPUT: {result.input}\n"
                    f"RESULT:\n{output}"
                )

        # 3. Message Enrichment with Progressive Skills and Tool Results
        enriched_message = request.message

        if active_skills:
            skill_guidance = "\n\n".join(
                f"[SKILL GUIDANCE: {s.name.upper()}]\n{s.instructions}"
                for s in active_skills
            )
            enriched_message = f"{skill_guidance}\n\n---\n\n{enriched_message}"

        if context_blocks:
            enriched_message += (
                "\n\nEVU TOOL RESULTS:\n"
                + "\n\n".join(context_blocks)
            )

        orchestration = await evu_orchestrator.run(
            OrchestrationRequest(
                message=enriched_message,
                provider=request.provider,
                model=request.model,
                use_rag=request.use_rag,
            )
        )

        return AgentResponse(
            response=orchestration.response,
            provider=orchestration.provider,
            model=orchestration.model,
            agent_used=True,
            rag_used=any(
                item.tool == "document_search"
                and item.success
                for item in steps
            ),
            steps=steps,
            sources=sources,
        )


evu_agent = EVUAgent()
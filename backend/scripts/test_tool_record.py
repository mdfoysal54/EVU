import asyncio
from pathlib import Path

Path("data/experience").mkdir(parents=True, exist_ok=True)

from app.model_lab.experience import ExperienceRecorder
from app.model_lab.experience.store import ExperienceStore
from app.model_lab.runtime import (
    record_request,
    record_tool_result,
    record_tool_start,
)

# Simulated web search function
async def dummy_web_search(query: str):
    await asyncio.sleep(0.1)
    return f"Search results for: '{query}'"


async def run_tool_cycle():
    store = ExperienceStore("./data/experience/runtime.jsonl")
    recorder = ExperienceRecorder(store)

    query = "latest AI news"

    with record_request(
        recorder,
        prompt=f"Search for {query}",
        model="evu",
        provider="evu",
        task_type="tool_agent",
    ) as session:

        # --- Tool Recording Block ---
        step_id = record_tool_start(
            name="web_search",
            arguments={"query": query},
        )
        try:
            result = await dummy_web_search(query)
            record_tool_result(
                step_id=step_id,
                result=result,
                success=True,
            )
        except Exception as exc:
            record_tool_result(
                step_id=step_id,
                result=None,
                success=False,
                error=str(exc),
            )
            raise
        # -----------------------------

        session.model_response(f"Found information: {result}")
        session.finish(success=True)

    print("Trajectory and tool execution recorded successfully!")


if __name__ == "__main__":
    asyncio.run(run_tool_cycle())
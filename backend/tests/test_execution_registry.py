import pytest

from app.agent.execution.bootstrap import (
    register_default_tools,
)
from app.agent.execution.registry import tool_registry


@pytest.fixture(autouse=True)
def setup_tools():
    register_default_tools()


def test_default_tools_are_registered():
    names = {
        item["name"]
        for item in tool_registry.list_tools()
    }

    assert "calculator" in names
    assert "current_time" in names
    assert "web_research" in names


@pytest.mark.asyncio
async def test_calculator_execution():
    result = await tool_registry.execute(
        "calculator",
        {
            "expression": "2 + 3 * 4",
        },
    )

    assert result == 14
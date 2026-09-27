from __future__ import annotations

from app.agent.tools.base import ToolExecution
from app.browser.service import browser_service
from app.core.config import settings


class BrowserTool:
    """
    Step 16 Browser Intelligence Agent tool.

    This first version supports:
        open URL
        inspect page
        click
        fill
        press
        back
        forward

    Browser sessions are intentionally controlled by EVU.
    """

    name = "browser"

    async def run(
        self,
        action: str,
        value: str = "",
        session_id: str = "",
        selector: str = "",
    ) -> ToolExecution:

        if not settings.BROWSER_ENABLED:
            return ToolExecution(
                name=self.name,
                input=action,
                output=(
                    "Browser automation is disabled."
                ),
                success=False,
            )

        action = action.strip().lower()

        try:

            if action == "open":

                if not value:
                    return ToolExecution(
                        name=self.name,
                        input=value,
                        output="URL is required.",
                        success=False,
                    )

                result = (
                    await browser_service.open(
                        value
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=value,
                    output=(
                        f"SESSION: "
                        f"{result.session_id}\n"
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    ),
                    success=result.success,
                )

            if not session_id:
                return ToolExecution(
                    name=self.name,
                    input=action,
                    output=(
                        "session_id is required "
                        "for this browser action."
                    ),
                    success=False,
                )

            if action == "inspect":

                result = (
                    await browser_service.inspect(
                        session_id
                    )
                )

                links = "\n".join(
                    [
                        (
                            f"- {item['text']} "
                            f"=> {item['href']}"
                        )
                        for item in result.links[:30]
                    ]
                )

                output = (
                    f"URL: {result.url}\n"
                    f"TITLE: {result.title}\n\n"
                    f"PAGE TEXT:\n"
                    f"{result.text}\n\n"
                    f"LINKS:\n"
                    f"{links}"
                )

                return ToolExecution(
                    name=self.name,
                    input=action,
                    output=output[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            if action == "click":

                if not selector:
                    return ToolExecution(
                        name=self.name,
                        input=selector,
                        output=(
                            "CSS selector is required."
                        ),
                        success=False,
                    )

                result = (
                    await browser_service.click(
                        session_id=session_id,
                        selector=selector,
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=selector,
                    output=(
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    )[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            if action == "fill":

                if not selector:
                    return ToolExecution(
                        name=self.name,
                        input=selector,
                        output=(
                            "CSS selector is required."
                        ),
                        success=False,
                    )

                result = (
                    await browser_service.fill(
                        session_id=session_id,
                        selector=selector,
                        value=value,
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=selector,
                    output=(
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    )[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            if action == "press":

                if not selector:
                    return ToolExecution(
                        name=self.name,
                        input=selector,
                        output=(
                            "CSS selector is required."
                        ),
                        success=False,
                    )

                result = (
                    await browser_service.press(
                        session_id=session_id,
                        selector=selector,
                        key=value,
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=selector,
                    output=(
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    )[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            if action == "back":

                result = (
                    await browser_service.back(
                        session_id
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=action,
                    output=(
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    )[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            if action == "forward":

                result = (
                    await browser_service.forward(
                        session_id
                    )
                )

                return ToolExecution(
                    name=self.name,
                    input=action,
                    output=(
                        f"URL: {result.url}\n"
                        f"TITLE: {result.title}\n\n"
                        f"{result.text}"
                    )[
                        : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
                    ],
                    success=result.success,
                )

            return ToolExecution(
                name=self.name,
                input=action,
                output=(
                    "Unsupported browser action. "
                    "Supported actions: "
                    "open, inspect, click, fill, "
                    "press, back, forward."
                ),
                success=False,
            )

        except Exception as exc:

            return ToolExecution(
                name=self.name,
                input=action,
                output=(
                    f"Browser tool error: {exc}"
                ),
                success=False,
            )


browser_tool = BrowserTool()
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ElementObservation:
    tag: str = ""
    text: str = ""
    role: Optional[str] = None
    aria_label: Optional[str] = None
    selector: Optional[str] = None
    href: Optional[str] = None
    visible: bool = True
    enabled: bool = True
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class PageObservation:
    url: str
    title: str = ""
    text: str = ""
    elements: List[ElementObservation] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class BrowserObserver:
    def __init__(self, page: Any = None) -> None:
        self.page = page

    def attach(self, page: Any) -> None:
        self.page = page

    async def observe(
        self,
        include_elements: bool = True,
    ) -> PageObservation:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        url = str(
            getattr(
                self.page,
                "url",
                "",
            )
        )

        title = await self.page.title()

        body_text = ""

        try:
            body_text = await self.page.locator(
                "body"
            ).inner_text()
        except Exception:
            pass

        elements: list[ElementObservation] = []

        if include_elements:
            elements = await self._observe_elements()

        return PageObservation(
            url=url,
            title=title,
            text=body_text,
            elements=elements,
        )

    async def _observe_elements(
        self,
    ) -> list[ElementObservation]:
        selectors = (
            "a,button,input,textarea,select,"
            "[role],img"
        )

        try:
            locator = self.page.locator(selectors)

            count = await locator.count()

            results: list[ElementObservation] = []

            for index in range(count):
                element = locator.nth(index)

                try:
                    tag = await element.evaluate(
                        "(el) => el.tagName.toLowerCase()"
                    )
                    text = (
                        await element.inner_text()
                    ).strip()
                except Exception:
                    tag = ""
                    text = ""

                try:
                    role = await element.get_attribute(
                        "role"
                    )
                    aria_label = await element.get_attribute(
                        "aria-label"
                    )
                    href = await element.get_attribute(
                        "href"
                    )
                except Exception:
                    role = None
                    aria_label = None
                    href = None

                try:
                    visible = await element.is_visible()
                except Exception:
                    visible = True

                try:
                    enabled = await element.is_enabled()
                except Exception:
                    enabled = True

                results.append(
                    ElementObservation(
                        tag=tag or "",
                        text=text,
                        role=role,
                        aria_label=aria_label,
                        href=href,
                        visible=visible,
                        enabled=enabled,
                    )
                )

            return results

        except Exception:
            return []
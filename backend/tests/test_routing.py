import importlib
import pytest
from app.ai.router.capabilities import get_provider_capability


def test_router_module_exists():
    module = importlib.import_module("app.ai.router.capabilities")
    assert module is not None


def test_selector_module_exists():
    module = importlib.import_module("app.ai.router.selector")
    assert module is not None


@pytest.mark.parametrize(
    "provider",
    ["openai", "anthropic", "gemini", "xai", "zai"],
)
def test_provider_capability_exists(provider: str):
    capability = get_provider_capability(provider)
    assert capability is not None
    assert bool(capability) is True
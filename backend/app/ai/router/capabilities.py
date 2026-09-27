from __future__ import annotations


PROVIDER_CAPABILITIES = {
    "openai": {
        "coding": 0.96,
        "reasoning": 0.96,
        "research": 0.94,
        "multimodal": 0.96,
        "writing": 0.96,
        "analysis": 0.96,
        "general": 0.96,
        "latency_score": 0.85,
        "cost_score": 0.45,
    },
    "anthropic": {
        "coding": 0.97,
        "reasoning": 0.97,
        "research": 0.92,
        "multimodal": 0.92,
        "writing": 0.95,
        "analysis": 0.96,
        "general": 0.95,
        "latency_score": 0.78,
        "cost_score": 0.40,
    },
    "gemini": {
        "coding": 0.90,
        "reasoning": 0.92,
        "research": 0.94,
        "multimodal": 0.98,
        "writing": 0.90,
        "analysis": 0.94,
        "general": 0.94,
        "latency_score": 0.90,
        "cost_score": 0.55,
    },
    "xai": {
        "coding": 0.90,
        "reasoning": 0.91,
        "research": 0.90,
        "multimodal": 0.90,
        "writing": 0.88,
        "analysis": 0.90,
        "general": 0.90,
        "latency_score": 0.86,
        "cost_score": 0.55,
    },
    "zai": {
        "coding": 0.88,
        "reasoning": 0.89,
        "research": 0.82,
        "multimodal": 0.85,
        "writing": 0.87,
        "analysis": 0.88,
        "general": 0.87,
        "latency_score": 0.82,
        "cost_score": 0.65,
    },
}


def get_provider_capabilities(provider: str) -> dict:
    return PROVIDER_CAPABILITIES.get(provider, {})


# Alias for singular import expected by tests and routers
get_provider_capability = get_provider_capabilities
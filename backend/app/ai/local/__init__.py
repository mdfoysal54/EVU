"""
EVU local model infrastructure.

Local models are accessed through external runtimes such as
Ollama or other OpenAI-compatible local servers.
"""

from app.ai.local.ollama import ollama_service
from app.ai.local.registry import local_model_registry

__all__ = [
    "ollama_service",
    "local_model_registry",
]
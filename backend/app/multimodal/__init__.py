"""
EVU Multimodal Input Foundation.

This package provides the normalized input layer for:
- images
- audio
- video
- documents
- text references

Actual multimodal intelligence such as vision reasoning
will be implemented in later EVU steps.
"""

from app.multimodal.service import multimodal_service

__all__ = [
    "multimodal_service",
]
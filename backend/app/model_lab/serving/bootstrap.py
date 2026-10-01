from __future__ import annotations

import os

from app.core.config import settings

from .provider import EVUOwnedProvider
from .service import EVUModelService


def build_evu_provider() -> EVUOwnedProvider:
    """Build EVU's owned provider."""

    service = EVUModelService(
        settings.EVU_MODEL_BUNDLE_DIR,
        device=settings.EVU_MODEL_DEVICE,
        quantization=os.getenv(
            "EVU_MODEL_QUANTIZATION",
            "none",
        ),
    )

    return EVUOwnedProvider(
        service
    )
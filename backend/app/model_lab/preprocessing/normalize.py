from __future__ import annotations

from collections.abc import Iterable
from ..datasets.cleaning import clean_text


def normalize_corpus(texts: Iterable[str]) -> list[str]:
    return [clean_text(text) for text in texts if clean_text(text)]
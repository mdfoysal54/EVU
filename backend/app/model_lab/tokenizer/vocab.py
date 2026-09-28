"""
EVU Model Lab vocabulary implementation.

Provides a deterministic token -> integer vocabulary with
special-token support and serialization helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class Vocabulary:
    """
    Bidirectional token vocabulary.
    """

    token_to_id: dict[str, int] = field(
        default_factory=dict
    )

    id_to_token: dict[int, str] = field(
        default_factory=dict
    )

    special_tokens: dict[str, str] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self._rebuild_reverse()

    def _rebuild_reverse(self) -> None:
        self.id_to_token = {
            int(index): token
            for token, index
            in self.token_to_id.items()
        }

    def add_token(
        self,
        token: str,
    ) -> int:
        if token in self.token_to_id:
            return self.token_to_id[token]

        index = len(self.token_to_id)

        self.token_to_id[token] = index
        self.id_to_token[index] = token

        return index

    def add_tokens(
        self,
        tokens: Iterable[str],
    ) -> int:
        added = 0

        for token in tokens:
            if token not in self.token_to_id:
                self.add_token(token)
                added += 1

        return added

    def add_special_token(
        self,
        name: str,
        token: str,
    ) -> int:
        self.special_tokens[name] = token

        return self.add_token(token)

    def get_id(
        self,
        token: str,
        default: int | None = None,
    ) -> int | None:
        return self.token_to_id.get(
            token,
            default,
        )

    def get_token(
        self,
        index: int,
        default: str | None = None,
    ) -> str | None:
        return self.id_to_token.get(
            index,
            default,
        )

    def __len__(self) -> int:
        return len(self.token_to_id)

    def __contains__(
        self,
        token: str,
    ) -> bool:
        return token in self.token_to_id

    def to_dict(self) -> dict:
        return {
            "token_to_id": self.token_to_id,
            "special_tokens": self.special_tokens,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Vocabulary":
        vocabulary = cls(
            token_to_id={
                str(token): int(index)
                for token, index
                in data.get(
                    "token_to_id",
                    {},
                ).items()
            },
            special_tokens=dict(
                data.get(
                    "special_tokens",
                    {},
                )
            ),
        )

        vocabulary._rebuild_reverse()

        return vocabulary

    def save(
        self,
        path: str | Path,
    ) -> None:
        import json

        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                self.to_dict(),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> "Vocabulary":
        import json

        path = Path(path)

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return cls.from_dict(data)
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass
class ByteBPETokenizerConfig:
    vocab_size: int = 4096
    min_frequency: int = 2
    special_tokens: tuple[str, ...] = (
        "<pad>", "<bos>", "<eos>", "<unk>",
        "<system>", "<user>", "<assistant>", "<tool>",
    )


class ByteBPETokenizer:
    """Small dependency-free byte-level BPE tokenizer owned by EVU.

    The implementation is intentionally compact and deterministic. It is
    suitable for EVU experiments and can later be replaced by a faster
    Rust-backed tokenizer without changing the model/training interfaces.
    """

    def __init__(self, config: ByteBPETokenizerConfig | None = None) -> None:
        self.config = config or ByteBPETokenizerConfig()
        self.special_tokens = list(self.config.special_tokens)
        self.merges: list[tuple[int, int]] = []
        self.token_to_id: dict[bytes, int] = {}
        self.id_to_token: dict[int, bytes] = {}
        self._trained = False

    def train(self, texts: Iterable[str]) -> None:
        sequences: list[list[int]] = []
        for text in texts:
            data = text.encode("utf-8", errors="replace")
            if data:
                sequences.append(list(data))

        self.token_to_id.clear()
        self.id_to_token.clear()

        # Reserve special IDs first.
        for token in self.special_tokens:
            encoded = token.encode("utf-8")
            self._add_token(encoded)

        for value in range(256):
            self._add_token(bytes([value]))

        target_merges = max(0, self.config.vocab_size - len(self.token_to_id))
        for _ in range(target_merges):
            pair_counts: Counter[tuple[int, int]] = Counter()
            for seq in sequences:
                pair_counts.update(zip(seq, seq[1:]))
            candidates = [
                (count, pair) for pair, count in pair_counts.items()
                if count >= self.config.min_frequency
            ]
            if not candidates:
                break

            _, pair = max(candidates, key=lambda item: (item[0], item[1]))
            new_id = len(self.token_to_id)
            left, right = pair
            left_bytes = self.id_to_token[left]
            right_bytes = self.id_to_token[right]
            self._add_token(left_bytes + right_bytes, token_id=new_id)
            self.merges.append(pair)

            sequences = [self._merge_sequence(seq, pair, new_id) for seq in sequences]

        self._trained = True

    def _add_token(self, token: bytes, token_id: int | None = None) -> int:
        if token in self.token_to_id:
            return self.token_to_id[token]
        idx = len(self.token_to_id) if token_id is None else token_id
        self.token_to_id[token] = idx
        self.id_to_token[idx] = token
        return idx

    @staticmethod
    def _merge_sequence(seq: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
        if len(seq) < 2:
            return seq
        out: list[int] = []
        i = 0
        while i < len(seq):
            if i + 1 < len(seq) and (seq[i], seq[i + 1]) == pair:
                out.append(new_id)
                i += 2
            else:
                out.append(seq[i])
                i += 1
        return out

    def _special_ids(self) -> dict[str, int]:
        return {
            token: self.token_to_id[token.encode("utf-8")]
            for token in self.special_tokens
        }

    @property
    def pad_token_id(self) -> int:
        return self._special_ids()["<pad>"]

    @property
    def bos_token_id(self) -> int:
        return self._special_ids()["<bos>"]

    @property
    def eos_token_id(self) -> int:
        return self._special_ids()["<eos>"]

    @property
    def unk_token_id(self) -> int:
        return self._special_ids()["<unk>"]

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        if not self._trained:
            raise RuntimeError("Tokenizer must be trained or loaded before encoding")

        raw = list(text.encode("utf-8", errors="replace"))
        ids = [self._byte_id(b) for b in raw]
        for pair in self.merges:
            ids = self._merge_sequence(ids, pair, self._pair_id(pair))
        if add_special_tokens:
            return [self.bos_token_id, *ids, self.eos_token_id]
        return ids

    def _byte_id(self, value: int) -> int:
        return self.token_to_id.get(bytes([value]), self.unk_token_id)

    def _pair_id(self, pair: tuple[int, int]) -> int:
        token = self.id_to_token[pair[0]] + self.id_to_token[pair[1]]
        return self.token_to_id[token]

    def decode(self, ids: Iterable[int], skip_special_tokens: bool = True) -> str:
        special_ids = set(self._special_ids().values())
        data = bytearray()
        for idx in ids:
            idx = int(idx)
            if skip_special_tokens and idx in special_ids:
                continue
            token = self.id_to_token.get(idx)
            if token is not None:
                data.extend(token)
        return bytes(data).decode("utf-8", errors="replace")

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "config": asdict(self.config),
            "special_tokens": self.special_tokens,
            "merges": [list(pair) for pair in self.merges],
            "token_to_id": {token.hex(): idx for token, idx in self.token_to_id.items()},
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ByteBPETokenizer":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        config_data = payload["config"]
        config_data["special_tokens"] = tuple(config_data["special_tokens"])
        obj = cls(ByteBPETokenizerConfig(**config_data))
        obj.special_tokens = list(payload["special_tokens"])
        obj.token_to_id = {bytes.fromhex(k): int(v) for k, v in payload["token_to_id"].items()}
        obj.id_to_token = {idx: token for token, idx in obj.token_to_id.items()}
        obj.merges = [tuple(pair) for pair in payload["merges"]]
        obj._trained = True
        return obj

    def __len__(self) -> int:
        return len(self.token_to_id)
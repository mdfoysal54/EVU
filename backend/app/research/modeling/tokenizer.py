from pathlib import Path


class EVUByteTokenizer:
    """
    Simple byte-level tokenizer for early EVU research.

    Every UTF-8 byte maps directly to one token.

    Reserved tokens:
        0 = PAD
        1 = BOS
        2 = EOS
        3 = UNK

    Actual byte tokens:
        4-259
    """

    PAD_ID = 0
    BOS_ID = 1
    EOS_ID = 2
    UNK_ID = 3

    BYTE_OFFSET = 4

    VOCAB_SIZE = 260

    def __init__(self):
        self.vocab_size = self.VOCAB_SIZE

    def encode(
        self,
        text: str,
        add_bos: bool = True,
        add_eos: bool = True,
    ) -> list[int]:

        tokens = []

        if add_bos:
            tokens.append(self.BOS_ID)

        try:
            raw = text.encode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            raw = b""

        tokens.extend(
            byte + self.BYTE_OFFSET
            for byte in raw
        )

        if add_eos:
            tokens.append(self.EOS_ID)

        return tokens

    def decode(
        self,
        tokens: list[int],
    ) -> str:

        byte_values = []

        for token in tokens:

            if token < self.BYTE_OFFSET:
                continue

            value = token - self.BYTE_OFFSET

            if 0 <= value <= 255:
                byte_values.append(value)

        return bytes(
            byte_values
        ).decode(
            "utf-8",
            errors="replace",
        )

    def save(
        self,
        path: str,
    ) -> None:

        target = Path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            "EVU byte tokenizer\n"
            f"vocab_size={self.vocab_size}\n",
            encoding="utf-8",
        )

    @classmethod
    def load(
        cls,
        path: str,
    ) -> "EVUByteTokenizer":

        if not Path(path).exists():
            raise FileNotFoundError(path)

        return cls()
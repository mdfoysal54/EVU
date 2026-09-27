from dataclasses import asdict, dataclass


@dataclass
class EVUModelConfig:
    """
    Configuration for an EVU decoder-only Transformer.

    The defaults are intentionally small enough for development.
    Increase dimensions only when appropriate compute is available.
    """

    vocab_size: int = 4096
    max_sequence_length: int = 512
    hidden_size: int = 256
    num_layers: int = 6
    num_attention_heads: int = 8
    intermediate_size: int = 1024
    dropout: float = 0.1

    @property
    def head_dim(self) -> int:
        if self.hidden_size % self.num_attention_heads != 0:
            raise ValueError(
                "hidden_size must be divisible by num_attention_heads."
            )
        return self.hidden_size // self.num_attention_heads

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def tiny(cls) -> "EVUModelConfig":
        return cls(
            vocab_size=260,
            max_sequence_length=256,
            hidden_size=128,
            num_layers=4,
            num_attention_heads=4,
            intermediate_size=512,
            dropout=0.1,
        )

    @classmethod
    def small(cls) -> "EVUModelConfig":
        return cls(
            vocab_size=260,
            max_sequence_length=512,
            hidden_size=256,
            num_layers=6,
            num_attention_heads=8,
            intermediate_size=1024,
            dropout=0.1,
        )

    @classmethod
    def evu_100m(cls) -> "EVUModelConfig":
        """
        Approximate 100M-class configuration.

        This is a configuration target, not a recommendation
        to train it locally on a normal laptop.
        """
        return cls(
            vocab_size=32768,
            max_sequence_length=2048,
            hidden_size=768,
            num_layers=12,
            num_attention_heads=12,
            intermediate_size=3072,
            dropout=0.1,
        )
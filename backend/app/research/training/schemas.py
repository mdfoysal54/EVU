from datetime import datetime

from pydantic import BaseModel, Field


class TrainingConfig(BaseModel):

    base_model: str = Field(
        default="EVU-from-scratch",
        min_length=1,
        max_length=300,
    )

    dataset_version: str = Field(
        min_length=1,
        max_length=200,
    )

    output_model_name: str = Field(
        min_length=1,
        max_length=200,
    )

    architecture: str = Field(
        default="evu-transformer",
        min_length=1,
        max_length=100,
    )

    model_size: str = Field(
        default="tiny",
        min_length=1,
        max_length=50,
    )

    epochs: int = Field(
        default=1,
        ge=1,
        le=100,
    )

    learning_rate: float = Field(
        default=0.0003,
        gt=0,
        le=1,
    )

    batch_size: int = Field(
        default=2,
        ge=1,
        le=256,
    )

    max_sequence_length: int = Field(
        default=256,
        ge=16,
        le=131072,
    )

    warmup_ratio: float = Field(
        default=0.03,
        ge=0,
        lt=1,
    )

    gradient_accumulation_steps: int = Field(
        default=1,
        ge=1,
        le=1024,
    )

    weight_decay: float = Field(
        default=0.1,
        ge=0,
        le=1,
    )

    seed: int = Field(
        default=42,
        ge=0,
    )


class TrainingValidationResponse(BaseModel):

    valid: bool

    errors: list[str]

    warnings: list[str]


class TrainingJobResponse(BaseModel):

    job_id: str

    status: str

    base_model: str

    dataset_version: str

    output_model_name: str

    architecture: str

    model_size: str

    created_at: datetime

    message: str
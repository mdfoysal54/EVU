import uuid
from datetime import datetime

from app.research.training.schemas import (
    TrainingConfig,
    TrainingJobResponse,
    TrainingValidationResponse,
)


class TrainingService:

    def validate(
        self,
        config: TrainingConfig,
    ) -> TrainingValidationResponse:

        errors = []
        warnings = []

        valid_sizes = {
            "tiny",
            "small",
            "evu-100m",
            "evu-300m",
            "evu-1b",
        }

        if (
            config.model_size.lower()
            not in valid_sizes
        ):
            errors.append(
                "Unsupported model_size."
            )

        if (
            config.max_sequence_length
            < 16
        ):
            errors.append(
                "Sequence length must be at least 16."
            )

        if (
            config.learning_rate
            > 0.01
        ):
            warnings.append(
                "Learning rate is unusually high."
            )

        if (
            config.model_size.lower()
            in {
                "evu-100m",
                "evu-300m",
                "evu-1b",
            }
        ):
            warnings.append(
                "Large model configuration should "
                "normally be trained on dedicated GPU infrastructure."
            )

        if config.batch_size >= 32:
            warnings.append(
                "Large batch sizes can require substantial GPU memory."
            )

        if (
            config.max_sequence_length
            >= 8192
        ):
            warnings.append(
                "Long context requires substantially more memory."
            )

        return TrainingValidationResponse(
            valid=not errors,
            errors=errors,
            warnings=warnings,
        )

    def create_job(
        self,
        config: TrainingConfig,
    ) -> TrainingJobResponse:

        validation = self.validate(
            config
        )

        if not validation.valid:
            raise ValueError(
                "; ".join(
                    validation.errors
                )
            )

        job_id = (
            "evu-train-"
            + uuid.uuid4().hex[:12]
        )

        return TrainingJobResponse(
            job_id=job_id,
            status="prepared",
            base_model=config.base_model,
            dataset_version=config.dataset_version,
            output_model_name=(
                config.output_model_name
            ),
            architecture=config.architecture,
            model_size=config.model_size,
            created_at=datetime.utcnow(),
            message=(
                "Training job prepared. "
                "Actual training is launched separately "
                "by the EVU research trainer."
            ),
        )


training_service = TrainingService()
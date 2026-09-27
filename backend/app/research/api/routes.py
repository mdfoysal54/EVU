from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)

from app.core.config import settings

from app.database.database import (
    get_db,
)

from app.database.models import User

from app.research.dataset.builder import (
    dataset_builder,
)

from app.research.dataset.schemas import (
    DatasetBuildRequest,
    DatasetBuildResponse,
    DatasetExportResponse,
)

from app.research.dataset.service import (
    dataset_service,
)

from app.research.training.schemas import (
    TrainingConfig,
    TrainingJobResponse,
    TrainingValidationResponse,
)

from app.research.training.service import (
    training_service,
)


router = APIRouter(
    prefix="/api/v1/research",
    tags=["EVU Research"],
)


def ensure_research_enabled():

    if not settings.RESEARCH_ENABLED:

        raise HTTPException(
            status_code=503,
            detail=(
                "EVU research system is disabled."
            ),
        )


@router.post(
    "/datasets/build",
    response_model=DatasetBuildResponse,
)
def build_dataset(
    request: DatasetBuildRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    ensure_research_enabled()

    if not settings.DATASET_BUILDER_ENABLED:

        raise HTTPException(
            status_code=503,
            detail=(
                "Dataset builder is disabled."
            ),
        )

    examples, total_candidates = (
        dataset_builder.build(
            db=db,
            user_id=current_user.id,
            request=request,
        )
    )

    return dataset_service.create_version(
        examples=examples,
        quality_threshold=(
            request.min_judge_score
        ),
        total_candidates=(
            total_candidates
        ),
    )


@router.post(
    "/datasets/export",
    response_model=DatasetExportResponse,
)
def export_dataset(
    dataset: DatasetBuildResponse,
    current_user: User = Depends(
        get_current_user
    ),
):

    ensure_research_enabled()

    if (
        dataset.accepted_examples
        != len(dataset.examples)
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset count does not "
                "match supplied examples."
            ),
        )

    return dataset_service.export_jsonl(
        dataset
    )


@router.post(
    "/training/validate",
    response_model=TrainingValidationResponse,
)
def validate_training(
    config: TrainingConfig,
    current_user: User = Depends(
        get_current_user
    ),
):

    ensure_research_enabled()

    if not settings.TRAINING_ENABLED:

        raise HTTPException(
            status_code=503,
            detail=(
                "Training system is disabled."
            ),
        )

    return training_service.validate(
        config
    )


@router.post(
    "/training/jobs",
    response_model=TrainingJobResponse,
)
def create_training_job(
    config: TrainingConfig,
    current_user: User = Depends(
        get_current_user
    ),
):

    ensure_research_enabled()

    if not settings.TRAINING_ENABLED:

        raise HTTPException(
            status_code=503,
            detail=(
                "Training system is disabled."
            ),
        )

    try:

        return training_service.create_job(
            config
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
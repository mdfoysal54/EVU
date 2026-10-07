import json

from app.model_lab.datasets.large_scale import (
    Deduplicator,
    DatasetMixer,
    DatasetSource,
    QualityFilter,
    Splitter,
)


def test_quality_filter():
    quality = QualityFilter(
        min_chars=10,
        min_words=2,
    )

    assert quality.accept(
        "This is a sufficiently useful text document."
    )

    assert not quality.accept("short")


def test_deduplication():
    dedup = Deduplicator()

    text = "EVU is an AI system."

    assert dedup.seen(text) is False
    assert dedup.seen(text) is True


def test_splitter():
    splitter = Splitter(
        validation_ratio=0.2,
        seed=42,
    )

    records = [{"id": i} for i in range(10)]

    train, validation = splitter.split(records)

    assert len(train) + len(validation) == 10
    assert len(validation) == 2


def test_mixer():
    mixer = DatasetMixer(seed=42)

    result = mixer.mix(
        [
            DatasetSource(
                name="a",
                records=[{"x": 1}],
                weight=1.0,
            ),
            DatasetSource(
                name="b",
                records=[{"x": 2}],
                weight=1.0,
            ),
        ],
        total_records=10,
    )

    assert len(result) == 10


def test_jsonl_pipeline(tmp_path):
    source = tmp_path / "source.jsonl"

    rows = [
        {
            "text": (
                "EVU is an independent artificial intelligence "
                "system designed for orchestration."
            )
        },
        {
            "text": (
                "EVU is an independent artificial intelligence "
                "system designed for orchestration."
            )
        },
        {
            "text": (
                "This is another sufficiently long training "
                "document for the dataset pipeline."
            )
        },
    ]

    source.write_text(
        "\n".join(
            json.dumps(row)
            for row in rows
        ),
        encoding="utf-8",
    )

    from app.model_lab.datasets.large_scale import (
        LargeScaleDatasetPipeline,
    )

    pipeline = LargeScaleDatasetPipeline(
        quality_filter=QualityFilter(
            min_chars=20,
            min_words=4,
        ),
        deduplicator=Deduplicator(),
        splitter=Splitter(
            validation_ratio=0.2
        ),
    )

    manifest = pipeline.process(
        [source],
        tmp_path / "output",
        dataset_name="test",
        dataset_version="v1",
    )

    assert manifest.train_records >= 1
    assert (tmp_path / "output" / "manifest.json").exists()
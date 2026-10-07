from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .dedup import Deduplicator
from .manifest import DatasetManifest
from .quality import QualityFilter
from .schema import DatasetRecord, DatasetStats
from .shard import ShardWriter
from .split import Splitter
from .stream import JSONLStream


@dataclass
class LargeScaleDatasetPipeline:
    quality_filter: QualityFilter
    deduplicator: Deduplicator
    splitter: Splitter

    def process(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path,
        *,
        dataset_name: str,
        dataset_version: str,
        text_field: str = "text",
        source_name: str = "unknown",
        license_name: str | None = None,
        records_per_shard: int = 10_000,
    ) -> DatasetManifest:
        stats = DatasetStats()
        accepted: list[dict] = []

        stream = JSONLStream(
            input_paths,
            text_field=text_field,
        )

        for raw in stream:
            stats.input_records += 1

            text = str(raw.get(text_field, "")).strip()

            if not self.quality_filter.accept(text):
                stats.rejected_records += 1
                continue

            if self.deduplicator.seen(text):
                stats.duplicate_records += 1
                continue

            record = DatasetRecord(
                text=text,
                source=str(
                    raw.get("source", source_name)
                ),
                license=raw.get(
                    "license",
                    license_name,
                ),
                language=raw.get("language"),
                record_id=raw.get("id"),
                metadata={
                    k: v
                    for k, v in raw.items()
                    if k != text_field
                },
            )

            accepted.append(record.to_dict())
            stats.accepted_records += 1

        train, validation = self.splitter.split(accepted)

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        writer = ShardWriter(
            output,
            records_per_shard=records_per_shard,
        )

        train_paths = writer.write(
            train,
            "train",
        )

        validation_paths = writer.write(
            validation,
            "validation",
        )

        manifest = DatasetManifest(
            name=dataset_name,
            version=dataset_version,
            source_count=len(input_paths),
            train_records=len(train),
            validation_records=len(validation),
            files=[
                str(path.name)
                for path in train_paths + validation_paths
            ],
            provenance=[
                {
                    "source": source_name,
                    "license": license_name,
                }
            ],
            metadata={
                "input_records": stats.input_records,
                "accepted_records": stats.accepted_records,
                "rejected_records": stats.rejected_records,
                "duplicate_records": stats.duplicate_records,
                "quality": {
                    "min_chars": self.quality_filter.min_chars,
                    "min_words": self.quality_filter.min_words,
                },
            },
        )

        manifest.save(
            output / "manifest.json"
        )

        return manifest
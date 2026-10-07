from __future__ import annotations

from collections.abc import Iterable


def bucket_by_length(
    sequences: Iterable[list[int]],
    boundaries: list[int],
) -> dict[int, list[list[int]]]:
    boundaries = sorted(set(boundaries))

    buckets = {
        boundary: []
        for boundary in boundaries
    }

    for sequence in sequences:
        length = len(sequence)

        for boundary in boundaries:
            if length <= boundary:
                buckets[boundary].append(sequence)
                break

    return buckets
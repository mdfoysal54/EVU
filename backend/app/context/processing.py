import hashlib
import re
from typing import Awaitable, Callable


def content_hash(text: str) -> str:
    normalized = " ".join(
        text.strip().split()
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def chunk_items(
    items: list[str],
    chunk_size: int = 400,
) -> list[list[str]]:
    return [
        items[i : i + chunk_size]
        for i in range(
            0,
            len(items),
            chunk_size,
        )
    ]


async def summarize_chunks_hierarchical(
    items: list[str],
    summarize_fn: Callable[[str], Awaitable[str]],
    chunk_size: int = 400,
    join_separator: str = "\n\n",
) -> str:
    """
    Map-Reduce summarization:
    1. Chunk items
    2. Summarize each chunk (Map)
    3. If multiple summaries remain, recurse until a single summary is produced (Reduce)
    """
    if not items:
        return ""

    # Base case: small enough to fit directly in one chunk
    if len(items) <= chunk_size:
        return await summarize_fn(join_separator.join(items))

    # 1. Chunking
    chunks = chunk_items(items, chunk_size=chunk_size)

    # 2. Map: Summarize each individual chunk
    intermediate_summaries: list[str] = []
    for chunk in chunks:
        chunk_text = join_separator.join(chunk)
        summary = await summarize_fn(chunk_text)
        if summary.strip():
            intermediate_summaries.append(summary.strip())

    # 3. Reduce: Recurse over intermediate summaries until final single summary
    return await summarize_chunks_hierarchical(
        items=intermediate_summaries,
        summarize_fn=summarize_fn,
        chunk_size=chunk_size,
        join_separator=join_separator,
    )


def create_abstract(
    content: str,
    max_chars: int = 256,
) -> str:
    content = re.sub(
        r"\s+",
        " ",
        content.strip(),
    )

    if len(content) <= max_chars:
        return content

    truncated = content[:max_chars]

    last_space = truncated.rfind(" ")

    if last_space > max_chars * 0.7:
        truncated = truncated[:last_space]

    return truncated.rstrip() + "..."


def create_overview(
    content: str,
    max_chars: int = 4000,
) -> str:
    content = content.strip()

    if len(content) <= max_chars:
        return content

    paragraphs = [
        p.strip()
        for p in content.split("\n\n")
        if p.strip()
    ]

    overview = ""

    for paragraph in paragraphs:
        candidate = (
            f"{overview}\n\n{paragraph}"
            if overview
            else paragraph
        )

        if len(candidate) > max_chars:
            break

        overview = candidate

    if overview:
        return overview

    return content[:max_chars].rstrip() + "..."
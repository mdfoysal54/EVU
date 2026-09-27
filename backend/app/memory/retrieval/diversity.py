def diversify_by_session(
    results: list[dict],
    *,
    max_per_session: int = 3,
) -> list[dict]:

    counts: dict[str, int] = {}
    output = []

    for result in results:

        session_id = (
            result.get("session_id")
            or "__unknown__"
        )

        count = counts.get(
            session_id,
            0,
        )

        if count >= max_per_session:
            continue

        counts[session_id] = count + 1
        output.append(result)

    return output
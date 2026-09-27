from app.ai.gateway import ai_gateway
from app.ai.synthesis.schemas import SynthesisCandidate


class SynthesisModel:
    """
    Uses the existing EVU AI Gateway.

    Synthesis never talks directly to OpenAI/Anthropic/Gemini.
    """

    def __init__(self) -> None:
        self.gateway = ai_gateway

    async def synthesize(
        self,
        prompt: str,
        candidates: list[SynthesisCandidate],
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str:

        candidate_text = []

        for index, candidate in enumerate(candidates, start=1):
            candidate_text.append(
                f"""
CANDIDATE {index}
Provider: {candidate.provider}
Model: {candidate.model}
Role: {candidate.role}
Score: {candidate.score}
Confidence: {candidate.confidence}

ANSWER:
{candidate.answer}
""".strip()
            )

        combined = "\n\n---\n\n".join(candidate_text)

        system_prompt = """
You are EVU's synthesis intelligence.

Your job is to combine several AI responses into one
high-quality final answer.

Rules:

1. Do not blindly trust any candidate.
2. Identify agreement between candidates.
3. Identify disagreements.
4. Prefer accurate, complete and well-supported information.
5. Do not invent facts simply because candidates disagree.
6. Remove duplicated information.
7. Preserve useful details.
8. If uncertainty exists, clearly state it.
9. Do not mention internal model routing unless explicitly asked.
10. Return one natural answer for the user.

You are a synthesizer, not a simple concatenator.
""".strip()

        user_prompt = f"""
USER REQUEST:

{prompt}

MODEL RESPONSES:

{combined}

Produce the best possible final answer.
""".strip()

        result = await self.gateway.chat(
            provider=provider,
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=temperature,
        )

        if isinstance(result, str):
            return result

        if isinstance(result, dict):
            return (
                result.get("content")
                or result.get("text")
                or result.get("answer")
                or str(result)
            )

        return str(result)


synthesis_model = SynthesisModel()
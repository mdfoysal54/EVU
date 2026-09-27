from app.ai.synthesis.candidate import normalize_candidates
from app.ai.synthesis.consensus import (
    calculate_consensus,
    detect_disagreements,
)
from app.ai.synthesis.schemas import (
    SynthesisRequest,
    SynthesisResponse,
)
from app.ai.synthesis.synthesizer import synthesis_model


class SynthesisEngine:

    async def run(
        self,
        request: SynthesisRequest,
    ) -> SynthesisResponse:

        candidates = normalize_candidates(
            request.candidates
        )

        if not candidates:
            raise ValueError(
                "No valid synthesis candidates were provided."
            )

        consensus = calculate_consensus(candidates)

        disagreements = detect_disagreements(
            candidates
        )

        if request.require_consensus and consensus < 0.25:
            raise ValueError(
                "Candidate responses do not have enough consensus."
            )

        answer = await synthesis_model.synthesize(
            prompt=request.prompt,
            candidates=candidates,
            provider=request.synthesis_provider,
            model=request.synthesis_model,
            temperature=request.temperature,
        )

        selected = [
            f"{candidate.provider}:{candidate.model}"
            for candidate in candidates
        ]

        return SynthesisResponse(
            answer=answer,
            candidates_used=len(candidates),
            selected_candidates=selected,
            consensus_score=consensus,
            disagreements=disagreements,
            synthesis_provider=request.synthesis_provider,
            synthesis_model=request.synthesis_model,
            metadata={
                "engine": "advanced_synthesis",
                "candidate_count": len(candidates),
            },
        )


synthesis_engine = SynthesisEngine()
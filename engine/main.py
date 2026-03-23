from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from engine.domain import detect_domain
    from engine.entropy import analyze_entropy
    from engine.interpretation import interpret_input, score_interpretation_confidence
    from engine.intent import detect_intent
    from engine.response import build_response
    from engine.routing import classify_route
    from engine.seed import decode_seed, extract_seed, merge_seed_context
except ModuleNotFoundError:
    from domain import detect_domain
    from entropy import analyze_entropy
    from interpretation import interpret_input, score_interpretation_confidence
    from intent import detect_intent
    from response import build_response
    from routing import classify_route
    from seed import decode_seed, extract_seed, merge_seed_context


app = FastAPI(
    title="IntelligentCue CQF Engine",
    description="Intent simulation and routing engine with CQF constructs.",
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    input: str = Field(..., min_length=1)
    seed: str | None = None


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    inline_seed_value, user_input = extract_seed(payload.input.strip())
    seed_value = payload.seed or inline_seed_value
    seed_context = decode_seed(seed_value)

    interpretation_result = interpret_input(user_input)
    intent_result = detect_intent(user_input)
    intent_result = {
        **intent_result,
        "confidence": score_interpretation_confidence(
            interpretation_result,
            float(intent_result["confidence"]),
        ),
    }
    domain_result = detect_domain(interpretation_result, intent_result["intent"])
    primary_domain = domain_result["primary_domain"]
    secondary_domain = domain_result.get("secondary_domain")
    routed_confidence = float(intent_result["confidence"])
    outcome_signal_present = bool(domain_result.get("outcome_priority"))
    entropy_result = analyze_entropy(user_input, intent_result["intent"])
    intent_result, entropy_result, _ = merge_seed_context(
        user_input=user_input,
        seed_context=seed_context,
        intent_result=intent_result,
        entropy_result=entropy_result,
        route_result=None,
    )
    route_result = classify_route(
        intent=intent_result["intent"],
        primary_domain=primary_domain,
        secondary_domain=secondary_domain,
        outcome_signal_present=outcome_signal_present,
        confidence=routed_confidence,
        entropy_data=entropy_result["missing_data"],
    )

    return build_response(
        user_input=user_input,
        domain_result=domain_result,
        intent_result=intent_result,
        entropy_result=entropy_result,
        route_result=route_result,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from engine.entropy import analyze_entropy
    from engine.intent import detect_intent
    from engine.response import build_response
    from engine.routing import classify_route
except ModuleNotFoundError:
    from entropy import analyze_entropy
    from intent import detect_intent
    from response import build_response
    from routing import classify_route


app = FastAPI(
    title="IntelligentCue CQF Engine",
    description="Intent simulation and routing engine with CQF constructs.",
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    input: str = Field(..., min_length=1)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    user_input = payload.input.strip()

    intent_result = detect_intent(user_input)
    entropy_result = analyze_entropy(user_input, intent_result["intent"])
    route_result = classify_route(
        user_input,
        intent_result["intent"],
        entropy_result["missing_data"],
    )

    return build_response(
        user_input=user_input,
        intent_result=intent_result,
        entropy_result=entropy_result,
        route_result=route_result,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

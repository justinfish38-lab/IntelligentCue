from __future__ import annotations

from typing import Any


ASSUMPTION_PHRASES = [
    "based on what you've said",
    "based on what you've shown",
    "it sounds like",
]

TEMPLATE_PHRASES = [
    "when a store is",
    "if the effort is there",
    "if x is happening",
    "the problem is usually",
    "the gap is",
    "the first priority is",
    "when audience growth stalls",
    "when life feels unclear",
    "the strongest signal here",
    "the real issue",
    "the useful move is",
]

ABSTRACT_TERMS = [
    "signal",
    "baseline",
    "underlying factor",
    "real issue",
    "core issue",
    "clearest path",
    "strongest signal",
    "feedback loop",
    "carrying more weight",
]

WEAK_ABSTRACTIONS = [
    "one part",
    "something is",
    "the situation",
    "things are",
    "what is actually happening",
    "where this is getting stuck",
]

COMMITMENT_MARKERS = [
    "usually",
    "most of the time",
    "tends to mean",
    "probably",
]

DOMAIN_CONCRETE_MARKERS = {
    "business": ["sales", "buy", "price", "store", "people", "reach", "attention"],
    "creative": ["work", "art", "music", "writing", "people", "reach", "seen"],
    "life": ["choice", "pressure", "job", "future", "energy", "decision"],
    "technical": ["router", "line", "server", "code", "api", "connection", "error"],
    "gaming": ["match", "play", "mistake", "rank", "game", "aim"],
    "general": ["people", "work", "result", "trying"],
}


def _has_repetition(response: str) -> bool:
    lowered = response.lower()
    repeated_fragments = [
        "people seeing it",
        "what you're trying to improve",
        "not working",
    ]
    return any(lowered.count(fragment) > 1 for fragment in repeated_fragments)


def verify_output(
    response: str,
    route: str,
    domain_result: dict[str, Any],
    behavior_mode: str,
    missing_data: list[str],
) -> dict[str, str | bool]:
    adjusted_response = response
    adjusted_route = route
    template_like = False

    for phrase in ASSUMPTION_PHRASES:
        adjusted_response = adjusted_response.replace(phrase, "")

    if domain_result.get("outcome_priority") and "skill_growth_pipeline" in adjusted_route:
        adjusted_route = adjusted_route.replace("skill_growth_pipeline", "creative_traction_pipeline")

    if len(missing_data) >= 3 and behavior_mode != "redirect":
        adjusted_response = adjusted_response.replace("This points more toward", "This may be more about").replace(
            "This points more strongly toward",
            "This may be more about",
        )

    lowered = adjusted_response.lower().strip()
    if any(lowered.startswith(phrase) for phrase in TEMPLATE_PHRASES):
        template_like = True

    if any(term in lowered for term in ABSTRACT_TERMS):
        template_like = True

    if any(term in lowered for term in WEAK_ABSTRACTIONS):
        template_like = True

    if not any(marker in lowered for marker in COMMITMENT_MARKERS):
        template_like = True

    primary_domain = str(domain_result.get("primary_domain", "general"))
    concrete_markers = DOMAIN_CONCRETE_MARKERS.get(primary_domain, DOMAIN_CONCRETE_MARKERS["general"])
    if not any(marker in lowered for marker in concrete_markers):
        template_like = True

    if _has_repetition(adjusted_response):
        template_like = True

    adjusted_response = " ".join(adjusted_response.split())

    return {
        "response": adjusted_response.strip(),
        "route": adjusted_route,
        "template_like": template_like,
    }

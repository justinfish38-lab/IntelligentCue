from __future__ import annotations

from typing import Any


ROUTE_MAP = {
    "ecommerce_performance_failure": "commerce_diagnosis_pipeline",
    "business_launch_uncertainty": "launch_strategy_pipeline",
    "creative_skill_development": "skill_growth_pipeline",
    "product_market_validation": "validation_pipeline",
    "audience_growth_block": "audience_growth_pipeline",
}


def _calculate_cqu(
    impact: float,
    reusability: float,
    observability: float,
    adaptivity: float,
    cost: float,
) -> float:
    if cost <= 0:
        return 0.0
    return round((impact * reusability * observability * adaptivity) / cost, 2)


def classify_route(
    user_input: str,
    intent: str,
    missing_data: list[str],
) -> dict[str, Any]:
    route = ROUTE_MAP.get(intent, "validation_pipeline")

    if missing_data:
        route = f"{route}_with_entropy_reduction"

    lowered = user_input.lower()
    if any(word in lowered for word in ["translate", "rewrite", "convert"]):
        route = "translation_pipeline"

    profile = {
        "S": 41,
        "A": 61,
        "B": 83,
        "I": 69,
        "P": 74,
    }
    construct = {
        "name": "routing_classification",
        "type": "Routing Construct",
        "profile": profile,
        "cqu": _calculate_cqu(9.0, 8.5, 8.2, 8.4, 3.3),
    }

    return {
        "route": route,
        "construct": construct,
    }

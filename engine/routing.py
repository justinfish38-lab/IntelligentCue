from __future__ import annotations

from typing import Any


ROUTE_MAP = {
    "ecommerce_performance_failure": "commerce_diagnosis_pipeline",
    "business_launch_uncertainty": "launch_strategy_pipeline",
    "creative_skill_development": "skill_growth_pipeline",
    "product_market_validation": "validation_pipeline",
    "audience_growth_block": "audience_growth_pipeline",
}

INTENT_DOMAIN_MAP = {
    "ecommerce_performance_failure": "business",
    "business_launch_uncertainty": "business",
    "creative_skill_development": "creative",
    "personal_growth": "life",
    "life_direction_uncertainty": "life",
    "product_market_validation": "business",
    "audience_growth_block": "business",
}

DOMAIN_ROUTE_MAP = {
    "business": "business_context_pipeline",
    "creative": "creative_context_pipeline",
    "life": "life_context_pipeline",
    "technical": "technical_context_pipeline",
    "gaming": "gaming_context_pipeline",
    "general": "general_context_pipeline",
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
    domain: str,
    missing_data: list[str],
) -> dict[str, Any]:
    domain_route = DOMAIN_ROUTE_MAP.get(domain, "general_context_pipeline")
    intent_route = ROUTE_MAP.get(intent)
    intent_domain = INTENT_DOMAIN_MAP.get(intent)

    if intent_route and (intent_domain is None or intent_domain == domain or domain == "general"):
        route = intent_route
    else:
        route = domain_route

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

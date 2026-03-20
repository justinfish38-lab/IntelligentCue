from __future__ import annotations

import re
from typing import Any


INTENT_RULES = {
    "ecommerce_performance_failure": {
        "keywords": {
            "shopify",
            "store",
            "sales",
            "purchase",
            "orders",
            "customers",
            "cart",
            "traffic",
            "conversion",
            "ads",
            "roas",
        },
        "patterns": [
            r"not getting (any )?sales",
            r"no sales",
            r"store.*not converting",
            r"traffic.*no sales",
            r"low conversion",
        ],
    },
    "business_launch_uncertainty": {
        "keywords": {
            "launch",
            "start",
            "business",
            "idea",
            "offer",
            "pricing",
            "service",
            "client",
            "freelance",
            "agency",
        },
        "patterns": [
            r"should i start",
            r"thinking about launching",
            r"not sure .* business",
            r"don't know how to launch",
        ],
    },
    "creative_skill_development": {
        "keywords": {
            "art",
            "draw",
            "drawing",
            "music",
            "write",
            "writing",
            "design",
            "creative",
            "practice",
            "improve",
            "portfolio",
        },
        "patterns": [
            r"how do i get better",
            r"want to improve .* skill",
            r"stuck .* creative",
            r"build a portfolio",
        ],
    },
    "product_market_validation": {
        "keywords": {
            "product",
            "market",
            "validate",
            "validation",
            "mvp",
            "demand",
            "audience",
            "users",
            "problem",
            "fit",
            "customer",
        },
        "patterns": [
            r"validate .* idea",
            r"product.market fit",
            r"will people buy",
            r"does anyone want",
        ],
    },
    "audience_growth_block": {
        "keywords": {
            "followers",
            "audience",
            "growth",
            "content",
            "views",
            "reach",
            "newsletter",
            "subscribers",
            "social",
        },
        "patterns": [
            r"not growing",
            r"no traction",
            r"not getting views",
            r"audience isn't growing",
        ],
    },
}


def _score_profile(
    structural: int,
    activity: int,
    behavior: int,
    information: int,
    portability: int,
) -> dict[str, int]:
    return {
        "S": structural,
        "A": activity,
        "B": behavior,
        "I": information,
        "P": portability,
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


def _score_intent(lowered: str, tokens: set[str], rule: dict[str, Any]) -> int:
    keyword_hits = len(tokens.intersection(rule["keywords"]))
    pattern_hits = sum(1 for pattern in rule["patterns"] if re.search(pattern, lowered))
    return keyword_hits + (pattern_hits * 3)


def detect_intent(user_input: str) -> dict[str, Any]:
    lowered = user_input.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    tokens = set(normalized.split())

    best_intent = "business_launch_uncertainty"
    best_score = 0

    for intent, rule in INTENT_RULES.items():
        score = _score_intent(lowered, tokens, rule)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score == 0:
        if any(word in tokens for word in {"sell", "sales", "customers", "store"}):
            best_intent = "ecommerce_performance_failure"
            best_score = 2
        elif any(word in tokens for word in {"launch", "business", "idea"}):
            best_intent = "business_launch_uncertainty"
            best_score = 2
        elif any(word in tokens for word in {"creative", "design", "draw", "music"}):
            best_intent = "creative_skill_development"
            best_score = 2
        else:
            best_intent = "product_market_validation"
            best_score = 1

    confidence = min(0.96, 0.52 + (best_score * 0.08))

    profile = _score_profile(34, 48, 82, 74, 79)
    construct = {
        "name": "intent_detection",
        "type": "Intent Construct",
        "profile": profile,
        "cqu": _calculate_cqu(8.8, 8.9, 8.4, 8.0, 3.4),
    }

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "construct": construct,
    }

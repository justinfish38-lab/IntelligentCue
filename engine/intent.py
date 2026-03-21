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
            "paint",
            "painting",
            "illustration",
            "sketch",
            "music",
            "guitar",
            "piano",
            "write",
            "writing",
            "poetry",
            "design",
            "creative",
            "practice",
            "improve",
            "better",
            "learn",
            "study",
            "skill",
            "craft",
            "portfolio",
        },
        "patterns": [
            r"how do i get better",
            r"want to get better",
            r"want to improve .* skill",
            r"want to get better at",
            r"how do i improve",
            r"how can i improve",
            r"learning .*",
            r"stuck .* creative",
            r"build a portfolio",
        ],
    },
    "personal_growth": {
        "keywords": {
            "discipline",
            "habit",
            "habits",
            "motivation",
            "focus",
            "confidence",
            "mindset",
            "routine",
            "improve",
            "progress",
            "better",
            "stuck",
            "burnout",
        },
        "patterns": [
            r"why am i not improving",
            r"i keep falling behind",
            r"how do i stay consistent",
            r"i'm stuck",
            r"not making progress",
        ],
    },
    "life_direction_uncertainty": {
        "keywords": {
            "life",
            "direction",
            "career",
            "path",
            "future",
            "purpose",
            "choose",
            "choice",
            "decision",
            "next",
            "long term",
            "lost",
        },
        "patterns": [
            r"what should i do with my life",
            r"not sure what to do",
            r"don't know what to do",
            r"which path should i take",
            r"where should i go next",
            r"i feel lost",
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
            "users",
            "fit",
            "customer",
            "customers",
            "sell",
            "selling",
            "business",
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


def _commercial_signal(tokens: set[str], lowered: str) -> bool:
    commercial_keywords = {
        "product",
        "business",
        "customer",
        "customers",
        "sell",
        "selling",
        "market",
        "store",
        "sales",
    }
    return bool(tokens.intersection(commercial_keywords)) or bool(
        re.search(r"\b(product|business|customer|customers|sell|selling|market)\b", lowered)
    )


def detect_intent(user_input: str) -> dict[str, Any]:
    lowered = user_input.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    tokens = set(normalized.split())

    best_intent = "personal_growth"
    best_score = 0

    for intent, rule in INTENT_RULES.items():
        score = _score_intent(lowered, tokens, rule)
        if intent == "product_market_validation" and not _commercial_signal(tokens, lowered):
            score = 0
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
        elif any(
            word in tokens
            for word in {
                "creative",
                "design",
                "draw",
                "drawing",
                "paint",
                "painting",
                "music",
                "write",
                "writing",
                "learn",
                "skill",
                "improve",
            }
        ):
            best_intent = "creative_skill_development"
            best_score = 2
        elif any(
            word in tokens
            for word in {"life", "direction", "career", "future", "path", "lost", "purpose"}
        ):
            best_intent = "life_direction_uncertainty"
            best_score = 2
        elif any(
            word in tokens
            for word in {"habit", "habits", "discipline", "focus", "confidence", "routine", "progress"}
        ):
            best_intent = "personal_growth"
            best_score = 2
        else:
            best_intent = "personal_growth"
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

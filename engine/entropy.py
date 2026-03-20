from __future__ import annotations

from typing import Any


ECOMMERCE_FIELDS = [
    ("traffic source", {"traffic", "visitors", "organic", "paid", "ads", "seo", "social"}),
    ("product type", {"product", "sku", "apparel", "jewelry", "supplement", "course"}),
    ("pricing strategy", {"price", "pricing", "discount", "offer", "premium", "cheap"}),
    ("conversion rate", {"conversion", "cvr", "add to cart", "checkout"}),
    ("marketing channel", {"email", "tiktok", "instagram", "facebook", "google", "youtube"}),
]


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


def _contains_any(lowered: str, markers: set[str]) -> bool:
    return any(marker in lowered for marker in markers)


def _ecommerce_missing_data(lowered: str) -> list[str]:
    missing_data: list[str] = []
    for label, markers in ECOMMERCE_FIELDS:
        if not _contains_any(lowered, markers):
            missing_data.append(label)
    return missing_data[:4]


def _general_missing_data(lowered: str, intent: str) -> list[str]:
    missing_data: list[str] = []

    if intent == "business_launch_uncertainty":
        if not _contains_any(lowered, {"idea", "product", "service", "offer"}):
            missing_data.append("what you're trying to sell")
        if not _contains_any(lowered, {"customer", "audience", "market", "niche"}):
            missing_data.append("who the buyer is")
        if not _contains_any(lowered, {"budget", "time", "cash", "runway"}):
            missing_data.append("what constraints you're operating under")
        if not _contains_any(lowered, {"launched", "started", "testing", "selling"}):
            missing_data.append("how far along the launch is")

    elif intent == "creative_skill_development":
        if not _contains_any(lowered, {"draw", "drawing", "design", "writing", "music", "editing"}):
            missing_data.append("which creative skill you're trying to improve")
        if not _contains_any(lowered, {"daily", "weekly", "practice", "hours", "routine"}):
            missing_data.append("what your current practice volume looks like")
        if not _contains_any(lowered, {"goal", "job", "client", "portfolio", "audition"}):
            missing_data.append("what outcome you're aiming for")
        if not _contains_any(lowered, {"stuck", "weak", "struggle", "problem"}):
            missing_data.append("where the actual bottleneck is")

    elif intent == "product_market_validation":
        if not _contains_any(lowered, {"problem", "pain", "need"}):
            missing_data.append("what problem the product solves")
        if not _contains_any(lowered, {"customer", "user", "audience", "market"}):
            missing_data.append("who the target customer is")
        if not _contains_any(lowered, {"test", "survey", "landing page", "preorder", "interview"}):
            missing_data.append("what validation you've already run")
        if not _contains_any(lowered, {"buy", "paid", "price", "willing"}):
            missing_data.append("whether anyone has shown buying intent")

    elif intent == "audience_growth_block":
        if not _contains_any(lowered, {"platform", "instagram", "tiktok", "youtube", "x", "newsletter"}):
            missing_data.append("which platform matters most")
        if not _contains_any(lowered, {"post", "content", "video", "emails"}):
            missing_data.append("what you're publishing right now")
        if not _contains_any(lowered, {"daily", "weekly", "consistent", "schedule"}):
            missing_data.append("how consistent your output is")
        if not _contains_any(lowered, {"views", "reach", "clicks", "subs", "followers"}):
            missing_data.append("what the current performance numbers look like")

    if not missing_data and len(lowered.split()) >= 4:
        missing_data = [
            "the current baseline numbers",
            "what you've already tried",
        ]

    return missing_data[:4]


def analyze_entropy(user_input: str, intent: str) -> dict[str, Any]:
    lowered = user_input.lower()

    if intent == "ecommerce_performance_failure":
        missing_data = _ecommerce_missing_data(lowered)
        if len(missing_data) < 2:
            for fallback in ["traffic source", "conversion rate", "pricing strategy"]:
                if fallback not in missing_data:
                    missing_data.append(fallback)
                if len(missing_data) == 2:
                    break
    else:
        missing_data = _general_missing_data(lowered, intent)

    if len(lowered.split()) >= 4 and not missing_data:
        missing_data = [
            "the current baseline numbers",
            "what result you're trying to reach",
        ]

    profile = {
        "S": 39,
        "A": 57,
        "B": 71,
        "I": 89,
        "P": 78,
    }
    construct = {
        "name": "entropy_analysis",
        "type": "Entropy Construct",
        "profile": profile,
        "cqu": _calculate_cqu(8.4, 8.7, 9.0, 8.2, 3.2),
    }

    return {
        "missing_data": missing_data[:4],
        "construct": construct,
    }

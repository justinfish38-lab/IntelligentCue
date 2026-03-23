from __future__ import annotations

import re


SIGNAL_CLUSTERS = [
    {
        "name": "commerce_outcome",
        "domain": "business",
        "strength": "strong",
        "anchors": {"sales", "store", "customers", "orders", "etsy", "shopify"},
        "support": {"pricing", "traffic", "offer", "buying"},
        "phrases": [r"no sales", r"not getting sales", r"people (?:are )?not buying"],
        "kind": "outcome",
    },
    {
        "name": "creative_work",
        "domain": "creative",
        "strength": "strong",
        "anchors": {"music", "painting", "art", "drawing", "writing", "design"},
        "support": {"creative", "portfolio", "work", "song", "paint", "draw"},
        "phrases": [r"people say it's good", r"my art", r"my music"],
        "kind": "activity",
    },
    {
        "name": "creative_progress",
        "domain": "creative",
        "strength": "support",
        "anchors": {"practice", "practicing", "learning", "improving", "skill"},
        "support": {"better", "study", "working", "trying"},
        "phrases": [r"get better at", r"working on", r"trying to improve"],
        "kind": "effort",
    },
    {
        "name": "traction_gap",
        "domain": "business",
        "strength": "strong",
        "anchors": {"traction", "growth", "results", "audience", "reach"},
        "support": {"attention", "momentum", "distribution", "response"},
        "phrases": [r"nothing is happening", r"not growing", r"no traction", r"no results"],
        "kind": "outcome",
    },
    {
        "name": "life_choice",
        "domain": "life",
        "strength": "strong",
        "anchors": {"life", "future", "career", "path", "direction", "purpose"},
        "support": {"choice", "decision", "lost", "next"},
        "phrases": [r"what should i do with my life", r"which path should i take", r"feel lost"],
        "kind": "context",
    },
    {
        "name": "personal_progress",
        "domain": "life",
        "strength": "support",
        "anchors": {"progress", "discipline", "focus", "habit", "motivation"},
        "support": {"routine", "stuck", "consistent", "confidence"},
        "phrases": [r"not making progress", r"stay consistent"],
        "kind": "outcome",
    },
    {
        "name": "technical_break",
        "domain": "technical",
        "strength": "strong",
        "anchors": {"code", "bug", "api", "server", "python", "build"},
        "support": {"error", "debug", "deploy", "stack"},
        "phrases": [r"not working", r"build failed", r"api error"],
        "kind": "outcome",
    },
    {
        "name": "gaming_performance",
        "domain": "gaming",
        "strength": "strong",
        "anchors": {"game", "gaming", "rank", "match", "fps", "quest"},
        "support": {"weapon", "aim", "level", "character"},
        "phrases": [r"how do i climb", r"ranked match"],
        "kind": "context",
    },
]

OUTCOME_PATTERNS = [
    r"nothing is happening",
    r"not growing",
    r"no results",
    r"not working",
    r"no sales",
    r"no traction",
    r"no progress",
]

EFFORT_PATTERNS = [
    r"learning",
    r"practicing",
    r"improving",
    r"trying",
    r"working on",
]


def _score_cluster(lowered: str, tokens: set[str], cluster: dict) -> int:
    strength_weight = 3 if cluster["strength"] == "strong" else 2
    anchor_hits = len(tokens.intersection(cluster["anchors"])) * strength_weight
    support_hits = len(tokens.intersection(cluster["support"]))
    phrase_hits = sum(strength_weight for pattern in cluster["phrases"] if re.search(pattern, lowered))
    return anchor_hits + support_hits + phrase_hits


def interpret_input(user_input: str) -> dict:
    lowered = user_input.lower()
    normalized = re.sub(r"[^a-z0-9\s']", " ", lowered)
    tokens = set(normalized.split())

    scored_clusters = []
    for cluster in SIGNAL_CLUSTERS:
        score = _score_cluster(lowered, tokens, cluster)
        if score > 0:
            scored_clusters.append(
                {
                    "name": cluster["name"],
                    "domain": cluster["domain"],
                    "score": score,
                    "strength": cluster["strength"],
                    "kind": cluster["kind"],
                }
            )

    scored_clusters.sort(key=lambda item: item["score"], reverse=True)
    top_clusters = scored_clusters[:3]

    outcome_signal_present = any(re.search(pattern, lowered) for pattern in OUTCOME_PATTERNS)
    effort_signal_present = any(re.search(pattern, lowered) for pattern in EFFORT_PATTERNS)

    return {
        "dominant_signal_clusters": top_clusters,
        "outcome_signal_present": outcome_signal_present,
        "effort_signal_present": effort_signal_present,
    }


def score_interpretation_confidence(interpretation_result: dict, intent_confidence: float) -> float:
    clusters = interpretation_result["dominant_signal_clusters"]
    if not clusters:
        return 0.42

    top_score = clusters[0]["score"]
    secondary_score = clusters[1]["score"] if len(clusters) > 1 else 0

    if top_score >= 6 and top_score >= secondary_score + 2:
        signal_confidence = 0.84
    elif top_score >= 4:
        signal_confidence = 0.68
    else:
        signal_confidence = 0.54

    if interpretation_result["outcome_signal_present"] and clusters:
        signal_confidence += 0.04

    blended = (signal_confidence + float(intent_confidence)) / 2
    return round(min(0.96, max(0.35, blended)), 2)

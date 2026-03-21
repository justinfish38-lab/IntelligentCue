from __future__ import annotations

import re


DOMAIN_CLUSTERS = [
    {
        "name": "commerce_platforms",
        "domain": "business",
        "weight": 3,
        "anchors": {"shopify", "etsy", "store", "sales", "selling", "customers"},
        "support": {"pricing", "conversion", "traffic", "orders", "offer"},
        "phrases": [r"not getting sales", r"no sales", r"low conversion"],
    },
    {
        "name": "product_validation",
        "domain": "business",
        "weight": 3,
        "anchors": {"product", "market", "customer", "business", "mvp"},
        "support": {"demand", "fit", "validate", "launch", "sell"},
        "phrases": [r"product market fit", r"validate .* idea", r"will people buy"],
    },
    {
        "name": "creative_practice",
        "domain": "creative",
        "weight": 3,
        "anchors": {"paint", "painting", "draw", "drawing", "music", "writing"},
        "support": {"practice", "creative", "skill", "improve", "portfolio", "art"},
        "phrases": [r"get better at", r"how do i improve", r"creative skill"],
    },
    {
        "name": "life_direction",
        "domain": "life",
        "weight": 3,
        "anchors": {"life", "career", "future", "path", "purpose", "direction"},
        "support": {"lost", "choice", "decision", "next", "long", "term"},
        "phrases": [r"what should i do with my life", r"which path should i take", r"feel lost"],
    },
    {
        "name": "personal_progress",
        "domain": "life",
        "weight": 2,
        "anchors": {"habit", "discipline", "motivation", "focus", "confidence"},
        "support": {"progress", "consistent", "routine", "stuck", "improve"},
        "phrases": [r"not making progress", r"how do i stay consistent"],
    },
    {
        "name": "technical_build",
        "domain": "technical",
        "weight": 3,
        "anchors": {"code", "bug", "build", "api", "python", "server"},
        "support": {"error", "deploy", "debug", "stack", "fastapi"},
        "phrases": [r"not working", r"build failed", r"api error"],
    },
    {
        "name": "gaming_play",
        "domain": "gaming",
        "weight": 3,
        "anchors": {"game", "gaming", "rank", "fps", "quest", "build"},
        "support": {"match", "level", "character", "weapon", "aim"},
        "phrases": [r"ranked match", r"how do i climb", r"game build"],
    },
]


EMOTIONAL_MODIFIERS = {
    "frustration": {"stuck", "sucks", "frustrated", "not working", "wtf"},
    "doubt": {"maybe", "not sure", "i think", "unsure"},
    "pressure": {"urgent", "asap", "quickly", "pressure"},
    "urgency": {"now", "immediately", "today"},
}

OUTCOME_SIGNALS = [
    r"nothing is happening",
    r"not growing",
    r"no results",
    r"not working",
    r"no sales",
    r"no traction",
    r"no progress",
]

EFFORT_SIGNALS = [
    r"learning",
    r"practicing",
    r"improving",
    r"trying",
    r"working on",
]


def _score_cluster(lowered: str, tokens: set[str], cluster: dict) -> int:
    anchor_hits = len(tokens.intersection(cluster["anchors"])) * cluster["weight"]
    support_hits = len(tokens.intersection(cluster["support"]))
    phrase_hits = sum(cluster["weight"] for pattern in cluster["phrases"] if re.search(pattern, lowered))
    return anchor_hits + support_hits + phrase_hits


def detect_domain(user_input: str, intent: str) -> dict[str, str | None]:
    lowered = user_input.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    tokens = set(normalized.split())

    cluster_scores = []
    domain_scores = {domain: 0 for domain in ["business", "creative", "life", "technical", "gaming"]}

    for cluster in DOMAIN_CLUSTERS:
        score = _score_cluster(lowered, tokens, cluster)
        if score > 0:
            cluster_scores.append((cluster["name"], cluster["domain"], score))
            domain_scores[cluster["domain"]] += score

    has_outcome_signal = any(re.search(pattern, lowered) for pattern in OUTCOME_SIGNALS)
    has_effort_signal = any(re.search(pattern, lowered) for pattern in EFFORT_SIGNALS)
    creative_signal = domain_scores["creative"] > 0

    if has_outcome_signal:
        if creative_signal:
            domain_scores["business"] += 2
        else:
            domain_scores["business"] += 3

    if has_effort_signal and not has_outcome_signal and creative_signal:
        domain_scores["creative"] += 1

    cluster_scores.sort(key=lambda item: item[2], reverse=True)
    top_clusters = cluster_scores[:3]

    for modifier_terms in EMOTIONAL_MODIFIERS.values():
        _ = any(term in lowered for term in modifier_terms)

    if not top_clusters:
        return {
            "primary_domain": "general",
            "secondary_domain": None,
            "confidence": "low",
        }

    ranked_domains = sorted(domain_scores.items(), key=lambda item: item[1], reverse=True)
    primary_domain, primary_score = ranked_domains[0]
    secondary_domain = None
    secondary_score = 0

    for domain, score in ranked_domains[1:]:
        if score > 0:
            secondary_domain = domain
            secondary_score = score
            break

    if intent in {"creative_skill_development"} and primary_domain != "creative":
        primary_domain = "creative"
    elif intent in {"personal_growth", "life_direction_uncertainty"} and primary_domain == "general":
        primary_domain = "life"
    elif intent in {
        "ecommerce_performance_failure",
        "business_launch_uncertainty",
        "product_market_validation",
    } and primary_domain == "general":
        primary_domain = "business"

    if primary_score >= 6 and (secondary_score == 0 or primary_score >= secondary_score + 3):
        confidence = "high"
    elif primary_score >= 3:
        confidence = "medium"
    else:
        primary_domain = "general"
        secondary_domain = None
        confidence = "low"

    if secondary_domain == primary_domain:
        secondary_domain = None

    return {
        "primary_domain": primary_domain,
        "secondary_domain": secondary_domain,
        "confidence": confidence,
    }

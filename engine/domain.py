from __future__ import annotations


def detect_domain(interpretation_result: dict, intent: str) -> dict[str, str | bool | None | list]:
    top_clusters = interpretation_result["dominant_signal_clusters"]

    if not top_clusters:
        return {
            "primary_domain": "general",
            "secondary_domain": None,
            "confidence": "low",
            "outcome_priority": False,
            "dominant_signal_clusters": [],
        }

    domain_scores = {domain: 0 for domain in ["business", "creative", "life", "technical", "gaming"]}
    for cluster in top_clusters:
        domain_scores[cluster["domain"]] += int(cluster["score"])

    has_outcome_signal = bool(interpretation_result["outcome_signal_present"])
    has_effort_signal = bool(interpretation_result["effort_signal_present"])
    creative_signal = domain_scores["creative"] > 0

    if has_outcome_signal:
        if creative_signal:
            domain_scores["business"] += 2
        else:
            domain_scores["business"] += 3

    if has_effort_signal and not has_outcome_signal and creative_signal:
        domain_scores["creative"] += 1

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
        "outcome_priority": has_outcome_signal,
        "dominant_signal_clusters": top_clusters,
    }

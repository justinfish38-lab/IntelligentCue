from __future__ import annotations

import re


TECHNICAL_MARKERS = {
    "conversion",
    "distribution",
    "traction",
    "strategy",
    "pricing",
    "architecture",
    "api",
    "pipeline",
    "validation",
    "technical",
}


def detect_cognitive_level(user_input: str) -> dict[str, str]:
    lowered = user_input.lower()
    words = re.findall(r"\b[\w']+\b", lowered)
    long_words = sum(1 for word in words if len(word) >= 8)
    technical_hits = sum(1 for word in words if word in TECHNICAL_MARKERS)
    clause_markers = sum(lowered.count(marker) for marker in [",", " because ", " but ", " although ", " while "])

    if len(words) <= 8 and technical_hits == 0 and clause_markers <= 1:
        level = "low"
    elif technical_hits >= 2 or long_words >= 6 or clause_markers >= 3:
        level = "high"
    else:
        level = "medium"

    return {"level": level}

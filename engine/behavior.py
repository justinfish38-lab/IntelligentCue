from __future__ import annotations

import re


def detect_behavior(
    user_input: str,
    intent_confidence: float,
    tone: str,
    missing_data: list[str],
) -> dict[str, float | str]:
    lowered = user_input.lower()

    redirect_signals = [
        "be honest",
        "honestly",
        "truthfully",
        "brutally honest",
        "should i keep",
        "should i continue",
        "am i wasting",
        "wrong direction",
    ]
    repetition_signals = [
        "still",
        "again",
        "keeps happening",
        "tried everything",
        "nothing works",
        "not working",
        "stuck",
    ]

    strong_redirect = any(signal in lowered for signal in redirect_signals)
    repeated_failure = any(signal in lowered for signal in repetition_signals)
    severe_entropy = len(missing_data) >= 3

    if intent_confidence >= 0.85 and strong_redirect:
        return {
            "mode": "redirect",
            "confidence": 0.9,
            "reason": "high-confidence mismatch or explicit request for blunt reorientation",
        }

    if intent_confidence >= 0.82 and repeated_failure and not severe_entropy:
        return {
            "mode": "push",
            "confidence": 0.86,
            "reason": "user appears stuck and a correction path is likely",
        }

    if intent_confidence >= 0.84 and tone == "frustrated" and len(missing_data) <= 2:
        return {
            "mode": "push",
            "confidence": 0.83,
            "reason": "frustration plus enough clarity to be more direct",
        }

    if intent_confidence >= 0.88 and re.search(r"\b(quit|pivot|keep going)\b", lowered):
        return {
            "mode": "redirect",
            "confidence": 0.88,
            "reason": "user is asking for a decisive directional correction",
        }

    return {
        "mode": "guide",
        "confidence": 0.74 if severe_entropy or tone == "uncertain" else 0.7,
        "reason": "more context is needed or the user needs a lower-force steer",
    }

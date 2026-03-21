from __future__ import annotations

import re


TONE_RULES = {
    "casual": {
        "keywords": {
            "lol",
            "bro",
            "idk",
            "kinda",
            "sorta",
            "nah",
            "yeah",
            "stuff",
        },
        "patterns": [
            r"\blmao\b",
            r"\bwtf\b",
            r"\bimo\b",
            r"\bngl\b",
        ],
    },
    "frustrated": {
        "keywords": {
            "sucks",
            "annoying",
            "broken",
            "stuck",
            "failed",
            "waste",
            "useless",
            "frustrating",
        },
        "patterns": [
            r"not working",
            r"this sucks",
            r"nothing works",
            r"so tired of",
            r"can't get .* to work",
        ],
    },
    "uncertain": {
        "keywords": {
            "maybe",
            "perhaps",
            "guess",
            "unsure",
            "uncertain",
            "wondering",
        },
        "patterns": [
            r"i think",
            r"not sure",
            r"might be",
            r"could be",
            r"i'm not sure",
        ],
    },
}


def detect_tone(user_input: str) -> dict[str, float | str]:
    lowered = user_input.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    tokens = set(normalized.split())

    best_tone = "serious"
    best_score = 0

    for tone, rule in TONE_RULES.items():
        keyword_hits = len(tokens.intersection(rule["keywords"]))
        pattern_hits = sum(1 for pattern in rule["patterns"] if re.search(pattern, lowered))
        score = keyword_hits + (pattern_hits * 2)
        if score > best_score:
            best_score = score
            best_tone = tone

    if best_score == 0:
        confidence = 0.62
    else:
        confidence = min(0.94, 0.58 + (best_score * 0.09))

    return {
        "tone": best_tone,
        "confidence": round(confidence, 2),
    }

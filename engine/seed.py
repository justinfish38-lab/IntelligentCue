from __future__ import annotations

import base64
import json
import re
from typing import Any


SEED_PATTERN = re.compile(r"(?:^|\s)seed:([A-Za-z0-9+/=_-]+)")


def extract_seed(user_input: str) -> tuple[str | None, str]:
    match = SEED_PATTERN.search(user_input)
    if not match:
        return None, user_input.strip()

    seed_value = match.group(1)
    cleaned_input = SEED_PATTERN.sub(" ", user_input).strip()
    return seed_value, re.sub(r"\s+", " ", cleaned_input)


def decode_seed(seed_value: str | None) -> dict[str, Any] | None:
    if not seed_value:
        return None

    try:
        padding = (-len(seed_value)) % 4
        normalized = seed_value + ("=" * padding)
        decoded = base64.urlsafe_b64decode(normalized.encode("utf-8")).decode("utf-8")
        payload = json.loads(decoded)
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    intent = payload.get("intent")
    route = payload.get("route")
    missing_data = payload.get("missing_data")

    if not isinstance(intent, str) or not isinstance(route, str) or not isinstance(missing_data, list):
        return None

    sanitized_missing = [item for item in missing_data if isinstance(item, str)][:4]

    return {
        "intent": intent,
        "route": route,
        "missing_data": sanitized_missing,
    }


def encode_seed(intent: str, route: str, missing_data: list[str]) -> str:
    payload = {
        "intent": intent,
        "route": route,
        "missing_data": missing_data[:4],
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def merge_seed_context(
    user_input: str,
    seed_context: dict[str, Any] | None,
    intent_result: dict[str, Any],
    entropy_result: dict[str, Any],
    route_result: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    if not seed_context:
        return intent_result, entropy_result, route_result

    merged_missing: list[str] = []
    for item in entropy_result["missing_data"] + seed_context.get("missing_data", []):
        if item not in merged_missing:
            merged_missing.append(item)

    if len(user_input.split()) <= 5 and intent_result["confidence"] < 0.75:
        intent_result = {
            **intent_result,
            "intent": seed_context["intent"],
            "confidence": max(intent_result["confidence"], 0.78),
        }

    current_route = route_result["route"] if route_result else None
    if current_route == "validation_pipeline_with_entropy_reduction" and seed_context.get("route"):
        route_result = {
            **route_result,
            "route": seed_context["route"],
        }

    entropy_result = {
        **entropy_result,
        "missing_data": merged_missing[:4],
    }

    return intent_result, entropy_result, route_result

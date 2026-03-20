from __future__ import annotations

from typing import Any


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


def _response_text(intent: str, missing_data: list[str]) -> str:
    if intent == "ecommerce_performance_failure":
        return (
            "If a store is getting little or no sales, the problem is usually one of three things: "
            "weak traffic, weak conversion, or weak offer fit. Right now the story is incomplete, so "
            "it's too early to blame the product. If traffic is barely there, the focus should be visibility, "
            "not store tweaks yet. If people are visiting and still not buying, the pressure moves to conversion, "
            "pricing, or how compelling the offer feels."
        )

    if intent == "business_launch_uncertainty":
        return (
            "Most launch anxiety comes from trying to solve positioning, offer design, and go-to-market "
            "all at once. The uncertainty usually means the business is still under-defined, not that the "
            "idea is automatically bad. The right focus is getting the offer and buyer clear enough that a real "
            "person can quickly say yes or no. Brand polish and bigger plans can wait until that part is solid."
        )

    if intent == "creative_skill_development":
        return (
            "Creative progress usually stalls when practice is happening without a clear target. The gap is "
            "rarely raw talent. It's usually feedback quality, repetition volume, or a fuzzy standard. The useful "
            "move is to tighten the target of practice, not chase more inspiration. More tools or content won't fix "
            "it if the repetition loop is still vague."
        )

    if intent == "product_market_validation":
        return (
            "Most product ideas fail before launch because demand was assumed instead of tested. The useful "
            "question isn't whether the idea sounds good. It's whether a specific customer already feels the problem. "
            "The focus should be evidence of pain and buying intent first, not feature depth yet. If demand is weak, "
            "building more usually just hides the real issue."
        )

    if intent == "audience_growth_block":
        return (
            "Audience growth usually breaks because the distribution channel, the content angle, or the posting "
            "discipline is off. Until those are visible, 'make better content' is too vague to help. The first focus "
            "should be on whether the platform-content match is working at all. Fine-tuning style matters later; weak "
            "distribution usually overwhelms creative quality early on."
        )

    return (
        "The situation has a real decision inside it, but the missing context still matters. Once the baseline "
        "is clear, the right path usually becomes obvious much faster. The first priority is finding the constraint "
        "that is actually shaping the result, not improving everything at once."
    )


def _next_step(intent: str, missing_data: list[str]) -> str:
    if intent == "ecommerce_performance_failure":
        if "traffic source" in missing_data:
            return "Where are your current visitors coming from: ads, organic search, social, email, or basically none?"
        if "conversion rate" in missing_data:
            return "What is your current conversion rate, or at least how many visitors it takes to get one sale?"
        if "product type" in missing_data:
            return "What exactly are you selling, and is it impulse-buy territory or something people compare carefully?"
        if "pricing strategy" in missing_data:
            return "How is the product priced relative to competitors, and are you leading with a discount, bundle, or full price?"
        if "marketing channel" in missing_data:
            return "Which channel are you actually pushing hardest right now: Meta ads, TikTok, Google, email, or something else?"

    if intent == "business_launch_uncertainty":
        if "what you're trying to sell" in missing_data:
            return "What are you actually planning to sell first: a product, a service, or something custom?"
        if "who the buyer is" in missing_data:
            return "Who is the first buyer you think would pay for this without needing a long explanation?"
        if "what constraints you're operating under" in missing_data:
            return "What constraints are real here: money, time, skill, or the fact that you need traction quickly?"
        if "how far along the launch is" in missing_data:
            return "Are you still at idea stage, or have you already put an offer in front of real people?"

    if intent == "creative_skill_development":
        if "which creative skill you're trying to improve" in missing_data:
            return "Which skill are you trying to sharpen right now: writing, design, music, drawing, or something else specific?"
        if "what your current practice volume looks like" in missing_data:
            return "How much focused practice are you actually getting in each week?"
        if "what outcome you're aiming for" in missing_data:
            return "What are you trying to become better for: paid work, audience growth, portfolio quality, or personal mastery?"
        if "where the actual bottleneck is" in missing_data:
            return "Where do you feel the work falls apart right now: ideas, consistency, technique, or finishing?"

    if intent == "product_market_validation":
        if "what problem the product solves" in missing_data:
            return "What painful problem does this product solve strongly enough that someone would switch behavior for it?"
        if "who the target customer is" in missing_data:
            return "Who exactly is this for, and who is it definitely not for?"
        if "what validation you've already run" in missing_data:
            return "What have you already done to test demand: interviews, a landing page, preorders, or just intuition so far?"
        if "whether anyone has shown buying intent" in missing_data:
            return "Has anyone shown real buying intent yet, even if they have not paid you yet?"

    if intent == "audience_growth_block":
        if "which platform matters most" in missing_data:
            return "Which platform actually matters here: TikTok, YouTube, Instagram, X, LinkedIn, or email?"
        if "what you're publishing right now" in missing_data:
            return "What are you publishing now, in plain terms, and how often?"
        if "how consistent your output is" in missing_data:
            return "How consistent has your output been over the last 30 days?"
        if "what the current performance numbers look like" in missing_data:
            return "What do the numbers look like right now: views, clicks, followers, or subscribers?"

    if missing_data:
        return f"What can you tell me about {missing_data[0]}?"

    return "What is the one number or signal that tells you this situation is not working?"


def build_response(
    user_input: str,
    intent_result: dict[str, Any],
    entropy_result: dict[str, Any],
    route_result: dict[str, Any],
) -> dict[str, Any]:
    missing_data = entropy_result["missing_data"]
    route = route_result["route"]
    intent = intent_result["intent"]

    output_construct = {
        "name": "structured_response_generation",
        "type": "Output Construct",
        "profile": {
            "S": 33,
            "A": 56,
            "B": 81,
            "I": 84,
            "P": 86,
        },
        "cqu": _calculate_cqu(8.9, 9.0, 8.7, 8.4, 3.1),
    }

    constructs = [
        intent_result["construct"],
        entropy_result["construct"],
        route_result["construct"],
        output_construct,
    ]

    scores = {
        construct["name"]: {
            "type": construct["type"],
            "profile": construct["profile"],
            "cqu": construct["cqu"],
        }
        for construct in constructs
    }

    return {
        "intent": intent,
        "confidence": intent_result["confidence"],
        "missing_data": missing_data,
        "route": route,
        "response": _response_text(intent, missing_data),
        "next_step": _next_step(intent, missing_data),
        "cqf": {
            "constructs": [
                {
                    "name": construct["name"],
                    "type": construct["type"],
                    "cqf_profile": construct["profile"],
                    "cqu": construct["cqu"],
                }
                for construct in constructs
            ],
            "scores": scores,
        },
    }

from __future__ import annotations

from typing import Any

try:
    from engine.behavior import detect_behavior
    from engine.cognitive import detect_cognitive_level
    from engine.seed import encode_seed
    from engine.tone import detect_tone
    from engine.verification import verify_output
except ModuleNotFoundError:
    from behavior import detect_behavior
    from cognitive import detect_cognitive_level
    from seed import encode_seed
    from tone import detect_tone
    from verification import verify_output


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


def _extract_subject_phrase(user_input: str, primary_domain: str) -> str:
    lowered = user_input.lower()
    subject_map = {
        "music": "your music",
        "painting": "your painting",
        "paint": "your painting",
        "art": "your art",
        "drawing": "your drawing",
        "draw": "your drawing",
        "writing": "your writing",
        "write": "your writing",
        "store": "the store",
        "shopify": "the store",
        "etsy": "the Etsy shop",
        "product": "the product",
        "business": "the business",
        "career": "your direction",
        "life": "your direction",
        "code": "the code",
        "api": "the API",
        "server": "the server",
        "game": "your play",
    }
    for token, phrase in subject_map.items():
        if token in lowered:
            return phrase

    fallback_map = {
        "business": "what you're building",
        "creative": "the work",
        "life": "the situation",
        "technical": "the system",
        "gaming": "your play",
    }
    return fallback_map.get(primary_domain, "this")


def _cluster_phrase(cluster_name: str) -> str:
    phrases = {
        "commerce_outcome": "sales and store response",
        "creative_work": "the work itself",
        "creative_progress": "getting better at the work",
        "traction_gap": "whether the work is actually reaching people",
        "life_choice": "where to go next",
        "personal_progress": "staying steady and moving forward",
        "technical_break": "the part that keeps breaking",
        "gaming_performance": "the part of play that keeps costing you",
    }
    return phrases.get(cluster_name, cluster_name.replace("_", " "))


def _build_pattern_buffer(
    user_input: str,
    domain_result: dict[str, Any],
    tone: str,
    cognitive_level: str,
    regeneration_index: int = 0,
) -> dict[str, Any]:
    subject = _extract_subject_phrase(user_input, str(domain_result["primary_domain"]))
    clusters = domain_result.get("dominant_signal_clusters", [])[:3]
    dominant_signal_clusters = [_cluster_phrase(cluster["name"]) for cluster in clusters]

    lowered = user_input.lower()
    outcome_phrase = "it still is not turning into much"
    outcome_map = {
        "nothing is happening": "it still is not leading anywhere",
        "not growing": "it still is not growing",
        "no results": "it still is not turning into real results",
        "not working": "it still is not working",
        "no sales": "it still is not turning into sales",
        "no traction": "it still is not picking up",
        "no progress": "it still is not moving forward",
    }
    for phrase, rewrite in outcome_map.items():
        if phrase in lowered:
            outcome_phrase = rewrite
            break

    return {
        "primary_domain": str(domain_result["primary_domain"]),
        "secondary_domain": domain_result.get("secondary_domain"),
        "dominant_signal_clusters": dominant_signal_clusters,
        "outcome_signal_present": bool(domain_result.get("outcome_priority")),
        "emotional_tone": tone,
        "cognitive_level": cognitive_level,
        "subject": subject,
        "outcome_phrase": outcome_phrase,
        "variant": (sum(ord(char) for char in user_input) + regeneration_index) % 2,
    }


def _dynamic_opening(buffer: dict[str, Any]) -> str:
    subject = buffer["subject"]
    outcome_phrase = buffer["outcome_phrase"]
    primary_domain = buffer["primary_domain"]
    secondary_domain = buffer["secondary_domain"]
    variant = buffer["variant"]

    if primary_domain == "creative" and buffer["outcome_signal_present"]:
        if secondary_domain == "business":
            options = [
                f"{subject.capitalize()} can get a good reaction and still end up where {outcome_phrase},",
                f"People can respond well to {subject} and it still land in a place where {outcome_phrase},",
            ]
        else:
            options = [
                f"You can put real time into {subject} and still end up where {outcome_phrase},",
                f"{subject.capitalize()} can matter a lot to you and still feel like {outcome_phrase},",
            ]
        return options[variant]

    if primary_domain == "business":
        options = [
            f"{subject.capitalize()} can be active on the surface and still sit in a place where {outcome_phrase},",
            f"You can keep putting effort into {subject} and still watch it stay in a place where {outcome_phrase},",
        ]
        return options[variant]

    if primary_domain == "life":
        options = [
            "The situation can keep pulling in different directions without getting any clearer,",
            "Circling the same decision for a while usually means something underneath it still has not been named cleanly,",
        ]
        return options[variant]

    if primary_domain == "technical":
        options = [
            f"{subject.capitalize()} can keep dropping out even after a few fixes,",
            f"{subject.capitalize()} still being unstable after a few attempts usually means the fault is narrower than it first looks,",
        ]
        return options[variant]

    if primary_domain == "gaming":
        options = [
            f"{subject.capitalize()} can keep slipping in the same places even when the hours are there,",
            f"Putting more games in does not help much if {subject} keeps breaking down in the same moments,",
        ]
        return options[variant]

    options = [
        f"{subject.capitalize()} still feels stuck, and that usually means one part of it is not doing its part yet,",
        f"{subject.capitalize()} not really moving yet usually comes down to one part of the situation dragging more than the others,",
    ]
    return options[variant]


def _dynamic_diagnosis(intent: str, mode: str, buffer: dict[str, Any]) -> str:
    primary_domain = buffer["primary_domain"]
    secondary_domain = buffer["secondary_domain"]
    subject = buffer["subject"]
    outcome_signal_present = buffer["outcome_signal_present"]
    clusters = buffer["dominant_signal_clusters"]
    cluster_phrase = clusters[0] if clusters else "what is actually happening"

    if primary_domain == "creative" and secondary_domain == "business" and outcome_signal_present:
        if mode == "redirect":
            return f"it makes sense to question {subject}, but what this usually means is that the work is getting some positive response and then dying before it reaches enough of the right people"
        if mode == "push":
            return f"the craft itself is probably not the main problem now, and this usually comes down to reach, consistency, or the work not being in front of the right people often enough"
        return f"this usually means the work is good enough to get a reaction, but not visible enough or steady enough to turn into anything yet"

    if intent == "ecommerce_performance_failure":
        if mode == "redirect":
            return "the surface details are easy to fixate on, but this usually comes down to people either not getting there in the first place, or getting there and not feeling ready to buy"
        if mode == "push":
            return "the slowdown is probably narrower than it looks, and most of the time it is traffic or buying hesitation, not store polish"
        return "this is usually not the whole store failing at once, but people either not arriving in the right numbers or dropping off before they buy"

    if primary_domain == "life":
        if mode == "redirect":
            return "keeping every option alive can feel safer, but most of the time that means the hardest tradeoff never gets faced directly"
        if mode == "push":
            return "one part of this is probably draining more energy than the rest, and that is usually the place deciding everything else"
        return "this usually gets muddy because one decision is tied up with a few others, so nothing feels clean until that knot loosens"

    if primary_domain == "technical":
        if "internet" in subject or "connection" in subject:
            return "this usually means either the router is dropping the connection or the line coming in is unstable"
        return "this usually means one part is failing and everything around it is only feeling broken because of that"

    if primary_domain == "gaming":
        return "this usually comes down to one repeat mistake showing up over and over and costing more than the rest"

    if mode == "push":
        return f"most of the time this comes back to {cluster_phrase}, and that is probably where things are breaking down"
    if mode == "redirect":
        return f"the first instinct is understandable, but this usually goes wrong around {cluster_phrase}"
    return f"what this tends to mean is that {cluster_phrase} is where things are starting to stall"


def _dynamic_direction(mode: str, buffer: dict[str, Any]) -> str:
    primary_domain = buffer["primary_domain"]
    secondary_domain = buffer["secondary_domain"]
    outcome_signal_present = buffer["outcome_signal_present"]
    subject = buffer["subject"]

    if primary_domain == "creative" and secondary_domain == "business" and outcome_signal_present:
        if mode == "redirect":
            return f"so a better direction is to stop treating {subject} as the only variable and look harder at how it is reaching people, how often it is being seen, and what happens after people respond well to it"
        if mode == "push":
            return f"so I would treat this as a reach problem before I treated it as a talent problem"
        return f"so I would look less at the work itself and more at how often the right people are actually seeing it"

    if primary_domain == "business":
        if mode == "redirect":
            return "so the better move is to find where the path breaks instead of trying to improve everything at once"
        if mode == "push":
            return "so I would narrow in on the part between attention and purchase before touching anything cosmetic"
        return "so I would look for the point where interest stops turning into action"

    if primary_domain == "life":
        if mode == "redirect":
            return "so the better move is to name the one pressure you actually need to answer first and let the rest wait"
        if mode == "push":
            return "so I would stop treating every open question as equal and deal with the heaviest one first"
        return "so getting clear on the hardest tradeoff will help more than trying to solve the whole future in one pass"

    if primary_domain == "technical":
        return "so I would check the part most likely to be failing before changing anything broader"

    if primary_domain == "gaming":
        return "so I would narrow in on that repeat mistake instead of overhauling everything"

    return "so I would stay with the part that is falling short instead of spreading effort across everything else"


def _apply_cognitive_level(response: str, level: str) -> str:
    if level == "low":
        return (
            response.replace("conversion", "people seeing it but not buying")
            .replace("distribution", "how it is reaching people")
            .replace("traction", "results")
            .replace("pricing", "price")
            .replace("validation", "proof")
        )
    if level == "high":
        return response
    return (
        response.replace("conversion", "people seeing it and not buying")
        .replace("distribution", "reach")
    )


def _response_text(
    user_input: str,
    intent: str,
    tone: str,
    mode: str,
    domain_result: dict[str, Any],
    cognitive_level: str,
    regeneration_index: int = 0,
) -> str:
    buffer = _build_pattern_buffer(
        user_input,
        domain_result,
        tone,
        cognitive_level,
        regeneration_index,
    )
    opening = _dynamic_opening(buffer)
    diagnosis = _dynamic_diagnosis(intent, mode, buffer)
    direction = _dynamic_direction(mode, buffer)
    base = f"{opening} {diagnosis}, {direction}."

    if tone == "casual":
        base = base.replace(
            "looks closer to where this is getting stuck",
            "looks more like where this is getting stuck",
        )

    elif tone == "frustrated":
        base = base.replace("it helps to", "what matters now is to")

    elif tone == "uncertain":
        base = base.replace(
            "looks closer to where this is getting stuck",
            "is probably closer to where this is getting stuck",
        )

    return _apply_cognitive_level(base, cognitive_level)


def _next_step(intent: str, missing_data: list[str]) -> str:
    if intent == "ecommerce_performance_failure":
        if "traffic source" in missing_data:
            return "Where are people actually finding the store right now?"
        if "conversion rate" in missing_data:
            return "What tends to happen after people land there?"
        if "product type" in missing_data:
            return "What are you selling, and is it something people buy quickly or think about for a while?"
        if "pricing strategy" in missing_data:
            return "How is the price sitting compared with the other options people could choose?"
        if "marketing channel" in missing_data:
            return "Which channel is doing most of the work for you right now?"

    if intent == "business_launch_uncertainty":
        if "what you're trying to sell" in missing_data:
            return "What are you actually trying to put in front of people first?"
        if "who the buyer is" in missing_data:
            return "Who do you think should care about this first?"
        if "what constraints you're operating under" in missing_data:
            return "What is the real constraint here: time, money, skill, or something else?"
        if "how far along the launch is" in missing_data:
            return "How far along is this really right now?"

    if intent == "creative_skill_development":
        if "which creative skill you're trying to improve" in missing_data:
            return "What part of the work are you actually trying to get better at?"
        if "what your current practice volume looks like" in missing_data:
            return "How often are you really doing the work right now?"
        if "what outcome you're aiming for" in missing_data:
            return "What are you hoping the work starts doing for you?"
        if "where the actual bottleneck is" in missing_data:
            return "Where does it start to break down for you most often?"

    if intent == "product_market_validation":
        if "what problem the product solves" in missing_data:
            return "What real problem is this meant to solve for someone?"
        if "who the target customer is" in missing_data:
            return "Who is this really for?"
        if "what validation you've already run" in missing_data:
            return "What have you actually done so far to see if people want it?"
        if "whether anyone has shown buying intent" in missing_data:
            return "Has anyone shown signs they would really pay for it?"

    if intent == "audience_growth_block":
        if "which platform matters most" in missing_data:
            return "Where is this work actually being seen right now?"
        if "what you're publishing right now" in missing_data:
            return "What are you putting out there most often?"
        if "how consistent your output is" in missing_data:
            return "How steady has the output really been lately?"
        if "what the current performance numbers look like" in missing_data:
            return "What is the response looking like right now?"

    if missing_data:
        return f"What have you actually seen so far around {missing_data[0]}?"

    return "What is the one number or signal that tells you this situation is not working?"


def build_response(
    user_input: str,
    domain_result: dict[str, Any],
    intent_result: dict[str, Any],
    entropy_result: dict[str, Any],
    route_result: dict[str, Any],
) -> dict[str, Any]:
    missing_data = entropy_result["missing_data"]
    route = route_result["route"]
    intent = intent_result["intent"]
    primary_domain = str(domain_result["primary_domain"])
    cognitive_result = detect_cognitive_level(user_input)
    tone_result = detect_tone(user_input)
    behavior_result = detect_behavior(
        user_input=user_input,
        intent_confidence=float(intent_result["confidence"]),
        tone=str(tone_result["tone"]),
        missing_data=missing_data,
    )
    response_text = _response_text(
        user_input,
        intent,
        str(tone_result["tone"]),
        str(behavior_result["mode"]),
        domain_result,
        str(cognitive_result["level"]),
        0,
    )
    verification_result = verify_output(
        response=response_text,
        route=route,
        domain_result=domain_result,
        behavior_mode=str(behavior_result["mode"]),
        missing_data=missing_data,
    )
    route = verification_result["route"]
    response_text = verification_result["response"]
    if verification_result["template_like"]:
        response_text = _response_text(
            user_input,
            intent,
            str(tone_result["tone"]),
            str(behavior_result["mode"]),
            domain_result,
            str(cognitive_result["level"]),
            1,
        )
        verification_result = verify_output(
            response=response_text,
            route=route,
            domain_result=domain_result,
            behavior_mode=str(behavior_result["mode"]),
            missing_data=missing_data,
        )
        route = verification_result["route"]
        response_text = verification_result["response"]
    route_result = {
        **route_result,
        "route": route,
    }
    seed = encode_seed(intent=intent, route=route, missing_data=missing_data)

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
        "response": response_text,
        "next_step": _next_step(intent, missing_data),
        "seed": seed,
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

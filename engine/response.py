from __future__ import annotations

from typing import Any

try:
    from engine.behavior import detect_behavior
    from engine.seed import encode_seed
    from engine.tone import detect_tone
except ModuleNotFoundError:
    from behavior import detect_behavior
    from seed import encode_seed
    from tone import detect_tone


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


def _base_response_text(intent: str, mode: str, primary_domain: str) -> str:
    if intent == "ecommerce_performance_failure":
        if mode == "push":
            return (
                "When a store is not getting sales, the issue usually sits in traffic, conversion, or offer fit, so the real job is finding the choke point rather than tinkering broadly. "
                "If traffic is barely there, focus on visibility first and stop overvaluing store tweaks, and if people are visiting and still not buying, "
                "treat it as a conversion, pricing, or offer problem until the numbers prove otherwise."
            )
        if mode == "redirect":
            return (
                "Focusing on the store itself is understandable when sales are weak, but the higher-probability issue is traffic or conversion, not cosmetic store changes. A stronger direction "
                "is to decide whether the real failure is lack of qualified traffic or failure to convert the traffic you already have."
            )
        return (
            "When a store is not getting sales, the problem is usually weak traffic, weak conversion, or weak offer fit, and the missing piece is figuring out which of those is actually failing. "
            "If traffic is barely there, the focus should be visibility, not store tweaks yet, but if people are visiting and still not buying, the pressure "
            "moves to conversion, pricing, or how compelling the offer feels."
        )

    if intent == "business_launch_uncertainty":
        if mode == "push":
            return (
                "Most launch anxiety comes from trying to solve positioning, offer design, and go-to-market all at once, which usually means the business is still under-defined rather than bad. "
                "The right move is to get the offer and buyer clear enough that a real person can react to it quickly, because brand polish and bigger plans are not the bottleneck yet."
            )
        if mode == "redirect":
            return (
                "Building the broader brand first can feel like progress, but the risk is staying too broad to get traction. A stronger direction is to narrow the buyer and offer until the value is obvious fast, then expand from there."
            )
        return (
            "Most launch anxiety comes from trying to solve positioning, offer design, and go-to-market all at once, and that usually means the business is still under-defined, not automatically bad. "
            "The right focus is getting the offer and buyer clear enough "
            "that a real person can quickly say yes or no. Brand polish and bigger plans can wait until that part is solid."
        )

    if intent == "creative_skill_development":
        if mode == "push":
            return (
                "When you keep practicing and the work still is not moving, the problem is rarely talent. It usually comes down to not being clear on what you're actually trying to improve, not seeing what is changing, or not practicing often enough, so tighten the focus first because more inspiration, more tools, or more browsing will not fix that."
            )
        if mode == "redirect":
            return (
                "When progress feels slow, taking in more input can feel productive, but that usually drifts you away from the real issue. A better direction is to get much clearer on what you're trying to improve and judge the work against that, because this looks more like a practice problem than an inspiration problem."
            )
        return (
            "When you keep putting effort into a creative skill and the work is not improving, the gap is rarely raw talent. It is usually that you are not fully clear on what you're trying to improve, not seeing what is actually changing, or not practicing often enough, so the useful move is to narrow the focus rather than chase more inspiration because more tools or content will not fix a vague practice loop."
        )

    if intent == "product_market_validation":
        if mode == "push":
            return (
                "When a product idea feels promising, the mistake is usually assuming demand instead of testing it, so the stronger move is validating pain "
                "and buying intent before spending more energy on features. The useful question is not whether the idea sounds smart, but whether a "
                "specific customer already feels the problem enough to move."
            )
        if mode == "redirect":
            return (
                "Building further can feel like the right move when you care about the product, but the bigger risk is building ahead of demand rather than building too little. A stronger direction is to look for evidence of pain and willingness to buy first, then let that shape the product."
            )
        return (
            "Most product ideas fail before launch because demand was assumed instead of tested, and the useful question is not whether the idea sounds good but whether a specific customer already feels the problem. "
            "The focus should be evidence of pain and buying intent first, not feature depth yet, because if demand is weak, building more usually just hides the real issue."
        )

    if intent == "audience_growth_block":
        if mode == "push":
            return (
                "When audience growth stalls, the issue is usually the channel, the angle, or the posting rhythm, so this points more toward a mismatch in how the content is reaching people than a vague quality issue. The first focus should be whether the distribution setup is working at all, because fine-tuning style comes later."
            )
        if mode == "redirect":
            return (
                "When growth is flat, refining the content itself is an understandable instinct, but this is more likely a distribution problem than a pure quality problem. A better direction is to fix how the content is reaching people first, because weak reach overwhelms creative quality early."
            )
        return (
            "When audience growth stalls, the issue is usually the channel, the angle, or the posting rhythm, and until those are visible, "
            "'make better content' is too vague to help. The first focus should be on whether the content is reaching the right people in the right way, because fine-tuning style "
            "matters later; weak distribution usually overwhelms creative quality early on."
        )

    if primary_domain == "life" and mode == "redirect":
        return (
            "When several parts of life feel tangled together, keeping every option open can feel safer, but it usually keeps the real issue blurry. A stronger direction is to find the one pressure point that is shaping the rest and work from there."
        )
    if primary_domain == "life" and mode == "push":
        return (
            "When progress feels scattered, there is usually one pressure point carrying more weight than the others, so the useful move is to name that clearly and stop treating every problem as equally urgent."
        )
    if primary_domain == "life":
        return (
            "When life feels unclear, the problem is usually not a lack of options but too many unresolved pressures sitting on top of each other. The useful move is to get clear on what is actually pulling the most weight right now instead of trying to solve everything at once."
        )
    if primary_domain == "technical" and mode == "redirect":
        return (
            "When something technical keeps breaking, it is easy to keep patching the surface, but that usually drags the problem out. A stronger direction is to isolate the failing part first and let that drive the next move."
        )
    if primary_domain == "technical" and mode == "push":
        return (
            "When a technical problem keeps showing up, there is usually one failing piece underneath it, so the useful move is to isolate that point instead of making broad changes across the whole system."
        )
    if primary_domain == "technical":
        return (
            "When something technical is not working, the issue is usually narrower than it first appears. The useful move is to separate the failing part from everything around it, because that is what makes the next decision clearer."
        )
    if primary_domain == "gaming" and mode == "redirect":
        return (
            "When progress in a game feels flat, it is easy to keep changing everything at once, but that usually hides the real weakness. A better direction is to focus on the one part of play that is costing the most and build from there."
        )
    if primary_domain == "gaming" and mode == "push":
        return (
            "When improvement in a game stalls, there is usually one weak link doing most of the damage, so the useful move is to narrow in on that instead of overhauling everything."
        )
    if primary_domain == "gaming":
        return (
            "When progress in a game stalls, the issue is usually one weak part of play showing up over and over rather than a general lack of ability. The useful move is to spot that pattern clearly before changing everything else."
        )
    if mode == "redirect":
        return (
            "Keeping multiple paths open can feel safer, but it usually spreads effort too thin and hides the real constraint, so a stronger direction is to find the factor actually shaping the result and let that determine the next move."
        )
    if mode == "push":
        return (
            "There is a real constraint shaping this outcome, and it is probably narrower than it feels right now, so the useful move is to identify it and stop spreading effort across everything else."
        )
    return (
        "The situation has a real decision inside it, but the missing context still matters because once the baseline is clear, the right path usually becomes obvious much faster. The first priority is finding the constraint that is actually shaping the result, not improving everything at once."
    )


def _response_text(intent: str, tone: str, mode: str, primary_domain: str) -> str:
    base = _base_response_text(intent, mode, primary_domain)

    if tone == "casual":
        return base.replace(
            "This points more strongly toward",
            "This points more toward",
        )

    if tone == "frustrated":
        if intent == "ecommerce_performance_failure":
            return (
                "When a store is not getting sales, the problem is usually weak traffic, weak conversion, or weak offer fit, and that narrows it more than it may feel right now. If traffic is barely there, the real issue is visibility, not store tweaks yet, but if people are visiting and still not buying, the problem is much more likely conversion, pricing, or the offer itself."
            )
        return base.replace("The uncertainty usually means", "That usually means").replace(
            "The situation has a real decision inside it, but the missing context still matters.",
            "There is a real constraint here, even if it feels muddled right now.",
        )

    if tone == "uncertain":
        return base.replace(
            "the problem is usually one of three things: weak traffic, weak conversion, or weak offer fit.",
            "the problem is usually one of three things: weak traffic, weak conversion, or weak offer fit, and it is still too early to jump to the worst conclusion.",
        ).replace(
            "it's too early to blame the product.",
            "it's too early to assume the product is the problem."
        ).replace(
            "The first priority is finding the constraint that is actually shaping the result, not improving everything at once.",
            "The first priority is finding the constraint that is actually shaping the result, rather than trying to fix everything at once."
        )

    return base


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
    domain_result: dict[str, Any],
    intent_result: dict[str, Any],
    entropy_result: dict[str, Any],
    route_result: dict[str, Any],
) -> dict[str, Any]:
    missing_data = entropy_result["missing_data"]
    route = route_result["route"]
    intent = intent_result["intent"]
    primary_domain = str(domain_result["primary_domain"])
    tone_result = detect_tone(user_input)
    behavior_result = detect_behavior(
        user_input=user_input,
        intent_confidence=float(intent_result["confidence"]),
        tone=str(tone_result["tone"]),
        missing_data=missing_data,
    )
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
        "response": _response_text(
            intent,
            str(tone_result["tone"]),
            str(behavior_result["mode"]),
            primary_domain,
        ),
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

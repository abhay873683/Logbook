from dataclasses import dataclass


@dataclass
class PriorityResult:
    priority: str
    score: int
    reasons: list[str]


URGENT_KEYWORDS = {
    "security breach",
    "critical",
    "system down",
    "outage",
    "immediate",
    "emergency",
    "account compromised",
}

HIGH_KEYWORDS = {
    "deadline",
    "overdue",
    "failed",
    "failure",
    "blocked",
    "approval required",
    "urgent",
    "high priority",
    "payment failed",
}

LOW_KEYWORDS = {
    "newsletter",
    "digest",
    "summary available",
    "weekly update",
    "fyi",
}


def prioritize_notification(
    title: str,
    message: str,
    notification_type: str = "info",
    category: str = "general",
    source: str = "system",
) -> PriorityResult:

    text = (
        f"{title} {message} "
        f"{category} {source}"
    ).lower()

    score = 20
    reasons = []

    if notification_type == "error":
        score += 35
        reasons.append(
            "Error notification"
        )

    elif notification_type == "warning":
        score += 20
        reasons.append(
            "Warning notification"
        )

    elif notification_type == "success":
        score -= 5
        reasons.append(
            "Success notification"
        )

    for keyword in URGENT_KEYWORDS:
        if keyword in text:
            score += 50
            reasons.append(
                f"Critical keyword: {keyword}"
            )

    for keyword in HIGH_KEYWORDS:
        if keyword in text:
            score += 25
            reasons.append(
                f"Important keyword: {keyword}"
            )

    for keyword in LOW_KEYWORDS:
        if keyword in text:
            score -= 15
            reasons.append(
                f"Low urgency keyword: {keyword}"
            )

    high_priority_categories = {
        "security",
        "deadline",
        "approval",
        "task",
        "system",
    }

    if category.lower() in high_priority_categories:
        score += 10
        reasons.append(
            f"Important category: {category}"
        )

    if score >= 80:
        priority = "urgent"

    elif score >= 50:
        priority = "high"

    elif score >= 20:
        priority = "normal"

    else:
        priority = "low"

    score = max(
        0,
        min(score, 100),
    )

    if not reasons:
        reasons.append(
            "Standard notification priority"
        )

    return PriorityResult(
        priority=priority,
        score=score,
        reasons=reasons,
    )

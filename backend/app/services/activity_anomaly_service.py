from collections import Counter
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.user import User

from app.services.activity_log_service import (
    is_admin,
)


DESTRUCTIVE_KEYWORDS = {
    "delete",
    "deleted",
    "trash",
    "remove",
    "removed",
    "revoke",
    "revoked",
}

SENSITIVE_KEYWORDS = {
    "permission",
    "role",
    "admin",
    "auth",
    "password",
    "security",
}

LOCAL_IPS = {
    "127.0.0.1",
    "::1",
    "localhost",
}


def normalize_datetime(
    value: datetime | None,
) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def normalize_text(
    value: str | None,
) -> str:
    return str(
        value or ""
    ).strip().lower()


def risk_level_from_score(
    score: int,
) -> str:
    if score >= 80:
        return "critical"

    if score >= 60:
        return "high"

    if score >= 30:
        return "medium"

    return "low"


def calculate_risk_level(
    score: int,
    signals: list[dict],
) -> str:
    severity_rank = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3,
    }

    score_level = (
        risk_level_from_score(
            score
        )
    )

    strongest_level = score_level

    for signal in signals:
        severity = str(
            signal.get(
                "severity",
                "low",
            )
        ).strip().lower()

        if (
            severity_rank.get(
                severity,
                0,
            )
            > severity_rank[
                strongest_level
            ]
        ):
            strongest_level = severity

    return strongest_level


def is_destructive_action(
    action: str | None,
) -> bool:
    normalized = normalize_text(
        action
    )

    return any(
        keyword in normalized
        for keyword in DESTRUCTIVE_KEYWORDS
    )


def is_sensitive_action(
    action: str | None,
) -> bool:
    normalized = normalize_text(
        action
    )

    return any(
        keyword in normalized
        for keyword in SENSITIVE_KEYWORDS
    )


def get_user_activity_window(
    db: Session,
    user_id: int,
    window_hours: int = 24,
):
    since = (
        datetime.now(timezone.utc)
        - timedelta(
            hours=window_hours
        )
    )

    return (
        db.query(ActivityLog)
        .filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at.isnot(None),
            ActivityLog.created_at >= since,
        )
        .order_by(
            ActivityLog.created_at.asc(),
            ActivityLog.id.asc(),
        )
        .all()
    )


def add_signal(
    signals: list[dict],
    code: str,
    severity: str,
    score: int,
    reason: str,
):
    signals.append(
        {
            "code": code,
            "severity": severity,
            "score": score,
            "reason": reason,
        }
    )


def detect_activity_anomalies(
    db: Session,
    user_id: int,
    window_hours: int = 24,
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise ValueError(
            "User not found"
        )

    logs = get_user_activity_window(
        db=db,
        user_id=user_id,
        window_hours=window_hours,
    )

    signals: list[dict] = []

    timestamps = [
        normalize_datetime(
            log.created_at
        )
        for log in logs
        if log.created_at is not None
    ]

    timestamps = [
        timestamp
        for timestamp in timestamps
        if timestamp is not None
    ]

    actions = [
        normalize_text(log.action)
        for log in logs
        if normalize_text(log.action)
    ]

    ips = [
        str(log.ip_address).strip()
        for log in logs
        if log.ip_address
        and str(log.ip_address).strip()
    ]

    unique_ips = set(ips)
    unique_actions = set(actions)

    destructive_logs = [
        log
        for log in logs
        if is_destructive_action(
            log.action
        )
    ]

    sensitive_logs = [
        log
        for log in logs
        if is_sensitive_action(
            log.action
        )
    ]

    # --------------------------------------------------
    # Signal 1:
    # Extremely high total activity in analysis window
    # --------------------------------------------------

    if len(logs) >= 100:
        add_signal(
            signals,
            code="high_activity_volume",
            severity="high",
            score=30,
            reason=(
                f"{len(logs)} activities detected "
                f"within {window_hours} hours"
            ),
        )

    elif len(logs) >= 50:
        add_signal(
            signals,
            code="elevated_activity_volume",
            severity="medium",
            score=15,
            reason=(
                f"{len(logs)} activities detected "
                f"within {window_hours} hours"
            ),
        )

    # --------------------------------------------------
    # Signal 2:
    # Rapid activity burst
    #
    # Day 56 legitimate test produced 12 operations
    # quickly, therefore threshold is intentionally
    # above that level to reduce false positives.
    # --------------------------------------------------

    max_five_minute_events = 0

    left = 0

    for right in range(
        len(timestamps)
    ):
        while (
            timestamps[right]
            - timestamps[left]
            > timedelta(minutes=5)
        ):
            left += 1

        current_count = (
            right - left + 1
        )

        max_five_minute_events = max(
            max_five_minute_events,
            current_count,
        )

    if max_five_minute_events >= 40:
        add_signal(
            signals,
            code="extreme_activity_burst",
            severity="critical",
            score=45,
            reason=(
                f"{max_five_minute_events} activities "
                "occurred within a 5-minute window"
            ),
        )

    elif max_five_minute_events >= 20:
        add_signal(
            signals,
            code="rapid_activity_burst",
            severity="high",
            score=25,
            reason=(
                f"{max_five_minute_events} activities "
                "occurred within a 5-minute window"
            ),
        )

    # --------------------------------------------------
    # Signal 3:
    # Destructive action burst
    # --------------------------------------------------

    destructive_timestamps = [
        normalize_datetime(
            log.created_at
        )
        for log in destructive_logs
        if log.created_at is not None
    ]

    destructive_timestamps = [
        timestamp
        for timestamp
        in destructive_timestamps
        if timestamp is not None
    ]

    max_destructive_burst = 0

    left = 0

    for right in range(
        len(destructive_timestamps)
    ):
        while (
            destructive_timestamps[right]
            - destructive_timestamps[left]
            > timedelta(minutes=10)
        ):
            left += 1

        current_count = (
            right - left + 1
        )

        max_destructive_burst = max(
            max_destructive_burst,
            current_count,
        )

    if max_destructive_burst >= 10:
        add_signal(
            signals,
            code="mass_destructive_activity",
            severity="critical",
            score=50,
            reason=(
                f"{max_destructive_burst} destructive "
                "actions occurred within 10 minutes"
            ),
        )

    elif max_destructive_burst >= 5:
        add_signal(
            signals,
            code="destructive_action_burst",
            severity="high",
            score=30,
            reason=(
                f"{max_destructive_burst} destructive "
                "actions occurred within 10 minutes"
            ),
        )

    # --------------------------------------------------
    # Signal 4:
    # Multiple IP addresses
    # --------------------------------------------------

    non_local_ips = {
        ip
        for ip in unique_ips
        if ip not in LOCAL_IPS
    }

    if len(non_local_ips) >= 5:
        add_signal(
            signals,
            code="many_source_ips",
            severity="high",
            score=30,
            reason=(
                f"Activity originated from "
                f"{len(non_local_ips)} different "
                "non-local IP addresses"
            ),
        )

    elif len(non_local_ips) >= 3:
        add_signal(
            signals,
            code="multiple_source_ips",
            severity="medium",
            score=15,
            reason=(
                f"Activity originated from "
                f"{len(non_local_ips)} different "
                "non-local IP addresses"
            ),
        )

    # --------------------------------------------------
    # Signal 5:
    # Fast IP switching
    # --------------------------------------------------

    ip_events = [
        (
            normalize_datetime(
                log.created_at
            ),
            str(log.ip_address).strip(),
        )
        for log in logs
        if log.created_at is not None
        and log.ip_address
        and str(log.ip_address).strip()
        not in LOCAL_IPS
    ]

    ip_events = [
        event
        for event in ip_events
        if event[0] is not None
    ]

    rapid_ip_switches = 0

    for index in range(
        1,
        len(ip_events),
    ):
        previous_time, previous_ip = (
            ip_events[index - 1]
        )

        current_time, current_ip = (
            ip_events[index]
        )

        if (
            previous_ip != current_ip
            and (
                current_time
                - previous_time
            )
            <= timedelta(minutes=2)
        ):
            rapid_ip_switches += 1

    if rapid_ip_switches >= 4:
        add_signal(
            signals,
            code="rapid_ip_switching",
            severity="high",
            score=30,
            reason=(
                f"{rapid_ip_switches} rapid IP "
                "switches were detected"
            ),
        )

    # --------------------------------------------------
    # Signal 6:
    # Sensitive action repetition
    # --------------------------------------------------

    if len(sensitive_logs) >= 10:
        add_signal(
            signals,
            code="repeated_sensitive_activity",
            severity="critical",
            score=40,
            reason=(
                f"{len(sensitive_logs)} sensitive "
                "actions were detected"
            ),
        )

    elif len(sensitive_logs) >= 5:
        add_signal(
            signals,
            code="sensitive_activity_spike",
            severity="high",
            score=25,
            reason=(
                f"{len(sensitive_logs)} sensitive "
                "actions were detected"
            ),
        )

    # --------------------------------------------------
    # Signal 7:
    # One action repeated excessively
    # --------------------------------------------------

    action_counts = Counter(
        actions
    )

    if action_counts:
        most_common_action, count = (
            action_counts.most_common(1)[0]
        )

        if count >= 30:
            add_signal(
                signals,
                code="repetitive_action_pattern",
                severity="high",
                score=25,
                reason=(
                    f"Action '{most_common_action}' "
                    f"occurred {count} times"
                ),
            )

    # --------------------------------------------------
    # Final score
    # --------------------------------------------------

    risk_score = min(
        100,
        sum(
            signal["score"]
            for signal in signals
        ),
    )

    risk_level = (
        calculate_risk_level(
            risk_score,
            signals,
        )
    )

    is_anomalous = (
        risk_score >= 30
    )

    return {
        "user_id": user_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "is_anomalous": is_anomalous,
        "analyzed_logs": len(logs),
        "window_hours": window_hours,
        "first_activity_at": (
            timestamps[0]
            if timestamps
            else None
        ),
        "last_activity_at": (
            timestamps[-1]
            if timestamps
            else None
        ),
        "unique_ips": len(
            unique_ips
        ),
        "unique_actions": len(
            unique_actions
        ),
        "destructive_actions": len(
            destructive_logs
        ),
        "signals": signals,
    }


def scan_activity_anomalies(
    db: Session,
    window_hours: int = 24,
):
    since = (
        datetime.now(timezone.utc)
        - timedelta(
            hours=window_hours
        )
    )

    user_ids = [
        row[0]
        for row in (
            db.query(
                ActivityLog.user_id
            )
            .filter(
                ActivityLog.user_id.isnot(
                    None
                ),
                ActivityLog.created_at.isnot(
                    None
                ),
                ActivityLog.created_at
                >= since,
            )
            .distinct()
            .all()
        )
    ]

    results = []

    for user_id in user_ids:
        analysis = (
            detect_activity_anomalies(
                db=db,
                user_id=user_id,
                window_hours=window_hours,
            )
        )

        results.append(
            {
                "user_id": (
                    analysis["user_id"]
                ),
                "risk_score": (
                    analysis["risk_score"]
                ),
                "risk_level": (
                    analysis["risk_level"]
                ),
                "is_anomalous": (
                    analysis["is_anomalous"]
                ),
                "signal_count": len(
                    analysis["signals"]
                ),
            }
        )

    results.sort(
        key=lambda item: (
            item["risk_score"],
            item["user_id"],
        ),
        reverse=True,
    )

    return {
        "analyzed_users": len(
            results
        ),
        "anomalous_users": sum(
            1
            for item in results
            if item["is_anomalous"]
        ),
        "high_risk_users": sum(
            1
            for item in results
            if item["risk_level"]
            == "high"
        ),
        "critical_risk_users": sum(
            1
            for item in results
            if item["risk_level"]
            == "critical"
        ),
        "results": results,
    }


def get_anomaly_for_current_user(
    db: Session,
    current_user: User,
    window_hours: int = 24,
):
    return detect_activity_anomalies(
        db=db,
        user_id=current_user.id,
        window_hours=window_hours,
    )


def get_anomaly_for_user(
    db: Session,
    current_user: User,
    user_id: int,
    window_hours: int = 24,
):
    if (
        current_user.id != user_id
        and not is_admin(current_user)
    ):
        raise PermissionError(
            "You do not have permission "
            "to analyze this user's activity"
        )

    return detect_activity_anomalies(
        db=db,
        user_id=user_id,
        window_hours=window_hours,
    )

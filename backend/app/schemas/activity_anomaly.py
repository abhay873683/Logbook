from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AnomalySignal(BaseModel):
    code: str
    severity: str
    score: int = Field(
        ge=0,
        le=100,
    )
    reason: str


class ActivityAnomalyResponse(BaseModel):
    user_id: int
    risk_score: int = Field(
        ge=0,
        le=100,
    )
    risk_level: str
    is_anomalous: bool

    analyzed_logs: int
    window_hours: int

    first_activity_at: datetime | None = None
    last_activity_at: datetime | None = None

    unique_ips: int
    unique_actions: int
    destructive_actions: int

    signals: list[AnomalySignal]

    model_config = ConfigDict(
        from_attributes=True
    )


class ActivityAnomalySummary(BaseModel):
    user_id: int
    risk_score: int
    risk_level: str
    is_anomalous: bool
    signal_count: int


class ActivityAnomalyScanResponse(BaseModel):
    analyzed_users: int
    anomalous_users: int
    high_risk_users: int
    critical_risk_users: int
    results: list[ActivityAnomalySummary]

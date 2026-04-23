"""Notify 이벤트·심각도 열거형."""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class Event(str, Enum):
    SESSION_SAVED = "session_saved"
    DAILY_RECAP = "daily_recap"
    MORNING_BRIEF = "morning_brief"
    TELEMETRY_ALERT = "telemetry_alert"
    RISK_P1 = "risk_p1"
    SHOOT_GATE = "shoot_gate"
    BUILD_FAILED = "build_failed"


# 이벤트별 기본 이모지 (제목 접두어)
EVENT_EMOJI: dict[Event, str] = {
    Event.SESSION_SAVED: "📝",
    Event.DAILY_RECAP: "📋",
    Event.MORNING_BRIEF: "🌅",
    Event.TELEMETRY_ALERT: "📊",
    Event.RISK_P1: "🚨",
    Event.SHOOT_GATE: "🎬",
    Event.BUILD_FAILED: "❌",
}


def format_title(event: Event, title: str) -> str:
    emoji = EVENT_EMOJI.get(event, "🔔")
    return f"{emoji} *{title}*"

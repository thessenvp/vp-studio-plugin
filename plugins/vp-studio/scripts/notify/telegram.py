"""
Telegram Bot API 저수준 클라이언트.

표준 라이브러리만 사용 (urllib).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


API_BASE = "https://api.telegram.org"
MAX_MSG_LEN = 4000  # Telegram 4096 — 여유 96


def send_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str | None = "Markdown",
    timeout: float = 15.0,
) -> dict[str, Any]:
    """단일 chat 에 메시지 전송. Telegram API 응답 dict 반환."""
    url = f"{API_BASE}/bot{token}/sendMessage"
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def split_message(text: str, limit: int = MAX_MSG_LEN) -> list[str]:
    """Telegram 길이 제한 초과 시 단순 분할. 마크다운 경계를 크게 고려하진 않음."""
    if len(text) <= limit:
        return [text]
    parts = []
    remaining = text
    while remaining:
        parts.append(remaining[:limit])
        remaining = remaining[limit:]
    return parts

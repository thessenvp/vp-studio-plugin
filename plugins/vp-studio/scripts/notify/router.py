"""
이벤트 라우팅 + throttle.

throttle: 동일 event_type 의 연속 발송을 기본 60초 내 1회로 제한.
state 는 _paths.throttle_state_path() 가 결정한 파일에 JSON 으로 영속.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ._paths import throttle_state_path


def _throttle_path() -> Path:
    return throttle_state_path()


def _load_state() -> dict[str, float]:
    p = _throttle_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(state: dict[str, float]) -> None:
    p = _throttle_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        p.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass  # throttle 쓰기 실패는 치명적이지 않음


def should_throttle(event_type: str, throttle_seconds: int) -> bool:
    """True 반환 시 이번 이벤트는 skip."""
    if throttle_seconds <= 0:
        return False
    state = _load_state()
    now = time.time()
    last = state.get(event_type, 0.0)
    if now - last < throttle_seconds:
        return True
    state[event_type] = now
    _save_state(state)
    return False


def mark_sent(event_type: str) -> None:
    """명시적으로 보낸 것만 기록하고 싶을 때."""
    state = _load_state()
    state[event_type] = time.time()
    _save_state(state)

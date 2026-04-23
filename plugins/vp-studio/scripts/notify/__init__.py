"""
Notify 공개 API.

사용:
    from notify import send, Event, Severity
    send(Event.SESSION_SAVED, title="Scene 042 saved", body="path/to/file.md")

Plugin 번들 버전 — 원본 `vp.modules.utils.notify` 에서 분리. Project 루트는
$CLAUDE_PROJECT_DIR 또는 $VP_STUDIO_ROOT 환경변수로 결정하며,
notify.yaml / throttle.json 경로는 `_paths.py` 가 resolve.
"""

from __future__ import annotations

import sys
from typing import Any

from . import config as _config
from . import router, telegram
from .events import EVENT_EMOJI, Event, Severity, format_title


def _coerce_event(value: Event | str) -> Event | None:
    """문자열/Enum 어느 쪽이든 Event 로 정규화. 실패 시 None."""
    if isinstance(value, Event):
        return value
    try:
        return Event(value)
    except ValueError:
        return None


def _coerce_severity(value: Severity | str) -> Severity:
    """알 수 없는 값은 INFO 로 폴백 (기존 동작 보존)."""
    if isinstance(value, Severity):
        return value
    try:
        return Severity(value)
    except ValueError:
        return Severity.INFO


def send(
    event: Event | str,
    title: str,
    body: str,
    severity: Severity | str = Severity.INFO,
    meta: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """
    Telegram 으로 이벤트 알림 전송.

    - 설정(token/chat_ids)은 config.load() 로 자동 로드.
    - throttle 적용: 동일 event_type 이 짧은 시간 반복되면 skip.
    - 실패해도 예외 아닌 결과 배열로 리턴.
    - **텔레메트리 emit 하지 않음** (훅 무한루프 방지).

    Returns:
        [{"chat_id": "...", "ok": bool, "error"?: str, "skipped"?: str}, ...]
    """
    event_enum = _coerce_event(event)
    if event_enum is None:
        return [{"ok": False, "error": f"unknown event: {event}"}]
    sev_enum = _coerce_severity(severity)

    # 설정 로드
    try:
        cfg = _config.load()
    except Exception as e:
        print(f"[notify] config load failed: {e}", file=sys.stderr)
        return [{"ok": False, "error": f"config: {e}"}]

    # mute 리스트
    if event_enum.value in cfg.mute_events:
        return [{"ok": True, "skipped": "muted"}]

    # throttle (dry-run 모드에선 skip 안 함)
    if not dry_run and router.should_throttle(event_enum.value, cfg.throttle_seconds):
        return [{"ok": True, "skipped": "throttled"}]

    targets = cfg.chat_ids_for(sev_enum.value)
    if not targets:
        return [{"ok": True, "skipped": "no chat_ids for severity"}]

    # 메시지 구성
    header = format_title(event_enum, title)
    full_text = f"{header}\n\n{body}".strip()

    if dry_run:
        return [
            {"chat_id": cid, "ok": True, "dry_run": True, "preview_len": len(full_text)}
            for cid in targets
        ]

    results: list[dict[str, Any]] = []
    for cid in targets:
        for part in telegram.split_message(full_text):
            try:
                telegram.send_message(cfg.token, cid, part)
                results.append({"chat_id": cid, "ok": True})
            except Exception as e:
                results.append({"chat_id": cid, "ok": False, "error": str(e)[:200]})
                break  # 한 chat 에서 실패하면 분할 나머지도 건너뜀
    return results


__all__ = ["send", "Event", "Severity", "EVENT_EMOJI", "format_title"]

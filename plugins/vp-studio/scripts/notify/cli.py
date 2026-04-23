"""
Notify CLI.

사용:
  python -m notify.cli send \\
    --event SESSION_SAVED --title "Scene 042 saved" --body "{docs_root}/.../session.md"
  python -m notify.cli send --event DAILY_RECAP --title test --body hi --dry-run

--body 가 '-' 이면 stdin 에서 읽음 (긴 본문용).

exit code:
  0: 전부 성공 (또는 모두 skipped)
  1: 일부/전부 실패
  2: 인자/설정 오류
"""

from __future__ import annotations

import argparse
import json
import sys

from . import Event, Severity, send


def _resolve_event(raw: str) -> Event | None:
    """대문자 이름/lowercase value 모두 허용. 실패 시 None."""
    try:
        return Event[raw] if raw.isupper() else Event(raw)
    except (KeyError, ValueError):
        return None


def _resolve_severity(raw: str | None) -> Severity | None:
    """argparse choices 로 1차 검증되지만 방어적으로 한 번 더. 실패 시 None."""
    if not raw:
        return Severity.INFO
    try:
        return Severity[raw.upper()]
    except KeyError:
        return None


def cmd_send(args: argparse.Namespace) -> int:
    event = _resolve_event(args.event)
    if event is None:
        print(f"[notify] unknown event: {args.event}", file=sys.stderr)
        print(f"  available: {', '.join(e.name for e in Event)}", file=sys.stderr)
        return 2

    severity = _resolve_severity(args.severity)
    if severity is None:
        print(f"[notify] unknown severity: {args.severity}", file=sys.stderr)
        return 2

    body = sys.stdin.read() if args.body == "-" else args.body

    meta = None
    if args.meta:
        try:
            meta = json.loads(args.meta)
        except Exception as e:
            print(f"[notify] --meta JSON 파싱 실패: {e}", file=sys.stderr)
            return 2

    results = send(
        event=event,
        title=args.title,
        body=body,
        severity=severity,
        meta=meta,
        dry_run=args.dry_run,
    )

    for r in results:
        print(json.dumps(r, ensure_ascii=False))

    # 모든 결과에 ok=True 이거나 skipped 면 성공
    any_fail = any(not r.get("ok", False) for r in results)
    return 1 if any_fail else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="notify")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send", help="이벤트 전송")
    p_send.add_argument("--event", required=True, help="Event enum name 또는 value")
    p_send.add_argument("--title", required=True)
    p_send.add_argument("--body", default="", help="'-' 이면 stdin 에서 읽음")
    p_send.add_argument("--severity", default="info", choices=["info", "warn", "critical"])
    p_send.add_argument("--meta", default=None, help="JSON 문자열")
    p_send.add_argument("--dry-run", action="store_true")
    p_send.set_defaults(func=cmd_send)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

"""
Notify 설정 로더.

Telegram token은 ~/.openclaw/openclaw.json 의 channels.telegram.botToken
재사용 (이중 관리 방지). 사용자 홈 디렉토리에 있는 파일이므로 스튜디오 독립.

VP 전용 라우팅 규칙은 `notify.yaml` 에서 읽음. 위치는 _paths.notify_config_path()
로 결정 — 기본은 {project_root}/tools/config/notify.yaml, legacy fallback
{project_root}/vp/config/notify.yaml.

notify.yaml 스키마 예시:
  chat_ids:
    - "1899267464"
    - "7998914882"
  severity_map:       # chat_id → 받을 severity 허용 리스트
    "1899267464": [info, warn, critical]
    "7998914882": [warn, critical]
  mute_events:        # 완전히 끌 이벤트 타입
    - "build_failed"
  throttle_seconds: 60
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import _yaml
from ._paths import notify_config_path

# 하위호환: `config._tiny_yaml_parse` 로 import 하는 외부 호출자 대비.
_tiny_yaml_parse = _yaml.parse


DEFAULT_CHAT_IDS: list[str] = []  # Plugin 기본값: 비어있음. Project 가 notify.yaml 로 주입.
DEFAULT_THROTTLE_SEC = 60


@dataclass
class NotifyConfig:
    token: str
    chat_ids: list[str] = field(default_factory=list)
    severity_map: dict[str, list[str]] = field(default_factory=dict)
    mute_events: set[str] = field(default_factory=set)
    throttle_seconds: int = DEFAULT_THROTTLE_SEC

    def chat_ids_for(self, severity: str) -> list[str]:
        """severity 에 맞는 chat_id 리스트. severity_map 없으면 전부 허용."""
        if not self.severity_map:
            return list(self.chat_ids)
        return [
            cid for cid in self.chat_ids
            if self.severity_map.get(cid) is None
            or severity in self.severity_map[cid]
        ]


def _load_token_from_openclaw() -> str | None:
    """~/.openclaw/openclaw.json 의 channels.telegram.botToken."""
    candidates = [
        Path.home() / ".openclaw" / "openclaw.json",
    ]
    for p in candidates:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            token = (data.get("channels", {}) or {}).get("telegram", {}).get("botToken")
            if token:
                return token
        except Exception:
            continue
    return None


def _load_yaml_rules(path: Path) -> dict[str, Any]:
    """
    notify.yaml 로드. PyYAML 이 있으면 정식 파서, 없으면 내장 `_yaml.parse` 사용.
    파일 부재·파싱 오류 시 빈 dict.
    """
    if not path.exists():
        return {}
    try:
        try:
            import yaml  # type: ignore
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except ImportError:
            return _yaml.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load() -> NotifyConfig:
    """설정 로드. 필수: token. 나머지는 기본값 + yaml 오버라이드."""
    token = _load_token_from_openclaw() or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Telegram bot token 을 찾을 수 없습니다. "
            "~/.openclaw/openclaw.json 의 channels.telegram.botToken 또는 "
            "TELEGRAM_BOT_TOKEN 환경변수를 설정하세요."
        )

    yaml_rules = _load_yaml_rules(notify_config_path())

    # 숫자가 섞여 오면 문자열화 (YAML 이 "1234567" 을 int 로 강제 변환하는 케이스 방어)
    chat_ids = [str(c) for c in (yaml_rules.get("chat_ids") or DEFAULT_CHAT_IDS)]

    severity_map_raw = yaml_rules.get("severity_map") or {}
    severity_map = {str(k): list(v) for k, v in severity_map_raw.items()}

    mute_events = set(yaml_rules.get("mute_events") or [])
    throttle = int(yaml_rules.get("throttle_seconds") or DEFAULT_THROTTLE_SEC)

    return NotifyConfig(
        token=token,
        chat_ids=chat_ids,
        severity_map=severity_map,
        mute_events=mute_events,
        throttle_seconds=throttle,
    )

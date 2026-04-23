"""
notify 패키지 공용 경로 헬퍼.

Plugin 버전은 Project 루트 탐색 대신 환경변수를 우선 사용.
"""

from __future__ import annotations

import os
from pathlib import Path


def find_project_root() -> Path:
    """
    Project 루트 경로 결정.

    우선순위:
      1. ``$CLAUDE_PROJECT_DIR`` — Claude Code 가 세션 Project 루트로 주입
      2. ``$VP_STUDIO_ROOT`` — 수동 오버라이드 (legacy 환경변수)
      3. 현재 작업 디렉토리 (cwd)
    """
    for var in ("CLAUDE_PROJECT_DIR", "VP_STUDIO_ROOT"):
        v = os.environ.get(var)
        if v:
            return Path(v)
    return Path.cwd()


def notify_config_path() -> Path:
    """
    notify.yaml 위치 결정.

    우선순위:
      1. ``$NOTIFY_CONFIG`` — 명시적 파일 경로
      2. ``{project_root}/tools/config/notify.yaml`` — new layout 기대 위치
      3. ``{project_root}/vp/config/notify.yaml`` — legacy 위치 (transition)
    """
    explicit = os.environ.get("NOTIFY_CONFIG")
    if explicit:
        return Path(explicit)
    root = find_project_root()
    new_path = root / "tools" / "config" / "notify.yaml"
    if new_path.exists():
        return new_path
    return root / "vp" / "config" / "notify.yaml"


def throttle_state_path() -> Path:
    """
    throttle.json 위치. Hub 의 logs 하위에 저장.

    우선순위:
      1. ``$NOTIFY_THROTTLE_PATH`` — 명시적 파일 경로
      2. ``{project_root}/tools/logs/notify/throttle.json`` — new layout
      3. ``{project_root}/vp/logs/notify/throttle.json`` — legacy
    """
    explicit = os.environ.get("NOTIFY_THROTTLE_PATH")
    if explicit:
        return Path(explicit)
    root = find_project_root()
    new_path = root / "tools" / "logs" / "notify" / "throttle.json"
    if new_path.parent.exists():
        return new_path
    return root / "vp" / "logs" / "notify" / "throttle.json"

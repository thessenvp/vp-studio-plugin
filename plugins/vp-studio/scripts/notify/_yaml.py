"""
notify.yaml 전용 초경량 YAML 파서.

PyYAML 이 없는 환경(CI·최소 설치)에서도 동작하도록 외부 의존성 없이
key: value / 리스트 / 2단 중첩 매핑만 지원한다.

지원하지 않는 문법(블록 스칼라, 앵커, 복합형 리스트 item 등)을 만나면
조용히 무시한다 — 본 파일은 `notify.yaml` 의 단순 스키마 전용이다.

외부에서 직접 쓰지 말 것 (`_` prefix).
"""

from __future__ import annotations

from typing import Any


def _coerce(value: str) -> Any:
    """YAML 스칼라를 bool/int/str 로 형변환."""
    s = value.strip().strip('"').strip("'")
    lowered = s.lower()
    if lowered in ("true", "yes"):
        return True
    if lowered in ("false", "no"):
        return False
    if s.isdigit():
        return int(s)
    return s


def parse(text: str) -> dict[str, Any]:
    """
    제한적 YAML 파싱 — key: value, 리스트(- item), 2단 중첩 매핑만 지원.

    Returns:
        최상위 key 를 dict 로 돌려준다. 파싱 실패 라인은 무시.
    """
    result: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list | None = None
    current_map: dict | None = None

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))

        if indent == 0 and ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                current_key = key
                current_list = None
                current_map = None
                result[key] = None
            else:
                result[key] = _coerce(val)
                current_key = None
                current_list = None
                current_map = None
            continue

        if indent >= 2 and current_key is not None:
            if stripped.startswith("- "):
                if current_list is None:
                    current_list = []
                    result[current_key] = current_list
                current_list.append(_coerce(stripped[2:]))
            elif ":" in stripped:
                if current_map is None:
                    current_map = {}
                    result[current_key] = current_map
                k, _, v = stripped.partition(":")
                k, v = k.strip(), v.strip()
                if v.startswith("[") and v.endswith("]"):
                    items = [_coerce(x) for x in v[1:-1].split(",") if x.strip()]
                    current_map[k] = items
                else:
                    current_map[k] = _coerce(v)
    return result

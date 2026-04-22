# 3-Layer Architecture

`vp-studio` plugin은 재사용 가능한 도구 레이어. Project·Hub와 역할이 분리되어 있다.

## 레이어 정의

| 레이어 | 정의 | 라이프사이클 | 경로 기준 |
|---|---|---|---|
| **Plugin** | 재사용 가능한 도구·에이전트·규칙·스크립트 | 버전 릴리스 | `${CLAUDE_PLUGIN_ROOT}` 내부 |
| **Project** | 특정 프로젝트의 설정·인프라·워크플로·토큰·로컬 드라이브 | 프로젝트 생명주기 | `${CLAUDE_PROJECT_DIR}` 루트 |
| **Hub** | task 산출물 데이터 (문서·세션·DB·로그·inbox·wiki·projects 메타) | 지속 누적 | `${CLAUDE_PROJECT_DIR}` 내부, userConfig 주입 |

## 의존 방향

```
Plugin ──uses──▶ Project (via userConfig: hub_cli.*, *_root paths)
Plugin ──reads──▶ Hub      (via userConfig: docs_root, sessions_root, ...)
Project ──writes──▶ Hub
```

Plugin은 Project·Hub 경로를 **절대 하드코딩하지 않는다**. 모두 `userConfig` 변수로 주입받는다.

## 각 레이어가 소유하는 것

### Plugin 소유
- `agents/` — agent SSOT (CLAUDE.md + rules)
- `skills/` — 재사용 가능한 skill 묶음
- `commands/` — 슬래시 커맨드
- `scripts/` — Plugin 번들 스크립트 (gemma.ps1, notify 어댑터)
- `hooks/hooks.json` — Plugin 기본 hook
- `.claude-plugin/plugin.json` — manifest + userConfig 스키마
- `.claude-plugin/settings.json` — Plugin 기본 권한·deny

### Project 소유
- 프로젝트 CLAUDE.md (worktree 정책, archive 정책, 이 repo 고유 규율)
- `.githooks/` — 이 repo git safety net
- 프로젝트 CLI 코드 (`doc_manager/`, `doc_verifier/`, `reviewer/`, `confluence_migrator/`)
- 프로젝트 설정 (`settings.json` 의 로컬 드라이브·엔드포인트·토큰)
- 프로젝트 인프라 (`.claude/docker/`, openclaw, unreal-mcp 등)
- 프로젝트 워크플로 스크립트 (worktree_sync, worktree_cleanup, daily_recap_push)
- telemetry 구현체 (도메인 지표 스키마)

### Hub 소유
- `vp/inbox/` — 원료 수집
- `vp/wiki/` — 증류된 지식
- `vp/docs/*/sessions/` — 세션 기록
- `vp/docs/daily/` — daily recap
- `vp/docs/*/troubleshooting/`, `technical/` 등 — 도메인 문서
- `vp/logs/` — 텔레메트리 jsonl, notify throttle
- `projects/` — 프로젝트 단위 SSOT 메타데이터 (project-agent·scenario-agent 관리)
- `doc_manager.db`·`doc_verifier.db` — 검색·검증 인덱스

## Cross-Layer Interface

| 방향 | 매개 | 예시 |
|---|---|---|
| Plugin→Hub | userConfig `*_root` | `${sessions_root}` 아래 세션 파일 탐색 |
| Plugin→Project | userConfig `hub_cli.*`, `vpo_plugin_root` 등 | skill 이 Project CLI shell out |
| Project→Hub | Project 코드가 Hub 경로로 직접 쓰기 | save-session → `${docs_root}/pipeline/sessions/` |
| Project→Plugin | 없음 (Plugin 은 Project 를 모름) | — |

## 설계 원칙

1. **Plugin 은 Hub 데이터를 동반 이동하지 않는다.** 스키마 enum·도메인 리스트도 Project 가 오버라이드 가능해야 한다.
2. **Plugin 은 Project 코드를 직접 import 하지 않는다.** CLI shell out (userConfig 로 경로 주입) 만 허용.
3. **Hub 파일 소유권** 은 각 Project 가 CLAUDE.md 에 명시한다. Plugin 은 "읽기 전용" 기본값.
4. **Plugin userConfig 미설정 시** — skill 은 default 로 동작하거나 graceful fallback (예: `ollama_enabled=false` 면 Gemma 위임 no-op).

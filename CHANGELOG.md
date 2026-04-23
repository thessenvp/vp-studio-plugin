# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-23

첫 번째 안정화 릴리즈. Phase 7 시리즈(스튜디오 공유 드라이브 통합)와
에이전트 권한 시스템이 완성되어 v1.0.0 으로 격상.
pre-production → on-set → post → 공유 승격까지 엔드-투-엔드 VP Supervisor
워크플로우가 플러그인 한 장으로 커버됨.

### Added (promote-share — Phase 7c)
- **`promote-share` skill** — 개인 스크래치 → `_shared/labs/` 승격 공식 절차
  - **Step 3 리뷰 게이트 필수**: 사용자 명시적 승인(번호 선택 또는 all) 없이 Step 4 절대 불가
  - Step 0: userConfig 검증 + Z:\ probe (오프라인 시 `.pending-promote.json` 기록)
  - Step 1~2: 후보 파일 탐색 + 요약 출력 (frontmatter + 첫 섹션)
  - Step 4: 파일명 규칙 적용(`{date}_{initials}_{topic}.md`) + cp(원본 유지)
  - `--dry-run` 옵션: 리뷰 게이트까지만 실행, 실제 복사 없음
  - 오프라인 대기 흐름: Z:\ 복구 후 재실행 시 대기 목록 자동 감지 + 이미 리뷰된 파일은 게이트 재생략
- `vp-agent/CLAUDE.md` 라우팅 테이블에 `승격 / promote / labs 올리기` 키워드 추가

### Added (settings.json — Phase 7)
- **`agents/vp-agent/.claude/settings.json`** — VP Supervisor 기본 Bash 권한
  - Allow: `find`, `ls`, `mkdir`, `cp`, `mv`, `cat`, `head`, `tail`, `wc`, `echo`, `python`, `powershell`, `git status/log/diff/add/show/branch`, `icacls`
  - Deny: `git commit/push/reset --hard/checkout/branch -D/rebase/merge`, `rm -rf/f`, `pip/npm install`
- **`agents/refactorer/.claude/settings.json`** — Refactorer 기본 Bash 권한 (읽기 중심)
  - Allow: 파일 읽기 + git 읽기 전용 (`find`, `ls`, `cat/head/tail/wc`, `git status/log/diff/show/branch`)
  - Deny: 모든 git 쓰기, 삭제, 패키지 관리

### Added (studio-share — Phase 7b)
- **4 new userConfig fields** in `plugin.json`:
  - `studio_share_root` — Z:/VPO/6_claude 공유 드라이브 루트 (비어 있으면 로컬 Hub 경로 유지)
  - `active_user` — 개인 스크래치 스코핑용 사용자 디렉토리명
  - `user_initials` — `_shared/` 파일명 충돌 방지 이니셜 (예: `MK`)
  - `labs_root` — `_shared/labs` 내부 실험 영역 (NTFS ACL 제한)
- **`studio-share.md` rule** (`agents/vp-agent/.claude/rules/`) — 3-tier 디렉토리 구조, promote-then-write 흐름, 오프라인 Z:\ probe 패턴, `_projects/` 쓰기 금지 정책
- `vp-agent/CLAUDE.md` 라우팅 테이블에 `studio share / labs / _shared / 공유 드라이브` 키워드 항목 추가

## [0.2.0] - 2026-04-23

Content migration wave — VP rules, agent SSOTs, Plugin scripts, and the
full VP Supervisor skill suite land. Plugin now covers the end-to-end
workflow (Pre-prod → Quality Gate → On-set → Post → Support). Still
beta (0.x); Project CLI wiring and multi-studio testing remain before
1.0.0.

### Added
- **15 vp-agent rules** under `agents/vp-agent/.claude/rules/`:
  - Domain-general (Phase 2, 8): `asset-naming`, `optitrack`,
    `color-pipeline`, `shoot-protocol`, `vp-equipment`, `vp-session`,
    `vp-supervisor`, `development`
  - Path-abstracted (Phase 3, 6): `gemma-delegation`, `knowledge-base`,
    `save-session`, `unreal-engine`, `perforce`, `plugins`
  - Principle-only port (Phase 3 addendum, 1): `modules`
- **4 agent SSOTs** + 2 pointer files + registry:
  - `agents/vp-agent/CLAUDE.md` with routing table of 27 keyword → rule
    / skill mappings (Project-scope routes `doc-verification`,
    `claude-ecosystem`, `openclaw-boundary`, `vp-review` intentionally
    excluded)
  - `agents/project-agent/CLAUDE.md`, `agents/scenario-agent/CLAUDE.md`
  - `agents/refactorer/CLAUDE.md` + `rules/refactor-policy.md` +
    `rules/escalation.md`
  - Pointer files `agents/vp-agent.md` + `agents/refactorer.md`
  - `agents/registry.md` reframed for Plugin scope
- **Plugin-bundled scripts** under `scripts/`:
  - `gemma.ps1` — reads `$env:OLLAMA_{ENDPOINT,MODEL,TEMP,ENABLED}`
    matching userConfig; `enabled=false` → exit 3 graceful no-op;
    optional telemetry hook via `$env:VP_TELEMETRY_SCRIPT`
  - `notify/` package — merged from origin's split layout
    (`vp/scripts/utils/notify` + `vp/modules/utils/notify`) into single
    flat package with relative imports; `notify.yaml` fallback chain
    (`$NOTIFY_CONFIG` → `tools/config/` → `vp/config/`); token still
    sourced from `~/.openclaw/openclaw.json`
- **16 VP Supervisor skills** (sync-check landed in v0.1.0; 16 added
  here bring total to 17):
  - Quality Gate / On-set (Phase 6.1, 7): `take-log`, `opt-review`,
    `color-check`, `shoot-gate`, `kpi-report`, `data-wrangle`,
    `handoff-pack`
  - Briefing / Risk / Recap / Pre-prep (Phase 6.2, 9):
    `asset-checklist`, `brief-scene`, `team-brief`, `mocap-brief`,
    `risk-flag`, `risk-scenario`, `resource-plan`, `supervisor-recap`,
    `daily-recap`
  - `asset-checklist` is a late addition — it was referenced as a
    shoot-gate prerequisite but missing from the original Phase plan
- **Graceful fallback** on every terminal ingest/notify step in Phase
  6.1 + 6.2 skills — if `hub_cli_doc_manager` / `notify_channels` are
  unset, skip the step with a one-line user notice showing the manual
  command, and treat the skill as 정상 완료 since the primary artefact
  is already on disk

### Changed
- Small quality improvements per pre-migration review (Q3=α):
  - `resource-plan`: burnout threshold levels made explicit
    (HIGH 3d consec → MEDIUM; 5d or weekend → HIGH), schedule-risk
    formula annotated with parallel-capacity multiplier
  - `supervisor-recap`: added explicit `risk-flag` file scan; grep
    patterns switched to `-E` regex for override/blocker keywords;
    warning when tomorrow's `shoot_schedule` is missing
  - `daily-recap`: `{요일}` template placeholder wired to Step 3's
    weekday display directive; note added on git-commit-date vs
    filename-date precedence
- Rule references throughout skills rewritten as
  "vp-agent 의 `<rule>.md` rule" prose to disambiguate from
  Project-layer rules with overlapping names

### Excluded (intentionally)
- `doc-stats` skill — 34-line CLI wrapper over `doc_manager stats`;
  Project-scope per A1 decision, stays at origin
- `openclaw-boundary.md`, `doc-verification.md`, `claude-ecosystem.md`
  rules — Project infrastructure, not portable across studios
- `worktree_sync.py`, `worktree_cleanup.py`, `doc_manager` / `doc_verifier`
  / `reviewer` / `confluence_migrator` / `telemetry` / `hook_recorder` —
  Project-owned CLIs reached via `hub_cli_*` userConfig (Hub CLI
  Contract)

### Added (infra)
- `plan-migration.md` — session handover document capturing full plan,
  progress, open decisions, and resumption instructions

### Known limitations
- Plugin convention expects flat `agents/*.md`; the folder-SSOT pattern
  (`agents/<name>/CLAUDE.md` + `.claude/rules/*.md`) triggers informational
  frontmatter warnings on non-pointer files from `claude plugin validate`.
  Functional agent definitions (pointer files) are fully valid.
- Project CLIs (`doc_manager`, `doc_verifier`, etc.) must be wired via
  userConfig before Hub-writing skills can round-trip through DB ingest.
  Missing config falls back to manual-ingest notice (graceful, not fatal).

## [0.1.0] - 2026-04-22

First pre-release. Scaffold + three-layer architecture contracts + Plugin layer PoC.

### Added
- Marketplace manifest (`vp-studio-plugin`) with kebab-case identifier.
- Plugin manifest (`vp-studio`) with 26 `userConfig` fields covering:
  - Hub paths (10): `hub_root`, `docs_root`, `sessions_root`,
    `briefings_root`, `mocap_sessions_root`, `risk_playbooks_root`,
    `daily_root`, `inbox_root`, `wiki_root`, `doc_manager_db_path`
  - Hub CLI bindings (5): `hub_cli_python`, `hub_cli_doc_manager`,
    `hub_cli_doc_verifier`, `hub_cli_reviewer`,
    `hub_cli_confluence_migrator`
  - Ollama/Gemma delegation (4): `ollama_{enabled,endpoint,model,temperature}`
  - Project infrastructure (3): `vpo_plugin_root`,
    `perforce_workspace_root`, `ue_engine_5_7_path`
  - External integrations (2): `confluence_{enabled,base_url}`
  - Feature toggles (2): `telemetry_enabled`, `notify_channels`
  - Safety (1): `hub_read_only_paths`
- Architecture docs under `plugins/vp-studio/docs/architecture/`:
  - `layers.md` — Plugin / Project / Hub three-layer separation and
    ownership, Plugin never hardcodes Project/Hub paths
  - `hub-cli-contract.md` — `hub_cli.*` userConfig contract, skill
    → Project CLI dependency matrix, MCP server stays in Project layer
  - `projects-permissions.md` — per-agent write matrix for `projects/`
    (project-agent → metadata, scenario-agent → scenarios/**, vp-agent
    → read-only via symlink)
- `sync-check` skill (Plugin layer PoC) — Genlock/Timecode chain
  verification with graceful `hub_cli_*` fallback.

### Changed
- Repo renamed from `vp-studio-marketplace` → `vp-studio-plugin`.
- Marketplace internal `name` aligned with repo name.
- Dropped explicit component paths in `plugin.json` (validator rejects
  empty directories declared as paths).

[Unreleased]: https://github.com/thessenvp/vp-studio-plugin/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thessenvp/vp-studio-plugin/releases/tag/v1.0.0
[0.2.0]: https://github.com/thessenvp/vp-studio-plugin/releases/tag/v0.2.0
[0.1.0]: https://github.com/thessenvp/vp-studio-plugin/releases/tag/v0.1.0

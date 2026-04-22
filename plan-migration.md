# VP-Studio 마이그레이션 플랜

> **작성일**: 2026-04-22
> **목적**: VP-Studio 를 Claude Code Plugin + 정돈된 Project/Knowledge 구조로 재편하는 중. 세션 인수인계용 전체 현황 문서.

---

## 1. 배경

기존 `VP-Studio/` 한 개 repo 에 플러그인성 재사용 도구 + 스튜디오 고유 설정 + task 산출 데이터가 전부 섞여 있음. 이를 **3-레이어 아키텍처** 로 분리 중.

- **Plugin** — 도구·에이전트·규칙·스킬 (다른 스튜디오에서도 재사용 가능)
- **Project (tools/)** — 이 스튜디오 고유 인프라 코드·CLI·설정
- **Knowledges** + **Projects (per-project)** — task 산출 데이터

---

## 2. 물리 저장소

| 저장소 | 역할 | 위치 |
|---|---|---|
| **`vp-studio-plugin/`** | Plugin repo | 로컬: `C:\Users\minkyun_park\Documents\Claude\vp-studio-plugin\` · GitHub: `thessenvp/vp-studio-plugin` |
| **`VP-Studio/`** | Project + Knowledge + Hub 모두 수용 (main repo) | `C:\Users\minkyun_park\Documents\Claude\VP-Studio\` |

---

## 3. 아키텍처 결정 사항 (확정)

### 3-1. 3-레이어 계약

Plugin 은 Project·Knowledge 에 대해 **경로를 하드코딩하지 않음**. `userConfig` 변수로 주입받음.

의존 방향:
```
Plugin ──uses──▶ Project  (via userConfig: hub_cli.*)
Plugin ──reads──▶ Knowledge/Hub (via userConfig: *_root)
Project ──writes──▶ Knowledge/Hub
```

상세: [`plugins/vp-studio/docs/architecture/layers.md`](plugins/vp-studio/docs/architecture/layers.md)

### 3-2. Hub CLI Contract

Plugin skill 은 Project 가 보유한 CLI 를 shell out 으로 호출. 경로는 userConfig `hub_cli_*` 로 주입.

상세: [`plugins/vp-studio/docs/architecture/hub-cli-contract.md`](plugins/vp-studio/docs/architecture/hub-cli-contract.md)

### 3-3. `projects/` 권한 매트릭스

- project-agent → `project.yaml` 쓰기
- scenario-agent → `scenarios/**` 쓰기
- vp-agent → 읽기만 (`vp/.project-refs/{PROJ}` symlink 경유)

상세: [`plugins/vp-studio/docs/architecture/projects-permissions.md`](plugins/vp-studio/docs/architecture/projects-permissions.md)

### 3-4. 폴더 구조 — VP-Studio 쪽 (확정, 단 `tools/` 네이밍은 잠정)

```
VP-Studio/
├── vp/                          # 🧊 FROZEN reference (절대 수정 금지, 삭제도 안 함)
├── knowledges/                  # 🆕 도메인 일반 지식 (cross-project)
│   ├── concepts/
│   ├── troubleshooting/{mocap,unreal,sync,icvfx,...}
│   ├── technical/{mocap,unreal,...}
│   ├── articles/
│   └── _archive/
├── projects/                    # 🆕 프로젝트별 진행 작업 (per-project)
│   └── {PROJ}/
│       ├── project.yaml
│       ├── scenarios/
│       ├── characters/
│       ├── environments/
│       ├── sessions/
│       ├── briefings/
│       ├── daily/
│       ├── takes/
│       ├── risk-playbooks/
│       └── data/
├── tools/                       # 🆕 [잠정] Project 인프라 코드
│   ├── config/
│   ├── scripts/{doc_manager,doc_verifier,reviewer,confluence_migrator,telemetry,worktree,...}
│   ├── modules/utils/{notify,telemetry}/
│   ├── tests/
│   ├── docker/openclaw/
│   └── unreal/mcp/
├── agents/                      # 현 위치 유지 (플러그인에도 동일 구조로 존재, drift 주의)
├── .claude/                     # 현 위치 유지
├── .githooks/                   # 현 위치 유지 (이 repo 전용)
├── .mcp.json                    # 현 위치 유지
└── CLAUDE.md                    # 유지 (라우팅은 점진적으로 플러그인 측으로 이동)
```

### 3-5. 플러그인 구조 (현 상태)

```
vp-studio-plugin/
├── .claude-plugin/marketplace.json
├── .github/workflows/
│   ├── validate.yml                   # jq 기반 매니페스트 검증
│   └── release.yml                    # v* tag 시 auto-release
├── CHANGELOG.md                       # Keep-a-Changelog
├── README.md
├── CHANGELOG.md
├── plan-migration.md                  # ← 이 문서
└── plugins/
    └── vp-studio/
        ├── .claude-plugin/plugin.json # userConfig 26 필드
        ├── README.md
        ├── docs/architecture/
        │   ├── layers.md
        │   ├── hub-cli-contract.md
        │   └── projects-permissions.md
        ├── agents/
        ├── skills/
        │   └── sync-check/SKILL.md     # Phase 1 완료
        ├── commands/ (빈)
        └── hooks/hooks.json (빈)
```

---

## 4. 전체 Phase 플랜

| Phase | 목적 | 상태 | 비고 |
|---|---|---|---|
| **0.1** | 3-레이어 계약 문서 작성 | ✅ | plugin 내 architecture 문서 3개 |
| **0.2** | userConfig 스키마 (26 필드) | ✅ | plugin.json |
| **0.3** | 버저닝 인프라 (Tag·Release·CI) | ✅ | validate.yml + release.yml |
| **1** | sync-check PoC | ✅ | Plugin layer 첫 skill |
| **2** | 도메인 일반 rules 이식 (8개) | 🔜 다음 | asset-naming / optitrack / color-pipeline / shoot-protocol / vp-equipment / vp-session / vp-supervisor / development |
| **3** | 경로 재작성 필요 rules 이식 (6개) | — | gemma-delegation / knowledge-base / save-session / unreal-engine / perforce / plugins |
| **4** | Agent SSOT 이식 | — | vp-agent / project-agent / scenario-agent / refactorer + registry + 포인터 2개 |
| **5** | Plugin 스크립트 이식 | — | gemma.ps1 (userConfig 주입), notify (modules 동반) |
| **6.1** | 세션 쓰기 skills (7개) | — | take-log / opt-review / color-check / shoot-gate / kpi-report / data-wrangle / handoff-pack |
| **6.2** | 브리핑·리스크·리뷰 skills (9개) | — | team-brief / mocap-brief / brief-scene / risk-flag / risk-scenario / resource-plan / supervisor-recap / daily-recap / doc-stats |
| **6.3** | new-plugin skill (별도) | — | Z:/VPO 하드코딩 → userConfig 주입 |
| **7** | Plugin settings.json (default perms) | — | wildcard 패턴 (`Bash(python **/notify/cli.py:*)` 등) |
| **9** | 최종 검증 + v1.0.0 릴리스 | — | 전체 재검수 + 로컬 install 스모크 테스트 |

**Phase 8 삭제**: MCP 서버는 Project 에 잔존 (A1 결정). Plugin 은 MCP 번들 안 함.

### 버전 bump 전략 (제안, 미확정)

| 지점 | 버전 |
|---|---|
| 현재 | `v0.1.0` ✅ |
| Phase 2-3 완료 | `v0.2.0` |
| Phase 4 완료 | `v0.3.0` |
| Phase 5 완료 | `v0.4.0` |
| Phase 6.1-6.3 완료 | `v0.5.0` |
| Phase 7 + 검증 통과 | `v1.0.0` |

---

## 5. 현재 진행 상황 (2026-04-22 기준)

### 5-1. 완료된 커밋 (Plugin repo `main`)

```
aceaa32 fix(ci): detect no-op bump by field equality, not git diff
5e0a39b fix(ci): resolve YAML parse error in release.yml PR body
976fee9 ci(release): auto-release workflow on v* tag push
2bf53ef ci(validate): add jq-based manifest validation workflow
cac3d6a feat(marketplace): pin plugin source to GitHub tag
9ca8d41 docs(changelog): initialize CHANGELOG with v0.1.0 entry
44a42e2 feat(plugin): add sync-check skill (Plugin layer PoC)
3475225 feat(plugin): add userConfig schema for hub paths and feature toggles
06524a2 docs(arch): define 3-layer contracts and projects/ permission matrix
078388b refactor: rename marketplace identifier to vp-studio-plugin
1fcd3db fix: marketplace source path + drop path declarations in plugin.json
e02b7d3 chore: scaffold vp-studio-marketplace + vp-studio plugin base
```

### 5-2. 태그·릴리스

- **`v0.1.0`** (`aceaa32`) — Scaffold + 3-layer contracts + sync-check PoC
- GitHub Release: https://github.com/thessenvp/vp-studio-plugin/releases/tag/v0.1.0

### 5-3. CI 상태

- `Validate` workflow: ✅ 통과 (jq 기반, 의존성 없음)
- `Release` workflow: ✅ 통과 (v0.1.0 에서 no-op PR + Release 생성)
- Repo 설정: `default_workflow_permissions=write`, `can_approve_pull_request_reviews=true` (PR 생성 허용)

### 5-4. 확정된 유저 결정

| # | 주제 | 결정 |
|---|---|---|
| A1 | doc_manager/confluence_migrator/reviewer CLI 위치 | **Project (tools/) 유지**, skill 은 `hub_cli_*` userConfig 로 경로 주입 |
| B | sync-check Phase 1 PoC | ✅ 진행 |
| C | `projects/` 권한 매트릭스 | ✅ 확정 (project-agent / scenario-agent / vp-agent) |
| 1 | wiki/concepts 처리 | Knowledge 로 이전 (Studio 는 삭제된 개념) |
| 2 | docs/troubleshooting 처리 | MVP 이후 skill 화 검토, 당장은 Knowledge 로 |
| 3 | worktree_*.py | backlog (일단 Project 쪽 유지) |
| 4 | gemma.ps1 Ollama 엔드포인트 | userConfig 3 필드 (`ollama_{enabled,endpoint,model}`) |
| 5 | settings.json 분리 | 일반 규칙 → Plugin, 프로젝트 특정 → Project |
| Q1 CI | validate workflow | **A**: jq 기반 (Claude CLI 무의존) |
| Q2 CI | 릴리스 자동화 전략 | **Y**: tag push → Action 이 marketplace.json ref 업데이트 PR 생성 |

---

## 6. 결정 필요 사항 (현재 open)

### 6-1. 폴더 네이밍 (마지막 하나)

- `vp/` → FROZEN (확정)
- `knowledges/` → 도메인 지식 (확정)
- `projects/` → 프로젝트별 작업 (확정)
- **`tools/` → Project 인프라 코드** ⚠️ 잠정. 다른 이름 원하면 확정 필요 (후보: `infra/`, `runtime/`)

### 6-2. 세션 기록 소유권 전환

기존: `vp/docs/{domain}/sessions/` (도메인별)
제안: `projects/{PROJ}/sessions/{domain}/` (프로젝트별)

이 변화는 Hub CLI 계약·skill 경로·userConfig 기본값 전반에 영향.

- 동의? 현 도메인 기반 유지?

### 6-3. "현재 활성 프로젝트" 선택 방식

skill 이 `sessions_root` 를 resolve 할 때 `{PROJ}` 어떻게 결정할지:

| 옵션 | 방식 |
|---|---|
| 옵션 X | userConfig `active_project: "Proj_FilmA"` |
| 옵션 Y | skill argument `--project Proj_FilmA` (매번 명시) |
| 옵션 Z | 조합 (userConfig 기본값 + argument override) |

제 추천: **Z** — 기본값 편의 + 명시적 override 가능.

### 6-4. Origin VP-Studio 정리 정책

Phase 9 이후 별도 결정. 현재는 **건드리지 않음** (유저 지시 "NEVER MODIFY ORIGIN").

옵션:
- A. 플러그인 소유분을 VP-Studio 에서 삭제 (단일 SSOT)
- B. 내용을 비우고 포인터만 남김
- C. 이중 유지

### 6-5. Project 측 CLI 개조 (Hub CLI Contract 준수)

Plugin skill 이 `hub_cli_*` 를 호출할 때 Project CLI 가 다음을 지원해야 함:

- 표준 서브커맨드 (`search`, `ingest`, `stats`, `new`, `verify`, `review`)
- 표준 플래그 (`--domain`, `--json`, `--quiet`)
- Exit code 규약

현재 `vp/scripts/utils/doc_manager/cli.py` 는 대부분 준수. 검증 필요. 개조 시 **origin 수정이라 별도 승인 필요**.

---

## 7. 핵심 규율 (이후 작업자 필수 숙지)

### 7-1. 절대 금지

- ❌ **`VP-Studio/` origin 파일 수정·삭제·이동** — 유저가 명시적으로 지시. 모든 마이그레이션은 **복사(read only)** → 플러그인/새 폴더에 작성.
- ❌ 플러그인 내부에 Hub/Project 경로 하드코딩 — 반드시 userConfig.
- ❌ 플러그인 skill 이 Project CLI 구현을 import — shell out (userConfig 경유) 만.
- ❌ `git push` 자동화 (settings.json `deny`로도 차단 — 유저 승인 유지).

### 7-2. 커밋·릴리스 규율

- 1 Phase = 1 논리 단위 = 1 커밋. 매 커밋마다 `claude plugin validate` + CI `Validate` 통과 필수.
- 커밋 메시지 scope prefix (`feat(plugin):`, `docs(arch):`, `ci(release):`) 사용.
- 버전 bump 시:
  1. `CHANGELOG.md` 에 새 섹션 추가
  2. `plugin.json` 의 `version` 업데이트
  3. 커밋 → tag `v<x.y.z>` → `git push --follow-tags`
  4. release.yml 이 자동으로 marketplace.json ref 업데이트 PR + GitHub Release 생성
  5. PR 수동 머지

### 7-3. 경로 재작성 참조

Plugin 내부 리소스 참조 시:
- **Plugin → Plugin 내부**: 상대경로 (skill 에서 다른 rule 참조 등)
- **Plugin → Hub**: `${CLAUDE_PROJECT_DIR}/...` 또는 userConfig `${*_root}`
- **Plugin → Project**: userConfig `hub_cli_*`, `vpo_plugin_root` 등
- **`${CLAUDE_PLUGIN_ROOT}` 은 settings.json permission matcher 에서 미지원** — 대신 wildcard 사용 (`Bash(python **/scripts/*/cli.py:*)`)

---

## 8. 이어받을 때 시작 포인트

### 8-1. 즉시 실행 가능

1. 결정 필요 사항 6-1 ~ 6-3 을 유저에게 확인
2. 6-1 확정되면 `studio/` or `tools/` 폴더 스캐폴드 작업 (단, **VP-Studio 쪽이라 유저 명시 승인 필요**)
3. Phase 2 진행 — 도메인 일반 rules 8개 이식:
   - origin: `VP-Studio/agents/vp-agent/.claude/rules/{asset-naming,optitrack,color-pipeline,shoot-protocol,vp-equipment,vp-session,vp-supervisor,development}.md`
   - 대상: `vp-studio-plugin/plugins/vp-studio/agents/vp-agent/.claude/rules/` (구조 동일 유지)

### 8-2. 주요 명령 치트시트

```bash
# 플러그인 검증
claude plugin validate "C:/Users/minkyun_park/Documents/Claude/vp-studio-plugin"
claude plugin validate "C:/Users/minkyun_park/Documents/Claude/vp-studio-plugin/plugins/vp-studio"

# 로컬 install 테스트 (Claude Code CLI)
claude --plugin-dir "C:/Users/minkyun_park/Documents/Claude/vp-studio-plugin/plugins/vp-studio"

# 또는 마켓플레이스 경유
# CLI 내에서:
#   /plugin marketplace add C:/Users/minkyun_park/Documents/Claude/vp-studio-plugin
#   /plugin install vp-studio@vp-studio-plugin

# CI 상태
gh run list --repo thessenvp/vp-studio-plugin --limit 5
gh release view v0.1.0 --repo thessenvp/vp-studio-plugin

# 릴리스 워크플로 (v0.2.0 예시)
# 1. plugin.json version 업데이트, CHANGELOG 추가, 커밋
# 2. git tag -a v0.2.0 -m "..."
# 3. git push origin main --follow-tags
# → 나머지는 자동
```

### 8-3. 참고 파일 한눈에

- 아키텍처: [`plugins/vp-studio/docs/architecture/`](plugins/vp-studio/docs/architecture/)
- Plugin 매니페스트: [`plugins/vp-studio/.claude-plugin/plugin.json`](plugins/vp-studio/.claude-plugin/plugin.json)
- Marketplace 매니페스트: [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
- CI 워크플로: [`.github/workflows/`](.github/workflows/)
- 변경 이력: [`CHANGELOG.md`](CHANGELOG.md)
- Plugin Phase 1 PoC: [`plugins/vp-studio/skills/sync-check/SKILL.md`](plugins/vp-studio/skills/sync-check/SKILL.md)

### 8-4. userConfig 주요 필드 요약 (26개 중 핵심)

| 필드 | 기본값 | 용도 |
|---|---|---|
| `hub_root` | `${CLAUDE_PROJECT_DIR}/vp` | Hub 루트 (⚠️ 새 폴더 구조 확정 시 `studio/hub` 등으로 기본값 변경 필요) |
| `sessions_root` | `${docs_root}/pipeline/sessions` | 세션 파일 루트 |
| `hub_cli_python` | `python` | Python 실행파일 |
| `hub_cli_doc_manager` | `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/doc_manager/cli.py` | doc_manager CLI 경로 |
| `ollama_enabled` | `false` | Gemma 위임 토글 |
| `ollama_endpoint` | `http://localhost:11434` | Ollama 서버 |
| `vpo_plugin_root` | `""` | UE VPO 플러그인 로컬 경로 |
| `hub_read_only_paths` | `vp/sessions/quick-notes.md,vp/_archive/**` | 쓰기 금지 경로 |

전체: [`plugins/vp-studio/.claude-plugin/plugin.json`](plugins/vp-studio/.claude-plugin/plugin.json)

---

## 9. 연락·검토 포인트

- 플러그인 GitHub: https://github.com/thessenvp/vp-studio-plugin
- 이슈 트래킹: GitHub Issues (없으면 생성 필요)
- 유저: `thessenvp@gmail.com` (플러그인 오너)

## 10. 이 문서의 라이프사이클

- **유지 기간**: Phase 9 (v1.0.0) 완료 시까지
- **업데이트 주체**: 매 Phase 완료 시 §5 "현재 진행 상황" 갱신
- **아카이브**: 마이그레이션 완료 후 `docs/history/` 로 이동 또는 `CHANGELOG.md` 에 병합

---
description: Claude Code ecosystem configuration guide — rules, skills, hooks, MCP servers, and document management. Plugin-portable form (paths via userConfig).
globs:
  - ".claude/**"
  - "CLAUDE.md"
---

# Claude Ecosystem Guide

> 본 규칙은 vp-studio 플러그인 내 SSOT 입니다. **경로는 모두 userConfig 변수**로 표기 (`${hub_cli_*}`, `${hub_root}`, `${CLAUDE_PROJECT_DIR}`). Project 측 SSOT 와 동기화 시 인라인 path rewrite 필요.

## 아키텍처 개요

```
CLAUDE.md                          ← 진입점 (키워드 라우팅 테이블)
  ├── .claude/rules/*.md           ← 자동 활성화 규칙 (globs 매칭)
  ├── .claude/skills/*/SKILL.md    ← 명시적 호출 스킬 (/command)
  ├── .claude/settings.json        ← MCP 서버, Hook, 권한 (팀 공유)
  ├── .claude/settings.local.json  ← 개인 설정 (Git 제외)
  └── ${hub_cli_doc_manager}       ← Project 보유 SQLite 문서 검색 CLI
```

## 규칙 파일 (.claude/rules/*.md)

### 작성 형식

```yaml
---
description: (영문 한 줄 설명 — Claude가 규칙 선택 시 사용)
globs:
  - "(파일 패턴 — 해당 파일 작업 시 자동 로드)"
---
```

- `description`: 영문, 한 줄 — Claude가 어떤 규칙을 로드할지 결정하는 핵심 기준
- `globs`: 파일 패턴 배열 — 이 패턴에 매칭되는 파일 작업 시 규칙이 자동 활성화
- 본문: Markdown, 한국어 설명 + 영어 기술 용어
- **하드코딩 금지** — 본문에서 Project 경로 참조 시 `${hub_cli_*}` 또는 `${CLAUDE_PROJECT_DIR}/...` 사용

### 명명 규칙

- 파일명: **kebab-case** (예: `asset-naming.md`, `vp-equipment.md`)
- 주제별 단일 파일 — 하나의 도메인 = 하나의 규칙
- 새 규칙 작성 전 기존 규칙과 중복 확인

### CLAUDE.md 라우팅 필수

새 규칙 파일 생성 시 **반드시** `agents/<agent>/CLAUDE.md` 의 키워드 라우팅 테이블에 항목 추가:

```markdown
| 키워드1, 키워드2, ... | `rule-file.md` | 설명 |
```

### 규칙 vs 스킬 구분

| 기준 | 규칙 (rules) | 스킬 (skills) |
|---|---|---|
| 활성화 | globs 자동 매칭 | 사용자 명시적 호출 (`/name`) |
| 용도 | 지속적 지침, 코딩 컨벤션 | 일회성 작업, 절차 실행 |
| 예시 | 네이밍 규칙, 개발 스타일 | 세션 저장, 문서 검색 |

### 현재 등록된 규칙 (vp-agent 기준)

플러그인 내 vp-agent 규칙 디렉토리: `agents/vp-agent/.claude/rules/`. 실제 등록 목록은 디렉토리 ls 로 확인 (drift 방지를 위해 본 표는 카테고리만 안내).

| 카테고리 | 대표 파일 | 용도 |
|---|---|---|
| 컨벤션 | `asset-naming.md`, `development.md` | UE 에셋·코드 스타일 |
| 도메인 지식 | `optitrack.md`, `unreal-engine.md`, `vp-equipment.md`, `color-pipeline.md`, `shoot-protocol.md` | VP 장비·엔진·촬영 |
| 워크플로 | `vp-session.md`, `save-session.md`, `knowledge-base.md`, `gemma-delegation.md` | 세션·위키·LLM 위임 |
| 거버넌스 | `vp-supervisor.md`, `plugins.md`, `modules.md`, `perforce.md` | Supervisor·플러그인·모듈·VCS |
| 메타 | `claude-ecosystem.md` (본 파일), `studio-share.md` | 생태계 설정·공유 드라이브 |

## 스킬 (.claude/skills/*/SKILL.md)

### 폴더 구조 및 위치 원칙

| Skill 유형 | 위치 (플러그인) | 기준 |
|---|---|---|
| 플러그인 공통 | `plugins/vp-studio/skills/<name>/SKILL.md` | 플러그인이 export 하는 모든 스킬 |
| Agent 한정 (메타 only) | `plugins/vp-studio/agents/<name>/.claude/skills/...` | 거의 사용 안 함 — 대부분 공통 위치로 |

### SKILL.md 형식

```yaml
---
name: (스킬 이름)
description: (설명 — Claude와 사용자 모두에게 표시)
allowed-tools: (허용 도구 목록, 공백 구분)
argument-hint: "(인자 힌트)"
---
```

- `name`: kebab-case
- `allowed-tools`: 최소 권한 원칙 — 필요한 도구만 명시 (Bash, Read, Write, Glob, Grep 등)
- `argument-hint`: 사용자에게 보이는 인자 힌트 (선택)
- 본문: 실행 절차 + 인자 설명 + 결과 해석 방법
- **CLI 호출은 `${hub_cli_python} ${hub_cli_<name>}` 패턴** — Project CLI 하드코딩 금지

### Hub CLI Contract — 스킬 작성자 필독

플러그인 스킬이 Project 의 CLI 를 호출할 때:

1. userConfig 에 `hub_cli_<name>` 필드가 등록되어 있어야 함 (`.claude-plugin/plugin.json`)
2. SKILL.md 에 **사전 조건** 섹션으로 필수 userConfig 명시
3. 호출은 `${hub_cli_python} ${hub_cli_<name>} <subcommand> [args]` 형태
4. CLI 미설치/경로 오류 시 graceful 폴백 메시지 출력 (스킬 중단 또는 skip)

세부: `plugins/vp-studio/docs/architecture/hub-cli-contract.md`

## 설정 파일 (.claude/settings.json)

### 구조

```json
{
  "permissions": {
    "additionalDirectories": ["(외부 경로)"]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "(도구 이름)",
        "hooks": [{ "type": "command", "command": "(bash 명령)" }]
      }
    ]
  }
}
```

### 팀 설정 vs 개인 설정

- `settings.json` — Git 추적, 팀 전체 공유
- `settings.local.json` — `.gitignore` 에 포함, 개인 환경

### MCP 서버 추가 방법 (Project 책임)

> **플러그인은 MCP 서버를 번들하지 않습니다** (plan-migration.md A1 결정). MCP 서버는 Project 측에 배치하고, 플러그인은 doc-manager MCP 가 제공하는 tool 만 read-only 로 활용.

Project 레벨 MCP 서버 등록은 **두 파일 분리**:
- **`.mcp.json`** (프로젝트 루트) — 서버 정의 (`command` / `args` / `env`)
- **`.claude/settings.json`** — 활성화 명시 (`enabledMcpjsonServers`)

> 주의: `.claude/settings.json` 의 `mcpServers` 필드는 현재 스키마에서 허용되지 않음. 반드시 `.mcp.json` 분리 방식을 사용.

#### 절차 (Project 측)

1. `${CLAUDE_PROJECT_DIR}/scripts/{tool}/mcp/server.py` 에 서버 코드 배치
2. 같은 디렉토리에 `requirements.txt` (의존성 명시)
3. 프로젝트 루트 `.mcp.json` 에 등록:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["scripts/{path}/mcp/server.py"],
      "env": { "KEY": "VALUE" }
    }
  }
}
```

4. `.claude/settings.json` 의 `enabledMcpjsonServers` 에 서버 이름 추가:

```json
"enabledMcpjsonServers": ["my-server"]
```

5. Claude Code 세션 재시작 → `claude mcp list` 로 상태 확인

### 권장 MCP 서버 (Project 측 운영 예시)

| 서버 | 위치 (Project) | 제공 기능 |
|---|---|---|
| `doc-manager` | `${CLAUDE_PROJECT_DIR}/scripts/utils/doc_manager/mcp/server.py` | 문서 DB 읽기 전용 — 5 tools: `search_docs` · `list_docs` · `get_doc` · `doc_stats` · `list_doc_categories` |

### Hook 추가 방법

- 지원 타입: `PreToolUse`, `PostToolUse`
- `matcher`: 도구 이름 (Write, Read, Bash 등)
- 환경변수 `$CLAUDE_TOOL_INPUT`: 도구 입력 JSON
- 에러 시 무시 처리 권장: `2>&1 || true`
- 기존 Hook과 matcher 충돌 여부 확인 필수

## 메모리 계층

Claude가 참조하는 정보의 영속성 계층:

```
1. CLAUDE.md              ← 항상 로드 (프로젝트 레벨)
2. .claude/rules/*.md     ← globs 매칭 시 자동 로드
3. .claude/skills/        ← 사용자 호출 시 로드
4. SQLite DB (Project)    ← /search-docs 로 검색
5. sessions/*.md          ← Git 추적, 검색으로 참조
6. Git history            ← git log / git blame
```

- 계층 1~3: 모든 세션에서 자동/수동 적용 (플러그인이 ship)
- 계층 4~5: 검색으로 접근 (Project 측 데이터)
- SQLite DB는 로컬 전용 — `${hub_cli_python} ${hub_cli_doc_manager} rebuild` 로 재구축

## Doc Manager 연동

### CLI 명령어

```bash
${hub_cli_python} ${hub_cli_doc_manager} <command> --project <project-name>
```

| 명령 | 설명 |
|---|---|
| `ingest --file <path>` | MD 파일 DB 등록 |
| `search --query <keyword>` | 키워드 검색 |
| `list` | 전체 문서 목록 |
| `stats` | DB 통계 |
| `rebuild` | DB 전체 재구축 |
| `export` | DB 내보내기 |

### 자동 인제스트 대상 (Project Hook 예시)

Project 측 hook 으로 다음 패턴 자동 ingest 권장:
- `<docs_root>/*/sessions/*.md` — 세션 기록
- `<docs_root>/*/troubleshooting/*.md` — 트러블슈팅
- `<modules_root>/*/module.md` — 코드 모듈 메타데이터

### 새 카테고리 추가 (Project 측)

1. Project 의 `doc_manager/schema.py` 의 `SEED_CATEGORIES` 에 추가
2. `doc_manager/cli.py` 의 `TEMPLATES` 에 템플릿 추가
3. `${hub_cli_python} ${hub_cli_doc_manager} rebuild` 실행

## 체크리스트: 새 구성요소 추가 시

### 규칙 추가

- [ ] `agents/<agent>/.claude/rules/{name}.md` 생성 (frontmatter: description + globs)
- [ ] `agents/<agent>/CLAUDE.md` 키워드 라우팅 테이블에 항목 추가
- [ ] 기존 규칙과 중복/충돌 확인
- [ ] `CHANGELOG.md` 다음 릴리즈 섹션에 등록

### 스킬 추가

- [ ] `plugins/vp-studio/skills/{name}/SKILL.md` 생성
- [ ] frontmatter (`name`, `description`, `allowed-tools`)
- [ ] CLI 호출은 `${hub_cli_*}` 변수 — 하드코딩 금지
- [ ] 사전 조건(필수 userConfig) 섹션 명시
- [ ] CLI 미설치 graceful 폴백
- [ ] `allowed-tools` 최소 권한 설정
- [ ] `CHANGELOG.md` 다음 릴리즈 섹션에 등록

### Hook 추가 (Project 측)

- [ ] Project 의 `.claude/settings.json` hooks 에 등록
- [ ] 기존 Hook 과 matcher 충돌 확인
- [ ] 에러 핸들링 (`2>&1 || true`)
- [ ] 테스트: 의도한 파일 패턴에서만 동작 확인

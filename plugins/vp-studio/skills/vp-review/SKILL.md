---
name: vp-review
description: VP-Studio incremental code review — git diff metrics, static analysis, VP conventions (naming, docstrings, module reuse). Senior-level Korean report.
allowed-tools: Bash Read Glob Grep
argument-hint: "[YYYY-MM-DD | --full]"
---

# Code Review Skill

Run an incremental code review on changes since a given date (or since last review).

## Arguments

- No argument → review changes since last saved review
- `YYYY-MM-DD` → review changes since that date
- `--full` → review entire project

## 사전 조건

- userConfig `hub_cli_python` (default: `python`)
- userConfig `hub_cli_reviewer` (default: `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/reviewer/cli.py`)

`hub_cli_reviewer` 가 가리키는 CLI 가 없으면 다음 메시지 출력 후 중단:

```
⚠️ vp-review 중단 — hub_cli_reviewer userConfig 가 가리키는 CLI 를 찾을 수 없습니다.
   현재 값: ${hub_cli_reviewer}
   Project 의 reviewer CLI 를 설치하거나 경로를 수정해주세요.
```

## Execution Steps

### Step 1: Run Collector

```bash
${hub_cli_python} ${hub_cli_reviewer} review --since "$ARGUMENTS" --json --save
```

If argument is `--full`:
```bash
${hub_cli_python} ${hub_cli_reviewer} review --full --json --save
```

If no argument (incremental since last review):
```bash
${hub_cli_python} ${hub_cli_reviewer} review --json --save
```

### Step 2: Interpret Results as Senior Developer

Read the JSON output from Step 1 and produce a structured Korean review report.
Apply the following **senior developer review checklist** to each changed file:

#### Architecture
- Module dependency direction (no circular imports)
- Single Responsibility Principle — one module/class = one job
- Layer separation — MCP tools vs modules vs scripts vs docs
- modules/ reuse — is there duplicate code that should be a module?

#### Code Quality
- Type hints on all public functions (return type + parameter types)
- Error handling — no bare `except:`, meaningful error messages
- No magic numbers — use named constants
- Function length < 50 lines, file length < 500 lines
- DRY — no copy-paste code blocks

#### Security
- No hardcoded secrets (API keys, tokens, passwords)
- No path traversal vulnerabilities (user input in file paths)
- No SQL injection (parameterized queries only)
- Input validation at system boundaries

#### Performance
- No N+1 queries (batch DB operations)
- Async/await correctness (no blocking calls in async)
- File I/O — streaming for large files, proper close/context managers

#### Convention (VP-Studio Rules)
- Code comments in Korean (development.md rule)
- Docstrings in English
- Print/log messages in English
- Frontmatter `description` field in English
- PascalCase class names, snake_case functions
- UE asset naming conventions (asset-naming.md)

#### Documentation
- Changed code has corresponding doc updates
- module.md exists for all modules/
- Frontmatter is valid (description, tags, category)

#### Testing
- Changed modules have test coverage
- Tests pass: `${hub_cli_python} -m pytest tests/ -v`

#### Git Hygiene
- Commit messages are descriptive
- No large binaries tracked
- .gitignore coverage

### Step 3: Output Report

Format the report in Korean with this structure:

```markdown
## 코드 리뷰 리포트

**기간**: {since} ~ {now}
**커밋**: {count}개
**변경 파일**: {count}개 (+{added} -{removed})

### Critical Issues
(심각한 보안/아키텍처 문제 — 즉시 수정 필요)

### Warnings
(품질/컨벤션 위반 — 다음 작업 시 수정 권장)

### Suggestions
(개선 제안 — 시간 있을 때 반영)

### Summary
(전체 코드 건강 상태 한 줄 평가)
```

When many changes exist, add Korean comments to explain major review points for team readability.

### Step 4: Run Tests

Verify all tests pass:
```bash
${hub_cli_python} -m pytest tests/ -v
```

Report the result at the end of the review.

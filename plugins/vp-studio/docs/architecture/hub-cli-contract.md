# Hub CLI Contract

Plugin skill 이 Project 가 보유한 CLI 를 호출할 때의 규약.

## 동기

Plugin 은 재사용 가능 레이어. 특정 Project 의 CLI 구현을 내포하면 다른 Project 에서 깨진다. 따라서 skill 은 **CLI 경로를 userConfig 로 주입받아** shell out 한다.

## userConfig 필드

| 필드 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `hub_cli.doc_manager` | string | `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/doc_manager/cli.py` | FTS5 문서 검색·ingest·stats |
| `hub_cli.doc_verifier` | string | `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/doc_verifier/cli.py` | 문서 주장 검증 |
| `hub_cli.reviewer` | string | `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/reviewer/cli.py` | VP 컨벤션 기반 코드 리뷰 |
| `hub_cli.confluence_migrator` | string | `${CLAUDE_PROJECT_DIR}/vp/scripts/utils/confluence_migrator/cli.py` | Confluence → MD 마이그레이션 |
| `hub_cli.python` | string | `python` | Python 실행파일 (venv override 용) |

## 호출 규약

모든 Hub CLI 는 다음을 보장해야 한다 (Project 책임):

1. **표준 서브커맨드**: `search`, `ingest`, `stats`, `new`, `classify`, `verify`, `review` 등. 각 skill 이 의존하는 서브커맨드는 skill `SKILL.md` 상단에 명시.
2. **표준 인자**:
   - `--domain <enum>` — 도메인 필터
   - `--json` — 기계 판독용 출력
   - `--quiet` — 로그 억제
3. **Exit code**: 0 = 성공, ≠0 = 실패. 실패 시 skill 은 사용자에게 원인 보고 후 중단.
4. **작업 디렉토리 무관**: CLI 는 내부적으로 Hub 경로(`docs_root` 등 Project `.env` 또는 CLI 인자 경유)를 알아서 해결.

## Skill 쪽 호출 패턴

```bash
# Plugin skill 내부에서
${hub_cli.python} ${hub_cli.doc_manager} search --query "${query}" --json
```

userConfig 변수가 해석되지 않는 컨텍스트면 skill 은 **명시적 instruction** 으로 표현:

> "Call `{userConfig.hub_cli.doc_manager}` with subcommand `search --query "$Q"`. If unset, abort and ask user to configure `hub_cli.doc_manager`."

## 미설정 시 동작

- userConfig 필드가 비어있음 → skill 은 사용자에게 **configuration 오류** 리포트. 임의 기본값으로 실행하지 않는다.
- 예외: `hub_cli.python` 은 `python` 기본값으로 진행.

## Skill ↔ CLI 의존 매트릭스

| Skill | 의존 CLI | 서브커맨드 |
|---|---|---|
| search-docs | `hub_cli.doc_manager` | `search` |
| doc-stats | `hub_cli.doc_manager` | `stats` |
| new-doc | `hub_cli.doc_manager` | `new` |
| verify-docs | `hub_cli.doc_verifier` | `classify`, `verify` |
| vp-review | `hub_cli.reviewer` | `review` |
| compile-wiki* | `hub_cli.doc_manager` | `ingest` (Project 잔존 skill — 참고용) |

*compile-wiki 는 Project layer 유지. Plugin 에 포함되지 않음.

## MCP 서버 대응

현재 `doc-manager` MCP 서버는 Project 소유(`vp/scripts/utils/doc_manager/mcp/`). Plugin 은 MCP 서버를 **번들하지 않는다**. MCP 기반 검색이 필요한 agent 는 Project 의 `.mcp.json` 에 등록된 서버에 의존.

## 버저닝

Hub CLI 의 서브커맨드·인자가 변경되면 **Project 책임으로 호환성 유지**. Plugin skill 은 현 contract (1항의 표준 서브커맨드) 가정. Breaking change 필요 시 Plugin 과 Project 양측 이슈 트래킹.

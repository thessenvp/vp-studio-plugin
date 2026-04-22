# Knowledge Base Rule

VP 도메인 **리서치 허브** 운영 원칙. Andrej Karpathy 의 [LLM Knowledge Bases 워크플로](https://x.com/karpathy/status/2039805659525644595) 를 구현. 사람은 raw 자료만 넣고, LLM 이 wiki 를 컴파일·유지보수한다.

---

## 핵심 원칙 (절대 어기지 말 것)

1. **사람은 `${inbox_root}` 만 채운다.** LLM 이 `${wiki_root}` 마크다운 위키를 컴파일·유지보수한다.
2. **`${wiki_root}` 는 LLM 전용 영역.** 사람이 직접 편집하지 않음 (예외: 명백한 사실 오류 수정).
3. **모든 wiki 페이지는 마크다운 + 백링크 포함.** Obsidian 호환 포맷.
4. **VP 자산 참조 순서 엄수**: 답변·컴파일 작업 시 `${wiki_root}` → `${inbox_root}` → `${docs_root}` → Project 의 modules 디렉토리 → doc_manager DB → 외부 검색 순.
5. **userConfig 변수 사용.** Plugin 은 Hub 경로를 하드코딩하지 않음 — 항상 `${wiki_root}`·`${inbox_root}`·`${docs_root}` 등 userConfig 주입값 사용.

---

## 디렉토리 역할

| 경로 (userConfig) | 누가 채우는가 | 내용 |
|---|---|---|
| `${inbox_root}/raw/papers/` | 사람 | 논문 PDF, arXiv 링크/메타 |
| `${inbox_root}/raw/articles/` | 사람 | 블로그·뉴스 마크다운 (Obsidian Web Clipper 산출물) |
| `${inbox_root}/raw/repos/` | 사람 | 코드 저장소 클론 또는 URL + 요약 메모 |
| `${inbox_root}/raw/media/` | 사람 | 이미지, 다이어그램, 스크린샷 |
| `${wiki_root}/index.md` | **LLM** | 마스터 인덱스 (전체 백링크 트리) |
| `${wiki_root}/concepts/` | **LLM** | 개념 단위 노트 (예: `gaussian_splatting.md`, `optical_flow.md`) |
| `${wiki_root}/articles/` | **LLM** | 자료별 요약 페이지 (raw 자료 1개당 1개) |

---

## 자료 참조 순서 (VP/필름 관련 질문·컴파일 작업 시)

1. **`${wiki_root}`** 에 이미 정리된 노트가 있는가? → 있으면 그것 사용
2. **`${inbox_root}`** 에 미컴파일 자료가 있는가? → 있으면 함께 분석
3. **`${docs_root}/{domain}/`** — 세션 기록, 트러블슈팅, 기술문서
4. Project 의 modules 디렉토리 — 검증된 코드 모듈 (경로는 Project 가 별도 변수로 제공; `modules.md` 참조)
5. **doc_manager DB 검색**:
   ```bash
   ${hub_cli_python} ${hub_cli_doc_manager} search "키워드" --project vp
   ```
6. 위 모두에 없으면 외부 검색 (WebSearch / WebFetch)

---

## 데이터베이스 (doc_manager)

`${doc_manager_db_path}` (SQLite) 를 공유한다. `--project` 플래그로 스코프 분리. CLI 실행 경로는 `${hub_cli_doc_manager}`.

| 작업 | 명령 |
|---|---|
| wiki 파일을 DB에 등록 | `${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${wiki_root}/concepts/X.md" --project vp` |
| wiki/rule 문서 검색 | `${hub_cli_python} ${hub_cli_doc_manager} search "키워드" --project vp` |
| 문서 목록 | `${hub_cli_python} ${hub_cli_doc_manager} list --project vp` |

`--project vp` 은 첫 ingest 시 자동으로 DB 의 `projects` 테이블에 등록됨.

---

## 마크다운 스타일 가이드 (wiki 작성용)

### 모든 wiki 파일의 frontmatter

```yaml
---
description: (한 줄 요약)
tags:
  - (관련 태그)
category: (concept | article | index)
source: (원본 ${inbox_root} 파일 경로 또는 URL)
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**날짜 값 제약**: `created`, `updated` 는 **반드시 따옴표 없는 순수 `YYYY-MM-DD` 문자열**. doc_manager ingester 는 YAML 파싱된 `datetime.date` 객체는 처리하지만 불필요한 문자열 변환을 피하려면 ISO-8601 형식을 그대로 쓸 것.

### 백링크 표기

- Obsidian 호환 위키 링크 사용: `[[concept_name]]`
- 동시에 클릭 가능한 마크다운 링크도 병기: `[[gaussian_splatting]] ([concepts/gaussian_splatting.md](concepts/gaussian_splatting.md))` — Obsidian 과 일반 마크다운 뷰어 양쪽에서 작동
- 모든 노트 하단에 **`## Backlinks`** 섹션을 두되, **다른 노트가 명시적으로 이 노트를 참조한 경우에만** 항목 추가
- 자기 자신의 forward 참조(본문 "관련 개념" 등)를 자신의 Backlinks 에 자동 미러링하지 않음 — 오직 외부 노트에서 들어오는 명시적 참조만 기록

### 코드 주석은 한국어

[development.md](development.md) 규칙과 동일하게, 위키 본문 설명은 한국어, 기술 용어는 영어 그대로.

---

## 절대로 하지 말 것

- ❌ `${inbox_root}/raw/` 의 원본 파일을 LLM 이 수정 (raw 는 read-only)
- ❌ userConfig `hub_read_only_paths` 에 나열된 경로 수정 (유저 소유 영역, archive 등)
- ❌ `${wiki_root}` 파일을 사람이 손으로 편집한 것처럼 위장
- ❌ 한 파일에 여러 개념 섞기 (개념 1개 = 노트 1개 원칙)
- ❌ Hub 경로 하드코딩 — 항상 userConfig 변수 사용

---

## 참고 자산

- 컴파일 워크플로: `/compile-wiki` 스킬 (현재 Project 에 유지 — Hub 파이프라인 특성상 Project 가 소유)
- doc_manager CLI: userConfig `${hub_cli_doc_manager}`
- 영감의 원천: [Karpathy LLM Knowledge Bases 트윗](https://x.com/karpathy/status/2039805659525644595)

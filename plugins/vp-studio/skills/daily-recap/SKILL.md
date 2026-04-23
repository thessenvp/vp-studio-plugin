---
name: daily-recap
description: Generate daily standup recap from Git commits, session records, and changed files.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[YYYY-MM-DD (기본: 오늘)]"
---

# Daily Recap — 데일리 회의용 회고록

대상 날짜: $ARGUMENTS (인자가 없으면 오늘 날짜 사용)

## 1. 데이터 수집

아래 3개 소스에서 해당 날짜의 작업 내역을 수집한다.

### 1.1 Git 커밋 로그

```bash
git log --since="{DATE} 00:00" --until="{DATE} 23:59" --oneline --all --no-merges
```

커밋이 없으면 "(커밋 없음)" 으로 기록.

### 1.2 Git diff stat (당일 변경 파일)

```bash
git log --since="{DATE} 00:00" --until="{DATE} 23:59" --all --no-merges --diff-filter=ACMR --name-status
```

### 1.3 세션 기록 검색

해당 날짜의 세션 기록 파일이 있는지 확인:

```bash
# 주의: Git 커밋 날짜와 세션 파일 날짜가 다를 수 있음 — 파일명 날짜 우선 사용.
find ${docs_root}/ -path "*/sessions/{DATE}*" -name "*.md" 2>/dev/null
```

**해당 날짜로 된 세션 파일은 모두 포함한다.** 커밋 일자·커밋 여부·파일 크기로 필터링하지 말 것. 파일명의 날짜가 {DATE} 와 일치하면 전부 읽어서 요약에 반영. 같은 날 여러 주제로 세션이 분리되어 있는 것이 정상이며, 회고록은 그 전체를 합쳐야 당일 작업 전경이 된다.

## 1.4 VP Supervisor 세션 파일 검색 (있는 경우)

```bash
find ${sessions_root} -name "{DATE}*" 2>/dev/null
find ${briefings_root} -name "{DATE}*" 2>/dev/null
find ${mocap_sessions_root} -name "{DATE}*" 2>/dev/null
```

촬영 관련 파일(brief, takes, opt-review 등)이 있으면 "촬영 현황" 섹션에 반영.

## 2. 회고록 작성

**경로:** `${daily_root}/{DATE}.md`

**형식:**

```markdown
---
description: {DATE} 데일리 회고록
tags:
  - daily-recap
category: daily-recap
---

# Daily Recap — {DATE} ({요일})

> **🔑 {오늘의 키포인트 한 줄}**

## 오늘 한 일
- (핵심 작업 항목, 3~7개 bullet point)
- (구체적으로: 무엇을 만들었는지, 무엇을 고쳤는지, 무엇을 결정했는지)

## 주요 변경 사항
- (변경된 파일/모듈 요약 — 개별 파일 나열이 아닌 의미 단위로 그룹핑)

## 이슈 & 해결
- (발생한 문제와 해결 방법, 없으면 섹션 생략)

## 촬영 현황 (VP Supervisor, 해당일에 촬영이 있었던 경우만)
- **완료 씬:** (씬명/컷번호) — OK {N}컷 / 전체 {N}컷
- **Opt 검수:** (씬명) → PASS/WARN/FAIL
- **내일 예정:** (다음 씬 — brief-scene 파일에서 추출)
- **부서별 현황:**
  - Art: (진행률 또는 블로커)
  - Previz: (진행률 또는 블로커)
  - MoCap: (진행률 또는 블로커)

## 내일 할 일
- (다음 작업 항목, 세션 기록의 TODO에서 추출)

## 회의 메모
- (빈 칸 — 회의 중 수기로 추가)
```

**촬영 현황 섹션 작성 규칙:**
- 오늘 `${sessions_root}/`에 `_takes.md` 또는 `_brief.md` 파일이 있을 때만 포함
- 없으면 섹션 전체 생략 (회의용이므로 간결하게)

## 3. 작성 규칙

- **회의용이므로 간결하게** — 각 항목 1줄, 전체 30줄 이내
- 기술 용어는 팀원이 알아듣는 수준으로 (클래스명 OK, 코드 블록 NO)
- 커밋 메시지를 그대로 복사하지 말 것 — 의미 단위로 재구성
- 같은 주제의 커밋은 하나로 합쳐서 기술
- **요일을 반드시 표시** (월/화/수/목/금/토/일) — 템플릿의 `{요일}` 플레이스홀더 채우기 필수
- **키포인트 한 줄 필수** — 제목 바로 아래에 당일 작업 중 가장 임팩트가 큰 성과를 한 문장으로 요약 (blockquote + 🔑 이모지)
- 불필요한 섹션은 생략 (이슈가 없으면 "이슈 & 해결" 섹션 제거)

## 4. DB Ingest

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "<file>" --project vp
```

(앞 Step 의 파일/산출물은 이미 저장됐으므로 skill 은 정상 완료로 간주.)

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${daily_root}/{DATE}.md" --project vp
```

## 5. 완료 메시지

```
📋 데일리 회고록 생성 완료: ${daily_root}/{DATE}.md

요약:
  - 커밋: {N}건
  - 변경 파일: {N}개
  - 세션 기록 참조: {N}건

내일 데일리 회의에서 사용하세요!
```

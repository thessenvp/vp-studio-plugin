---
name: supervisor-recap
description: VP Supervisor — 감독 관점 일일 회고. 의사결정 로그 + 부서별 퍼포먼스 + 내일 선제 준비. daily-recap 확장판으로 촬영 감독 전용 섹션 포함.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[YYYY-MM-DD (기본: 오늘)]"
---

# Supervisor Recap — 감독 일일 회고

단순 작업 나열이 아닌 **의사결정 로그 + 팀 퍼포먼스 + 내일 선제 준비**.  
`/daily-recap` 의 VP Supervisor 확장판. KPI 리포트 + 모든 씬 완료 후 실행.

## Arguments

- `[YYYY-MM-DD]` : 날짜 (기본: 오늘)

## Procedure

### Step 1: 당일 데이터 수집

```bash
# Git 커밋 로그
git log --since="{DATE} 00:00" --until="{DATE} 23:59" --oneline --no-merges

# 당일 VP Supervisor 관련 세션 파일 전체
find ${sessions_root} -name "{DATE}*" 2>/dev/null
find ${briefings_root} -name "{DATE}*" 2>/dev/null
find ${mocap_sessions_root} -name "{DATE}*" 2>/dev/null
find ${daily_root} -name "{DATE}*" 2>/dev/null

# risk-flag 파일 명시적 탐색
find ${sessions_root} -name "*{DATE}*risk-flag*" 2>/dev/null
```

수집 대상:
- `*_shoot-gate.md` — GO/NO-GO 판정 기록
- `*_takes.md` — 테이크 로그
- `*_kpi.md` — KPI 측정
- `*_opt-review.md` — 최적화 검수
- `*_brief.md` — 씬 브리핑
- `*_risk-*.md` — 리스크 플래그 기록
- 기존 `${daily_root}/{DATE}.md` — daily-recap 생성 여부 확인

### Step 2: 감독 결정 로그 파싱

shoot-gate 파일에서 GO/NO-GO 기록 추출 (정규식 패턴 사용 — 한글/영문 혼합 대응):

```bash
grep -hE "최종 판정|CONDITIONAL|NO-GO|GO" ${sessions_root}/{DATE}*shoot-gate*.md 2>/dev/null
grep -hE "오버라이드|블로커|override|blocker" ${sessions_root}/{DATE}*shoot-gate*.md 2>/dev/null
```

RISK FLAG 파일 탐색:

```bash
grep -rhE "RISK FLAG|P1 블로커|P1 blocker" ${sessions_root}/{DATE}*.md 2>/dev/null
```

### Step 3: 부서별 퍼포먼스 데이터

takes.md 에서 부서별 NG 집계:

```bash
grep -h "| NG |" ${sessions_root}/{DATE}*takes*.md 2>/dev/null
```

opt-review 에서 Art Team 퍼포먼스 지표:

```bash
grep -h "판정\|FPS\|GPU\|Nanite\|LOD" ${sessions_root}/{DATE}*opt-review*.md 2>/dev/null
```

### Step 4: 내일 브리핑 초안 인자 추출

내일 씬 정보 파악 (resource-plan 또는 brief-scene 파일에서):

```bash
find ${docs_root}/pipeline -name "*resource*" -newer ${sessions_root}/{DATE}* 2>/dev/null | head -3
```

내일 `/brief-scene` 호출에 필요한 인자 자동 추출 (씬명, 배우 수 등).

> 내일 시나리오 파일 없으면: "⚠️ 내일 촬영 시나리오 미정 — project.yaml shoot_schedule 확인 필요" 안내.

### Step 5: 리포트 파일 생성

→ gemma4 위임 가능: Step 7 (내일 권고 텍스트 서술). 수치·판정은 Claude 직접.

**경로:** `${sessions_root}/{DATE}_supervisor-recap.md`

```markdown
---
description: {DATE} VP Supervisor 일일 회고
tags:
  - supervisor-recap
  - daily-recap
category: session-records
---

# VP Supervisor Recap — {DATE} ({요일})

> **🎬 {오늘의 한 줄 평가 — VP Supervisor 관점}**

---

## 감독 결정 로그

오늘 VP Supervisor가 내린 GO/NO-GO 및 주요 기술 결정:

| 시각 | 씬 | 결정 | 사유 |
|---|---|---|---|
| {TIME} | {scene} | **GO** | 전 게이트 PASS |
| {TIME} | {scene} | **CONDITIONAL-GO** | opt-review WARN — FPS 마진 8%, 허용 판단 |
| {TIME} | {scene} | **NO-GO** | Genlock FAIL — 재촬영 일정 조정 |

**오버라이드 결정:** {있으면 사유 포함, 없으면 "없음"}

---

## 3대 KPI 종합

| KPI | 씬1 | 씬2 | 당일 평균 |
|---|---|---|---|
| Frame Rate | {A/R/F} | {A/R/F} | {결과} |
| Visual Consistency | {A/R/F} | {A/R/F} | {결과} |
| Efficiency | {A/R/F} | {A/R/F} | {결과} |

**OK 테이크 합계:** {N}컷 / 전체 {N}컷 ({N}%)  
**총 기술 다운타임:** {N}분 (허용 기준: 72분/8h)

---

## 부서별 퍼포먼스

계획 대비 실제 퍼포먼스를 팀별로 평가:

### Art Team
- **계획:** {resource-plan에서 추출한 목표}
- **실제:** {opt-review PASS/WARN, NG 기여 건수}
- **블로커:** {있으면 기록}
- **평가:** {GOOD / ON-TRACK / NEEDS-ATTENTION}

### Previz Team
- **계획:** {목표}
- **실제:** {VCam/라이팅 이슈 여부}
- **블로커:** {있으면 기록}
- **평가:** {GOOD / ON-TRACK / NEEDS-ATTENTION}

### MoCap Team
- **계획:** {배우 수, 캘리브레이션 목표}
- **실제:** {mocap NG 건수, 트래킹 이슈}
- **블로커:** {있으면 기록}
- **평가:** {GOOD / ON-TRACK / NEEDS-ATTENTION}

### Engineering
- **계획:** {동기화 체인 목표}
- **실제:** {sync-check 결과, tech NG 건수}
- **블로커:** {있으면 기록}
- **평가:** {GOOD / ON-TRACK / NEEDS-ATTENTION}

---

## 리스크 이벤트

| 시각 | 유형 | 심각도 | 다운타임 | 해결 |
|---|---|---|---|---|
| {TIME} | {RiskType} | {P1/P2/P3} | {N}분 | {해결/미결} |

---

## 내일 선제 준비

### 내일 촬영 씬

| 씬 | 복잡도 | 주요 리스크 | 선제 조치 |
|---|---|---|---|
| {scene} | {등급} | {리스크} | {조치} |

### 내일 `/brief-scene` 호출 초안

```
/brief-scene {SceneName} --sequence {S##C##} --actors {N}
```

### 오늘 미해결 항목

- [ ] {미해결 블로커 또는 TODO}
- [ ] HOLD 테이크 포스트팀 판정 회신 대기: {T###}

### 사전 점검 필요 항목

- [ ] {내일 씬 복잡도 기반 사전 검수 필요 항목}
- [ ] {장비 점검 필요 항목}

---

## 오늘의 교훈

{오늘 발생한 문제 중 다음번 재발 방지를 위한 인사이트 1~2개}

---

## 참조 파일

- KPI 리포트: `{*_kpi.md}`
- Shoot Gate: `{*_shoot-gate.md}`
- Take Log: `{*_takes.md}`
```

### Step 6: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "<file>" --project vp
```

(앞 Step 의 파일/산출물은 이미 저장됐으므로 skill 은 정상 완료로 간주.)

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{DATE}_supervisor-recap.md" \
  --project vp
```

### Step 7: 완료 출력

```
🎬 Supervisor Recap 생성 완료 — {DATE}

오늘의 결정:
  GO: {N}건 / CONDITIONAL-GO: {N}건 / NO-GO: {N}건

팀 퍼포먼스:
  Art: {평가} / Previz: {평가} / MoCap: {평가} / Engineering: {평가}

KPI 종합:
  Frame Rate: {결과} | Visual: {결과} | Efficiency: {결과}

파일: ${sessions_root}/{DATE}_supervisor-recap.md

내일 준비:
  → /brief-scene {내일씬} 실행 권장 ({아침 시간} 전까지)
```

## 주의사항

- `/kpi-report` 먼저 실행 권장 (KPI 데이터 없으면 수치 섹션 "데이터 부족"으로 기록)
- 부서별 "NEEDS-ATTENTION" 판정 시 해당 파트장에게 내일 아침 브리핑 시 안내
- 교훈 섹션 → `risk-scenario` 업데이트 또는 신규 생성으로 연결
- Gemma4 위임: "내일 선제 준비" 서술과 "오늘의 교훈" 서술만 (수치·판정은 Claude)
- 참조: vp-agent 의 `vp-supervisor.md` (KPI·감독 권한), `shoot-protocol.md` (퍼포먼스 기준) rule

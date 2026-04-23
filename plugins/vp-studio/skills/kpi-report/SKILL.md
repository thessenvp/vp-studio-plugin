---
name: kpi-report
description: VP Supervisor — 3대 KPI 측정 (Frame Rate / Visual Consistency / Efficiency). 씬/일 단위 성과 문서화. /data-wrangle + /take-log 데이터 기반.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[--scene S##C##] [YYYY-MM-DD] [--all-scenes]"
---

# KPI Report — VP Supervisor 3대 KPI 측정

**3대 KPI**: Frame Rate · Visual Consistency · Efficiency
씬 단위 또는 일 단위 성과를 측정하고 다음 씬 개선 권고사항을 도출.

## Arguments

- `--scene S##C##` : 특정 씬 KPI (기본)
- `[YYYY-MM-DD]` : 측정 날짜 (기본: 오늘)
- `--all-scenes` : 당일 전체 씬 집계

## Procedure

### Step 1: 소스 데이터 수집

```bash
# 해당 날짜/씬의 모든 세션 파일 — ${sessions_root} 는 userConfig
find ${sessions_root} -name "*{DATE}*{scene}*" 2>/dev/null
find ${sessions_root} -name "*{DATE}*takes*" 2>/dev/null
find ${sessions_root} -name "*{DATE}*opt-review*" 2>/dev/null
find ${sessions_root} -name "*{DATE}*color*" 2>/dev/null
find ${sessions_root} -name "*{DATE}*metadata*" 2>/dev/null
```

**`--all-scenes` 모드:**
```bash
find ${sessions_root} -name "*{DATE}*" 2>/dev/null
```

### Step 2: KPI 1 — Frame Rate 측정

**소스:** `*_opt-review.md` (씬별 최적화 검수 결과)

```bash
grep -h "판정:" ${sessions_root}/*{DATE}*opt-review*.md 2>/dev/null
grep -h "FPS" ${sessions_root}/*{DATE}*opt-review*.md 2>/dev/null
```

측정 지표:
- opt-review 판정 (PASS/WARN/FAIL)
- 예상 FPS vs 목표 FPS (24fps)
- GPU 예상 부하 (A6000 기준)
- FPS 관련 NG 테이크 수 (takes.md `tech` NG 중 FPS 원인)

**FPS NG 추출:**
```bash
grep -h "tech" ${sessions_root}/*{DATE}*{scene}*takes*.md 2>/dev/null | grep -i "fps\|frame\|drop"
```

### Step 3: KPI 2 — Visual Consistency 측정

**소스:** `*_color-pipeline.md` (컬러 파이프라인 검수)

```bash
grep -h "판정:" ${sessions_root}/*{DATE}*color*.md 2>/dev/null
```

측정 지표:
- color-check 판정 (PASS/WARN/FAIL)
- LED ↔ 카메라 색온도 차이 (ΔT)
- 패널 균일도 (ΔE)
- LED 관련 NG 테이크 수 (takes.md `led` NG)
- HOLD 테이크 수 (포스트 판정 대기)

### Step 4: KPI 3 — Efficiency 측정

**소스:** `*_takes.md`, `*_metadata.json`

**테이크 집계:**
```bash
# OK/NG/HOLD 카운트
grep -c "| OK |" ${sessions_root}/*{DATE}*{scene}*takes*.md 2>/dev/null
grep -c "| NG |" ${sessions_root}/*{DATE}*{scene}*takes*.md 2>/dev/null
```

**다운타임 추정 (기술 원인):**
- `tech` NG 건수 × 평균 15분 (기본 추정)
- RISK FLAG 발생 횟수 및 유형 (있는 경우)
- 블로커 경고 섹션 탐색

```bash
grep -h "블로커" ${sessions_root}/*{DATE}*{scene}*takes*.md 2>/dev/null
grep -h "RISK FLAG" ${sessions_root}/*{DATE}*{scene}*takes*.md 2>/dev/null
```

**효율 지표:**
- 총 테이크 대비 OK 비율: `OK / 총테이크 × 100%`
- 기술 다운타임: `tech_NG × 15분` (추정)
- 촬영 총 시간: 유저 확인 또는 TC 범위에서 추산

### Step 5: KPI 리포트 파일 생성

→ gemma4 위임 가능 (서술 부분): 개선 권고사항 텍스트 — userConfig `ollama_enabled=true` 일 때만
→ 수치 계산은 Claude 직접

**경로:** `${sessions_root}/{DATE}_{scene}_kpi.md`

```markdown
---
description: {scene} KPI 리포트 — {DATE}
tags:
  - kpi-report
  - {scene}
category: session-records
---

# KPI 리포트 — {scene} ({DATE})

**측정일:** {DATE}
**씬:** {scene}
**VP Supervisor:** (이름)

---

## KPI 1: Frame Rate ⚡

| 항목 | 결과 | 기준 |
|---|---|---|
| Opt Review 판정 | {PASS/WARN/FAIL} | PASS |
| 예상 FPS | {N}fps | 24fps |
| GPU 부하 | {N}% | < 85% |
| FPS 관련 NG | {N}건 | 0건 |

**Frame Rate KPI: {ACHIEVED/AT-RISK/FAILED}**

---

## KPI 2: Visual Consistency 🎨

| 항목 | 결과 | 기준 |
|---|---|---|
| Color Check 판정 | {PASS/WARN/FAIL} | PASS |
| LED ↔ 카메라 색온도 차이 | ΔT={N}K | < 200K |
| 패널 균일도 | ΔE={N} | < 3 |
| LED 관련 NG | {N}건 | 0건 |
| HOLD 테이크 | {N}건 | — |

**Visual Consistency KPI: {ACHIEVED/AT-RISK/FAILED}**

---

## KPI 3: Efficiency ⏱️

| 항목 | 결과 | 기준 |
|---|---|---|
| 총 테이크 | {N} | — |
| OK 비율 | {N}% | > 60% |
| 기술 다운타임 (추정) | {N}분 | < 72분/8h |
| RISK FLAG 발생 | {N}건 | 0건 |

**다운타임 분류:**

| 원인 | 건수 | 추정 시간 |
|---|---|---|
| tech (FPS/sync) | {N} | {N}분 |
| art (에셋) | {N} | {N}분 |
| mocap | {N} | {N}분 |
| led | {N} | {N}분 |

**Efficiency KPI: {ACHIEVED/AT-RISK/FAILED}**

---

## 종합 판정

| KPI | 결과 |
|---|---|
| Frame Rate | {ACHIEVED/AT-RISK/FAILED} |
| Visual Consistency | {ACHIEVED/AT-RISK/FAILED} |
| Efficiency | {ACHIEVED/AT-RISK/FAILED} |

**씬 종합: {ALL GREEN / PARTIAL / NEEDS IMPROVEMENT}**

---

## 다음 씬 개선 권고사항 (최대 3개)

1. {가장 시급한 개선 항목 — 구체적 조치 포함}
2. {두 번째 개선 항목}
3. {세 번째 개선 항목}

---

## 참조 파일

- Take Log: `{*_takes.md}`
- Opt Review: `{*_opt-review.md}`
- Color Check: `{*_color-pipeline.md}`
- Metadata: `{*_metadata.md}`
```

#### `--all-scenes` 모드 추가 섹션

```markdown
## 일 단위 집계 ({DATE})

| 씬 | Frame Rate | Visual | Efficiency | 종합 |
|---|---|---|---|---|
| {scene1} | ACHIEVED | ACHIEVED | AT-RISK | PARTIAL |
| {scene2} | PASS | PASS | PASS | ALL GREEN |

**당일 OK 테이크 합계:** {N}컷
**당일 총 기술 다운타임:** {N}분
**내일 개선 우선 항목:** {1가지}
```

### Step 6: DB 인제스트

```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{DATE}_{scene}_kpi.md" \
  --project vp
```

### Step 7: 완료 출력

```
📊 KPI 리포트 완료 — {scene} ({DATE})

Frame Rate:        {ACHIEVED/AT-RISK/FAILED}
Visual Consistency:{ACHIEVED/AT-RISK/FAILED}
Efficiency:        {ACHIEVED/AT-RISK/FAILED}

주요 개선 권고:
  1. {항목}

파일: ${sessions_root}/{DATE}_{scene}_kpi.md

다음 단계:
→ /supervisor-recap   (감독 일일 회고)
→ /handoff-pack {scene}  (미완료 시)
```

## 주의사항

- 다운타임 추정(tech_NG × 15분)은 추정값 — 실제 시간 기록이 있으면 우선 사용
- Gemma4 위임: 개선 권고사항 서술만. 수치·판정은 Claude 직접
- `--all-scenes` 모드에서 metadata.json 없는 씬은 "데이터 부족"으로 표시
- 참조: vp-agent `vp-supervisor.md` (3대 KPI 정의), `shoot-protocol.md` (다운타임 기준)

---
name: data-wrangle
description: VP Supervisor — 씬 완료 후 촬영 메타데이터 구조화. take-log 기반 메타데이터를 JSON+MD로 정리. /handoff-pack 및 /kpi-report의 원천 데이터.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "--scene S##C## [--takes T001,T002,...] [--wrap]"
---

# Data Wrangle — 촬영 메타데이터 구조화

씬 완료 후 촬영 중 축적된 데이터를 구조화. 포스트팀 핸드오프의 전제 조건.
`/take-log wrap` 또는 감독 씬 완료 선언 후 즉시 실행.

## Arguments

- `--scene S##C##` : 씬/컷 식별자 (필수)
- `--takes T001,T002,...` : 특정 테이크만 포함 (기본: 전체)
- `--wrap` : Scene Wrap 집계 모드 — 전체 씬 통계 포함

## Procedure

### Step 1: 관련 파일 수집

```bash
# 해당 씬의 모든 관련 파일 탐색 — Hub 경로는 userConfig
find ${sessions_root} -name "*{scene}*" 2>/dev/null
find ${mocap_sessions_root} -name "*{scene}*" 2>/dev/null
find ${briefings_root} -name "*{scene}*" 2>/dev/null
```

수집 대상:
- `*{scene}*_takes.md` — 테이크 로그 (take-log 출력)
- `*{scene}*_opt-review.md` — 최적화 검수 결과
- `*{scene}*_color*.md` — 컬러 파이프라인 검수
- `*{scene}*_brief.md` — 씬 브리핑
- `*{scene}*_shoot-gate.md` — Shoot Gate 판정 기록
- 해당 씬 MoCap 세션 파일 (Motive 파일명 패턴 기반)

### Step 2: takes.md 파싱 — 테이크 집계

`*{scene}*_takes.md` 를 읽고:

```
OK 테이크: T### 목록
NG 테이크: T### 목록 (부서별 집계)
HOLD 테이크: T### 목록
총 테이크 수: N
```

NG 부서별 분류:
- tech: N건
- art: N건
- mocap: N건
- acting: N건
- led: N건

### Step 3: 타임코드 범위 파악

유저에게 확인 요청 (Tentacle Sync 기준):

```
타임코드 시작 (첫 OK 테이크): HH:MM:SS:FF
타임코드 종료 (마지막 OK 테이크): HH:MM:SS:FF
렌즈 정보 (초점거리, 조리개): ___mm / f___
```

정보가 없으면 "N/A" 로 기록.

### Step 4: UE 씬 스냅샷 파악

유저에게 확인 요청 또는 brief-scene 파일에서 추출:

- 사용 레벨 (Level 경로)
- 라이팅 프리셋 이름
- nDisplay 설정 (사용 여부 + NDC_ 파일명)
- Sequencer 사용 여부

### Step 5: OptiTrack 파일 목록

Motive 세션 파일명 패턴: `{Project}_S##_C##_{Character}_{###}.tak`
해당 씬의 .tak 파일 경로 목록 확인 (유저 확인 또는 Hub MoCap 세션 파일 참조):

```bash
find ${mocap_sessions_root} -name "*{scene}*" 2>/dev/null
```

### Step 6: 메타데이터 파일 생성

#### A. 마크다운 파일

**경로:** `${sessions_root}/{DATE}_{scene}_metadata.md`

```markdown
---
description: {scene} 촬영 메타데이터 — {DATE}
tags:
  - data-wrangle
  - metadata
  - {scene}
category: session-records
---

# 촬영 메타데이터 — {scene} ({DATE})

## 씬 정보

- **씬/컷:** {scene}
- **촬영일:** {DATE}
- **VP Supervisor:** (이름)

---

## 테이크 집계

| 판정 | 수량 | 테이크 번호 |
|---|---|---|
| OK | {N} | {T001, T003, ...} |
| NG | {N} | {T002, T004, ...} |
| HOLD | {N} | {...} |
| **합계** | **{N}** | |

### NG 원인 분류

| 부서 | 건수 |
|---|---|
| tech | {N} |
| art | {N} |
| mocap | {N} |
| acting | {N} |
| led | {N} |

---

## 타임코드 & 렌즈

- **TC 시작:** {HH:MM:SS:FF} (Tentacle Sync 기준)
- **TC 종료:** {HH:MM:SS:FF}
- **초점거리:** {N}mm
- **조리개:** f/{N}

---

## UE 씬 구성

- **사용 레벨:** {경로}
- **라이팅 프리셋:** {이름}
- **nDisplay 설정:** {NDC_파일명 또는 미사용}
- **Sequencer:** {사용/미사용}

---

## OptiTrack / MoCap

### .tak 파일 목록

| 파일명 | 캐릭터 | 테이크 |
|---|---|---|
| {Project}_S##_C##_{Char}_001.tak | {Character} | T001 |

---

## 카메라 트래킹 데이터

- **OptiTrack 카메라 데이터 경로:** {경로 또는 N/A}
- **컬러 레퍼런스 파일:** {Motive세션명}_colorref_001 (X-Rite ColorChecker)

---

## HOLD 테이크 처리

| 테이크 | 메모 | 포스트 판정 |
|---|---|---|
| {T###} | {note} | 미결 |

---

## 참조 파일

- 씬 브리핑: {*_brief.md 경로}
- Opt 검수: {*_opt-review.md 경로}
- Shoot Gate: {*_shoot-gate.md 경로}
- Take Log: {*_takes.md 경로}

---

## 포스트팀 전달 패키지 요약

→ `/handoff-pack {scene}` 실행으로 전달 패키지 생성
```

#### B. JSON 파일

**경로:** `${sessions_root}/{DATE}_{scene}_metadata.json`

```json
{
  "scene": "{scene}",
  "date": "{DATE}",
  "takes": {
    "ok": ["{T###}", ...],
    "ng": ["{T###}", ...],
    "hold": ["{T###}", ...]
  },
  "ng_by_dept": {
    "tech": N,
    "art": N,
    "mocap": N,
    "acting": N,
    "led": N
  },
  "timecode": {
    "start": "{HH:MM:SS:FF}",
    "end": "{HH:MM:SS:FF}",
    "source": "Tentacle Sync E"
  },
  "lens": {
    "focal_length_mm": N,
    "aperture": "f/N"
  },
  "ue_scene": {
    "level": "{경로}",
    "lighting_preset": "{이름}",
    "ndisplay_config": "{파일명 또는 null}",
    "sequencer": true
  },
  "mocap_files": [
    "{Project}_S##_C##_{Char}_001.tak"
  ],
  "hold_takes": [
    {"take": "{T###}", "note": "{메모}"}
  ]
}
```

### Step 7: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "${sessions_root}/{DATE}_{scene}_metadata.md" --project vp
```

메타데이터 MD+JSON(Step 6)은 이미 저장됐으므로 skill 은 정상 완료.

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{DATE}_{scene}_metadata.md" \
  --project vp
```

### Step 8: 완료 출력

```
📦 Data Wrangle 완료 — {scene}
   OK: {N}컷 / NG: {N}컷 / HOLD: {N}컷
   총 테이크: {N}
   기술 다운타임 추정: {tech NG 수 × 평균 NG 소요 시간}분

   생성 파일:
   - ${sessions_root}/{DATE}_{scene}_metadata.md
   - ${sessions_root}/{DATE}_{scene}_metadata.json

   다음 단계:
   → /handoff-pack {scene}     (포스트팀 전달 패키지)
   → /kpi-report --scene {scene}  (KPI 측정)
```

## 주의사항

- JSON은 포스트팀 파이프라인 자동화용 — 형식 엄수
- HOLD 테이크는 handoff-pack에 반드시 포함 (포스트팀이 최종 판정)
- TC 정보가 없으면 N/A 기록 (추측 금지)
- 참조: vp-agent `shoot-protocol.md` (씬 완료 기준), `optitrack.md` (파일명 패턴)

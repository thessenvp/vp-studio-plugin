---
name: resource-plan
description: VP Supervisor — 씬 난이도 × 아티스트 숙련도 기반 업무 배분 계획. 번아웃 리스크 및 일정 리스크 사전 감지. Pre-production 단계 사용.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<SceneName> [--deadline YYYY-MM-DD] [--sequence S##C##]"
---

# Resource Plan — 씬 리소스 계획

씬 난이도를 분석해 부서별 업무를 배분하고 일정 리스크를 사전 감지.  
Pre-production 단계 `/risk-scenario` 이후, `/brief-scene` 이전 실행 권장.

## Arguments

- `<SceneName>` : 씬 이름 (예: `FilmA_영웅추격씬`)
- `--deadline YYYY-MM-DD` : 촬영 목표일
- `--sequence S##C##` : 씬/컷 번호 (선택)

## Procedure

### Step 1: 기존 브리핑/씬 데이터 수집

해당 씬의 기존 계획 파일 탐색:

```bash
find ${docs_root}/pipeline -name "*{SceneName}*" 2>/dev/null
find ${docs_root}/pipeline -name "*{sequence}*" 2>/dev/null
```

`brief-scene` 파일이 있으면 참조해 씬 정보 추출.

### Step 2: 씬 복잡도 점수 산정

유저에게 다음 항목을 확인 요청:

| 항목 | 수치 | 복잡도 가중치 |
|---|---|---|
| 촬영 배우 수 | N명 | × 2점/명 (MoCap 수트 필요 배우 포함) |
| 씬 내 에셋 수 (예: 차량·건물 등) | N개 | × 1점/개 |
| 특수 FX (Niagara, 파티클) | Y/N | Y = +3점 |
| 복잡한 LED 배경 (동적 배경) | Y/N | Y = +3점 |
| 카메라 이동 복잡도 (VCam) | 고정/단순/복잡 | 0/1/3점 |
| nDisplay 사용 여부 | Y/N | Y = +2점 |
| 리타겟팅 신규 캐릭터 | N개 | × 3점/개 |

**복잡도 총점:** {합산}

| 총점 | 등급 |
|---|---|
| 0~5 | LOW — 간단한 씬 |
| 6~12 | MEDIUM — 표준 씬 |
| 13~20 | HIGH — 복잡한 씬 |
| 21+ | CRITICAL — 특별 검토 필요 |

### Step 3: 부서별 예상 작업 시간 산정

복잡도 등급 기반 기본값 (시간 단위, 유저 조정 가능):

| 파트 | LOW | MEDIUM | HIGH | CRITICAL |
|---|---|---|---|---|
| Art Team | 4h | 8h | 16h | 24h+ |
| Previz Team | 2h | 4h | 8h | 12h+ |
| MoCap Team | 2h | 4h | 6h | 8h+ |
| Engineering | 1h | 2h | 4h | 6h+ |

Gemma4 위임 가능 (텍스트 서술 부분): 각 파트의 구체적 작업 내용 작성.

### Step 4: 일정 리스크 평가

`--deadline` 인자가 있으면:

```
현재 날짜: {TODAY}
촬영 목표일: {deadline}
남은 기간: {N}일 (영업일 기준)

예상 총 준비 작업량:
- Art: {N}h
- Previz: {N}h
- MoCap: {N}h
- Engineering: {N}h
```

**리스크 판정:**
- 여유 있음 (남은 기간 × 8h × 병렬 인원 ≥ 최대 파트 작업량 × 1.5): ✅ GREEN
- 빡빡함 (마진 < 20%): ⚠️ YELLOW — 병렬 작업 필요
- 위험 (예상 작업량 > 남은 시간): 🔴 RED — 씬 단순화 또는 일정 조정 필요

> 주석: `남은 기간 × 8h` 는 단일 아티스트 기준. 실제 병렬 작업 능력 (예: 3명 아티스트 = 3 × 8h) 을 곱한 총 가용시간 기준으로 판단.

### Step 5: 역할별 우선순위 배정

P1/P2/P3 분류:

- **P1 (촬영 필수)**: 없으면 NO-GO — 핵심 에셋, MoCap 캘리브레이션, Genlock 세팅
- **P2 (씬 품질)**: 없으면 WARN — LOD 최적화, 텍스처 스트리밍, 컬러 체크
- **P3 (개선)**: 있으면 좋지만 없어도 GO — 소품 디테일, 보조 FX

### Step 6: 출력 파일 생성

→ gemma4 로 텍스트 서술 위임 (수치 판단은 Claude 직접)

**경로:** `${sessions_root}/{DATE}_{SceneName}_resource.md`

```markdown
---
description: {SceneName} 리소스 계획 — {DATE}
tags:
  - resource-plan
  - {SceneName}
category: session-records
---

# 리소스 계획 — {SceneName}

**작성일:** {DATE}  
**촬영 목표일:** {deadline}  
**VP Supervisor:** (이름)

---

## 씬 복잡도

| 항목 | 수치 | 점수 |
|---|---|---|
| 배우 수 | {N}명 | {N}점 |
| 에셋 수 | {N}개 | {N}점 |
| 특수 FX | {Y/N} | {N}점 |
| LED 배경 | {Y/N} | {N}점 |
| VCam 복잡도 | {등급} | {N}점 |
| nDisplay | {Y/N} | {N}점 |
| 신규 리타겟팅 | {N}개 | {N}점 |
| **총점** | | **{총점}** |

**복잡도 등급: {LOW/MEDIUM/HIGH/CRITICAL}**

---

## 파트별 업무 계획

### Art Team ({N}h 예상)

**P1 (촬영 필수):**
- [ ] (항목)

**P2 (씬 품질):**
- [ ] (항목)

**P3 (개선):**
- [ ] (항목)

### Previz Team ({N}h 예상)

**P1:**
- [ ] (항목)

**P2:**
- [ ] (항목)

### MoCap Team ({N}h 예상)

**P1:**
- [ ] 배우 {N}명 슈트 배정 및 캘리브레이션
- [ ] Motive 세션 파일명 확인

**P2:**
- [ ] (항목)

### Engineering ({N}h 예상)

**P1:**
- [ ] Genlock/TC 체인 확인
- [ ] (항목)

---

## 일정 리스크

- **남은 준비 기간:** {N}일 ({N}영업일)
- **예상 총 작업량:** Art {N}h / Previz {N}h / MoCap {N}h / Engineering {N}h
- **일정 판정:** {GREEN/YELLOW/RED}
- **리스크 사유:** (있을 경우)
- **권장 조치:** (있을 경우)

---

## 번아웃 리스크

복잡도 HIGH 이상 씬 연속 배정 시 아티스트 번아웃 리스크 경고:

- **MEDIUM 리스크**: 복잡도 HIGH 3일 연속 같은 아티스트에게 배정되면 번아웃 리스크 MEDIUM — 다음 씬부터 파트장 협의 권장.
- **HIGH 리스크**: 복잡도 HIGH 5일 연속 또는 주말 포함 연속 배정 → 번아웃 리스크 HIGH (즉시 배분 조정). 대체 아티스트 확보 또는 씬 단순화 협의 필수.
- 특정 파트에 작업 집중 없는지 확인
- 파트장에게 우선순위 재확인 권장

---

## 다음 단계

- `/risk-scenario` — 장비 장애 플레이북 설계
- `/brief-scene {SceneName}` — 씬 마스터 브리핑 생성
```

### Step 7: DB 인제스트

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
  --file "${sessions_root}/{DATE}_{SceneName}_resource.md" \
  --project vp
```

### Step 8: 완료 출력

```
📊 리소스 계획 완료 — {SceneName}
   복잡도: {등급} ({N}점)
   일정 리스크: {판정}
   
   파일: ${sessions_root}/{DATE}_{SceneName}_resource.md
   
   권장 다음 스킬:
   → /risk-scenario (장비 플레이북)
   → /brief-scene {SceneName} (씬 브리핑)
```

## 주의사항

- 수치(시간 추정, 복잡도 점수)는 Claude 직접 — Gemma 위임 금지
- 텍스트 서술 부분만 Gemma4 위임 가능 (루트 CLAUDE.md 위임 정책 참조)
- 리드 타임 RED 시 VP Supervisor가 씬 단순화 옵션을 감독과 협의
- 참조: vp-agent 의 `vp-session.md` (파이프라인 단계), `vp-supervisor.md` (감독 권한) rule

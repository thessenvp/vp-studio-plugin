---
name: take-log
description: VP Supervisor — 실시간 테이크 판정 기록. OK/NG/HOLD 로그 누적, 5연속 NG 자동 블로커 경고.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<T###> <OK|NG|HOLD> [--note \"\"] [--dept tech|art|mocap|acting|led]"
---

# Take Log — 실시간 테이크 기록

현장 실시간 테이크 판정을 누적 기록. `/shoot-gate` GO 후 활성화.
`/kpi-report`와 `/data-wrangle`의 원천 데이터.

## Arguments

- `<T###>` : 테이크 번호 (예: `T001`, `T023`)
- `<OK|NG|HOLD>` : 판정 코드
- `--note "..."` : 판정 메모 (선택)
- `--dept tech|art|mocap|acting|led` : NG 부서 분류 (NG 시 권장)
- `--scene S##C##` : 씬/컷 (첫 호출 시 설정, 이후 유지)

## 판정 코드 참조

→ vp-agent 의 `shoot-protocol.md` 테이크 판정 기준 참조

| 코드 | 의미 |
|---|---|
| `OK` | 사용 가능한 테이크 |
| `NG` | 사용 불가 (--dept 로 원인 분류 권장) |
| `HOLD` | 보류 — 포스트 확인 후 최종 판정 |

## Procedure

### Step 1: 세션 파일 확인/초기화

```bash
# 현재 활성 씬의 takes 파일 확인 — ${sessions_root} 는 userConfig 주입값
find ${sessions_root} -name "*{scene}*takes*" 2>/dev/null | head -1
```

파일이 없으면 새 take 세션 초기화:
**경로:** `${sessions_root}/{DATE}_{scene}_takes.md`

```markdown
---
description: {scene} 테이크 로그
tags:
  - take-log
  - {scene}
category: session-records
---

# Take Log — {scene} ({DATE})

**시작:** {TIME}
**모드:** Shooting
**VP Supervisor:** (이름)

---

## 테이크 기록

| 테이크 | 판정 | 부서 | 메모 | 시각 |
|---|---|---|---|---|

---

## 통계

- OK: 0
- NG: 0
- HOLD: 0
- 연속 NG: 0

---
```

### Step 2: 테이크 기록 추가

기존 파일에 행 추가:

```
| {T###} | {OK/NG/HOLD} | {dept} | {note} | {TIME} |
```

### Step 3: 5연속 NG 감지

NG 기록 후 해당 씬의 최근 5테이크가 모두 NG인지 확인:

```bash
# 마지막 5줄에서 NG 개수 확인
tail -5 "${sessions_root}/{DATE}_{scene}_takes.md"
```

5연속 NG 감지 시:
1. 콘솔 경고 출력
2. takes.md에 블로커 섹션 자동 추가:

```markdown
## ⚠️ 블로커 경고 — {TIME}

5연속 NG 발생. VP Supervisor 판단 필요.

**NG 원인 집계:**
- tech: {N}건
- art: {N}건
- mocap: {N}건

**권장 액션:**
- 가장 많은 NG 원인: {dept} → 해당 팀 즉각 점검
- `/risk-flag {dept} --severity high` 실행 고려
```

### Step 4: 통계 업데이트

매 기록 후 통계 섹션 갱신:
- OK / NG / HOLD 총 카운트
- 연속 NG 카운트 (OK/HOLD 시 리셋)

### Step 5: 콘솔 확인 출력

```
📹 {T###} → {판정} 기록됨
   씬: {scene} | {TIME}
   현황: OK {N} / NG {N} / HOLD {N} | 연속NG: {N}
   파일: ${sessions_root}/{DATE}_{scene}_takes.md
```

## HOLD 처리 규칙

HOLD 테이크는 takes.md 하단 별도 섹션으로 관리:

```markdown
## HOLD 테이크 목록

| 테이크 | 메모 | 포스트 판정 |
|---|---|---|
| {T###} | {note} | 미결 |
```

씬 완료 후 포스트팀 전달 패키지(`/handoff-pack`)에 HOLD 목록 포함.

## 씬 완료 (Scene Wrap) 요약

`/take-log wrap` 또는 씬 완료 시:
```
🎬 Scene Wrap — {scene}
   OK: {N}컷 / NG: {N}컷 / HOLD: {N}컷
   총 테이크: {N}
   기술 다운타임: {N}분 (NG tech 원인)

   → /data-wrangle --scene {scene} 실행 권장
```

## 주의사항

- takes.md는 누적 기록 — 절대 덮어쓰지 말 것 (append-only)
- --dept 미지정 NG는 `?` 로 기록 후 나중에 수정 가능
- vp-agent 의 `shoot-protocol.md` 블로커 기준 참조
- 5연속 NG 후 `/risk-flag` 발동은 VP Supervisor 재량

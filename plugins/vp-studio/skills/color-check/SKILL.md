---
name: color-check
description: VP Supervisor quality gate — LED 월 ↔ 카메라 색감 일치 검수. Visual Consistency KPI 직결. ACES 워크플로우 적용 여부 판정.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[--mode aces|sdr] [--led MODEL] [--date YYYY-MM-DD]"
---

# Color Check — 색 파이프라인 검수

Visual Consistency KPI 직결. LED 월 색감 ↔ 카메라 색감 불일치는 포스트에서 복구 불가.
**현장에서 고치자 불가능** — 이 검수가 FAIL이면 /shoot-gate는 NO-GO.

## Arguments

- `--mode aces|sdr` : 색 파이프라인 모드 (미지정 시 자동 판정)
- `--led MODEL` : LED 패널 모델명 (사양 참조용)
- `--date YYYY-MM-DD` : 촬영 날짜 (기본: 오늘)

## Procedure

### Step 1: 기존 color-check 파일 확인

```bash
find ${sessions_root} -name "*color*" -name "*{DATE}*" 2>/dev/null
```

### Step 2: ACES 워크플로우 적용 여부 판정

vp-agent `color-pipeline.md` 의 결정 기준에 따라 유저에게 확인:

1. **납품 포맷**: 극장(DCI P3/HDR) → ACES 적용, 웹/방송(BT.709) → SDR 파이프라인
2. **LED 패널 색역**: BT.2020/P3 → ACES 검토, BT.709 이하 → SDR
3. **카메라 Log 촬영 여부**: Log 촬영 → ACES 권장
4. **포스트팀 파이프라인**: DaVinci ACES → 반드시 ACES 적용

→ 판정 결과를 `--mode` 인자로 확정. 미지정 시 위 기준으로 자동 추론.

### Step 3: 각 체크포인트 검수

#### 3-1. LED 패널 캘리브레이션
- [ ] 제조사 캘리브레이션 파일 로드 완료 여부 확인
- [ ] 패널 색역(Color Gamut) 확인
  - BT.2020 지원 패널: `--mode aces` 필수
  - P3 지원 패널: `--mode aces` 권장
  - BT.709 패널: `--mode sdr` 가능
- [ ] 패널 균일도(Uniformity) 측정값 확인 (ΔE < 3: PASS, 3~5: WARN, >5: FAIL)
- [ ] 프레임레이트 동기화: 패널 주사율 ↔ 카메라 셔터 일치

#### 3-2. UE OCIO 설정
- [ ] OCIO 설정 파일 경로 확인: `Content/00_Project/Tools/OCIO/luts/`
- [ ] Display Transform: LED 패널 색역에 맞는 프로파일 선택
- [ ] View Transform 설정 (모니터링 기준)
- [ ] UE 레벨 전체 OCIO 적용 확인

#### 3-3. 카메라 세팅
- [ ] 자동노출 OFF 확인
- [ ] 화이트밸런스 고정 확인 (LED 패널 색온도 기준)
- [ ] 카메라 Color Profile 확정
- [ ] 현장 모니터링 LUT 로드 확인

#### 3-4. 조명 동기화 (조명 감독 협업)
- [ ] LED 월 주요 광원 색온도 파악
- [ ] 실제 Fill Light 색온도 매칭
- [ ] 가상 광원 (UE SkyLight/Directional) 색온도 일치

#### 3-5. 컬러차트 촬영 계획
- [ ] X-Rite ColorChecker 촬영 일정 확인
- [ ] 컬러차트 저장 경로 지정
- [ ] 포스트팀 전달 패키지 포함 확인

### Step 4: Moiré 리스크 확인

vp-agent `color-pipeline.md` 의 Moiré 방지 기준 참조:
- [ ] 카메라 셔터 각도 설정 확인 (LED 주사율 기준)
- [ ] 렌즈 조리개 범위 확인 (F4~F8 권장)

### Step 5: 판정

| 판정 | 조건 |
|---|---|
| **PASS** | 전 항목 충족, ΔE < 3 |
| **WARN** | ΔE 3~5, OCIO 부분 적용, 또는 모아레 리스크 존재 |
| **FAIL** | ΔE > 5, OCIO 미적용, 컬러차트 촬영 미완료, 색온도 차이 > 500K |

### Step 6: 보고서 파일 저장

**경로:** `${sessions_root}/{DATE}_color-pipeline.md`

```markdown
---
description: {DATE} 색 파이프라인 검수 보고서
tags:
  - color-check
  - color-pipeline
  - {mode}
category: session-records
---

# Color Check — {DATE}

## 판정: [PASS / WARN / FAIL]

**파이프라인 모드:** {ACES / SDR}
**LED 패널 색역:** {BT.709 / P3 / BT.2020}
**검수 담당:** VP Supervisor

---

## 검수 결과 요약

| 항목 | 상태 | 비고 |
|---|---|---|
| LED 패널 캘리브레이션 | ✅/⚠️/❌ | |
| 패널 균일도 (ΔE) | ✅/⚠️/❌ | ΔE = {값} |
| UE OCIO 설정 | ✅/⚠️/❌ | |
| 카메라 세팅 | ✅/⚠️/❌ | |
| 조명 동기화 | ✅/⚠️/❌ | |
| 컬러차트 촬영 | ✅/⚠️/❌ | |
| Moiré 리스크 | ✅/⚠️/❌ | |

---

## ACES 워크플로우 판정 근거

- 납품 포맷: {format}
- 카메라 프로파일: {profile}
- LED 색역: {gamut}
- 결론: {ACES 적용 / SDR 유지} — {이유}

---

## 조명 감독 협업 항목

- LED 월 기준 색온도: {K}
- Fill Light 설정: {K}
- 협의 필요 사항: {내용}

---

## WARN/FAIL 항목 액션

| 항목 | 조치 | 담당 |
|---|---|---|
| (항목) | (구체적 조치) | (담당) |

---

## 컬러차트 파일 경로

- 촬영 시각: {TIME}
- 저장 경로: {Motive 파일명}_colorref_001
- 포스트팀 전달: 포함
```

### Step 7: DB 인제스트

```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{DATE}_color-pipeline.md" \
  --project vp
```

### Step 8: 완료 메시지

```
🎨 Color Check 완료

판정: [PASS / WARN / FAIL]
모드: {ACES / SDR}
파일: ${sessions_root}/{DATE}_color-pipeline.md

/shoot-gate 반영: GO / CONDITIONAL-GO / NO-GO
```

## 주의사항

- Gemma4 위임 불가 — 색감 판정은 정밀도 최우선
- ACES/SDR 판정은 포스트팀과 사전 합의 필수
- 색 파이프라인 전체 기준: vp-agent `color-pipeline.md`
- LED 장비 사양: vp-agent `vp-equipment.md`
- UE 색 관리: vp-agent `unreal-engine.md`
- sRGB → Linear 변환: vp-agent `development.md` UI Color Rules

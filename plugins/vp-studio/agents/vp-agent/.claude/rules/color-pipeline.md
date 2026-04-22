# Color Pipeline — 색 관리 파이프라인

VP Supervisor의 Visual Consistency KPI 직결. LED 월 색감 ↔ 카메라 색감 불일치는 포스트에서 복구 불가.  
모든 결정 기준을 담은 SSOT. `/color-check` 스킬이 이 규칙을 참조한다.

---

## ACES 워크플로우 결정 기준

### ACES 적용 (권장)
아래 조건 **중 하나**라도 해당하면 ACES 적용:
- 최종 납품 포맷이 극장(DCI P3) 또는 HDR(PQ/HLG)
- LED 패널 색역이 BT.2020 또는 P3 이상
- 카메라가 Log 촬영 (ARRI LogC3, Sony S-Log3, RED Log3G10 등)
- 포스트 팀이 DaVinci Resolve ACES 파이프라인을 사용

### ACES 보류 (SDR 파이프라인)
아래 조건이 **모두** 해당하면 sRGB/BT.709 파이프라인:
- 최종 납품 포맷이 웹/SNS/방송 (BT.709)
- LED 패널 색역이 BT.709 이하
- 촬영 카메라가 표준 Rec.709 프로파일
- 포스트 팀이 별도 색 관리 워크플로우 없음

---

## 색역(Color Gamut) 계층

| 색역 | 커버리지 | VP 적용 시점 |
|---|---|---|
| BT.709 | sRGB 기준 | 방송/웹 납품, SDR 파이프라인 |
| P3 (DCI/Display) | BT.709의 약 140% | 극장 납품, 고급 스트리밍 |
| BT.2020 | P3의 약 130% | HDR 납품, 차세대 파이프라인 |

---

## LED ↔ 카메라 색감 일치 체크포인트

### 1. LED 패널 보정 (사전)
- [ ] LED 패널 제조사 제공 캘리브레이션 파일 로드
- [ ] 패널 균일도(Uniformity) 측정 — 코너 대비 센터 ΔE < 3
- [ ] 색온도 기준점 설정 (기본: D65 / 6500K)
- [ ] 프레임레이트 동기화 (LED 주사율 ↔ 카메라 셔터)

### 2. UE OCIO 설정
- [ ] OCIO 설정 파일 경로: `Content/00_Project/Tools/OCIO/luts/` (프로젝트별)
- [ ] Display Transform 설정: LED 패널 색역에 맞는 변환 선택
  - BT.709 패널: `sRGB → Display BT.709`
  - P3 패널: `sRGB → Display P3 D65`
- [ ] View Transform: 촬영 모니터 기준 (`Rec.709 (ACES)` 또는 `Disabled`)
- [ ] UE 레벨 씬 전체 OCIO 적용 확인 (OCIO Display 컴포넌트)

### 3. 카메라 세팅 동기화
- [ ] 카메라 ISO/노출 설정 고정 (자동노출 OFF)
- [ ] 화이트밸런스 고정 (LED 패널 색온도와 일치)
- [ ] 카메라 Color Profile 선택: Log 촬영 vs Rec.709 촬영
- [ ] 모니터링 LUT 로드 (현장 확인용 — 최종 LUT와 구분)

### 4. 실제 조명 ↔ 가상 광원 동기화
조명 감독과 협업 체크리스트:
- [ ] LED 월 주요 광원 색온도 파악 → 실제 조명에 반영
- [ ] 가상 Sky Light / Directional Light 색온도: LED 배경과 동일
- [ ] 실제 Fill Light 색온도: LED 월 반사광과 매칭
- [ ] 실제 Back Light: 씬 분위기 기준 ±500K 허용

### 5. 그레이카드/컬러차트 촬영 (필수)
- [ ] 씬 최초 촬영 전 X-Rite ColorChecker 촬영
- [ ] 저장 경로: `MoCap 세션 파일명_colorref_001` (Motive 동기화)
- [ ] 포스트팀 전달 패키지에 반드시 포함

---

## 색감 불일치 판정 기준

| 지표 | PASS | WARN | FAIL |
|---|---|---|---|
| LED ↔ 카메라 색온도 차이 | ΔT < 200K | ΔT 200~500K | ΔT > 500K |
| 패널 균일도 | ΔE < 3 | ΔE 3~5 | ΔE > 5 |
| OCIO 적용 여부 | 적용 완료 | 부분 적용 | 미적용 |
| 컬러차트 촬영 | 완료 | — | 미촬영 |

---

## Moiré 방지 기준

LED 월 ↔ 카메라 센서 간 모아레(Moiré) 발생 조건 및 대처:

| 원인 | 대처 |
|---|---|
| 카메라 셔터 각도 ↔ LED 주사율 불일치 | 셔터 각도를 LED 주사율에 맞게 조정 (180도 법칙 기준) |
| 카메라 렌즈 회절 + LED 픽셀 피치 | 렌즈 조리개 조정 (F4~F8 권장) |
| 카메라 해상도 ↔ LED 픽셀 해상도 근접 | 카메라-LED 거리 조정 또는 소프트 필터 |

---

## 참고 장비 및 색역 소스

- **LED 패널 사양 확인:** `vp-equipment.md` → LED 월 섹션
- **UE OCIO 공식 문서:** `dev.epicgames.com/documentation/.../color-management-with-opencolorio`
- **ACES:** `acescentral.com` — Academy Color Encoding System 공식
- **D65 기준 화이트포인트:** CIE 표준 (x=0.3127, y=0.3290)

---
name: mocap-brief
description: VP Supervisor — MoCap 팀 전용 상세 브리핑. 배우별 리타겟팅 계획, Motive 세션 설정, 슈트 배정 문서 생성.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<ProjectName> <S##> <C##> <CharName1> [CharName2] [CharName3]"
---

# MoCap Brief — 모션 캡처 팀 전용 브리핑

MoCap 팀에 배포할 상세 브리핑 문서. `/team-brief mocap`의 확장판.  
배우별 슈트 배정, Motive 세션 설정, MetaHuman 리타겟팅 계획까지 포함.

## Arguments

- `<ProjectName>` : 프로젝트명 (예: `FilmA`)
- `<S##>` : 씬 번호 (예: `S03`)
- `<C##>` : 컷 번호 (예: `C01`)
- `<CharName>` : 캐릭터명 (최대 3명, OptiTrack 최대 동시 배우 수 제한)

예: `/mocap-brief FilmA S03 C01 HeroA VillainB`

## Procedure

### Step 1: 기존 MoCap 브리핑 확인

```bash
find ${mocap_sessions_root} -name "*S{##}*C{##}*" 2>/dev/null
find ${sessions_root} -name "*S{##}C{##}*brief*" 2>/dev/null
```

마스터 브리핑(`/brief-scene`)이 있으면 MoCap 섹션 참조.

### Step 2: MoCap 정보 수집

vp-agent 의 `optitrack.md` rule 기준으로 확인:

1. **배우 수 검증**: 최대 3명 제한 → 초과 시 즉시 P1 리스크 플래그
2. **캡처 공간 확인**: 유효 캡처 영역 9m x 5m — 씬 연기 동선과 비교
3. **MetaHuman 리타겟팅 대상**: 각 캐릭터의 MetaHuman ID 확인

필요 시 유저에게 추가 확인:
- 배우 키/체형 (슈트 사이즈 선택)
- 씬 동선 범위 (유효 캡처 영역 초과 여부)
- 특수 동작 (낙법, 점프, 싸움 씬 등)

### Step 3: Motive 파일명 패턴 확정

vp-agent 의 `optitrack.md` rule 의 네이밍 패턴 기준:

**패턴:** `{Project}_S{##}_C{##}_{MoCapCharacter}_{###}`

| 캐릭터 | 파일명 패턴 | 첫 테이크 예시 |
|---|---|---|
| {CharName1} | `{Project}_S{##}_C{##}_{CharName1}_{###}` | `FilmA_S03_C01_HeroA_001` |
| {CharName2} | `{Project}_S{##}_C{##}_{CharName2}_{###}` | `FilmA_S03_C01_VillainB_001` |

### Step 4: 브리핑 문서 생성

**경로:** `${mocap_sessions_root}/{DATE}_{Project}_S{##}C{##}_mocap-brief.md`

```markdown
---
description: {Project} S{##}C{##} MoCap 팀 브리핑
tags:
  - mocap-brief
  - mocap
  - {Project}
  - S{##}C{##}
category: session-records
---

# MoCap Brief — {Project} S{##}C{##}

**촬영 날짜:** {DATE}  
**캡처 씬:** {Project} Scene {S##} Cut {C##}  
**배포 대상:** MoCap Team 전용  
**배우 수:** {N}명 / 최대 3명 제한 ✅

---

## ⚠️ 사전 확인 사항

- [ ] 배우 수 {N}명 — OptiTrack 최대 동시 배우 수(3명) {이내/초과}
- [ ] 유효 캡처 영역: 9m x 5m — 씬 동선 {수용 가능/주의 필요}
- [ ] 특수 동작: {낙법/점프/없음}

---

## 세션 설정

### Motive 소프트웨어 설정
| 항목 | 설정값 |
|---|---|
| 소프트웨어 버전 | Motive 3.4.0.2 |
| 캡처 프레임레이트 | {fps}fps |
| 캡처 공간 | 11m x 6.5m x 3m (유효: 9m x 5m) |
| 타임코드 소스 | Ambient Lockit (Tentacle Sync E 기준) |

### 카메라 구성
| 카메라 | 수량 |
|---|---|
| PrimeX41 (IR) | 6대 |
| PrimeX22 (IR) | 14대 |
| **총합** | **20대** |

---

## 캐릭터별 슈트 배정

| 캐릭터 | 배우 | 슈트 번호 | 마커 세트 | 특이사항 |
|---|---|---|---|---|
| {CharName1} | (배우명) | (번호) | (마커 설명) | |
| {CharName2} | (배우명) | (번호) | (마커 설명) | |

### 슈트 체크리스트
- [ ] 슈트 사이즈 배우별 확인
- [ ] 마커 부착 완료 (슈트별 마커 세트 고정)
- [ ] 슬라이딩 마커 없음 확인
- [ ] 리지드 바디 마커 별도 설정 (도구류, 무기 등)

---

## Motive 파일명 패턴

> **팀원 필독: 아래 패턴 정확히 준수**

```
패턴: {Project}_S{##}_C{##}_{CharName}_{###}
```

| 캐릭터 | 파일명 패턴 |
|---|---|
| {CharName1} | `{Project}_S{S#}_C{C#}_{CharName1}_001` ~ |
| {CharName2} | `{Project}_S{S#}_C{C#}_{CharName2}_001` ~ |

**주의:**
- 테이크 번호는 001부터 순서대로
- 리테이크 시 번호 이어서 (초기화 금지)
- 실패 테이크도 저장 (파일명 그대로)

---

## MetaHuman 리타겟팅 계획

| MoCap 캐릭터 | MetaHuman ID | 리타겟터 에셋 | 리타겟 담당 |
|---|---|---|---|
| {CharName1} | {MHI_이름} | `RTG_{CharName1}_to_MH` | (담당자) |
| {CharName2} | {MHI_이름} | `RTG_{CharName2}_to_MH` | (담당자) |

리타겟터 에셋 경로: `Content/00_Project/Assets/Chr/{CharName}/`

---

## LiveLink 브릿지 설정

| 항목 | 설정값 |
|---|---|
| Motive → UE 브릿지 | OptiTrack LiveLink Plugin |
| LiveLink 프리셋 | `LLP_OptiTrack_Main` |
| 포트 | 기본값 (충돌 없음 확인) |
| 레이턴시 목표 | < 30ms |

LiveLink 체크리스트:
- [ ] UE LiveLink 소스 연결 확인 (`FOptLiveLinkMonitor` GREEN)
- [ ] 캐릭터별 Subject 이름 Motive ↔ UE 일치
- [ ] 프레임레이트 {fps}fps 동기화

---

## 촬영 당일 순서

1. 카메라 웜업 (30분)
2. 배우 슈트 착용 + 마커 부착
3. **리지드 바디/스켈레톤 캘리브레이션** (← 가장 중요)
4. Motive 세션 파일 생성 (파일명 패턴 확인)
5. LiveLink 브릿지 연결 확인
6. 테스트 테이크 1회 (T001 — OK 여부 확인 후 삭제)
7. 본 촬영 시작

---

## 체크리스트 (촬영 시작 전 전원 서명)

- [ ] 카메라 캘리브레이션 완료 (Wand Error < 0.3mm)
- [ ] 스켈레톤 마커 세트 저장 완료
- [ ] Motive 세션 파일명 패턴 확인
- [ ] LiveLink 연결 및 레이턴시 확인
- [ ] 타임코드 동기화 확인 (Ambient Lockit)
- [ ] 배우별 슈트 최종 확인
- [ ] 테스트 테이크 OK 확인
```

### Step 5: DB 인제스트

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
  --file "${mocap_sessions_root}/{DATE}_{Project}_S{##}C{##}_mocap-brief.md" \
  --project vp
```

### Step 6: 완료 메시지

```
🏃 MoCap Brief 생성 완료

씬: {Project} S{##}C{##} | 배우: {N}명
파일: ${mocap_sessions_root}/{DATE}_{Project}_S{##}C{##}_mocap-brief.md

Motive 파일명 패턴:
  {Project}_S{S#}_C{C#}_{CharName}_{###}

다음 단계:
  → /sync-check  (Genlock/TC 체인 확인)
  → /shoot-gate  (GO/NO-GO 최종 판정)
```

## 주의사항

- 배우 수 > 3명 시 P1 리스크 플래그 자동 생성 (vp-agent 의 `optitrack.md` rule 제한)
- 캘리브레이션 미완료는 `/shoot-gate` NO-GO 조건
- vp-agent 의 `optitrack.md` rule 의 Motive 파일명 패턴이 SSOT — 이 문서보다 우선
- MetaHuman ID는 UE 프로젝트에서 직접 확인 필요

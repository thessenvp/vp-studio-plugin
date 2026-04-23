---
name: brief-scene
description: VP Supervisor — 씬 촬영 시작 전 다학제 팀 브리핑 문서 생성. Art/Previz/MoCap/Engineering 부서 지시사항을 하나의 마스터 문서로 통합.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<SceneName> [--sequence S##C##] [--actors N] [--date YYYY-MM-DD]"
---

# Brief Scene — 씬 마스터 브리핑

VP Supervisor가 다학제 팀(Art/Previz/MoCap/Engineering)에 배포할 브리핑 문서를 생성한다.  
각 파트의 기술적 언어가 다르므로 이를 하나의 문서로 통합하는 역할.

## Arguments

- `<SceneName>` : 씬 식별자 (예: `FilmA_영웅추격씬`)
- `--sequence S##C##` : 씬/컷 번호 (예: `S03C01`)
- `--actors N` : 동시 MoCap 촬영 배우 수 (기본: 1, 최대: 3)
- `--date YYYY-MM-DD` : 촬영 예정일 (기본: 오늘)

## Procedure

### Step 1: 기존 관련 파일 확인

```bash
# 이전 같은 씬 브리핑 파일 있는지 확인
find ${docs_root}/pipeline -name "*{SceneName}*" 2>/dev/null
find ${briefings_root} -name "*{sequence}*" 2>/dev/null
```

### Step 2: 씬 정보 수집

유저에게 다음 정보를 확인한다 (인자에 없는 경우):

1. **씬 개요**: 씬의 목적, 감정선, 배경 설정
2. **기술 요구사항**:
   - 배우 수 및 캐릭터명 (MoCap 명명 패턴 준비)
   - 특수 FX (Niagara, Groom, 파티클)
   - LED 월 콘텐츠 유형 (HDRI/실사 영상/실시간 UE)
   - VCam 구성 (iPad/iPhone 대수, 예상 렌즈 프리셋)
3. **opt-review 결과**: 이미 `/opt-review`를 실행했다면 결과 참조

### Step 3: 마스터 브리핑 문서 생성

**경로:** `${sessions_root}/{DATE}_{SceneName}_brief.md`

```markdown
---
description: {SceneName} 씬 마스터 브리핑
tags:
  - briefing
  - {sequence}
  - {SceneName}
category: session-records
---

# 씬 브리핑 — {SceneName} ({sequence})

**촬영 예정:** {DATE}  
**작성:** VP Supervisor  
**배포:** Art / Previz / MoCap / Engineering

---

## 씬 개요

> (감독 의도와 감성 키워드 — 모든 팀원이 같은 방향을 볼 수 있도록)

- **목적:** (씬이 이야기에서 하는 역할)
- **분위기:** (감성 키워드 3-5개)
- **예상 길이:** (컷 수 또는 분)
- **특이사항:** (특수 요구, 제약)

---

## ✅ 리스크 플래그

> GO 전에 반드시 해소해야 할 항목

| 리스크 | 심각도 | 담당 | 해소 기준 |
|---|---|---|---|
| (항목) | P1/P2/P3 | (부서) | (완료 조건) |

*(리스크 없으면 섹션 유지하되 "없음"으로 기재)*

---

## 🎨 Art Team 지시사항

### 최적화 기준 (Frame Rate KPI)
- 목표 FPS: {target_fps}fps (기본 24fps)
- `/opt-review` 판정: (PASS/WARN/FAIL — 해당 날짜 결과 참조)

### 에셋 우선순위
| 우선순위 | 에셋 | LOD 프로파일 | Nanite | 마감 |
|---|---|---|---|---|
| P1 | (주요 에셋) | Hero | 필수 | (날짜) |
| P2 | (보조 에셋) | Supporting | 권장 | (날짜) |
| P3 | (배경 에셋) | Background | 선택 | (날짜) |

### 텍스처 가이드라인
- LED 월 해상도 기준: (해상도)
- 단일 텍스처 메모리 상한: 512MB
- (특이 사항)

### 체크리스트
- [ ] 주요 에셋 Nanite 활성화 확인
- [ ] LOD 프로파일 (UOptCharacterLODProfile) 설정
- [ ] 텍스처 스트리밍 메모리 Top20 확인
- [ ] Perforce 최종 제출 완료
- [ ] `/opt-review` 통과 확인

---

## 🎬 Previz Team 지시사항

### VCam 구성
- iPad/iPhone 대수: {N}대
- 예상 렌즈 프리셋: (초점거리)
- LiveLink 프리셋: `LLP_OptiTrack_Main` (또는 지정 프리셋)

### 라이팅 기조
- LED 월 콘텐츠: (HDRI명 / 실사 영상 / 실시간 UE)
- 가상 광원 설정: (SkyLight/Directional/HDRI 구성)
- 실제 조명 협의 포인트: (조명 감독과 동기화할 색온도/강도)

### ShotName 규칙
패턴: `{Project}_S{##}_C{##}_{ShotDescription}`  
예시: `FilmA_S03_C01_HeroChase`

### Sequencer 설정
- 대상 시퀀서 경로: (UE Content Browser 경로)
- FPS: {target_fps}fps 고정
- Movie Render Preset: (프리셋명)

### 체크리스트
- [ ] VCam LiveLink 연결 확인
- [ ] 라이팅 프리셋 로드 및 조정
- [ ] ShotName 규칙 적용 확인
- [ ] Sequencer 설정 완료
- [ ] HDRI/LED 콘텐츠 로드 확인

---

## 🏃 MoCap Team 지시사항

### 세션 정보
| 항목 | 내용 |
|---|---|
| 배우 수 | {N}명 (최대 3명 제한) |
| 캡처 공간 | 9m x 5m 기준 |
| 동시 촬영 캐릭터 | (캐릭터명 목록) |

### Motive 파일명 패턴
```
{Project}_S{##}_C{##}_{Character}_{###}
```
예시: `FilmA_S03_C01_HeroA_001`, `FilmA_S03_C01_HeroA_002`

### 캐릭터별 슈트 배정
| 캐릭터 | 배우 | 슈트 번호 | 마커 세트 |
|---|---|---|---|
| (캐릭터1) | (배우명) | (번호) | (마커 설명) |

### MetaHuman 리타겟팅 대상
| MoCap 캐릭터 | MetaHuman ID | 리타겟터 |
|---|---|---|
| (캐릭터) | (ID) | (RTG_명) |

### 체크리스트
- [ ] OptiTrack 카메라 캘리브레이션 완료
- [ ] 스켈레톤 마커 세트 확인
- [ ] Motive → UE LiveLink 브릿지 연결
- [ ] 파일명 패턴 사전 설정
- [ ] 최대 배우 수(3명) 이내 확인

---

## ⚙️ Engineering 지시사항

### 동기화 체인 확인 순서
1. SPG 8000 출력 신호 (HD/SD tri-level sync)
2. Blacktrax eSync Genlock 수신
3. Tentacle Sync E 타임코드 수신
4. Ambient Lockit x4 무선 TC 배포
5. UE Genlock Monitor 상태 (FOptGenlockMonitor)
6. UE Timecode Monitor 상태 (FOptTimecodeMonitor)
7. LiveLink 소스 연결 (FOptLiveLinkMonitor)

### UE 플러그인 상태
- Optimazation 플러그인 프로파일: Shooting 모드 (UOptSetupProfile)
- 대상 FPS: {target_fps}fps

### LED 월 세팅
- nDisplay 구성: (NDC_ 프리셋명)
- 해상도: (LED 패널 해상도)
- 색 공간 설정: (OCIO 프로파일)

### 체크리스트
- [ ] `/sync-check` 실행 완료
- [ ] 전 동기화 체인 정상
- [ ] Optimazation 플러그인 Shooting 프로파일 로드
- [ ] nDisplay 설정 확인
- [ ] 네트워크 레이턴시 확인

---

## 📋 촬영 전 최종 체크 (VP Supervisor)

- [ ] `/opt-review` PASS 확인
- [ ] `/color-check` PASS 확인 (별도 실행 시)
- [ ] Art/Previz/MoCap/Engineering 브리핑 배포 완료
- [ ] `/sync-check` PASS 확인
- [ ] 모든 리스크 플래그 해소
- [ ] `/shoot-gate` GO 발동 준비
```

### Step 4: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "<file>" --project vp
```

(앞 Step 의 파일/산출물은 이미 저장됐으므로 skill 은 정상 완료로 간주.)

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${sessions_root}/{DATE}_{SceneName}_brief.md" --project vp
```

### Step 5: 완료 메시지

```
📋 마스터 브리핑 생성 완료

파일: ${sessions_root}/{DATE}_{SceneName}_brief.md

다음 단계:
  1. /team-brief art --scene {SceneName}   (Art 전용 배포본)
  2. /team-brief previz --scene {SceneName} (Previz 전용 배포본)
  3. /team-brief mocap --scene {SceneName}  (MoCap 전용 배포본)
  4. /opt-review --scene {sequence}         (최적화 검수)
  5. /sync-check                            (동기화 체인 확인)
```

## 주의사항

- 배우 수 > 3명 시 자동으로 P1 리스크 플래그 생성 (vp-agent 의 `optitrack.md` rule 제한)
- Gemma4 부분 위임 가능: 씬 개요 텍스트 서술 (→ gemma4 로 씬 개요 생성 위임)
- 규칙 참조 순서: vp-agent 의 `optitrack.md` → `vp-session.md` → `vp-equipment.md` → `vp-supervisor.md` rule
- opt-review 결과가 있으면 Art Team 섹션에 자동 반영

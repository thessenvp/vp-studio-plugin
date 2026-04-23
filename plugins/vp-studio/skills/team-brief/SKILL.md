---
name: team-brief
description: VP Supervisor — 특정 부서에 배포할 전용 브리핑 문서 생성. 체크박스 형식으로 팀원이 바로 읽고 실행 가능한 단일 부서 문서.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<art|previz|mocap|engineering> [--scene SceneName] [--sequence S##C##]"
---

# Team Brief — 부서별 배포용 브리핑

VP Supervisor가 각 부서에 배포할 **전용 문서**를 생성한다.  
팀원은 Claude에 직접 접근하지 않으므로, 문서는 체크박스 형식으로 **즉시 실행 가능**해야 한다.

## Arguments

- `<team>` : 대상 부서 — `art` | `previz` | `mocap` | `engineering`
- `--scene SceneName` : 씬 식별자 (brief-scene의 SceneName과 동일)
- `--sequence S##C##` : 씬/컷 번호

## Procedure

### Step 1: 마스터 브리핑 참조

```bash
# 오늘 생성된 마스터 브리핑 찾기
find ${sessions_root} -name "*_brief.md" -newer /dev/null 2>/dev/null | head -5
find ${sessions_root} -name "*{scene}*brief*" 2>/dev/null
```

마스터 브리핑(`/brief-scene` 결과물)이 있으면 해당 내용을 기반으로 생성.  
없으면 유저에게 씬 정보 직접 요청.

### Step 2: 부서별 문서 생성

**경로:** `${briefings_root}/{team}_{SceneName}_brief.md`

---

#### Art Team 문서

```markdown
---
description: {SceneName} Art Team 브리핑
tags: [briefing, art, {SceneName}]
category: session-records
---

# 🎨 Art Team 브리핑 — {SceneName}

**날짜:** {DATE}  
**씬:** {sequence}  
**발행:** VP Supervisor

---

## 미션

> (씬 핵심 목적 1줄 — 모든 팀원이 같은 방향을 볼 수 있도록)

---

## ⚡ 최적화 기준 (Frame Rate KPI)

> 이 기준을 지키지 않으면 촬영이 불가능합니다.

- **목표 FPS:** {target_fps}fps
- **렌더 머신:** NVIDIA A6000 (VRAM 48GB)
- **GPU 부하 상한:** 80%

### Nanite 적용 기준
| 폴리곤 수 | Nanite 적용 |
|---|---|
| > 50,000 | **필수** |
| 10,000 ~ 50,000 | 권장 |
| < 10,000 | 선택 |

### LOD 프로파일 설정
| 캐릭터 등급 | 프로파일 | Nanite | Screen Size |
|---|---|---|---|
| Hero | `Hero` | 필수 | > 0.3 |
| Supporting | `Supporting` | 권장 | > 0.15 |
| Background | `Background` | 선택 | > 0.05 |

*(UOptCharacterLODProfile DataAsset에서 설정)*

### 텍스처 메모리 제한
- 단일 텍스처 상한: **512MB**
- LED 월 기준 해상도: (해상도)

---

## 📋 에셋 작업 목록

### P1 — 촬영 전 필수 완료
- [ ] (에셋명) — (조치사항) — 마감: {날짜}
- [ ] (에셋명) — Nanite 활성화

### P2 — 가능하면 완료
- [ ] (에셋명) — LOD 프로파일 설정

### P3 — 여유 있을 때
- [ ] (에셋명) — 텍스처 최적화

---

## 🚀 Perforce 제출 체크리스트
- [ ] 모든 P1 에셋 Changelist 제출 완료
- [ ] 에셋 네이밍 컨벤션 확인 (SM_, SK_, T_, M_ 등 prefix 필수)
- [ ] Perforce 경로: `${perforce_workspace_root}\1_Project\{ProjectName}\`

---

## ⚠️ 알려진 이슈

(이슈가 있으면 기재, 없으면 "없음")

---

## 📞 문의

최적화 기준 관련 → VP Supervisor에게 확인
```

---

#### Previz Team 문서

```markdown
---
description: {SceneName} Previz Team 브리핑
tags: [briefing, previz, {SceneName}]
category: session-records
---

# 🎬 Previz Team 브리핑 — {SceneName}

**날짜:** {DATE}  
**씬:** {sequence}  
**발행:** VP Supervisor

---

## 미션

> (씬 핵심 목적 1줄)

---

## 📷 VCam 구성

| 항목 | 설정값 |
|---|---|
| 대수 | {N}대 (iPad/iPhone) |
| 렌즈 프리셋 | (예: 35mm, 50mm) |
| LiveLink 프리셋 | `LLP_OptiTrack_Main` |
| LiveLink 연결 확인 | UE LiveLink 창 → 소스 상태 Green |

### 체크리스트
- [ ] VCam LiveLink 플러그인 활성화
- [ ] 지정 렌즈 프리셋 로드
- [ ] 화면 Preview 정상 확인

---

## 💡 라이팅 기조

**LED 월 콘텐츠:** (HDRI명 / 실사 영상 / 실시간 UE 레벨)

| 광원 | 설정 | 색온도 |
|---|---|---|
| HDRI/SkyLight | (강도) | (K) |
| Directional Light | (강도) | (K) |
| 추가 광원 | (설명) | (K) |

### 조명 감독 동기화 포인트
> LED 월이 거대한 조명 역할을 하므로 실제 현장 조명과 색온도/강도를 맞춰야 합니다.

- [ ] 가상 광원 색온도를 실제 조명과 협의
- [ ] LED 월 밝기 vs 보조 조명 밸런스 확인
- [ ] 그레이카드로 White Balance 촬영 (색 검수용)

---

## 🎞️ Sequencer 설정

| 항목 | 값 |
|---|---|
| 시퀀서 경로 | (Content Browser 경로) |
| FPS | {target_fps}fps (고정) |
| ShotName 패턴 | `{Project}_S{##}_C{##}_{ShotDesc}` |
| Movie Render Preset | (프리셋명) |

**ShotName 예시:** `FilmA_S03_C01_HeroChase`

### 체크리스트
- [ ] FPS {target_fps}fps 고정 확인
- [ ] ShotName 규칙 적용
- [ ] Sequencer 레코딩 세팅 확인
- [ ] HDRI/LED 콘텐츠 로드 완료

---

## ⚠️ 알려진 이슈

(이슈가 있으면 기재, 없으면 "없음")
```

---

#### MoCap Team 문서

```markdown
---
description: {SceneName} MoCap Team 브리핑
tags: [briefing, mocap, {SceneName}]
category: session-records
---

# 🏃 MoCap Team 브리핑 — {SceneName}

**날짜:** {DATE}  
**씬:** {sequence}  
**발행:** VP Supervisor

---

## 세션 정보

| 항목 | 내용 |
|---|---|
| 동시 촬영 배우 | {N}명 (**최대 3명 제한**) |
| 유효 캡처 공간 | 9m x 5m |
| 소프트웨어 | Motive 3.4.0.2 |

---

## 📁 Motive 파일명 패턴

```
{Project}_S{##}_C{##}_{Character}_{###}
```

**이 씬의 파일명:**
- `{Project}_S{##}_C{##}_{Char1}_001` (첫 번째 테이크)
- `{Project}_S{##}_C{##}_{Char1}_002` (두 번째 테이크)
- (추가 캐릭터가 있을 경우 계속)

---

## 👤 캐릭터별 배정

| 캐릭터 | 배우 | 슈트 | 마커 세트 특이사항 |
|---|---|---|---|
| (캐릭터1) | (배우명) | 슈트 #{N} | (특이사항) |
| (캐릭터2) | (배우명) | 슈트 #{N} | |

---

## 🔗 MetaHuman 리타겟팅 대상

| MoCap 캐릭터 | MetaHuman ID | 리타겟터 애셋 |
|---|---|---|
| (캐릭터) | (MHI_명) | (RTG_명) |

---

## 📋 캘리브레이션 체크리스트

### 촬영 전 (필수)
- [ ] OptiTrack 카메라 전체 켜짐 확인 (PrimeX41 x6, PrimeX22 x14)
- [ ] Motive 캘리브레이션 완료 (오차 < 0.3mm 목표)
- [ ] 캡처 공간(9x5m) 내 마커 배치 확인
- [ ] 배우별 슈트 + 마커 세트 착용 확인
- [ ] 스켈레톤 마킹 → Motive에서 캐릭터 인식 확인

### UE 연동 확인
- [ ] UE LiveLink 소스 → OptiTrack 연결 확인 (Green 상태)
- [ ] `LLP_OptiTrack_Main` 프리셋 로드
- [ ] LocodromeToolkits 리타겟터 활성화 확인
- [ ] FOptLiveLinkMonitor 레이턴시 정상 범위 (< 5ms 목표)

---

## ⚠️ 알려진 이슈

(이슈가 있으면 기재, 없으면 "없음")
```

---

#### Engineering 문서

```markdown
---
description: {SceneName} Engineering 브리핑
tags: [briefing, engineering, {SceneName}]
category: session-records
---

# ⚙️ Engineering 브리핑 — {SceneName}

**날짜:** {DATE}  
**씬:** {sequence}  
**발행:** VP Supervisor

---

## 🔄 동기화 체인 점검 순서

> 이 순서대로 확인하지 않으면 동기화 실패의 원인 파악이 어렵습니다.

- [ ] **1. SPG 8000** — HD/SD tri-level sync 출력 신호 확인
- [ ] **2. Blacktrax eSync** — Genlock 수신 상태 확인
- [ ] **3. Tentacle Sync E** — eSync로부터 타임코드 수신 확인
- [ ] **4. Ambient Lockit x4** — 무선 TC 배포 전 장치 수신 확인
- [ ] **5. UE Genlock Monitor** — `FOptGenlockMonitor` → 상태 Green
- [ ] **6. UE Timecode Monitor** — `FOptTimecodeMonitor` → 상태 Green
- [ ] **7. LiveLink Monitor** — `FOptLiveLinkMonitor` → 레이턴시 < 5ms

**목표 FPS:** {target_fps}fps — 전 시스템 일치 필수

---

## 🎛️ Optimazation 플러그인 설정

| 항목 | 설정값 |
|---|---|
| 프로파일 | Shooting 모드 (`UOptSetupProfile`) |
| 목표 FPS | {target_fps}fps |
| Ctrl+Shift+V | VP Monitor 창 열기 |
| Ctrl+Shift+M | Frame Monitor 창 열기 |
| Ctrl+Shift+O | Opt Panel 창 열기 |

- [ ] Optimazation 플러그인 로드 확인
- [ ] Shooting 프로파일 적용
- [ ] Frame Drop Analyzer 대기 상태 확인

---

## 🖥️ LED 월 (nDisplay) 설정

| 항목 | 설정값 |
|---|---|
| nDisplay 구성 | (NDC_ 프리셋명) |
| 해상도 | (LED 패널 해상도) |
| OCIO 프로파일 | (OCIO_명) |
| 색 공간 | (BT.2020 / P3 / BT.709) |

- [ ] nDisplay 구성 파일 로드
- [ ] OCIO 색 관리 설정
- [ ] LED 패널 전원 및 연결 확인

---

## 🌐 네트워크

- [ ] 렌더 머신(A6000) ↔ 개발 워크스테이션 연결
- [ ] OptiTrack ↔ UE LiveLink 포트 개방 확인
- [ ] VCam 와이파이 연결 확인

---

## ⚠️ 알려진 이슈 & 트러블슈팅

(이슈가 있으면 기재, 없으면 "없음")

트러블슈팅 자료: `/search-docs <증상 키워드>` 로 검색
```

---

### Step 3: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "<file>" --project vp
```

(앞 Step 의 파일/산출물은 이미 저장됐으므로 skill 은 정상 완료로 간주.)

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${briefings_root}/{team}_{SceneName}_brief.md" --project vp
```

### Step 4: 완료 메시지

```
📋 {team} 브리핑 생성 완료

파일: ${briefings_root}/{team}_{SceneName}_brief.md
→ 팀원에게 직접 전달하세요.

남은 부서:
  (생성되지 않은 부서 목록)
```

## 주의사항

- Gemma4 부분 위임 가능: 씬 미션 서술 부분 (기술 수치는 Claude 직접 주입)
- 체크박스 형식 필수 — 팀원이 프린트해서 현장에서 사용할 수 있어야 함
- `/brief-scene` 마스터 브리핑이 있으면 해당 내용을 정확히 부서별로 분리할 것
- 규칙 참조: vp-agent 의 `optitrack.md`, `unreal-engine.md`, `vp-equipment.md`, `vp-supervisor.md` rule

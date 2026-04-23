---
name: opt-review
description: VP Supervisor quality gate — 에셋 최적화 검수. 아티스트 결과물이 실시간 촬영 FPS를 유지하는지 PASS/WARN/FAIL로 판정하고 아티스트 액션 아이템 생성.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[--scene S##C##] [--target-fps 24|60]"
---

# Opt Review — 실시간 최적화 검수

VP Supervisor의 가장 중요한 업무. Frame Rate KPI 직결.
**"현장에서 고치자" 불가능** — 이 검수가 FAIL이면 /shoot-gate는 NO-GO.

## Arguments

- `--scene S##C##` : 대상 씬/컷 (예: `S01C03`)
- `--target-fps 24|60` : 목표 프레임레이트 (기본: 24fps)

## Procedure

### Step 1: 검수 대상 정보 수집

현재 UE 프로젝트 경로와 씬 정보를 파악한다.

```bash
# Perforce 워크스페이스에서 프로젝트 경로 확인 — ${perforce_workspace_root} 는 userConfig
ls "${perforce_workspace_root}/1_Project/" 2>/dev/null || echo "P4 경로 없음 — 직접 경로 입력 필요"
```

유저에게 다음 정보를 확인한다 (인자로 없을 경우):
1. UE 프로젝트 경로 (예: `${perforce_workspace_root}/1_Project/Proj_FilmA`)
2. 대상 씬 레벨명
3. 배우 수 (MoCap 동시 촬영)
4. 특수 FX 여부 (Niagara, Groom 등)

### Step 2: Optimazation 플러그인 데이터 참조

Optimazation 플러그인(`${vpo_plugin_root}/Extra/UE_57/Optimazation/`)의 주요 시스템 기준으로 각 항목을 검토한다.

**검수 항목 체크리스트:**

#### 2-1. Nanite 적용 검수
- Nanite 적용 대상 에셋 (Static Mesh, 복잡도 높은 Prop) 확인
- Nanite 미적용 에셋 중 폴리곤 > 50k인 항목 경고
- `UOptCharacterLODProfile` DataAsset 설정 확인 (Hero/Supporting/Background)

#### 2-2. LOD 프로파일 검수
| 캐릭터 등급 | Nanite | Screen Size | LOD 전환 거리 |
|---|---|---|---|
| Hero (주인공) | 필수 | > 0.3 | 5m 이하 |
| Supporting (조연) | 권장 | > 0.15 | 10m 이하 |
| Background (엑스트라) | 선택 | > 0.05 | 20m 이하 |

#### 2-3. 텍스처 스트리밍 Top20 메모리
- 씬 내 텍스처 메모리 상위 20개 에셋 목록 요청
- `SOptTextureStreamingWidget` 기준: 단일 텍스처 > 512MB 경고
- LED 월 해상도 대비 과도한 고해상도 텍스처 플래그

#### 2-4. Groom/Hair 제어
- Groom 에셋 사용 여부 확인
- Hair 스트랜드 수 vs. 렌더 머신(A6000) 허용 범위 검토
- `r.HairStrands.Strands` 설정 권고값 제시

#### 2-5. GPU 예상 부하 계산
렌더 머신(A6000, VRAM 48GB) 기준:
- 예상 DrawCall 수 (에셋 수 × 복잡도 계수)
- 예상 VRAM 사용량 (텍스처 + 지오메트리 + 버퍼)
- 안전 마진: GPU 부하 < 80% 목표

#### 2-6. Shot 예산 추적
`SOptShotBudgetWidget` 기준 각 샷별 FPS 예산 확인:
- 씬 당 평균 예상 FPS
- 가장 복잡한 컷의 최저 예상 FPS

### Step 3: 판정 및 보고서 생성

**판정 기준:**

| 판정 | 조건 | 다음 액션 |
|---|---|---|
| **PASS** | 목표 FPS 달성 확실 (마진 > 10%) | /shoot-gate GO 허용 |
| **WARN** | FPS 마진 < 10% 또는 일부 항목 경계값 | CONDITIONAL-GO 검토 |
| **FAIL** | FPS 드랍 확실 또는 VRAM 초과 예상 | 반드시 수정 후 재검수 |

### Step 4: 보고서 파일 저장

**경로:** `${sessions_root}/YYYY-MM-DD_{scene}_opt-review.md`

```markdown
---
description: {scene} 최적화 검수 보고서
tags:
  - opt-review
  - optimization
  - {scene}
category: session-records
---

# Opt Review — {scene} ({DATE})

## 판정: [PASS / WARN / FAIL]

**목표 FPS:** {target_fps}fps
**검수 담당:** VP Supervisor

## 검수 결과 요약

| 항목 | 상태 | 비고 |
|---|---|---|
| Nanite 적용 | ✅/⚠️/❌ | (상세) |
| LOD 프로파일 | ✅/⚠️/❌ | (상세) |
| 텍스처 메모리 | ✅/⚠️/❌ | (상세) |
| Groom/Hair | ✅/⚠️/❌ | (상세) |
| GPU 예상 부하 | ✅/⚠️/❌ | (상세) |
| Shot 예산 | ✅/⚠️/❌ | (상세) |

## 세부 결과

### Nanite
- 적용: (목록)
- 미적용 경고: (목록)

### LOD 프로파일
(Hero/Supporting/Background 각 설정)

### 텍스처 메모리 Top 5
| 에셋 | 메모리 | 판정 |
|---|---|---|

### Groom/Hair
(상태 및 권고값)

### GPU 예상 부하
- 예상 DrawCall: {N}
- 예상 VRAM: {N}GB / 48GB
- 예상 GPU 부하: {N}%

## FAIL/WARN 항목 — 아티스트 액션 아이템

| 우선순위 | 항목 | 담당 | 조치 사항 |
|---|---|---|---|
| P1 | (항목) | Art | (구체적 조치) |

## Optimazation 플러그인 권고 세팅

(UOptSetupProfile 기준 권고 CVar 목록)
```

### Step 5: DB 인제스트

```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{date}_{scene}_opt-review.md" \
  --project vp
```

## 주의사항

- FAIL 판정 시 `/shoot-gate`에 자동으로 NO-GO 반영됨
- Gemma4 위임 불가 — 최적화 판단은 정밀도 최우선
- Optimazation 플러그인 API 참조: vp-agent `plugins.md` → Optimazation 섹션
- 렌더 머신 사양 참조: vp-agent `vp-equipment.md` → Workstations 섹션
- `${vpo_plugin_root}` 미설정 시 플러그인 소스 탐색 스킵

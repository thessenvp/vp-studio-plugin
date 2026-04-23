---
name: asset-checklist
description: VP Supervisor quality gate — UE 에셋 네이밍 컨벤션 검증 + Perforce 제출 상태 확인. /shoot-gate 전제 조건 중 하나.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<ProjectPath> [--scene S##C##] [--validate-naming]"
---

# Asset Checklist — 에셋 상태 검수

에셋 네이밍 컨벤션 위반 및 Perforce 미제출 에셋 탐지. `/shoot-gate` GO 조건 중 하나.  
네이밍 위반이 P1 아이템이면 NO-GO.

## Arguments

- `<ProjectPath>` : UE 프로젝트 Content 경로 (예: `${perforce_workspace_root}\1_Project\Proj_FilmA\Content`)
- `--scene S##C##` : 특정 씬 관련 에셋만 검수 (선택)
- `--validate-naming` : 네이밍 컨벤션 전체 검증 실행

## Procedure

### Step 1: 에셋 목록 수집

```bash
# UE Content 경로에서 에셋 목록 수집
find "{ProjectPath}/00_Project" -name "*.uasset" -o -name "*.umap" 2>/dev/null | head -200

# 씬 지정 시 해당 씬 관련 에셋만
find "{ProjectPath}" -name "*{scene}*" -type f 2>/dev/null
```

### Step 2: 네이밍 컨벤션 검증

vp-agent 의 `asset-naming.md` rule 의 Prefix/Suffix 규칙 기준으로 검증. Gemma4 위임 가능 (네이밍 검증 로직).

#### 검증 항목

**Prefix 검증** — 파일명이 올바른 Prefix로 시작하는가:
| 에셋 타입 | 올바른 Prefix | 잘못된 예 |
|---|---|---|
| Static Mesh | `SM_` | `Mesh_`, `sm_`, prefix 없음 |
| Skeletal Mesh | `SK_` | `SkMesh_`, prefix 없음 |
| Blueprint | `BP_` | `Blueprint_`, `bp_` |
| Material | `M_` | `Mat_`, `Material_` |
| Texture (BC) | `T_` + `_BC` suffix | `Tex_`, `texture_` |

→ 전체 Prefix 목록: vp-agent 의 `asset-naming.md` rule

**케이스 검증** — PascalCase 적용:
```bash
# 소문자 시작, snake_case, 특수문자 포함 파일명 탐지
find "{ProjectPath}" -name "*.uasset" | grep -E "[a-z_][A-Za-z]|[^A-Za-z0-9_.]"
```

**금지 문자 검증**:
- 공백, 백슬래시, 특수문자 (`@`, `#`, `!`, `-` 등)

#### Gemma4 위임 (대량 검증 시)

10개 이상 에셋 네이밍 검증은 Gemma4에 위임:
→ gemma4로 네이밍 검증 위임

```bash
echo "다음 에셋 파일명 목록에서 asset-naming.md 규칙 위반 항목을 찾아라.
규칙: SM_, SK_, BP_, M_, T_, ABP_, PA_, IKR_, RTG_, FX_, FXS_, MI_, PPM_ 등 prefix 필수.
PascalCase 필수. 공백/특수문자 금지.
출력: 위반항목|이유|권장명 형식으로만.
---
{파일명 목록}" | powershell -NoProfile -ExecutionPolicy Bypass -File ${CLAUDE_PLUGIN_ROOT}/scripts/gemma.ps1
```

Gemma 결과를 검수 후 리포트에 반영.

### Step 3: Perforce 제출 상태 확인

```bash
# P4 미제출 파일 확인 (p4 명령 사용 가능한 경우)
p4 status "{ProjectPath}/..." 2>/dev/null | grep -v "^$"

# P4 없을 경우 최근 수정 파일 확인
find "{ProjectPath}" -name "*.uasset" -newer "{ProjectPath}/{ProjectName}.uproject" | head -50
```

확인 항목:
- [ ] 씬 관련 에셋 모두 Perforce에 제출(Submit) 완료
- [ ] Checked Out 상태 에셋 없음 (촬영 전 잠금 해제)
- [ ] Depot 경로 올바름: `${perforce_workspace_root}\1_Project\{ProjectName}\`

### Step 4: 우선순위 분류

발견된 위반 항목을 우선순위로 분류:

| 우선순위 | 기준 | 예시 |
|---|---|---|
| P1 | 촬영에 직접 사용되는 에셋의 네이밍 위반 | 주인공 SK_, 씬 레벨 |
| P2 | 씬 연관 에셋 위반 | 배경 SM_, 조명 BP_ |
| P3 | 씬 미사용 에셋 위반 | 미사용 텍스처 |

### Step 5: 보고서 생성

**경로:** `${sessions_root}/{DATE}_{scene}_asset-checklist.md` (씬 지정 시)  
또는 `${sessions_root}/{DATE}_asset-checklist.md` (전체)

```markdown
---
description: {DATE} 에셋 상태 검수 보고서
tags:
  - asset-checklist
  - asset-naming
category: session-records
---

# Asset Checklist — {DATE} ({scene})

## 판정: [PASS / WARN / FAIL]

판정 기준:
- PASS: 네이밍 위반 0건, P4 미제출 0건
- WARN: P3 위반만 존재 또는 비씬 에셋 미제출
- FAIL: P1 위반 존재 또는 씬 에셋 P4 미제출

---

## 네이밍 위반 목록

| 우선순위 | 현재 파일명 | 위반 내용 | 권장 파일명 |
|---|---|---|---|
| P1 | (파일명) | (위반 내용) | (권장명) |

총 위반: P1 {N}건 / P2 {N}건 / P3 {N}건

---

## Perforce 상태

| 상태 | 에셋 수 |
|---|---|
| 제출 완료 | {N} |
| 미제출 (pending) | {N} |
| Checked Out | {N} |

---

## 아티스트 액션 아이템

| 우선순위 | 담당 | 조치 사항 | 기한 |
|---|---|---|---|
| P1 | Art | 파일명 변경 후 P4 Submit | 촬영 전 |

---

## /shoot-gate 반영

네이밍 위반 P1 {N}건 → {GO / NO-GO}
```

### Step 6: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "<file>" --project vp
```

(앞 Step 의 파일/산출물은 이미 저장됐으므로 skill 은 정상 완료로 간주.)

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${sessions_root}/{DATE}_{scene}_asset-checklist.md" --project vp
```

### Step 7: 완료 메시지

```
📋 Asset Checklist 완료

판정: [PASS / WARN / FAIL]
  - 네이밍 위반: P1 {N}건 / P2 {N}건 / P3 {N}건
  - P4 미제출: {N}건

/shoot-gate 반영: GO / CONDITIONAL-GO / NO-GO
```

## 주의사항

- 네이밍 검증 로직 Gemma4 위임 가능 (대량 처리), 위반 우선순위 판단은 Claude 직접
- P4 명령 사용 불가 환경에서는 수동 확인 요청
- vp-agent 의 `asset-naming.md` rule 의 전체 Prefix 목록 참조 필수
- UE 프로젝트 구조: vp-agent 의 `unreal-engine.md` rule → UE Project Folder Structure 참조

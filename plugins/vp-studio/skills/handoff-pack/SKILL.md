---
name: handoff-pack
description: VP Supervisor — 포스트팀 데이터 인계 패키지 생성. /data-wrangle + /take-log + /brief-scene 결과를 통합해 VFX/편집팀 전달용 문서로 정리.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<SceneName> [--date YYYY-MM-DD]"
---

# Handoff Pack — 포스트팀 데이터 인계

씬 촬영 완료 후 VFX/편집/DI 팀에 전달하는 공식 인계 패키지.
**전제 조건:** `/data-wrangle` 완료 후 실행.

## Arguments

- `<SceneName>` : 씬 이름 (예: `FilmA_영웅추격씬`)
- `--date YYYY-MM-DD` : 촬영일 (기본: 오늘)
- `--scene S##C##` : 씬/컷 번호 (선택)

## Procedure

### Step 1: 소스 파일 수집

해당 씬의 모든 관련 파일 탐색 (Hub 경로는 userConfig):

```bash
# 세션 파일 전체 (metadata, takes, opt-review, color, shoot-gate, 마스터 브리핑)
find ${sessions_root} -name "*{SceneName}*" 2>/dev/null
find ${sessions_root} -name "*{date}*{scene}*" 2>/dev/null

# 부서별 브리핑 파일 (team-brief 출력 경로)
find ${briefings_root} -name "*{SceneName}*" 2>/dev/null

# MoCap 세션 파일
find ${mocap_sessions_root} -name "*{scene}*" 2>/dev/null
```

**파일 저장 경로 구분:**

| 스킬 | 저장 경로 | 파일 패턴 |
|---|---|---|
| `/brief-scene` (마스터 브리핑) | `${sessions_root}` | `{DATE}_{SceneName}_brief.md` |
| `/team-brief` (부서별 배포본) | `${briefings_root}` | `{team}_{SceneName}_brief.md` |

→ 탐색 시 두 경로를 모두 확인한다.

**필수 소스 파일:**

| 파일 | 경로 | 내용 | 필수 여부 |
|---|---|---|---|
| `*_metadata.md` + `*_metadata.json` | `${sessions_root}` | 테이크·TC·렌즈 메타데이터 | **필수** |
| `*_takes.md` | `${sessions_root}` | 테이크 로그 | **필수** |
| `{DATE}_{SceneName}_brief.md` | `${sessions_root}` | 씬 마스터 브리핑 | 권장 |
| `{team}_{SceneName}_brief.md` | `${briefings_root}` | 부서별 배포 브리핑 | 참고 |
| `*_opt-review.md` | `${sessions_root}` | 최적화 검수 | 권장 |
| `*_color*.md` | `${sessions_root}` | 컬러 파이프라인 검수 | 권장 |
| `*_shoot-gate.md` | `${sessions_root}` | GO/NO-GO 판정 기록 | 참고 |

metadata 파일이 없으면:
```
⚠️ metadata.json 없음 — /data-wrangle --scene {scene} 먼저 실행하세요.
```

### Step 2: 데이터 집계

**metadata.json** 에서:
- OK/NG/HOLD 테이크 목록
- 타임코드 범위
- 렌즈 정보
- UE 씬 구성
- OptiTrack .tak 파일 목록

**takes.md** 에서:
- HOLD 테이크 세부 내역 (포스트 판정 필요)
- NG 원인 집계 (VFX팀 참고용)

### Step 3: 핸드오프 패키지 생성

**경로:** `${sessions_root}/{date}_{SceneName}_handoff.md`

```markdown
---
description: {SceneName} 포스트팀 핸드오프 패키지 — {date}
tags:
  - handoff-pack
  - {SceneName}
category: session-records
---

# 핸드오프 패키지 — {SceneName}

**촬영일:** {date}
**작성자:** VP Supervisor
**전달 대상:** VFX팀 / 편집팀 / DI팀

---

## ✅ OK 테이크 목록 (사용 가능)

| 테이크 | 타임코드 | 비고 |
|---|---|---|
| T001 | {HH:MM:SS:FF} | |
| T003 | {HH:MM:SS:FF} | |

**OK 총 {N}컷**

---

## ⏸️ HOLD 테이크 (포스트 최종 판정 필요)

| 테이크 | 타임코드 | 보류 사유 | 판정 요청 |
|---|---|---|---|
| T002 | {HH:MM:SS:FF} | {사유} | VFX 확인 후 판정 |

**포스트팀 요청:** 위 HOLD 테이크를 검토 후 최종 OK/REJECT 판정 회신 요망.

---

## 📹 카메라 & 렌즈 정보

- **타임코드 소스:** Tentacle Sync E
- **TC 시작 (첫 OK):** {HH:MM:SS:FF}
- **TC 종료 (마지막 OK):** {HH:MM:SS:FF}
- **초점거리:** {N}mm
- **조리개:** f/{N}
- **프레임레이트:** {fps}fps

---

## 🎭 OptiTrack / MoCap 데이터

### .tak 파일 목록

| 파일명 | 캐릭터 | 테이크 | 비고 |
|---|---|---|---|
| {Project}_S##_C##_{Char}_001.tak | {Character} | T001 | OK |

**Motive 버전:** 3.4.0.2

---

## 🎨 컬러 레퍼런스

- **X-Rite ColorChecker 파일:** {Motive세션명}_colorref_001
- **컬러 파이프라인:** {ACES/sRGB BT.709}
- **LED 색역:** {BT.2020/P3/BT.709}
- **화이트밸런스:** {N}K

---

## 🌍 UE 씬 정보

- **사용 레벨:** {경로}
- **라이팅 프리셋:** {이름}
- **nDisplay 설정:** {NDC_파일명 또는 미사용}
- **UE 버전:** 5.7

---

## 📊 촬영 통계 (참고)

| 판정 | 수량 |
|---|---|
| OK | {N} |
| NG | {N} |
| HOLD | {N} |
| **합계** | **{N}** |

**NG 주요 원인:**
- tech {N}건 / art {N}건 / mocap {N}건

---

## 📁 첨부 파일 경로

| 파일 | 경로 |
|---|---|
| 메타데이터 JSON | `${sessions_root}/{date}_{scene}_metadata.json` |
| 테이크 로그 | `${sessions_root}/{date}_{scene}_takes.md` |
| 씬 마스터 브리핑 | `${sessions_root}/{date}_{SceneName}_brief.md` |
| Art 브리핑 | `${briefings_root}/art_{SceneName}_brief.md` |
| MoCap 브리핑 | `${briefings_root}/mocap_{SceneName}_brief.md` |
| Opt 검수 | `${sessions_root}/{date}_{scene}_opt-review.md` |
| 컬러 파이프라인 | `${sessions_root}/{date}_{scene}_color-pipeline.md` |

---

## 📌 포스트팀 주의사항

1. HOLD 테이크 판정 후 VP Supervisor에게 회신 요망
2. MoCap 리타겟팅 전 슈트 캘리브레이션 오프셋 확인 (mocap-brief 참조)
3. 컬러 레퍼런스 파일은 DI 파이프라인 첫 단계에 반드시 사용
4. 추가 문의: 이 문서의 작성자(VP Supervisor)에게 직접 연락
```

### Step 4: DB 인제스트

```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{date}_{SceneName}_handoff.md" \
  --project vp
```

### Step 5: 완료 출력

```
📬 핸드오프 패키지 생성 완료 — {SceneName}
   OK 테이크: {N}컷
   HOLD 테이크: {N}컷 (포스트 판정 필요)

   파일: ${sessions_root}/{date}_{SceneName}_handoff.md

   전달 절차:
   1. 위 파일을 포스트팀에 공유
   2. metadata.json 별도 전달 (자동화 파이프라인용)
   3. OptiTrack .tak 파일은 Perforce 경로 안내

   다음 단계:
   → /kpi-report --scene {scene}  (KPI 측정)
   → /supervisor-recap             (일일 감독 회고)
```

## 주의사항

- `/data-wrangle` 먼저 실행 필수 (metadata.json 없으면 실행 불가)
- HOLD 테이크는 절대 OK로 업그레이드하지 말 것 — 포스트팀 권한
- 렌즈 정보 없으면 N/A 기록 (추측 금지)
- metadata.json 은 포스트 자동화용 — 형식 수정 금지

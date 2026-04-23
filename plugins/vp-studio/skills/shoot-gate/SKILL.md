---
name: shoot-gate
description: VP Supervisor — Pillar B+C+D 스킬 결과 집계 → GO / NO-GO / CONDITIONAL-GO 최종 촬영 판정. 모든 품질 게이트의 종착점.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<SceneName> [--override-risk \"사유\"]"
---

# Shoot Gate — GO / NO-GO 최종 판정

VP Supervisor의 최종 결정 권한. Pillar B(품질) + C(팀 조율) + D(현장 운영) 전 결과를 집계.
**이 판정이 GO여야 촬영 시작 가능.**

## Arguments

- `<SceneName>` : 씬 식별자 (예: `FilmA_영웅추격씬`)
- `--override-risk "사유"` : CONDITIONAL-GO 강제 발동 (감독 판단, 사유 필수)

## Procedure

### Step 1: 전제 조건 파일 수집

당일 해당 씬 관련 검수 파일 자동 탐색:

```bash
# 오늘 날짜 기준 씬 관련 파일 검색 — ${sessions_root}, ${briefings_root}, ${mocap_sessions_root} 는 userConfig
find ${sessions_root} -name "*{TODAY}*{SceneName}*" 2>/dev/null
find ${sessions_root} -name "*{TODAY}*opt-review*" 2>/dev/null
find ${sessions_root} -name "*{TODAY}*color*" 2>/dev/null
find ${sessions_root} -name "*{TODAY}*asset-checklist*" 2>/dev/null
find ${briefings_root} -name "*{SceneName}*" 2>/dev/null
find ${mocap_sessions_root} -name "*{TODAY}*" 2>/dev/null
```

파일이 없는 항목은 "미실행"으로 표시.

### Step 2: 각 게이트 결과 확인

vp-agent `vp-supervisor.md` 의 GO/NO-GO 판정 기준 참조.

#### Gate B-1: Opt Review (Frame Rate KPI)
```bash
grep -h "판정:" ${sessions_root}/*{TODAY}*opt-review*.md 2>/dev/null | tail -1
```
- PASS → GO 허용
- WARN → CONDITIONAL-GO 검토
- FAIL → **NO-GO (즉시)**
- 미실행 → NO-GO

#### Gate B-2: Color Check (Visual Consistency KPI)
```bash
grep -h "판정:" ${sessions_root}/*{TODAY}*color*.md 2>/dev/null | tail -1
```
- PASS → GO 허용
- WARN → CONDITIONAL-GO 검토
- FAIL → **NO-GO (즉시)**
- 미실행 → NO-GO

#### Gate B-3: Asset Checklist
```bash
grep -h "판정:" ${sessions_root}/*{TODAY}*asset-checklist*.md 2>/dev/null | tail -1
```
- PASS → GO 허용
- WARN (P3 위반만) → CONDITIONAL-GO 가능
- FAIL (P1 위반 존재) → **NO-GO**
- 미실행 → WARN (운영 판단)

#### Gate C: 브리핑 배포 완료
```bash
find ${briefings_root} -name "*{SceneName}*" 2>/dev/null | wc -l
find ${mocap_sessions_root} -name "*{SceneName}*mocap-brief*" 2>/dev/null
```
- 모든 부서 브리핑 배포 완료 → GO
- 일부 누락 → WARN

#### Gate D: Sync Check (Efficiency KPI)
```bash
# sync-check은 콘솔 출력 — 유저에게 마지막 실행 결과 확인 요청
```
유저에게 직접 확인:
- PASS → GO 허용
- WARN → CONDITIONAL-GO 검토
- FAIL → **NO-GO (즉시)**
- 미실행 → NO-GO

### Step 3: 종합 판정

#### GO 조건 (전부 충족)
- `/opt-review` PASS
- `/color-check` PASS
- `/asset-checklist` PASS (P1 위반 0건)
- `/sync-check` PASS
- `/brief-scene` + 부서별 브리핑 배포 완료
- MoCap 캘리브레이션 완료 (있는 경우)

#### CONDITIONAL-GO 조건 (감독 판단)
- `/opt-review` WARN (FPS 마진 < 10%)
- 알려진 이슈 있으나 촬영 치명적이지 않음
- `--override-risk "사유"` 필수 기록

#### NO-GO 조건 (하나라도 해당)
- `/opt-review` FAIL
- Genlock/Timecode 체인 불완전 (`/sync-check` FAIL)
- P1 에셋 네이밍 위반 미해결
- MoCap 캘리브레이션 미완료 (있는 경우)
- 핵심 에셋 P4 미제출

### Step 4: 판정 결과 처리

#### GO 발동 시
```
🎬 SHOOT GATE: GO
   씬: {SceneName} | {DATE} {TIME}

   → /take-log 세션 초기화
   → 촬영 시작
```

`/take-log` 세션 자동 초기화 안내 (파일 생성은 첫 take-log 호출 시):

```bash
echo "take-log 세션 준비 완료. '/take-log T001 OK' 로 첫 테이크를 기록하세요."
```

#### CONDITIONAL-GO 발동 시
```
⚠️ SHOOT GATE: CONDITIONAL-GO
   씬: {SceneName} | {DATE} {TIME}
   오버라이드 사유: {사유}

   미해결 리스크:
   - (항목): (상태) → (허용 사유)

   → 촬영 시작 허용, 해당 리스크 모니터링 강화
```

#### NO-GO 발동 시
```
🚫 SHOOT GATE: NO-GO
   씬: {SceneName} | {DATE} {TIME}

   블로커 항목:
```

NO-GO 시 블로커 담당 액션 아이템 자동 생성:

| 항목 | 현재 상태 | 담당 | 해결 조치 | 기한 |
|---|---|---|---|---|
| (게이트명) | (상태) | (부서) | (구체적 조치) | 재검수 전 |

### Step 4.5: Telegram Notify (모든 판정 결과)

**사전 조건**: Plugin 번들 notify CLI 호출 가능 여부. 다음 중 하나라도 충족 안 되면 이 Step 을 스킵:
- `userConfig.notify_channels` 가 비어있거나 `"telegram"` 미포함
- Project 에 `~/.openclaw/openclaw.json` 또는 `$TELEGRAM_BOT_TOKEN` 미설정
- Project 에 `notify.yaml` 없고 chat_ids 미설정

스킵 시 유저에게 한 줄 알림: `⚠️ Telegram notify 스킵 — notify.yaml 또는 token 미설정`.

판정 기록 파일 저장(Step 5)은 무조건 진행.

Step 4 판정 직후, 결과에 따른 severity 로 Telegram 푸시. Plugin 번들 notify CLI 사용.

| 판정 | severity | 이모지(제목) |
|---|---|---|
| GO | `info` | ✅ |
| CONDITIONAL-GO | `warn` | ⚠️ |
| NO-GO | `critical` | 🚫 |

```bash
case "$VERDICT" in
  GO)             SEV=info     ; ICON="✅" ;;
  "CONDITIONAL-GO") SEV=warn   ; ICON="⚠️" ;;
  NO-GO)          SEV=critical ; ICON="🚫" ;;
esac

${hub_cli_python} ${CLAUDE_PLUGIN_ROOT}/scripts/notify/cli.py send \
  --event SHOOT_GATE \
  --severity "$SEV" \
  --title "${ICON} ${VERDICT}: ${SceneName}" \
  --body "$(printf '게이트 결과:\n- Opt Review: %s\n- Color Check: %s\n- Asset Checklist: %s\n- Sync Check: %s\n\n블로커: %s\n오버라이드: %s' "$OPT" "$COLOR" "$ASSET" "$SYNC" "${BLOCKERS:-없음}" "${OVERRIDE:-없음}")"
```

- 실패해도 Step 5 판정 기록 파일 저장은 계속 진행
- 동일 씬 60초 내 재판정은 throttle 로 자동 skip
- NO-GO 는 critical severity 라 chat_id 별 severity_map 설정 시 우선 수신
- notify CLI 설정이 없으면 이 스텝은 graceful skip (notify.yaml 미존재 or token 부재)

### Step 5: 판정 기록 파일 저장

**경로:** `${sessions_root}/{DATE}_{SceneName}_shoot-gate.md`

```markdown
---
description: {SceneName} Shoot Gate 판정 기록
tags:
  - shoot-gate
  - {판정결과}
  - {SceneName}
category: session-records
---

# Shoot Gate — {SceneName} ({DATE})

## 최종 판정: [GO / CONDITIONAL-GO / NO-GO]

**판정 시각:** {TIME}
**VP Supervisor 서명:** ___________________

---

## 게이트 결과 집계

| 게이트 | 스킬 | 결과 | 파일 |
|---|---|---|---|
| Frame Rate | /opt-review | PASS/WARN/FAIL/미실행 | (파일명) |
| Visual Consistency | /color-check | PASS/WARN/FAIL/미실행 | (파일명) |
| 에셋 상태 | /asset-checklist | PASS/WARN/FAIL/미실행 | (파일명) |
| 동기화 체인 | /sync-check | PASS/WARN/FAIL/미실행 | (확인) |
| 브리핑 배포 | /brief-scene + team-brief | 완료/미완료 | (파일명) |
| MoCap 캘리브레이션 | (확인) | 완료/미완료/해당없음 | — |

---

## 블로커 항목 (NO-GO / CONDITIONAL-GO 시)

| 항목 | 담당 | 조치 | 완료 여부 |
|---|---|---|---|

---

## CONDITIONAL-GO 오버라이드 (해당 시)

- **오버라이드 사유:** {사유}
- **허용 리스크:** (항목)
- **모니터링 강화:** (방법)

---

## 촬영 이후

GO 후 진행 스킬:
- `/take-log T001 ...` — 실시간 테이크 기록
- `/risk-flag` — 긴급 상황 발생 시
- `/data-wrangle` — 씬 완료 후
```

### Step 6: DB 인제스트

**사전 조건**: userConfig `hub_cli_doc_manager` 가 설정되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ DB ingest 스킵 — hub_cli_doc_manager userConfig 미설정.
  수동 등록: python <project-doc_manager-cli> ingest --file "${sessions_root}/{DATE}_{SceneName}_shoot-gate.md" --project vp
```

판정 기록 파일(Step 5)은 이미 저장됐으므로 skill 은 정상 완료.

설정되어 있으면 실행:
```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest \
  --file "${sessions_root}/{DATE}_{SceneName}_shoot-gate.md" \
  --project vp
```

## 주의사항

- CONDITIONAL-GO는 VP Supervisor 단독 결정 가능 (vp-agent `vp-supervisor.md` 감독 권한 참조)
- NO-GO 후 블로커 해결 완료 시 `/shoot-gate`를 다시 실행해 GO 확인
- 오버라이드 사유는 반드시 구체적으로 기록 (감사 추적)
- 게이트 파일이 당일 날짜 기준으로 없으면 "미실행"으로 처리 — 재실행 요청
- vp-agent `vp-supervisor.md` 의 GO/NO-GO 판정 기준이 이 스킬의 SSOT

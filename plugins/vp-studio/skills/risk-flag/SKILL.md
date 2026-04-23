---
name: risk-flag
description: VP Supervisor — 현장 긴급 상황 즉각 대응. /risk-scenario 플레이북 자동 참조, takes.md RISK 섹션 추가, 즉각 조치 안내.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "<RiskType> [--severity critical|high|medium] [--system genlock|fps|mocap|led|network|ue]"
---

# Risk Flag — 현장 긴급 상황 대응

현장 긴급 상황 즉각 대응. 사전 설계된 `/risk-scenario` 플레이북을 자동 참조해 즉각 조치를 제시.  
**5초 이내 응답** — 복잡한 분석보다 즉각 조치 우선.

## Arguments

- `<RiskType>` : 리스크 유형 (아래 분류 참조)
- `--severity critical|high|medium` : 심각도 (기본: high)
- `--system` : 관련 시스템 (빠른 플레이북 조회용)

## RiskType 분류

| RiskType | 설명 | 기본 Severity |
|---|---|---|
| `genlock` | Genlock/동기화 체인 실패 | critical |
| `fps` | FPS 드랍 (목표의 70% 이하) | critical |
| `mocap` | MoCap 트래킹 실패 | high |
| `led` | LED 패널 불량 | high |
| `network` | 네트워크/LiveLink 지연 | medium |
| `ue` | UE 에디터 크래시/불안정 | critical |
| `tc` | 타임코드 드리프트 | high |
| `asset` | 현장 에셋 팝핑/스트리밍 실패 | medium |

## Procedure

### Step 1: 즉각 조치 출력 (< 5초)

vp-agent 의 `shoot-protocol.md` rule 의 리스크 대응 매트릭스를 즉시 참조해 콘솔에 출력:

```
🚨 RISK FLAG — {RiskType} [{SEVERITY}]
시각: {TIME}

즉각 조치:
1. {가장 먼저 할 일}
2. {두 번째}
3. {세 번째}

P1 블로커 판정: [YES / NO]
```

### Step 2: 플레이북 파일 조회

사전 설계된 risk-scenario 플레이북 탐색:

```bash
find ${risk_playbooks_root} -name "*{system}*" 2>/dev/null
find ${risk_playbooks_root} -name "*{risktype}*" 2>/dev/null
```

파일이 있으면:
```
📋 플레이북 참조: ${risk_playbooks_root}/{system}_scenario.md
   단기 조치 (< 30분): {플레이북에서 발췌}
   촬영 중단 기준: {플레이북에서 발췌}
```

파일이 없으면:
```
⚠️ 사전 플레이북 없음 — /risk-scenario --equipment {system} 실행 권장 (사후)
```

### Step 3: P1 블로커 판정

vp-agent 의 `shoot-protocol.md` rule P1 블로커 기준 적용:

**즉시 촬영 중단 조건:**
- genlock/timecode 체인 완전 실패
- FPS 목표의 50% 이하 드랍 (24fps → 12fps 이하)
- LED 패널 1/4 이상 불량
- MoCap 카메라 3대 이상 동시 실패
- UE 에디터 크래시

P1 블로커 해당 시:
```
🛑 P1 블로커 감지 — 촬영 즉시 중단 권고
   /shoot-gate 재실행 필요 (해결 후)
```

### Step 3.5: Telegram Notify (P1 블로커 시에만)

**사전 조건**: userConfig `notify_channels` 가 설정되고 토큰이 구성되어 있어야 함.

미설정이거나 빈 값이면 이 Step 을 스킵하고 유저에게 한 줄로 알림:
```
⚠️ Notify 스킵 — notify_channels userConfig 미설정 (또는 토큰 없음).
  콘솔 출력으로만 진행합니다.
```

(takes.md 기록 Step 4는 계속 진행.)

설정되어 있으면 — 심각도가 `critical` 이거나 Step 3 에서 **P1 블로커 판정** 된 경우에만 즉시 Telegram 푸시:

```bash
# SEVERITY=critical 또는 P1_BLOCKER=YES 인 경우만 실행
${hub_cli_python} ${CLAUDE_PLUGIN_ROOT}/scripts/notify/cli.py send \
  --event RISK_P1 \
  --severity critical \
  --title "{RiskType} — {System}" \
  --body "$(printf '심각도: %s\nP1 블로커: %s\n\n즉각 조치:\n1. %s\n2. %s\n3. %s' "$SEVERITY" "$P1_BLOCKER" "$조치1" "$조치2" "$조치3")"
```

- `severity=high|medium` 은 푸시 생략 (본인 콘솔 출력으로 충분)
- 실패해도 takes.md 기록(Step 4)은 계속 진행 — notify 오류 무시
- 동일 RiskType 60초 내 중복 호출은 throttle 로 자동 skip

### Step 4: takes.md RISK 섹션 추가

현재 활성 씬의 takes.md 파일을 찾아 RISK 섹션 추가:

```bash
find ${sessions_root} -name "*takes*" -newer /dev/null 2>/dev/null | sort -r | head -1
```

해당 파일에 추가:

```markdown
## ⚠️ RISK FLAG — {TIME}

- **유형:** {RiskType}
- **심각도:** {SEVERITY}
- **P1 블로커:** {YES/NO}
- **즉각 조치:**
  1. {조치1}
  2. {조치2}
- **플레이북:** {경로 또는 "없음"}
- **해결 여부:** 미결
```

### Step 5: 해결 안내

```
다음 단계:
- 해결 완료 시: /risk-flag {risktype} resolved --note "{해결 방법}" 입력
- P1 블로커 시: /shoot-gate {SceneName} 재실행 (해결 확인 후)
- 플레이북 없을 때: /risk-scenario --equipment {system} (촬영 종료 후)
```

## RISK FLAG RESOLVED 처리

`/risk-flag {risktype} resolved --note "해결 방법"` 호출 시:

takes.md RISK 섹션의 **해결 여부** 를 업데이트:

```markdown
- **해결 여부:** ✅ 해결 — {TIME} — {해결 방법}
```

그리고 콘솔 출력:

```
✅ RISK FLAG 해결 — {RiskType}
   해결 시각: {TIME}
   다운타임: {FLAG_TIME ~ 해결_TIME} 분
   → /kpi-report 에 Efficiency 데이터로 반영됩니다.
```

## 주의사항

- P1 블로커 판정은 VP Supervisor 단독 권한 (vp-agent 의 `vp-supervisor.md` rule 참조)
- CONDITIONAL-GO 취소 시 `/shoot-gate` 재실행 필요
- 플레이북 없으면 현장 즉흥 대응 후 반드시 /risk-scenario 로 사후 기록
- 참조: vp-agent 의 `shoot-protocol.md` rule (P1/P2/P3 블로커 기준 + 리스크 대응 매트릭스)

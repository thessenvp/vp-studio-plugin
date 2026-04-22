---
name: sync-check
description: VP Supervisor — SPG 8000 → eSync → Tentacle → Lockit → UE 전 동기화 체인 검증. Efficiency KPI 직결. /shoot-gate 전제 조건.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[--fps 24] [--mode shooting|previz]"
---

# Sync Check — 동기화 체인 검증

VP Supervisor의 Efficiency KPI 직결. 전 장비 동기화 실패는 `/shoot-gate` NO-GO.
**현장에서 고치자 불가능** — 촬영 시작 전 이 체인이 완전해야 한다.

## Arguments

- `--fps 24|30|60` : 목표 프레임레이트 (기본: 24fps)
- `--mode shooting|previz` : 촬영 모드 (기본: shooting)

## Sync Chain 구조

```
SPG 8000 (마스터)
  └→ Blacktrax eSync (Genlock 분배)
       ├→ Tentacle Sync E (타임코드 수신 → 배포)
       │    └→ Ambient Lockit x4 (무선 TC → 카메라/MoCap)
       └→ UE Optimazation Plugin
            ├→ FOptGenlockMonitor (Genlock 상태 감시)
            ├→ FOptTimecodeMonitor (타임코드 상태 감시)
            └→ FOptLiveLinkMonitor (LiveLink 연결 감시)
```

## Procedure

### Step 1: 체인 순서대로 상태 확인

유저에게 다음 항목을 순서대로 확인 요청:

#### 1-1. SPG 8000 (마스터 소스)
- [ ] SPG 8000 전원 ON / 신호 출력 중
- [ ] 출력 신호: HD tri-level sync (HD 프로젝트) 또는 SD bi-level sync
- [ ] Lock 상태: 내부 레퍼런스 또는 외부 GPS 동기화
- [ ] 프레임레이트 설정: `{fps}fps` 와 일치

#### 1-2. Blacktrax eSync (Genlock 분배)
- [ ] eSync Genlock 입력: SPG 8000 신호 Lock
- [ ] eSync → UE 출력 신호 정상
- [ ] eSync → Tentacle Sync E 출력 정상

#### 1-3. Tentacle Sync E (타임코드)
- [ ] Tentacle Sync E 타임코드 수신: eSync로부터 Lock
- [ ] TC 프레임레이트: `{fps}fps` 와 일치
- [ ] Tentacle → Ambient Lockit 무선 배포 정상
- [ ] Tentacle Sync App에서 TC 흐름 확인

#### 1-4. Ambient Lockit x4 (무선 TC 분배)
- [ ] Lockit #1~#4 TC 수신 상태 (배터리 잔량 확인)
- [ ] 카메라 장착 Lockit TC 슬레이트 화면 확인
- [ ] MoCap 장착 Lockit TC 확인

#### 1-5. UE Optimazation Plugin 모니터
UE 에디터에서 Optimazation 플러그인 열어 상태 확인:
- [ ] `FOptGenlockMonitor` 상태: **GREEN** (Locked)
- [ ] `FOptTimecodeMonitor` 상태: **GREEN** (Receiving TC)
- [ ] `FOptLiveLinkMonitor` 상태: **GREEN** (All sources connected)
- [ ] 현재 엔진 프레임레이트: `{fps}fps` ±1 이내

### Step 2: 판정

각 체크 결과를 수집해 판정:

| 판정 | 조건 |
|---|---|
| **PASS** | 전 항목 GREEN |
| **WARN** | 비치명적 항목 1~2개 미확인 (배터리 경고 등) |
| **FAIL** | Genlock 또는 Timecode 체인 중 하나라도 실패 |

### Step 3: 실패 항목 자동 트러블슈팅

FAIL/WARN 항목이 있으면 Project의 doc_manager CLI 를 통해 관련 문서 자동 검색 (Hub CLI Contract 경유):

```bash
{userConfig.hub_cli_python} {userConfig.hub_cli_doc_manager} search "{실패 항목 키워드}" --project vp
```

userConfig 변수가 설정되어 있지 않거나 CLI 가 없으면 이 Step 을 스킵하고 사용자에게 한 줄로 알림:
`→ hub_cli.doc_manager 미설정 — 자동 검색 생략`

검색 결과에서 관련 트러블슈팅 문서 링크 제시.

### Step 4: 결과 출력 (콘솔)

파일 저장 없이 콘솔 출력이 기본:

```
🔗 Sync Check 결과 — {DATE} {TIME}
모드: {mode} / 목표 FPS: {fps}fps

SPG 8000        ✅ / ⚠️ / ❌
eSync           ✅ / ⚠️ / ❌
Tentacle Sync E ✅ / ⚠️ / ❌
Ambient Lockit  ✅ / ⚠️ / ❌  (배터리: {N}%)
UE Genlock Mon  ✅ / ⚠️ / ❌
UE TC Monitor   ✅ / ⚠️ / ❌
UE LiveLink Mon ✅ / ⚠️ / ❌

판정: [PASS / WARN / FAIL]

FAIL 항목:
  ❌ {항목}: {원인} → 관련 문서: {링크}

/shoot-gate 반영: GO / CONDITIONAL-GO / NO-GO
```

### Step 5: FAIL 시 `/risk-flag` 연동

Genlock 또는 Timecode FAIL 시 즉시 안내:

```
🚨 P1 블로커 감지 — /risk-flag genlock --severity critical 실행을 권장합니다.
```

## 주의사항

- Previz 모드는 Genlock 요구사항 완화 (Tentacle/Lockit 없어도 WARN 처리)
- Shooting 모드는 전 체인 완전 필수 — 하나라도 FAIL이면 무조건 NO-GO
- 장비 사양 참조: vp-agent 의 `vp-equipment.md` rule
- UE 플러그인 API 참조: vp-agent 의 `plugins.md` rule → Optimazation 섹션
- vp-agent 의 `shoot-protocol.md` rule 의 P1 블로커 기준 참조

## Plugin 의존성 (userConfig)

이 skill 은 다음 userConfig 필드를 사용:

- `hub_cli_python` (기본: `python`) — Python 실행파일
- `hub_cli_doc_manager` (기본: Project 의 `doc_manager/cli.py` 경로) — 문서 검색 CLI

양쪽 미설정 시 Step 3 만 스킵. 나머지 Step 은 설정 무관하게 동작.

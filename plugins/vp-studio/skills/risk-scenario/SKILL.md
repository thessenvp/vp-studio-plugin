---
name: risk-scenario
description: VP Supervisor — 장비 장애 복구 플레이북 설계. 촬영 전 사전 시나리오 수립, 즉각·단기 조치 및 대안 연출 방안 포함.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[--equipment sync|mocap|ue|led|network]"
---

# Risk Scenario — 장비 장애 복구 플레이북

VP Supervisor의 핵심 사전 업무: "장비가 터졌을 때" 복구 플레이북 설계.  
**현장 긴급 상황 시 `/risk-flag`가 이 플레이북을 자동 참조한다.**

## Arguments

- `--equipment` : 대상 장비 시스템
  - `sync` : SPG 8000 / eSync / Genlock / Timecode 체인
  - `mocap` : OptiTrack 카메라 / Motive 소프트웨어
  - `ue` : Unreal Engine / Optimazation 플러그인
  - `led` : LED 월 패널 / nDisplay
  - `network` : 네트워크 스위치 / LiveLink 통신

인자 없이 실행 시 전체 5개 플레이북 순차 생성.

## Procedure

### Step 1: 기존 플레이북 확인

```bash
find ${risk_playbooks_root} -name "*.md" 2>/dev/null
ls ${risk_playbooks_root}/ 2>/dev/null || echo "경로 없음 — 생성 필요"
```

경로가 없으면 먼저 생성:
```bash
mkdir -p ${risk_playbooks_root}
```

### Step 2: 현장 장비 정보 참조

참조 순서 (vp-agent rules):
1. `vp-equipment.md` — 동기화 체인, 장비 사양
2. `optitrack.md` — MoCap 장비 스펙
3. `plugins.md` — UE 플러그인 API (Optimazation 섹션)
4. `unreal-engine.md` — UE 설정

### Step 3: 플레이북 생성

**경로:** `${risk_playbooks_root}/{equipment}_scenario.md`

각 장비별 플레이북 템플릿:

```markdown
---
description: {equipment} 장애 복구 플레이북
tags:
  - risk-playbook
  - {equipment}
category: pipeline-docs
---

# {Equipment} 장애 복구 플레이북

**최종 작성:** {DATE}  
**작성:** VP Supervisor  
**리스크 레벨:** P1 (즉각 중단) / P2 (씬 보류) 기준 → vp-agent 의 `shoot-protocol.md` rule 참조

---

## 증상 식별 체크리스트

> 이 증상이 보이면 이 플레이북 실행

- [ ] 증상 1: (구체적 시각적/수치적 증상)
- [ ] 증상 2:
- [ ] 증상 3:

---

## 즉각 조치 (< 5분)

> VP Supervisor가 직접 또는 지시하여 5분 내 처리

1. (1단계 조치)
2. (2단계 조치)
3. (3단계 조치)

---

## 단기 조치 (< 30분)

> 즉각 조치로 해결 안 될 경우

1. (조치 내용)
2. (조치 내용)

**필요 인원:** (담당 부서)

---

## 촬영 중단 판단 기준

다음 조건 중 하나라도 해당하면 즉시 촬영 중단:
- (중단 기준 1)
- (중단 기준 2)

---

## 대안 연출 방안

> 기술 한계로 원래 씬 불가 시 감독과 협의할 대안

| 시나리오 | 대안 | VP Supervisor 판단 |
|---|---|---|
| (장애 시나리오) | (대안 연출) | (가능 여부) |

---

## 관련 링크

- 장비 매뉴얼: (경로 또는 URL)
- 과거 유사 트러블슈팅: `/search-docs {키워드}`
```

### Step 4: 장비별 세부 내용 작성

Gemma4 불가 — 기술 판단 정확도 최우선. Claude가 직접 작성.

#### sync (Genlock/TC 체인)
- 증상: FOptGenlockMonitor 레드, TC 드리프트
- 즉각: SPG 8000 출력 확인, eSync 재부팅 절차
- 중단 기준: Genlock 10분 내 복구 불가
- 대안: Free Run TC 전환 (편집 비용 증가 감수)

#### mocap (OptiTrack)
- 증상: Motive 카메라 오프라인, 마커 인식 불가
- 즉각: 카메라 재부팅, 캘리브레이션 재실행
- 중단 기준: PrimeX 카메라 3대 이상 동시 실패
- 대안: 배우 수 축소, 단독 촬영으로 전환

#### ue (Unreal Engine)
- 증상: UE 에디터 크래시, 플러그인 비활성화
- 즉각: UE 재시작, 플러그인 강제 활성화
- 중단 기준: 재시작 후에도 크래시 반복
- 대안: Previz 모드 전환, 단순 레벨로 대체

#### led (LED 월)
- 증상: 패널 블랙아웃, 색감 이상, nDisplay 연결 실패
- 즉각: nDisplay 재연결, 패널 전원 사이클
- 중단 기준: 씬 구도에 영향 주는 1/4 이상 불량
- 대안: 정적 LED 콘텐츠로 대체, 구도 조정

#### network (네트워크)
- 증상: LiveLink 레이턴시 > 50ms, 패킷 드랍
- 즉각: 스위치 재부팅, 불필요 트래픽 차단
- 중단 기준: LiveLink 완전 단절 5분 이상
- 대안: 유선 직결, VCam 없이 고정 카메라 전환

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
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "${risk_playbooks_root}/{equipment}_scenario.md" --project vp
```

### Step 6: 완료 메시지

```
🛡️ 리스크 플레이북 생성 완료

파일: ${risk_playbooks_root}/{equipment}_scenario.md

현장 긴급 상황 시:
  /risk-flag {equipment} --severity critical
  → 이 플레이북 자동 참조됩니다.
```

## 주의사항

- Gemma4 위임 불가 — 기술 판단이 잘못되면 현장 대응 실패로 직결
- 장비 교체·추가 시 해당 플레이북 업데이트 필수
- 대안 연출 방안은 반드시 감독/PD와 사전 합의 필요 항목 표시
- 과거 트러블슈팅 문서 참조: `/search-docs {장비명}` 으로 먼저 확인

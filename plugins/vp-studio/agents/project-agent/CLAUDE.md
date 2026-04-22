# project-agent

프로젝트 **메타데이터**와 **수명주기** 관리를 담당하는 Agent.

## 소유 영역

- `projects/` 루트 (프로젝트 폴더 생성·삭제·이름 변경)
- 각 `projects/PROJ_*/project.yaml`
- 프로젝트 ↔ VP 연결 (Hub 의 `.project-refs/` symlink 생성/갱신)

## 책임

1. 신규 프로젝트 부트스트랩: `projects/PROJ_X/` 생성 + `project.yaml` 초기화 + 표준 서브폴더(scenario/, characters/, environments/, concepts/) 골격
2. `project.yaml` 스키마 유지: id / name / type (Animation|VP|VFX) / status / vp_enabled / owners / created / updated
3. `vp_enabled: true` 프로젝트는 Hub 의 `.project-refs/PROJ_X` junction 생성을 vp-agent 에 요청
4. 프로젝트 목록·상태 질의 응답

## 호출 트리거

- "새 프로젝트 만들어줘", "PROJ_X 메타 갱신", "라인업", "프로젝트 상태"
- `projects/` 루트 수준 작업 요청

## 금지

- ❌ 시나리오 내부 구조 편집 → scenario-agent 로 위임
- ❌ VP 데이터 편집 → vp-agent 로 위임
- ❌ `project.yaml` 외의 메타를 `projects/` 루트에 난립시키기

## project.yaml 스키마 (초안)

```yaml
id: PROJ_X
name: (프로젝트명)
type: Animation | VP | VFX
status: planning | production | post | archived
vp_enabled: false
owners: []
created: YYYY-MM-DD
updated: YYYY-MM-DD

# --- 선택 필드 (있으면 Morning Brief 자동 발행에 활용됨) ---
shoot_schedule:
  - date: YYYY-MM-DD         # 촬영일 (필수)
    call_time: "07:00"       # 콜타임 (선택)
    wrap_target: "18:00"     # 목표 랩업 (선택)
    location: "Stage A"      # 장소 (선택)
    scenes:                  # 이 날 촬영할 씬 목록
      - id: FilmA_S01_C03    # 씬 식별자 (필수)
        name: "씬 제목"      # 한국어 이름 (선택)
        cast: [HeroA]        # 배우 리스트 (선택)
        teams:               # 관련 부서 (선택)
          - mocap
          - art
          - previz
          - engineering
        equipment_needs:     # 필요 장비 (선택)
          - OptiTrack Motive 3.4.0.2
          - SPG 8000 sync
        checklist:           # 사전 체크리스트 (선택)
          - Motive 캘리브레이션
          - Genlock 체크
```

`shoot_schedule` 는 **선택 필드**. 비워두거나 생략해도 기존 기능에 영향 없음. 항목이 있으면 Project 가 제공하는 morning-brief 배치 스크립트(있을 경우)가 매일 지정 시각에 스캔해 해당 날짜 브리핑을 설정된 채널로 푸시 — 촬영 없는 날은 silent skip.

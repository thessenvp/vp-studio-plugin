# `projects/` Ownership Matrix

Hub 안의 `projects/` 디렉토리는 프로젝트 단위 SSOT 메타데이터 저장소. 여러 agent 가 접근하므로 쓰기 권한을 명시.

## 경로 가정

Hub 기준: `${CLAUDE_PROJECT_DIR}/projects/{PROJ}/`

각 프로젝트는:
```
projects/{PROJ}/
├── project.yaml           # 프로젝트 메타데이터 (id, schema_version, ...)
├── scenarios/             # 시나리오·아크·시퀀스·씬
│   ├── arcs/
│   ├── sequences/
│   └── beats/
├── characters/            # 캐릭터 시트
├── environments/          # 환경 설정
├── concepts/              # 콘셉트 이미지·참조
└── vp/                    # VP 전용 서브트리 (해당 시)
    └── ...
```

## Agent별 권한

| Agent | 쓰기 | 읽기 | 비고 |
|---|---|---|---|
| **project-agent** | `project.yaml`, 루트 메타 파일 | 전체 | 프로젝트 생성·메타 변경의 유일한 쓰기 책임자 |
| **scenario-agent** | `scenarios/**` 하위 전체 | 전체 | arc·sequence·scene·beat 구조 관리 |
| **vp-agent** | ❌ **쓰기 금지** | `vp/` 서브트리만 (symlink 경유) | Hub 의 `vp/.project-refs/{PROJ}` 심볼릭으로만 접근 |
| **기타 agent** | 명시되지 않은 쓰기 금지 | 필요 시 읽기 | 새 agent 추가 시 이 문서 갱신 필수 |

## 충돌 방지 원칙

1. **project-agent 가 `project.yaml` 의 스키마 핵심 필드** (`id`, `schema_version`) 를 **유일하게** 관리. 다른 agent 가 수정 시도 시 project-agent 로 라우팅.
2. **scenario-agent 는 `scenarios/**` 밖을 쓰지 않는다.** 시나리오에서 캐릭터 필드가 필요하면 project-agent 에 요청.
3. **vp-agent 는 `vp/.project-refs/{PROJ}` 읽기만.** VP 데이터를 프로젝트에 쓰고 싶다면 `vp/` Hub 영역(심볼릭 원본) 에만 쓰고 project 쪽은 심볼릭으로 비추기.
4. **동시 수정 방지**: 한 파일을 여러 agent 가 같은 세션에서 쓰려 하면 순차 처리. 메인 Claude 가 중재.

## 새 agent 추가 시 절차

1. 해당 agent 의 `agents/<name>/CLAUDE.md` 에 `projects/` 권한 명시
2. 이 매트릭스 표에 행 추가
3. 권한 충돌이 기존 agent 와 있으면 스코프 조정 (예: 하위 디렉토리 한정)

## Hub symlink 정책 (vp-agent 전용)

`vp/.project-refs/{PROJ}` → `projects/{PROJ}/vp/` symlink.

- vp-agent 는 이 심볼릭을 **읽기 전용** 으로 사용.
- symlink 유지 책임은 **project-agent**. 프로젝트 생성·삭제 시 symlink 갱신.
- symlink 끊김 시 vp-agent 는 작업 중단 + project-agent 위임.

## 읽기 전용 영역 (Claude 전체)

- `vp/sessions/quick-notes.md` — 유저 직접 소유 (CLAUDE.md 에 명시)
- `_archive/` — 히스토리 참고 전용

Plugin skill 은 userConfig `hub_read_only_paths` (comma-separated glob) 로 이 영역을 인지. 해당 경로 쓰기 시도는 자동 차단 권장.

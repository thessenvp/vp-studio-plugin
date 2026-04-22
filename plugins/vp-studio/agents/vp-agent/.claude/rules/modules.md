# Code Module Library

## 원칙

검증된 코드를 모듈로 저장하고, 동일/유사한 작업 시 재사용한다. "작성 전 재사용 확인" 은 VP 스튜디오 공용 원칙.

## 위치

**Project 가 모듈 루트를 제공**한다. Plugin 은 구체 경로를 하드코딩하지 않음.

- Project 는 자기 repo 에 `modules/` 루트를 두고, Claude Code 가 이를 인지하도록 userConfig 또는 Project 자체 문서에서 경로를 알림.
- Plugin skill 이나 rule 이 모듈을 참조할 때는 "Project 의 modules 디렉토리에서 찾는다" 수준의 추상 지시만 사용.

VP-Studio 에서는 전통적으로 `vp/modules/` 를 사용했으나, 새 폴더 구조 도입 시 `tools/modules/` 또는 `modules/` 루트로 이전될 수 있음. **구체 경로는 Project CLAUDE.md 에서 선언**.

## 권장 도메인 분할

모듈은 도메인별 서브디렉토리로 정리. 예시:

```
{modules_root}/
├── unreal/          # UE Python Editor Scripting 모듈
├── mcp/             # MCP 서버/클라이언트 모듈
├── optitrack/       # OptiTrack/Motive 자동화 모듈
├── perforce/        # Perforce 워크플로우 모듈
├── pipeline/        # 파이프라인 유틸리티 모듈
└── utils/           # 범용 유틸리티 모듈
```

도메인 수·이름은 Project 재량. 위는 VP 일반 권장사항.

## 모듈 구조

각 모듈은 **하나의 폴더**로 구성:

```
{modules_root}/{domain}/{module_name}/
├── module.md        # 메타데이터 (필수)
├── {module_name}.py # 메인 코드 (필수)
└── ...              # 추가 파일 (선택)
```

## module.md 형식

```markdown
---
description: (한줄 설명)
tags:
  - (관련 태그)
category: code-modules
domain: (unreal | mcp | optitrack | perforce | pipeline | utils)
language: (python | cpp | blueprint)
dependencies:
  - (필요 패키지/모듈)
ue_compatible: (true | false)
---

# 모듈명

## 용도
(언제, 왜 이 모듈을 사용하는지)

## 사용법
(import 방법, 함수 호출 예시)

## API
(주요 함수/클래스 시그니처)

## 사용 이력
(어디서 사용했는지 기록)
```

## 모듈 작성 규칙

1. **단일 책임** — 모듈 하나는 한 가지 작업만 수행
2. **독립 실행 가능** — 다른 모듈에 의존하지 않도록 (utils 공용 모듈 제외)
3. **`if __name__ == "__main__":` 가드** 필수 — 단독 테스트 가능하도록
4. **코드 주석 한국어** — [development.md](development.md) 규칙 준수
5. **UE 호환** — `ue_compatible: true` 모듈은 `import unreal` 환경에서 실행 가능해야 함

## Claude 사용 규칙

### 코드 작성 전

1. `/search-docs` 또는 `search_docs` MCP tool 로 관련 모듈 검색
2. Project 의 modules 디렉토리에서 유사 모듈 확인
3. **기존 모듈이 있으면 재사용** — 새로 작성하지 않음

### 모듈 등록 시점

다음 조건을 **모두** 만족하면 모듈로 등록:
- 재사용 가능성이 있는 독립적 기능
- 2회 이상 사용되었거나 될 것으로 예상
- 10줄 이상의 의미 있는 로직

### 등록 절차

1. `{modules_root}/{domain}/{module_name}/` 폴더 생성
2. 코드 파일 + `module.md` 작성
3. Project 의 doc_manager CLI 로 ingest:
   ```bash
   ${hub_cli_python} ${hub_cli_doc_manager} ingest --file "{modules_root}/{domain}/{module_name}/module.md" --project vp
   ```

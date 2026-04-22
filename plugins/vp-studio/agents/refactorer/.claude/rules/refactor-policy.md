# Refactor Policy

## 네이밍

- 레포 컨벤션 우선: Python/Unreal 은 PascalCase 함수/클래스·snake_case 지역변수. PowerShell 은 `Verb-Noun` + PascalCase 파라미터.
- 약어는 두 글자 이상이면 대문자 유지 (`HTTPClient` OK, `HttpClient` 도 OK — 기존 파일 스타일 따라감)
- 단독 문자 변수 (i, j, k, x, y) 는 루프·수학식 외에서 금지 → 의미 있는 이름으로

## 주석

- 한국어 본문 + 영어 기술 용어 (레포 공통)
- 주석은 **WHY** 중심. WHAT 은 코드로 충분.
- 삭제 대상: "TODO: ..." 중 날짜 미기재 1년 이상 된 것, 주석 처리된 죽은 코드
- docstring 은 공개 함수에만 필수 (한 줄 요약 + 주요 인자/반환)

## 중복 병합

- 동일 로직이 2회 이상 복제된 경우 공용 함수로 추출
- 추출 위치: 같은 모듈 내 private helper → 도메인 utils → Project 가 보유한 공용 utils 모듈(예: `{modules_root}/utils/`) 순 — Project 의 modules 레이아웃은 vp-agent `modules.md` 참조
- **외부 호출 없는 내부 함수만 대상**. 공개 API 는 건드리지 않음.

## 미사용 코드 삭제 기준

삭제하려면 **전부 만족**해야 함:

1. Grep 전체 레포에서 사용처 0건
2. 외부 Python entry point (setup.py, pyproject.toml, hook 명령) 에 등록되지 않음
3. `__all__` 목록에 없음
4. plugin API (`.uplugin` 등록, Blueprint 노출) 아님

하나라도 불확실하면 삭제 대신 `# DEPRECATED: <사유>` 주석만 추가하고 NEEDS_REVIEW.

## 함수 분할

- 40 LOC 초과 + cyclomatic complexity 체감상 높음 → 분할 검토
- 분할된 헬퍼는 private (`_` prefix). 공개로 노출 금지.
- 분할이 원본 시그니처를 바꿔야 한다면 중단 → NEEDS_REVIEW

## import 정리

- 표준 → 서드파티 → 로컬 3블록, 알파벳 순
- 사용처 Grep 으로 확인 후 미사용만 제거
- `from X import *` 발견 시 삭제하지 말고 NEEDS_REVIEW (외부 영향 불확실)

## 매직 넘버·상수화

- 2회 이상 등장하는 리터럴은 모듈 상단 상수로
- 단 포트 번호·버전 문자열 등 설정성 값은 이미 있는 config 로 이동 (새 상수 생성 금지)

## 테스트 취급

- 기존 테스트 파일은 건드리지 않음. 리팩터 후 실행해서 green 이면 OK, red 면 변경 롤백 후 NEEDS_REVIEW.
- 테스트 누락 시 신규 테스트 작성 금지 (파트 경계 초과). NEEDS_REVIEW 사유로 기록.

## 커밋 관련

- 커밋·푸시 금지. 메인 Claude 가 처리.
- diff 요약을 출력에 포함 (변경 파일 + 한 줄 요약).

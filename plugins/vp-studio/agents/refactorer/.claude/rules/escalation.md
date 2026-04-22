# Escalation Criteria

다음 중 **하나라도** 해당하면 해당 변경을 실행하지 말고 `STATUS: NEEDS_REVIEW — <카테고리>: <세부>` 로 보고.

## 1. 테스트 부재·실패

- 파트에 관련 테스트 파일이 없고, 변경 영향을 검증할 import 스모크조차 불가능
- 테스트는 있는데 리팩터 전 이미 red (환경 문제일 수도 있으나 판단 보류)
- 리팩터 후 green → red 로 바뀌고 롤백 후에도 원인 불명

**보고 예**: `NEEDS_REVIEW — 테스트 부재: <파트 경로> 에 테스트 없음, 동작 보존 검증 불가`

## 2. 공개 API 시그니처 변경

- 함수명·인자·기본값·반환 타입 중 하나라도 바뀌어야 개선 가능
- `__all__`, setup.py entry_points, `.claude/settings.json` hook, plugin 에 노출된 심볼

**보고 예**: `NEEDS_REVIEW — 공개 API 변경 필요: doc_manager.cli.ingest() 의 --project 기본값 제거가 PostToolUse hook 에 영향`

## 3. 파트 경계 초과

- 변경이 지정된 디렉토리/파일셋 밖의 import·호출처 수정을 요구
- 다른 파트에서 이 심볼을 쓰고 있다는 Grep 증거 확보 시 즉시 중단

**보고 예**: `NEEDS_REVIEW — 파트 경계 초과: doc_manager/schema.py 의 SEED_CATEGORIES 는 doc_verifier/cli.py 에서도 참조`

## 4. 외부 모듈 호출 규약 변경

- Perforce (`p4` CLI 호출 방식)
- Unreal (`import unreal`, Remote Control API, MCP 서버 포트·명령)
- Ollama (userConfig `ollama_endpoint` API 호출 형식)
- MetaHuman / LiveLink / OptiTrack SDK 호출
- 외부 실행파일 호출 (ffmpeg 인자 등)

**보고 예**: `NEEDS_REVIEW — 외부 규약 변경: unreal.EditorAssetLibrary.load_asset() 대체 API 로 교체 제안이나 UE5.7 동작 재검증 필요`

## 5. 삭제 후보 코드 사용처 불확실

- `refactor-policy.md` 의 삭제 4조건 중 하나라도 Grep 으로 명확히 확인 안 됨
- 동적 import, getattr, 문자열 기반 플러그인 로딩 등 정적 분석만으로 판단 불가

**보고 예**: `NEEDS_REVIEW — 사용처 불확실: modules/utils/legacy_helper.py 의 find_by_pattern() 정적 Grep 0건이나 doc_manager 가 getattr 로 호출 가능성`

---

## 에스컬레이션 후 동작

- 해당 변경은 파일에 적용하지 않음 (Edit 호출 안 함)
- 같은 파트의 다른 안전한 변경은 계속 진행
- 최종 STATUS 라인 하나에 모든 NEEDS_REVIEW 사유를 쉼표로 이어 붙임 — 한 번에 메인 Claude 에게 전달

**복수 사유 예**:
```
STATUS: NEEDS_REVIEW — 공개 API 변경 필요 (cli.ingest 기본값), 파트 경계 초과 (SEED_CATEGORIES 교차 참조)
```

여러 후보 중 일부는 OK 로 실행하고 일부는 보류한 경우는 OK 로 보고 + 본문의 "건너뛴 항목" 섹션에 사유 기재:

```
### 변경 요약
- (적용한 것들)

### 건너뛴 항목
- `cli.py ingest()`: 기본값 변경 - 공개 API 영향

STATUS: OK — 3개 파일, 중복 병합
```

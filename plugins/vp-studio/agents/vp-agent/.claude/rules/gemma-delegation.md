# Gemma4 위임 패턴 — vp-agent

Plugin 의 Gemma4 위임 정책 (`userConfig.ollama_*`) 을 vp-agent 도메인에 맞춰 구체화한 규칙. 호출 래퍼는 Plugin 번들 스크립트 `${CLAUDE_PLUGIN_ROOT}/scripts/gemma.ps1`.

모든 호출은 **한국어 응답 유도 + 출력 형식 선제 제약**. 응답이 기대와 어긋나면 Claude 가 직접 재작성 (Gemma 재시도 금지).

## 사전 조건

- userConfig `ollama_enabled` 이 `true` — 비활성화면 모든 위임은 no-op, Claude 직접 수행
- userConfig `ollama_endpoint` 로 Ollama 서버 도달 가능
- userConfig `ollama_model` 에 지정된 모델 tag 가 Ollama 에 pull 되어 있음

---

## 1. Daily 리포트 자동화

### 트리거
- 유저 발화: "daily 정리", "오늘 요약", "{날짜} 리포트"
- `/save-session` 스킬 완료 직후 같은 날짜 세션 ≥ 2건이면 자동 제안
- `${daily_root}/YYYY-MM-DD.md` 가 비어있을 때만 (기존 파일 덮어쓰기 금지)

### 입력
- 해당 날짜의 `${docs_root}/*/sessions/YYYY-MM-DD_*.md` 전수
- 전일 daily 가 있으면 "Yesterday carry-over" 로 앞에 concat (선택)

### 출력 섹션 (고정)
1. 주요 성과 (3-5 bullet)
2. 진행 중 (3-5 bullet)
3. 이슈 / 블로커 (있을 때만)
4. 내일 예정 (3-5 bullet)

### 프롬프트 템플릿
```
-System "당신은 VP 스튜디오 파이프라인 엔지니어의 데일리 리포트 작성자입니다.
아래 세션 노트를 읽고 한국어 마크다운으로 일일 요약을 작성하세요.
고정 섹션: 1) 주요 성과 2) 진행 중 3) 이슈/블로커 4) 내일 예정. 각 3-5 bullet.
추측 금지, 노트에 있는 사실만. 파일명·경로는 노트 그대로 인용."
```

### 검수 체크리스트 (Claude)
- [ ] 4개 섹션 구조 준수
- [ ] 추측 문장 없음 (세션 노트에 없는 내용 삽입 여부)
- [ ] 파일 경로·커밋 해시 원문 대조
- [ ] 한국어 본문, 영어 기술 용어 유지

검수 통과 시에만 `${daily_root}/` 에 Write.

### 연동 스킬
`daily-recap` 스킬 내부에서 이 위임을 사용 가능. 현재 스킬이 Gemma 를 쓰지 않는다면 Claude 가 직접 호출 추가.

---

## 2. 문서 자동 태깅·카테고리

### 트리거
- Project 의 doc_manager ingest 실행 후 `auto_tags` 또는 `auto_category` 가 비어있는 문서 발견 시
- 배치: userConfig `hub_cli_doc_manager` 로 list 조회 후 `auto_tags` 공란 항목 필터

### 입력
- MD 본문 앞 2000자 (frontmatter 제외)
- Project 의 doc_manager 가 노출하는 `TAG_KEYWORDS` 사전 (Project 책임: `hub_cli_doc_manager --show-tag-vocab` 등 서브커맨드로 제공하거나, 문서화된 경로에서 정적 로드)
- Project 의 카테고리 enum (Project 책임)

> **Plugin 관점 주의**: 태그 사전과 카테고리 enum 은 VP 도메인 고유 스키마이므로 Project 에 소유권 있음. Plugin 은 Project CLI 를 통해 조회만 하며, 사전 콘텐츠 자체는 하드코딩하지 않는다.

### 출력 포맷 (엄격)
```
tags: <쉼표 구분 소문자 태그 3-7개>
category: <후보 중 하나>
```
다른 형식은 파기.

### 프롬프트 템플릿
```
-System "TAG_KEYWORDS 사전과 카테고리 후보만 사용.
사전 외 태그 생성 금지. 출력은 정확히 2줄:
tags: t1,t2,t3
category: <후보>
설명·이유 출력 금지."
```

### 검수 체크리스트
- [ ] 모든 태그가 Project TAG_KEYWORDS 에 존재 (사전 외 생성 태그 제거)
- [ ] 카테고리가 Project 의 기본 카테고리 enum 내
- [ ] 최종 DB 반영은 Claude 가 `${hub_cli_python} ${hub_cli_doc_manager} update-meta` 로 직접 실행

---

## 3. Confluence HTML 정제·요약

사전 조건: userConfig `confluence_enabled` 이 `true`.

### 트리거
- Project 의 confluence_migrator HTML→MD 변환 후 frontmatter `summary:` 가 공란인 경우
- 호출 경로: `${hub_cli_python} ${hub_cli_confluence_migrator}` 서브커맨드
- 배치 이관 시 전수 적용

### 입력
- 변환된 MD 본문 (HTML 제거된 순수 마크다운)
- 최대 3000자 — 초과 시 앞 1500 + 뒤 1500 split

### 출력 포맷
```
summary: <한국어 1-2문장, 150자 이내>
```

### 프롬프트 템플릿
```
-System "아래 VP 파이프라인 문서를 읽고 한국어 1-2문장 요약을 생성.
150자 이내. 고유명사(제품명·버전·약어)는 원문 그대로.
출력은 'summary: ...' 단 한 줄."
```

### 검수 체크리스트
- [ ] 150자 이내
- [ ] 원문 고유명사 (UE/Motive/MetaHuman/OptiTrack/버전 번호) 누락 없음
- [ ] 200자 초과 또는 영문 응답 시 Claude 재작성 (Gemma 재시도 금지)
- [ ] 실패 시 `summary:` 공란 유지 (빈 값 OK, 잘못된 요약 주입 금지)

### 위험 요소
- HTML 표·코드블록 변환이 불완전한 문서는 요약 품질 저하 → 폴백
- Ollama 미기동 시 전체 배치 중 첫 실패 이후 Claude 가 남은 문서 직접 처리

---

## 공통 계약

- **호출 방법**: `powershell -NoProfile -ExecutionPolicy Bypass -File ${CLAUDE_PLUGIN_ROOT}/scripts/gemma.ps1` 패턴. 스크립트는 userConfig `ollama_*` 를 환경변수로 자동 읽음.
- **위임 알림**: 위임할 때마다 한 줄 "→ supergemma4 로 {작업} 위임"
- **파일 쓰기**: Gemma stdout 을 변수로 받은 후 Edit/Write 로만 기록. `>` 리다이렉트 금지
- **재시도 금지**: 기대 포맷 이탈 시 같은 프롬프트 재호출 X, Claude 직접 폴백
- **Ollama 다운 감지**: 세션 내 첫 실패 후 해당 세션의 남은 Gemma 호출 모두 스킵 + Claude 폴백 (ollama_enabled 를 세션 내 false 로 취급)

## 운용 테스트 기준

3회 실사용 후:
- 검수 재작성률 > 50% → 프롬프트 재설계 또는 해당 영역 위임 철회
- 성공률 > 70% → 스크립트화 승격 검토 (Plugin 또는 Project 쪽에 재사용 스크립트 추가)

---
name: promote-share
description: VP Supervisor — 개인 스크래치에서 _shared/labs/ 로 파일 승격. 복사 전 반드시 사람 리뷰 게이트를 통과해야 한다. Z:\ 오프라인 시 로컬 대기 목록에 기록.
allowed-tools: Bash Read Write Glob Grep
argument-hint: "[file-path ...] [--topic topic_name] [--dry-run]"
---

# Promote Share — 개인 스크래치 → _shared/labs/ 승격

개인 스크래치(`${studio_share_root}/${active_user}/`)에서 작성된 파일을
팀 공유 공간(`${labs_root}`)으로 복사하는 공식 절차.

**핵심 제약 — 절대 생략 불가:**
> Step 3 리뷰 게이트에서 사용자가 명시적으로 **승인(approve)** 하지 않으면
> Step 4 이후를 절대 진행하지 않는다.

## Arguments

- `[file-path ...]` : 승격할 파일 명시 (없으면 Step 2에서 후보 탐색)
- `--topic topic_name` : 공유 파일명의 `{topic}` 부분 (기본: 원본 파일명)
- `--dry-run` : 실제 복사 없이 리뷰 게이트까지만 실행

---

## Procedure

### Step 0: 환경 확인

**A. userConfig 검증**

필수 필드가 비어 있으면 즉시 중단:

```
❌ 필수 userConfig 미설정:
   - studio_share_root : Z:/VPO/6_claude
   - active_user       : minkyun_park
   - user_initials     : MK
   - labs_root         : Z:/VPO/6_claude/_shared/labs

   Settings 에서 설정 후 재실행하세요.
```

**B. Z:\ 가용성 probe**

```bash
if [ -d "${studio_share_root}" ]; then
  echo "online"
else
  echo "offline"
fi
```

**오프라인인 경우:**

```
⚠️ Z:\ 드라이브 오프라인 — 승격 보류 목록에 기록합니다.
   대기 목록: ${CLAUDE_PROJECT_DIR}/vp/sessions/.pending-promote.json
```

대기 목록에 추가 후 스킬 종료 (오프라인 처리는 아래 "오프라인 대기 흐름" 참조).

---

### Step 1: 승격 후보 파일 수집

인자로 파일을 지정한 경우: 해당 파일만 목록화.

인자가 없는 경우: 개인 스크래치에서 후보 탐색:

```bash
# 오늘 날짜 기준 최근 파일 (sessions, briefings, daily)
find "${studio_share_root}/${active_user}" \
  -type f -name "*.md" \
  -newer "${studio_share_root}/${active_user}/.last-promote" \
  2>/dev/null | sort
```

후보가 없으면:
```
ℹ️ 승격 후보 파일 없음 — 개인 스크래치에 새 파일이 없습니다.
   경로: ${studio_share_root}/${active_user}/
```

---

### Step 2: 후보 목록 출력

사용자에게 승격 대상 파일 목록과 각 파일의 **요약 내용**을 보여준다.

출력 형식:

```
📋 승격 후보 파일 목록
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  No.  파일명                                 크기    수정일
  [1]  2026-04-23_brief_FilmA_S01.md         4.2KB   오늘 14:32
  [2]  2026-04-23_handoff_S01C03.md          6.8KB   오늘 16:10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

각 파일 요약:
[1] brief_FilmA_S01 — S01 씬 마스터 브리핑. GO 판정. Art/MoCap/Previz 배포용.
[2] handoff_S01C03  — S01C03 포스트팀 인계 패키지. OK 5컷, HOLD 2컷.
```

각 파일의 첫 20줄(또는 frontmatter + 첫 섹션)을 Read 로 읽어 요약 제공.

---

### Step 3: 리뷰 게이트 (MANDATORY — 절대 생략 금지)

**사용자에게 다음 질문을 명시적으로 출력하고 응답을 기다린다:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 리뷰 게이트 — _shared/labs/ 승격 전 검토

위 파일을 검토하셨습니까?
승격하면 팀 전체가 접근 가능한 공유 공간에 복사됩니다.
원본은 개인 스크래치에 유지됩니다.

승격할 파일 번호를 입력하세요 (예: 1,2 또는 all):
취소하려면 'cancel' 입력.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**응답 처리:**
- `cancel` 또는 빈 입력 → 즉시 종료, 파일 변경 없음
- 번호 목록 (예: `1,2`) → 해당 파일만 승격
- `all` → 후보 전체 승격

**`--dry-run` 플래그:** 이 단계까지만 실행하고 실제 복사 없이 종료.

---

### Step 4: 파일명 규칙 적용 및 복사

승인된 파일 각각에 대해:

**목적지 파일명 생성:**
```
{YYYY-MM-DD}_{user_initials}_{topic}.md
```
- `{YYYY-MM-DD}` : 오늘 날짜
- `{user_initials}` : userConfig 값 (예: MK)
- `{topic}` : `--topic` 인자 또는 원본 파일명에서 날짜 prefix 제거한 부분

**예시:**
- 원본: `2026-04-23_brief_FilmA_S01.md`
- 목적지: `2026-04-23_MK_brief_FilmA_S01.md`

**목적지 경로:** `${labs_root}/{생성된 파일명}`

충돌 확인:
```bash
ls "${labs_root}/${dest_filename}" 2>/dev/null
```
이미 존재하면:
```
⚠️ 파일명 충돌: {dest_filename} 이미 존재.
   덮어쓰기 하시겠습니까? (y/N): 
```
N 또는 빈 입력 → 해당 파일 스킵, 나머지 계속.

복사 실행:
```bash
cp "${src_path}" "${labs_root}/${dest_filename}"
```

---

### Step 5: 대기 목록 갱신

성공적으로 복사된 파일은 `.pending-promote.json` 에서 제거.

`.last-promote` 타임스탬프 갱신:
```bash
touch "${studio_share_root}/${active_user}/.last-promote"
```

---

### Step 6: 완료 출력

```
✅ 승격 완료

   승격된 파일:
   - ${labs_root}/2026-04-23_MK_brief_FilmA_S01.md
   - ${labs_root}/2026-04-23_MK_handoff_S01C03.md

   원본 위치 (유지됨):
   - ${studio_share_root}/${active_user}/sessions/2026-04-23_brief_FilmA_S01.md
   - ${studio_share_root}/${active_user}/sessions/2026-04-23_handoff_S01C03.md

   팀 공유 경로: ${labs_root}/
```

---

## 오프라인 대기 흐름

Z:\ 오프라인 시 `${CLAUDE_PROJECT_DIR}/vp/sessions/.pending-promote.json` 에 기록:

```json
{
  "pending": [
    {
      "src": "${studio_share_root}/${active_user}/sessions/2026-04-23_brief_FilmA_S01.md",
      "dest_filename": "2026-04-23_MK_brief_FilmA_S01.md",
      "queued_at": "2026-04-23T16:30:00",
      "reviewed_by": "${active_user}"
    }
  ]
}
```

Z:\ 복구 후 `/promote-share` 를 인자 없이 실행하면 대기 목록을 자동 감지하고
**리뷰 게이트 없이** (이미 리뷰 완료 표시) 복사를 재시작.

단, `reviewed_by` 가 현재 `active_user` 와 다르면 리뷰 게이트를 다시 거친다.

---

## 주의사항

- ❌ Step 3 리뷰 게이트 없이 Step 4 진행 절대 금지
- ❌ 원본 파일 삭제 금지 — 복사(cp)만 허용
- ❌ `_projects/` 에 직접 쓰기 금지 (admin 전용)
- ❌ `user_initials` 없이 공유 공간에 쓰기 금지 (Step 0 에서 차단)
- 리뷰 게이트에서 `cancel` 입력 시 어떤 파일도 수정하지 않고 정상 종료

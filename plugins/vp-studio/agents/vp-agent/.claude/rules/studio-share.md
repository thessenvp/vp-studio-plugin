---
description: "Z:\\VPO\\6_claude\\ 스튜디오 공유 드라이브 경로 해석 규칙 — 3-tier 구조(personal/shared/archive) 쓰기 정책, 사용자 스코핑, labs 승격 흐름"
globs: []
---

# Studio Share Rule

`${studio_share_root}` (예: `Z:/VPO/6_claude`) 기반 스튜디오 공유 드라이브 운영 규칙.

---

## 3-tier 디렉토리 구조

```
${studio_share_root}/
  {active_user}/          # 개인 스크래치 (write: 본인만)
  _shared/                # 공유 영역 (write: labs 멤버 NTFS ACL)
    labs/                 # ${labs_root} — 내부 실험·검수 아티팩트
  _projects/              # 프로젝트 아카이브 (write: admin만)
```

---

## 경로 해석 우선순위

`studio_share_root` 가 **설정된 경우**:

| Hub 경로 변수 | 기본 매핑 |
|---|---|
| `sessions_root` | `${studio_share_root}/${active_user}/sessions` 로 override 권장 |
| `briefings_root` | `${studio_share_root}/${active_user}/briefings` 로 override 권장 |
| `daily_root` | `${studio_share_root}/${active_user}/daily` 로 override 권장 |
| `labs_root` | `${studio_share_root}/_shared/labs` (userConfig 직접 지정) |

`studio_share_root` 가 **비어 있으면** (기본값): 기존 `${CLAUDE_PROJECT_DIR}/vp/...` Hub 경로 그대로 사용.

---

## 쓰기 정책

### 개인 스크래치 (`{active_user}/`)
- 본인 세션·브리핑·daily 파일을 자유롭게 쓴다.
- 파일명에 `user_initials` 불필요 (본인 폴더라 충돌 없음).

### 공유 영역 (`_shared/`)
- **파일명 규칙**: `{YYYY-MM-DD}_{user_initials}_{topic}.md`
  - 예: `2026-04-22_MK_shoot-summary.md`
- `user_initials` 가 비어 있으면 `_shared/` 쓰기 전 경고:
  ```
  ⚠️ user_initials userConfig 미설정 — 파일명 충돌 방지를 위해 설정 후 재실행 권장.
  ```
- **promote-then-write 흐름**: 개인 스크래치에 작성 → 검수 후 `_shared/` 로 복사(원본 유지).

### 아카이브 (`_projects/`)
- Plugin skills 는 `_projects/` 에 **직접 쓰지 않는다** (admin 전용).
- 읽기는 허용 (`hub_read_only_paths` 에 `_projects/**` 추가 권장).

---

## labs_root 활용 (Phase 7c 이후)

`${labs_root}` 가 설정된 경우 해당 스킬(예: new-plugin, sync-check)은 빌드 아티팩트를 `labs_root` 에도 복사한다. 미설정이면 해당 단계를 조용히 스킵.

---

## 오프라인·네트워크 단절 감지

Z:\ 드라이브 접근 전 probe:

```bash
# Windows: 드라이브 존재 여부 확인
if [ -d "${studio_share_root}" ]; then
  echo "online"
else
  echo "offline — ${studio_share_root} 접근 불가, 로컬 Hub 경로 사용"
fi
```

오프라인 시 `${CLAUDE_PROJECT_DIR}/vp/...` 경로로 자동 폴백. 세션 종료 전 유저에게 Z:\ 동기화 필요 여부 알림.

---

## 절대로 하지 말 것

- ❌ `_projects/` 에 직접 쓰기 (admin 전용)
- ❌ `user_initials` 없이 `_shared/` 에 쓰기 (경고 후 진행은 허용, 단 경고 생략 금지)
- ❌ `studio_share_root` 하드코딩 — 항상 userConfig 변수 사용
- ❌ Z:\ probe 없이 드라이브가 마운트됐다고 가정

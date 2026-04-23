# notify (Plugin bundle)

Plugin 내장 Telegram 알림 패키지. 원본은 VP-Studio 의 `vp/scripts/utils/notify/` +
`vp/modules/utils/notify/` 두 경로에 나뉘어 있었음. Plugin 에서는 단일 패키지
`scripts/notify/` 로 병합.

## 구조

```
scripts/notify/
├── __init__.py               # 공개 API: send(), Event, Severity
├── cli.py                    # python -m notify.cli send ... 엔트리
├── events.py                 # Event / Severity enum, EVENT_EMOJI
├── config.py                 # 설정 로더 (token, chat_ids, severity_map)
├── router.py                 # throttle (파일 기반)
├── telegram.py               # Bot API 호출
├── _yaml.py                  # PyYAML 없을 때 쓰는 초경량 파서
├── _paths.py                 # notify.yaml / throttle.json 경로 resolve
└── config.example.yaml       # 유저용 샘플
```

## 실행 방법

```bash
python -m notify.cli send \
  --event SESSION_SAVED \
  --title "Scene 042 saved" \
  --body "path/to/session.md" \
  --severity info
```

또는 CLI 모듈 실행:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/notify/cli.py send --event DAILY_RECAP ...
```

## 설정

| 변수 / 파일 | 용도 | 기본값 |
|---|---|---|
| `$CLAUDE_PROJECT_DIR` | Project 루트 | cwd |
| `$NOTIFY_CONFIG` | notify.yaml 경로 (명시) | fallback chain |
| `$NOTIFY_THROTTLE_PATH` | throttle.json 경로 (명시) | Hub logs 아래 |
| `~/.openclaw/openclaw.json` | Telegram bot token 재사용 | — |
| `$TELEGRAM_BOT_TOKEN` | token fallback | — |

`notify.yaml` fallback chain:
1. `$NOTIFY_CONFIG`
2. `${CLAUDE_PROJECT_DIR}/tools/config/notify.yaml`
3. `${CLAUDE_PROJECT_DIR}/vp/config/notify.yaml` (legacy)

## Plugin ↔ Project 계약

- **Plugin 이 제공**: 채널 어댑터 (Telegram)·이벤트 enum·throttle·dry-run
- **Project 가 제공**: `notify.yaml` 내용 (chat_ids·severity_map·mute·throttle)
- **User 홈 디렉토리**: `~/.openclaw/openclaw.json` (token, 스튜디오 독립)

## userConfig 연동

Plugin `plugin.json` 의 `notify_channels` userConfig 필드는 현재 선언만 되어 있고
이 CLI 가 직접 소비하지 않음 (config.yaml 에서 severity/chat 제어). 추후 channel
어댑터가 늘어나면 (discord / slack 등) 이 필드가 사용됨.

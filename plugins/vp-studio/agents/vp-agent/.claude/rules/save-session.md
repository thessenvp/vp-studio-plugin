# Session Save Rules

When the user types **"세션 저장"** (save session), execute the following procedure immediately.

## Step 1: Write MD File

**Path:** `${docs_root}/{domain}/sessions/YYYY-MM-DD_{topic_summary}.md`

> Session ownership model (pending final decision): this Plugin rule
> currently targets the Hub-level `${docs_root}/{domain}/sessions/`
> layout. If the Project switches to per-project session storage
> (`${project_root}/sessions/{domain}/`), the destination path will
> be remapped via userConfig.

### Domain Selection

Determine the primary domain from the session's main topic:

| Domain Folder | When to use |
|---|---|
| `mocap` | OptiTrack, Motive, motion capture, LiveLink streaming |
| `unreal` | UE level, rendering, MetaHuman, plugin, sequencer |
| `icvfx` | In-Camera VFX, LED wall shooting, NIPA operations |
| `sync` | Genlock, timecode, SPG, Tentacle, Ambient Lockit |
| `pipeline` | Doc manager, CLI tools, automation scripts, Git workflow |
| `perforce` | P4 workspace, depot, changelist |
| `ai-rnd` | AI/ML research, QWEN, ComfyUI, Hunyuan, StableMotion, 3D generation |
| `camera` | Camera testing, photogrammetry, Reality Capture, photoscan |
| `general` | Doesn't fit above categories |

- Date is today's date
- Topic summary in English snake_case, 3–5 words (e.g., `sqlite_doc_manager_setup`)
- If the same date and topic already exist, append `_2`, `_3`, etc.

**Structure:**

```markdown
---
description: (one-line summary)
tags:
  - (related tags)
category: session-records
---

# Session: (title)

## Work Performed
- (list of tasks completed)

## Decisions Made
- (decisions and their reasoning)

## Issues Resolved
- (symptom → cause → resolution pattern)

## Files Changed
- (exact file paths and changes)

## TODO / Remaining Work
- (what to continue next)

## Notes
- (settings, caveats, tips)
```

## Step 2: DB Ingest

Run immediately after file creation using Project's doc_manager CLI:

```bash
${hub_cli_python} ${hub_cli_doc_manager} ingest --file "{file_path}" --project vp
```

`${hub_cli_doc_manager}` is the userConfig-injected path to Project's doc_manager CLI. If unset, report the missing config to the user and skip DB ingest (session file write still proceeds).

## Step 3: Git Commit

After ingest completes, auto-commit the session file:

```bash
git add "{file_path}"
git commit -m "Session record: {title}"
```

## Writing Guidelines

- Focus on summaries — do not copy the entire conversation, only key points
- Be specific — include file names, function names, settings values
- Make it reproducible — document issues as symptom → cause → resolution
- Omit unnecessary sections (e.g., skip "Issues Resolved" if none exist)

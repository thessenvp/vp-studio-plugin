# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-22

First pre-release. Scaffold + three-layer architecture contracts + Plugin layer PoC.

### Added
- Marketplace manifest (`vp-studio-plugin`) with kebab-case identifier.
- Plugin manifest (`vp-studio`) with 26 `userConfig` fields covering:
  - Hub paths (10): `hub_root`, `docs_root`, `sessions_root`,
    `briefings_root`, `mocap_sessions_root`, `risk_playbooks_root`,
    `daily_root`, `inbox_root`, `wiki_root`, `doc_manager_db_path`
  - Hub CLI bindings (5): `hub_cli_python`, `hub_cli_doc_manager`,
    `hub_cli_doc_verifier`, `hub_cli_reviewer`,
    `hub_cli_confluence_migrator`
  - Ollama/Gemma delegation (4): `ollama_{enabled,endpoint,model,temperature}`
  - Project infrastructure (3): `vpo_plugin_root`,
    `perforce_workspace_root`, `ue_engine_5_7_path`
  - External integrations (2): `confluence_{enabled,base_url}`
  - Feature toggles (2): `telemetry_enabled`, `notify_channels`
  - Safety (1): `hub_read_only_paths`
- Architecture docs under `plugins/vp-studio/docs/architecture/`:
  - `layers.md` — Plugin / Project / Hub three-layer separation and
    ownership, Plugin never hardcodes Project/Hub paths
  - `hub-cli-contract.md` — `hub_cli.*` userConfig contract, skill
    → Project CLI dependency matrix, MCP server stays in Project layer
  - `projects-permissions.md` — per-agent write matrix for `projects/`
    (project-agent → metadata, scenario-agent → scenarios/**, vp-agent
    → read-only via symlink)
- `sync-check` skill (Plugin layer PoC) — Genlock/Timecode chain
  verification with graceful `hub_cli_*` fallback.

### Changed
- Repo renamed from `vp-studio-marketplace` → `vp-studio-plugin`.
- Marketplace internal `name` aligned with repo name.
- Dropped explicit component paths in `plugin.json` (validator rejects
  empty directories declared as paths).

[Unreleased]: https://github.com/thessenvp/vp-studio-plugin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/thessenvp/vp-studio-plugin/releases/tag/v0.1.0

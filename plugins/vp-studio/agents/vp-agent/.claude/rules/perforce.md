# Perforce Rules

## Version

- **Perforce** P4V/NTX64/2025.4/2886649

## Workspace Structure

**Depot root (Project-configurable):** `${perforce_workspace_root}` — local mapping of the Perforce depot. Default example on Windows: `C:\ws\depot`. Plugin never hardcodes a specific drive letter or workspace path.

| Folder | Purpose | Project Prefix |
|---|---|---|
| `0_Dev/` | Development projects | `Dev_` |
| `1_Project/` | Default depot working projects | `Proj_` |
| `2_Test/` | Test projects | `Test_` |
| `3_Template/` | Template project updates | — |

**Examples (with perforce_workspace_root = `C:\ws\depot`):**
- `${perforce_workspace_root}/0_Dev/Dev_AutoMoCap/`
- `${perforce_workspace_root}/1_Project/Proj_FilmA/`

## Git ↔ Perforce Relationship

- This Plugin consumer repo (VP-Studio) is managed with **Git** (team rules, scripts, plugins)
- UE projects are managed with **Perforce** (assets, levels, sequences, etc.)
- Scripts are developed in Git, then copied/symlinked to UE projects as needed

## Reference

- Perforce Helix Core Documentation: `https://help.perforce.com/helix-core/`

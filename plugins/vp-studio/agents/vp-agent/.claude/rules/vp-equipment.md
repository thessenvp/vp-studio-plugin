# VP Equipment Rules

## Sync Generator

- **Tektronix SPG 8000** — master sync signal generator
- SPG 8000 → Blacktrax eSync → full system Genlock

## Timecode Devices

- **Tentacle Sync E** — receives timecode from eSync
- **Ambient Lockit** x4 — wireless timecode distribution
- Sync chain: `SPG 8000 → eSync → Tentacle / Ambient Lockit`
- **All systems must be Genlock & Timecode synchronized**

## Workstations

### Render Machine
- **GPU:** 1x NVIDIA A6000
- Handles real-time rendering and mocap processing

### Developer Workstation
- **GPU:** NVIDIA GeForce RTX 4090
- General development, tool authoring, local LLM inference (Ollama — `0xIbra/supergemma4-26b-uncensored-gguf-v2:Q4_K_M`)

## Framerate & Render Settings

- **Default framerate: 24fps** (highest priority)
- Special cases: 23.98 / 29.97 / 30 / 59.94 / 60 fps
- **Render codec: H.264** (Movie Render Queue presets are stored within the UE project)

## Reference

- Tektronix SPG 8000 Service Manual: `https://download.tek.com/manual/SPG8000-Master-Sync-Clock-Reference-Generator-Service-Manual_1.pdf`
- Tentacle Sync E Manual: `https://manuals.tentaclesync.com/en/sync-e-manual.html`
- Ambient Lockit Handbook: `https://cvp.com/pdf/acn-cl-lockit-synchronizer-handbook.pdf`

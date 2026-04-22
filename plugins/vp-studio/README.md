# vp-studio

VP Studio toolkit for animation, virtual production, and VFX pipelines.

## Scope

- Motion capture (OptiTrack) and MetaHuman workflows
- Unreal Engine 5.x + nDisplay + LED wall operations
- Genlock / timecode sync, LiveLink
- Asset naming rules and Perforce workflow helpers
- VP pipeline automation scripts

## Status

`0.1.0` — scaffold only. Content migration from `VP-Studio/` repo is the next step.

## Layout

```
vp-studio/
├── .claude-plugin/plugin.json
├── commands/    # slash commands
├── agents/      # subagent definitions
├── skills/      # reusable skill packs (each <name>/SKILL.md)
├── hooks/hooks.json
└── README.md
```

## Install (after publishing)

```
/plugin marketplace add thessenvp/vp-studio-plugin
/plugin install vp-studio@vp-studio-plugin
```

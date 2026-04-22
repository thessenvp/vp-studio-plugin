# vp-studio-marketplace

Claude Code plugin marketplace hosting VP Studio tools for animation, virtual production, and VFX.

## Install the marketplace

```
/plugin marketplace add <repo-url-or-local-path>
```

Local example (during development):

```
/plugin marketplace add C:/Users/minkyun_park/Documents/Claude/vp-studio-marketplace
```

## Plugins

| Name | Description | Version |
|---|---|---|
| [`vp-studio`](plugins/vp-studio) | VP domain toolkit (mocap, MetaHuman, Unreal, nDisplay, LED wall, asset naming) | 0.1.0 |

## Install a plugin

```
/plugin install vp-studio@vp-studio-marketplace
```

## Layout

```
vp-studio-marketplace/
├── .claude-plugin/marketplace.json
├── plugins/
│   └── vp-studio/          # bundled plugin (relative-path source)
└── README.md
```

## Status

Scaffold only. No plugin content yet — migration from the main `VP-Studio` repo is the next step.

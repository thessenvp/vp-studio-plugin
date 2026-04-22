# Production Pipeline & Automation

## Production Pipeline

```
Scenario Delivery
  → Level Creation
  → MetaHuman & Character Creation
  → Motion Capture Preparation
  → Asset Integration into UE Level
  → Real-time Shooting (Virtual Camera + MoCap Actor)
  → Simultaneous Recording (UE Recording / Motive Backup / FFmpeg Real-time)
  → Real-time Editing
  → Edit Delivery → Approval
  → EDL Export (Unreal Engine)
  → Scene Revision
  → Final Rendering
  → Delivery to Video Editor
```

## Automation Targets (Priority)

| Area | Description |
|---|---|
| **MoCap Data Processing** | Motive → UE data import/retargeting automation |
| **Level Setup** | Character/prop placement automation, sequencer configuration |
| **Recording Management** | UE Take Recorder + FFmpeg + Motive simultaneous recording trigger |
| **EDL Workflow** | EDL Export → scene split → revision automation |
| **Rendering** | Movie Render Queue batch render automation |
| **File Organization** | Automated asset/file cleanup & validation per naming conventions |

## Reference

- UE Take Recorder: `dev.epicgames.com/documentation/.../take-recorder`
- Movie Render Queue: `dev.epicgames.com/documentation/.../movie-render-queue`

# UE Asset Naming Convention (Detailed)

**Original document:** (삭제됨 — 이 파일이 정식 네이밍 규칙 문서)
**Epic Games recommended:** https://github.com/Allar/ue5-style-guide

## Basic Rules

- **Structure:** `{Prefix}_{AssetName}_{Descriptor}_{Variant}_{Suffix}`
- Use **PascalCase**, only alphanumeric characters and `_`
- No special symbols, backslashes, or spaces
- Keep paths from becoming too long

## Prefix & Suffix Full List

| Category | Asset Type | Prefix | Suffix |
|---|---|---|---|
| **Mesh** | Static Mesh | `SM_` | |
| | Skeletal Mesh | `SK_` | |
| | Foliage | `Fol_` | |
| **Character** | Skeleton | `SKEL_` | |
| | Physics Asset | `PA_` | |
| | IKRig | `IKR_` | |
| | IKRetargeter | `RTG_` | |
| **Material** | Material | `M_` | |
| | Material Instance | `MI_` | |
| | Post Process Material | `PPM_` | |
| **Texture** | Texture (Base Color) | `T_` | `_BC` |
| | Texture (Normal) | `T_` | `_N` |
| | Texture (Roughness) | `T_` | `_R` |
| | Texture (Metallic) | `T_` | `_M` |
| | Texture (AO) | `T_` | `_O` |
| | Texture (Emissive) | `T_` | `_E` |
| | Texture (Mask) | `T_` | `_Mask` |
| | Packed (O/S/M) | `T_` | `_OSM` |
| | Packed (S/R/M) | `T_` | `_SRM` |
| | HDR | `HDR_` | |
| | RenderTarget | `RT_` | |
| **Blueprint** | Blueprint | `BP_` | |
| | AnimBlueprint | `ABP_` | |
| | EditorUtilityWidget | `EUW_` | |
| | DataTable | `DT_` | |
| **FX** | NiagaraEmitter | `FX_` | |
| | NiagaraSystem | `FXS_` | |
| | NiagaraFunction | `FXF_` | |
| **Animation** | AnimMontage | `AM_` | |
| | AnimSequence | `AS_` | |
| | BlendSpace | `BS_` | |
| **Media** | Media Source | `MS_` | |
| | Media Output | `MO_` | |
| | Media Player | `MP_` | |
| | Media Profile | `MPR_` | |
| | Media Texture | `MT_` | |
| | File Media Source | `FMS_` | |
| | Img Media Source | `IMS_` | |
| | SoundWave (Audio) | `A_` | |
| **VP Related** | LevelSnapshots | `SNAP_` | |
| | RemoteControlPreset | `RCP_` | |
| | LiveLinkPreset | `LLP_` | |
| | OCIO Profile | `OCIO_` | |
| | nDisplay Config | `NDC_` | |
| | Movie Render Preset | `MRC_` | |
| | Movie Render Graph | `MRG_` | |
| **MetaHuman** | MetaHuman Identity | `MHI_` | |
| **Other** | Font | `Font_` | |

## Examples

- `SK_Echo_Cloth_A` — Skeletal Mesh, Echo character, Cloth part, variant A
- `T_WoodFloor_BC` — Texture, WoodFloor, Base Color
- `BP_MoCap_Trigger` — Blueprint, MoCap Trigger
- `MRC_Final_H264` — Movie Render Preset Config
- `LLP_OptiTrack_Main` — LiveLink Preset

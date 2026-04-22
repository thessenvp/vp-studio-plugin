# Unreal Engine Rules

## Version Policy

- **UE 5.7 is the default** — always check the latest version (5.7) first for APIs, docs, and features
- UE 5.6 is referenced only when compatibility checks are needed

## Engine Path Resolution

**Do not hardcode engine paths.** Resolution order:

1. **Windows registry (preferred)**:
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\EpicGames\Unreal Engine\{version}\InstalledDirectory
   ```
2. **userConfig fallback** when registry lookup fails or on non-Windows:
   - `${ue_engine_5_7_path}` — install directory for UE 5.7
   - Additional versions: `${ue_engine_5_6_path}`, `${ue_engine_5_8_path}`, etc. (Project may define as needed)

Common default installs on Windows (example only, always resolve dynamically):
- `5.7` → `C:\Program Files\Epic Games\UE_5.7`
- `5.6` → `C:\Program Files\Epic Games\UE_5.6`
- `5.5` → `C:\Program Files\Epic Games\UE_5.5`

## UE Project Folder Structure (Template)

Template path (Project-configurable): `${perforce_workspace_root}/3_Template/TemplateProject`

```
Content/
├── 00_Project/
│   ├── Assets/
│   │   ├── Arch/              # Architecture assets
│   │   ├── Chr/               # Character assets
│   │   ├── Decals/
│   │   ├── FX/                # Effects
│   │   ├── HDRs/
│   │   ├── MasterMaterials/
│   │   ├── MaterialFunctions/
│   │   ├── Props/             # Props
│   │   ├── SetDecs/           # Set decorations
│   │   ├── Terrain/
│   │   └── Vegetation/
│   ├── Envs/                  # Environments / Levels
│   ├── Media/                 # Media files
│   ├── Sequences/             # Sequencer
│   └── Tools/
│       └── OCIO/luts/         # Color management
├── Characters/
│   └── Mannequins/            # Default mannequin (Anims, Materials, Meshes, Rigs, Textures)
```

## UE Asset Naming Convention

→ **`asset-naming.md` 참조** (전체 Prefix/Suffix 목록, 같은 rules/ 디렉토리)

## VR Rendering

VR 프로젝트는 성능 마진이 짧아(Quest 2 = 72fps = 13.8ms · Quest 3/Index = 90fps = 11.1ms) **단계적 최적화 적용** 필수. Optimazation 플러그인의 Tips 위젯에서 VR-Base → VR-Performance → VR-Quality-Cut 순으로 적용.

### Tier 1 — VR-Base (필수 · 항상 ON)

| CVar | 값 | 이유 |
|---|---|---|
| `t.MaxFPS` | 72 | Quest 2 리프레시 (Quest 3/Index 는 90) |
| `vr.InstancedStereo` | 1 | 양안 단일 패스 — DrawCall 2배 절감. Forward Shading 필수 |
| `r.AntiAliasingMethod` | 5 | SMAA (아래 설명) |
| `r.DynamicGlobalIlluminationMethod` · `r.ReflectionMethod` · `r.Lumen.*` | 0 | Lumen 은 VR 미지원 · GPU 과부하 |
| `r.RayTracing.ForceAllRayTracingEffects` | 0 | RT 전체 킬 스위치 — RT Shadow/Reflection/GI 전부 강제 OFF |
| `vr.PixelDensity` | 0.8 | 80% 픽셀 밀도 + TSR 업스케일 |
| `r.MotionBlur.Max` | 0 | **VR 멀미 방지 — 강제 OFF** |

### Tier 2 — VR-Performance (72fps 미달 시)

| CVar | 값 | 이유 |
|---|---|---|
| `xr.VRS.FoveationLevel` | 2 | **단일 최대 최적화** — 주변부 저해상도 셰이딩 · 30-40% GPU 절감. OpenXR/Meta XR 하드웨어 VRS 필요 |
| `xr.VRS.DynamicFoveation` | 1 | GPU 부하 기반 자동 강도 |
| `xr.VRS.GazeTrackedFoveation` | 1 | 시선 추적 HMD (Quest Pro/Varjo) 전용 |
| `r.DynamicRes.OperationMode` | 2 | 타겟 프레임 유지용 동적 해상도 |
| `r.SSR.Quality` | 0 | SSR OFF |

### Tier 3 — VR-Quality-Cut (최후 수단 · 품질 하락)

`r.Shadow.DistanceScale=0.5` · `r.Shadow.MaxResolution=1024` · `r.DepthOfFieldQuality=0` · `r.BloomQuality=2` · `foliage.MinimumScreenSize=0.02` · `a.URO.Enable=1` · `r.HairStrands.Strands=0` · `r.Streaming.PoolSize=2048`.

### Project Settings (엔진 재시작 필요 · CVar 불가)

- **Rendering → Forward Shading** ON (InstancedStereo 전제)
- **Rendering → VR → Instanced Stereo** ON
- **Rendering → VR → Mobile Multi-View** ON (Mobile VR 타겟)
- **Rendering → VR → Round Robin Occlusion Queries** ON (CPU 부하 분산)
- **Rendering → Support Compute Skincache** ON
- **OpenXR/MetaXR Plugin Settings** → Foveated Rendering Enable
- **`DefaultEngine.ini` [/Script/Engine.RendererSettings]** → `r.DefaultFeature.MotionBlur=False`

### SMAA (Subpixel Morphological Anti-Aliasing)

`r.AntiAliasingMethod=5`. 화면 공간 3-pass (엣지 감지 → 형태 분류 → 블렌드). **공간(spatial) 전용 — 이전 프레임 정보 불필요 → 고스팅·플리커 0**. 시차로 고스팅이 심한 TAA(2)/TSR(4) 와 달리 VR 양안 렌더에 적합. 비용 순: FXAA < **SMAA** < TAA < MSAA 4x < TSR. 서브픽셀 디테일은 `vr.PixelDensity` 로 보완.

## Virtual Camera (V-Cam)

- iPad / iPhone based V-Cam
- LiveLink plugin integration required
- LiveLinkPreset: use `LLP_` prefix

## Facial Capture

- iPhone-based (ARKit)
- High-fidelity upgrade under review — processing overhead issue exists
- Live Link Face app integration

## Reference

- UE 5.7 Documentation: `dev.epicgames.com/documentation/.../unreal-engine-5-7-documentation`
- UE 5.6 Documentation: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/unreal-engine-5-6-documentation?application_version=5.6`
- UE C++ Programming: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/programming-with-cplusplus-in-unreal-engine`
- UE C++ API: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/API`
- Blueprint Visual Scripting: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/blueprints-visual-scripting-in-unreal-engine`
- Blueprint API: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/BlueprintAPI`
- UE Python API: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/PythonAPI`
- UE Node Reference: `https://dev.epicgames.com/documentation/ko-kr/unreal-engine/node-reference`

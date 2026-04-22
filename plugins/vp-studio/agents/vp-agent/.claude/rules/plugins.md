# VP Pipeline Plugins

## Plugin Root

**Perforce depot path (server-side):** `//VPO_depot/Plugins/Extra/UE_57/`

**Local workspace mapping (Project-configurable via userConfig):** `${vpo_plugin_root}/Extra/UE_57/`

> Plugin never hardcodes a local drive letter. Project sets `vpo_plugin_root` in its user configuration (e.g., `Z:/VPO/1_Plugins` for one studio, `C:/ws/VPO/1_Plugins` for another). If `vpo_plugin_root` is empty, plugin-related skills are disabled.
> Claude 작업 시 `${vpo_plugin_root}/Extra/UE_57/{PluginName}/Source/` 경로 사용.

## Plugin Registry

| Plugin | 경로 (relative to `${vpo_plugin_root}`) | 역할 | 상태 |
|---|---|---|---|
| **VPTools** | `Extra/UE_57/VPTools/` | 마스터 UI (EUW_VPMaster), 장비 라이브러리, LED 시뮬, MoCap 매니저 | v5.6.0 완성 |
| **Optimazation** | `Extra/UE_57/Optimazation/` | 실시간 VP 성능 모니터링, 프레임드롭 분석, GPU/LiveLink/Timecode 감시 | v0.1.0 개발중 · `OptEditorStyle` 팔레트는 [development.md](./development.md) UI Color Rules (UE 5.7 Starship Dark) 기준, 재빌드 시 신 팔레트로 갱신 |
| **EDLTools** | `Extra/UE_57/EDLTools/` | EDL 파싱/임포트/익스포트, Free Run TC 오프셋, 시퀀서 Shot Track 적용 | 완성 |
| **BSToFBXConverter** | `Extra/UE_57/BSToFBXConverter/` | BP/SM → FBX 배치 익스포트 (피벗 재계산, 텍스처 추출) | 완성 |
| **LocodromeToolkits** | `Extra/UE_57/LocodromeToolkits/` | Locodrome ↔ Agora Control Rig 브릿지, IK/FK, 포즈 미러링 | 완성 |
| **MLSLabsRenderer** | `Extra/UE_57/MLSLabsRenderer/` | Gaussian Splatting + 4DGS 볼류메트릭 비디오 (CUDA/LibTorch) | Beta (서드파티) |
| **AI Hand Tracking** | TBD | 핑거 트래킹 증강 | 다른 팀원 개발중 |

## Key APIs per Plugin

### VPTools
- **진입점:** Python `Toolbar.py` → `EUW_VPMaster` 위젯
- **모듈:** CineDesigner (장비), LEDSimulator, MocapManager, Ingestor, Renamer 등 18+ EUW
- **에셋 수:** 1,057개 (Blueprint, Material, Mesh, DataTable)

### Optimazation (VP Monitor)
- **서브시스템:** `UOptMonitoringSubsystem` (EngineSubsystem)
- **주요 클래스:**
  - `FOptFrameDropAnalyzer` — 프레임드롭 원인 분류 (GPU/GameThread/RenderThread/LiveLink/Timecode/Genlock 등)
  - `FOptGpuUsageMonitor` — NVML 기반 GPU 모니터링 (렌더 머신 A6000 + 워크스테이션 RTX 4090)
  - `FOptLiveLinkMonitor` — LiveLink 소스 상태/지연/드롭 감지
  - `FOptTimecodeMonitor` / `FOptGenlockMonitor` — 동기화 감시
  - `FOptActionDatabase` — JSON 기반 CVar 추천 액션 DB
  - `FOptDecisionHistory` — 사용자 결정 기록 (학습)
  - `UOptSetupProfile` — 시나리오별 CVar 프리셋 (Shooting/Previz/Rendering)
- **델리게이트:** `OnFrameDropDetected`, `OnSessionRiskDetected`, `OnLiveLinkStateChanged`
- **소스 위치:** `${vpo_plugin_root}/Extra/UE_57/Optimazation/Source/` (Public/Core, FrameAnalysis, GPU, LiveLink, SceneAnalysis, Profile)

### EDLTools
- **파서:** `FEDLParser` (static) — EDL 파일 파싱 + MovieScene 적용 + EDL 익스포트
- **데이터:** `FEDLEvent` (이벤트), `FEDLFileData` (파일), `FEDLImportSettings` (TC 오프셋 모드)
- **TC 오프셋 모드:** AutoOffset, ForceZero, Raw, Manual
- **UI:** `SEDLViewer` Slate 위젯 (Window > Virtual Production 메뉴)

### BSToFBXConverter
- **익스포터:** `FBSToFBXExporter` (static) — Blueprint → FBX 변환
- **기능:** 피벗 재계산, 텍스처 추출, 썸네일 렌더, 매니페스트 JSON 생성
- **UI:** `SBSToFBXWidget` (드래그앤드롭 패널)

### LocodromeToolkits
- **서브시스템:**
  - `ULocoRigSubsystem` — Control Rig 감지/분류 (Body/Face/BodyFace)
  - `ULocoMappingSubsystem` — MetaHuman ↔ Agora 네임 매핑 (JSON)
  - `ULocoPatchSubsystem` — Locodrome 위젯 패치, Tick Hook 기반 동적 변환
- **매핑 파일:** `Content/Locodrome/FacePicker/Mappings/MH_to_Agora_{CharName}.json`

### MLSLabsRenderer
- **렌더러:** Gaussian Splatting + 4DGS 볼류메트릭 비디오
- **의존성:** CUDA, LibTorch (PyTorch 2.7.0), DirectX 12, FBX SDK
- **제약:** Win64 전용, 컴파일된 DLL (소스 비공개)

## Plugin 코드 참조 규칙

1. 새 기능 구현 전 **반드시** 해당 플러그인에 이미 유사 기능이 있는지 확인
2. 플러그인 수정 시 `${vpo_plugin_root}/Extra/UE_57/{PluginName}/Source/` 경로에서 직접 작업 (userConfig 미설정 시 경고)
3. 플러그인 간 의존성 추가 시 `.uplugin` 파일의 Plugins 섹션에 명시
4. MLSLabsRenderer는 서드파티 — 소스 수정 불가, API 레벨에서만 연동

# Development Language Rules

## Python

- **UE Python Editor Scripting compatible** by default (`import unreal`)
- Must be executable within UE Editor
- Standalone scripts should use `if __name__ == "__main__":` guard

## C++

- Follow UE C++ Coding Standards (Epic Coding Guidelines)
- Plugin structure: place source in `plugins/` directory
- `.uplugin` manifest is required

## Blueprint

- Use EditorUtilityWidget (EUW) — Prefix: `EUW_`
- Complex logic should be implemented in C++ or Python, then called from Blueprint

## Common Rules

- **Write code comments in Korean**
- Use **PascalCase** naming (UE convention)
- **코드 작성 전 재사용 가능한 모듈 확인** — 프로젝트의 모듈 라이브러리에서 기존 구현 조회 후 신규 작성 (`modules.md` 규칙 참조)
- **새 스크립트 위치** — 프로젝트의 스크립트 디렉토리 컨벤션에 따라 도메인별 서브디렉토리에 배치 (예: `unreal/`, `optitrack/`, `perforce/`, `vp_equipment/`, `utils/`)
- **재사용 모듈 위치** — 프로젝트의 `modules/{domain}/{module_name}/` 컨벤션 사용

> **Note (Plugin 관점)**: 구체적 스크립트·모듈 경로는 Project 가 `tools_scripts_root`·`tools_modules_root` 등 userConfig 변수로 제공해야 한다. 위 가이드라인은 "이 위치에 있어야 한다" 가 아니라 "도메인별로 분리해 두어야 한다" 는 원칙 기술.

## UI Color Rules (UE 5.7 Editor — Starship Dark)

> UE 5.7 Engine Source 의 `StyleColors.cpp` (`InitalizeDefaults`) 에서 추출한 Starship Dark 테마 기준. 원본 경로는 Project 가 설정한 UE 설치 루트(예: `${ue_engine_5_7_path}/Engine/Source/Runtime/SlateCore/Private/Styling/StyleColors.cpp`).

Style definition file: `OptEditorStyle.h/.cpp` (또는 `{PluginName}EditorStyle.h/.cpp`)

### sRGB → Linear 변환 필수

HEX 열은 **sRGB** (포토샵/모니터에서 보이는 색). Slate 의 `FLinearColor` 는 **Linear** 색공간이므로 직접 hex/255 를 넣으면 감마가 이중 적용되어 밝아진다. 반드시 아래 방식 중 하나로 변환:

```cpp
// 방법 1 — FColor RGBA 바이트 (static init 안전, 권장)
FLinearColor::FromSRGBColor(FColor(0x24, 0x24, 0x24, 0xFF))

// 방법 2 — UE 엔진 매크로 (StyleColors.h 에서 정의)
#define COLOR(HexValue) FLinearColor::FromSRGBColor(FColor::FromHex(HexValue))
COLOR("242424FF")
```

### Background Colors

| Name | HEX (sRGB) | C++ 초기화 | Usage · `EStyleColor` |
|------|------|-------------|-------|
| BG_Dark | `#1A1A1A` | `FromSRGBColor(FColor(0x1A, 0x1A, 0x1A, 0xFF))` | Top-level background · `Recessed` |
| BG_Panel | `#242424` | `FromSRGBColor(FColor(0x24, 0x24, 0x24, 0xFF))` | Panel/header background · `Panel` |
| BG_Card | `#242424` | `FromSRGBColor(FColor(0x24, 0x24, 0x24, 0xFF))` | Card/section background · `Panel` |
| BG_CardHover | `#575757` | `FromSRGBColor(FColor(0x57, 0x57, 0x57, 0xFF))` | Card hover · `Hover` |

### Accent Colors

| Name | HEX (sRGB) | C++ 초기화 | Usage · `EStyleColor` |
|------|------|-------------|-------|
| Accent | `#26BBFF` | `FromSRGBColor(FColor(0x26, 0xBB, 0xFF, 0xFF))` | Primary accent · `AccentBlue` |
| AccentHover | `#0E86FF` | `FromSRGBColor(FColor(0x0E, 0x86, 0xFF, 0xFF))` | Hover · `PrimaryHover` |
| AccentDim | `#0050A0` | `FromSRGBColor(FColor(0x00, 0x50, 0xA0, 0xFF))` | Dimmed accent · `PrimaryPress` |
| AccentBG | `#26BBFF` α15% | `FLinearColor(FromSRGBColor(FColor(0x26, 0xBB, 0xFF)), 0.15f)` | Blue tint background |

### Status Indicators

| Name | HEX (sRGB) | C++ 초기화 | Usage · `EStyleColor` |
|------|------|-------------|-------|
| Status_Good | `#1FE44B` | `FromSRGBColor(FColor(0x1F, 0xE4, 0x4B, 0xFF))` | Normal/OK · `Success` |
| Status_Warning | `#FFB800` | `FromSRGBColor(FColor(0xFF, 0xB8, 0x00, 0xFF))` | Warning · `Warning` |
| Status_Error | `#EF3535` | `FromSRGBColor(FColor(0xEF, 0x35, 0x35, 0xFF))` | Error · `Error` |

### Text & Separators

| Name | HEX (sRGB) | C++ 초기화 | Usage · `EStyleColor` |
|------|------|-------------|-------|
| Text_Primary | `#C0C0C0` | `FromSRGBColor(FColor(0xC0, 0xC0, 0xC0, 0xFF))` | Primary text · `Foreground` |
| Text_Secondary | `#808080` | `FromSRGBColor(FColor(0x80, 0x80, 0x80, 0xFF))` | Secondary text · `AccentGray` |
| Separator | `#383838` | `FromSRGBColor(FColor(0x38, 0x38, 0x38, 0xFF))` | Divider line · `Dropdown` |

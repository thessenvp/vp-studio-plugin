---
name: new-plugin
description: UE 5.7 C++ plugin scaffolding — generates backend, frontend (Slate), batch scripts, and README.
allowed-tools: Bash Read Write Glob Grep Edit
argument-hint: "PluginName [--description \"설명\"] [--subsystem] [--slate]"
---

# Create New UE 5.7 Plugin

인자: $ARGUMENTS

## 0. 사전 조건 — vpo_plugin_root 필수

**이 스킬은 userConfig `vpo_plugin_root` 가 설정되어 있어야 동작**한다. UE 플러그인은 Perforce 로 관리되는 로컬 workspace 아래에 생성되므로 Project 가 해당 경로를 알려줘야 한다.

- 미설정/빈 값이면 스킬 중단. 유저에게 안내:
  ```
  🚫 new-plugin 중단 — userConfig `vpo_plugin_root` 미설정.
    Plugin 설정에서 Perforce VPO 플러그인 workspace 로컬 경로를 지정하세요.
    예: Z:/VPO/1_Plugins  또는  C:/ws/VPO/1_Plugins
  ```
- 설정되어 있으면 `${vpo_plugin_root}/Extra/UE_57/` 가 쓰기 가능한지 확인 (Bash `test -d` + `touch` 드라이런).

## 1. 인자 파싱

`$ARGUMENTS`에서 다음을 추출:

| 인자 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `PluginName` | O | — | 첫 번째 위치 인자, PascalCase |
| `--description "..."` | X | `"VP Pipeline Plugin"` | 플러그인 설명 |
| `--subsystem` | X | false | Runtime+Editor 듀얼 모듈 + UEngineSubsystem |
| `--slate` | X | false | Slate UI 패널 + EditorStyle(UE 5.7 Starship Dark) |

## 2. 유효성 검사

1. `PluginName`이 PascalCase인지 확인 (첫 글자 대문자, 공백/특수문자 없음)
2. `${vpo_plugin_root}/Extra/UE_57/{PluginName}/` 경로가 이미 존재하지 않는지 확인
3. 인자 누락 시 사용법 출력 후 중단

## 3. 파일 생성

**루트 경로:** `${vpo_plugin_root}/Extra/UE_57/{PluginName}/`

---

### 3.1 {PluginName}.uplugin

**기본 (--subsystem 없음):**

```json
{
	"FileVersion": 3,
	"Version": 1,
	"VersionName": "0.1.0",
	"FriendlyName": "{PluginName}",
	"Description": "{Description}",
	"Category": "Virtual Production",
	"CreatedBy": "VP-Studio",
	"CanContainContent": true,
	"EnabledByDefault": true,
	"Modules": [
		{
			"Name": "{PluginName}",
			"Type": "Editor",
			"LoadingPhase": "PostEngineInit"
		}
	]
}
```

**--subsystem 사용 시:**

```json
{
	"FileVersion": 3,
	"Version": 1,
	"VersionName": "0.1.0",
	"FriendlyName": "{PluginName}",
	"Description": "{Description}",
	"Category": "Virtual Production",
	"CreatedBy": "VP-Studio",
	"CanContainContent": true,
	"EnabledByDefault": true,
	"Modules": [
		{
			"Name": "{PluginName}",
			"Type": "Runtime",
			"LoadingPhase": "Default"
		},
		{
			"Name": "{PluginName}Editor",
			"Type": "Editor",
			"LoadingPhase": "Default"
		}
	]
}
```

---

### 3.2 Build.cs

**기본 (단일 Editor 모듈) — `Source/{PluginName}/{PluginName}.Build.cs`:**

```csharp
// Copyright VP-Studio. All Rights Reserved.

using UnrealBuildTool;

public class {PluginName} : ModuleRules
{
	public {PluginName}(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Slate",
			"SlateCore",
			"UnrealEd",
			"ToolMenus",
			"WorkspaceMenuStructure",
			"Projects",
		});
	}
}
```

**--subsystem 사용 시 Runtime 모듈 — `Source/{PluginName}/{PluginName}.Build.cs`:**

```csharp
// Copyright VP-Studio. All Rights Reserved.

using UnrealBuildTool;

public class {PluginName} : ModuleRules
{
	public {PluginName}(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Json",
		});

		// 에디터 전용 기능
		if (Target.Type == TargetType.Editor)
		{
			PrivateDependencyModuleNames.Add("UnrealEd");
		}
	}
}
```

**--subsystem 사용 시 Editor 모듈 — `Source/{PluginName}Editor/{PluginName}Editor.Build.cs`:**

```csharp
// Copyright VP-Studio. All Rights Reserved.

using UnrealBuildTool;

public class {PluginName}Editor : ModuleRules
{
	public {PluginName}Editor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"{PluginName}",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"Slate",
			"SlateCore",
			"InputCore",
			"UnrealEd",
			"LevelEditor",
			"WorkspaceMenuStructure",
			"Projects",
			"ToolMenus",
		});
	}
}
```

---

### 3.3 Module.h / Module.cpp

**기본 (단일 Editor 모듈)**

**`Source/{PluginName}/Public/{PluginName}Module.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class F{PluginName}Module : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	/** 탭 스포너 등록 */
	void RegisterTabSpawner();
	/** 탭 스포너 해제 */
	void UnregisterTabSpawner();
	/** 메뉴 확장 등록 */
	void RegisterMenuExtensions();
	/** 메인 탭 생성 */
	TSharedRef<class SDockTab> SpawnMainTab(const class FSpawnTabArgs& Args);
};
```

**`Source/{PluginName}/Private/{PluginName}Module.cpp`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#include "{PluginName}Module.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Text/STextBlock.h"
#include "Framework/Docking/TabManager.h"
#include "WorkspaceMenuStructure.h"
#include "WorkspaceMenuStructureModule.h"
#include "ToolMenus.h"
#include "Styling/AppStyle.h"

#define LOCTEXT_NAMESPACE "{PluginName}"

static const FName {PluginName}TabId("{PluginName}Tab");

void F{PluginName}Module::StartupModule()
{
	RegisterTabSpawner();
	RegisterMenuExtensions();

	UE_LOG(LogTemp, Log, TEXT("{PluginName}: 모듈 시작"));
}

void F{PluginName}Module::ShutdownModule()
{
	UnregisterTabSpawner();

	UE_LOG(LogTemp, Log, TEXT("{PluginName}: 모듈 종료"));
}

void F{PluginName}Module::RegisterTabSpawner()
{
	FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
		{PluginName}TabId,
		FOnSpawnTab::CreateRaw(this, &F{PluginName}Module::SpawnMainTab))
		.SetDisplayName(LOCTEXT("TabTitle", "{PluginName}"))
		.SetTooltipText(LOCTEXT("TabTooltip", "{Description}"))
		.SetGroup(WorkspaceMenu::GetMenuStructure().GetToolsCategory())
		.SetIcon(FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports"));
}

void F{PluginName}Module::UnregisterTabSpawner()
{
	FGlobalTabmanager::Get()->UnregisterNomadTabSpawner({PluginName}TabId);
}

void F{PluginName}Module::RegisterMenuExtensions()
{
	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateLambda([]()
	{
		UToolMenu* WindowMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
		if (WindowMenu)
		{
			FToolMenuSection& Section = WindowMenu->FindOrAddSection("VirtualProduction");
			Section.Label = LOCTEXT("VPSection", "Virtual Production");

			Section.AddMenuEntry(
				"Open{PluginName}",
				LOCTEXT("MenuLabel", "{PluginName}"),
				LOCTEXT("MenuTooltip", "{Description}"),
				FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports"),
				FUIAction(FExecuteAction::CreateLambda([]()
				{
					FGlobalTabmanager::Get()->TryInvokeTab({PluginName}TabId);
				}))
			);
		}
	}));
}

TSharedRef<SDockTab> F{PluginName}Module::SpawnMainTab(const FSpawnTabArgs& Args)
{
	return SNew(SDockTab)
		.TabRole(ETabRole::NomadTab)
		.Label(LOCTEXT("TabLabel", "{PluginName}"))
		[
			SNew(STextBlock)
			.Text(LOCTEXT("Placeholder", "{PluginName} — 여기에 UI를 구현하세요"))
		];
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(F{PluginName}Module, {PluginName})
```

**--subsystem 사용 시:**

Runtime 모듈은 최소한의 Module.h/.cpp만 생성 (탭/메뉴 없음):

**`Source/{PluginName}/Public/{PluginName}Module.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class F{PluginName}Module : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};
```

**`Source/{PluginName}/Private/{PluginName}Module.cpp`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#include "{PluginName}Module.h"

#define LOCTEXT_NAMESPACE "{PluginName}"

void F{PluginName}Module::StartupModule()
{
	UE_LOG(LogTemp, Log, TEXT("{PluginName}: Runtime 모듈 시작"));
}

void F{PluginName}Module::ShutdownModule()
{
	UE_LOG(LogTemp, Log, TEXT("{PluginName}: Runtime 모듈 종료"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(F{PluginName}Module, {PluginName})
```

Editor 모듈의 Module.h/.cpp (탭/메뉴 포함):

**`Source/{PluginName}Editor/Public/{PluginName}EditorModule.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class F{PluginName}EditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	void RegisterTabSpawner();
	void UnregisterTabSpawner();
	void RegisterMenuExtensions();
	TSharedRef<class SDockTab> SpawnMainTab(const class FSpawnTabArgs& Args);
};
```

**`Source/{PluginName}Editor/Private/{PluginName}EditorModule.cpp`:**

위의 기본 Module.cpp와 동일한 구조이나:
- 클래스명: `F{PluginName}EditorModule`
- IMPLEMENT_MODULE: `IMPLEMENT_MODULE(F{PluginName}EditorModule, {PluginName}Editor)`
- `--slate` 플래그 시 SpawnMainTab에서 `SNew(S{PluginName}Panel)` 사용

---

### 3.4 Subsystem (--subsystem 시에만)

**`Source/{PluginName}/Public/{PluginName}Subsystem.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "{PluginName}Subsystem.generated.h"

/**
 * {PluginName} 엔진 서브시스템
 * 엔진 라이프사이클에 따라 자동 생성/소멸
 */
UCLASS()
class {PluginName_UPPER}_API U{PluginName}Subsystem : public UEngineSubsystem
{
	GENERATED_BODY()

public:
	// USubsystem 인터페이스
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	/** 서브시스템 인스턴스 가져오기 */
	static U{PluginName}Subsystem* Get();
};
```

- `{PluginName_UPPER}`은 PluginName을 대문자로 변환 (예: `MyTool` → `MYTOOL`)

**`Source/{PluginName}/Private/{PluginName}Subsystem.cpp`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#include "{PluginName}Subsystem.h"

void U{PluginName}Subsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	UE_LOG(LogTemp, Log, TEXT("{PluginName}: 서브시스템 초기화"));
}

void U{PluginName}Subsystem::Deinitialize()
{
	UE_LOG(LogTemp, Log, TEXT("{PluginName}: 서브시스템 종료"));
	Super::Deinitialize();
}

U{PluginName}Subsystem* U{PluginName}Subsystem::Get()
{
	return GEngine->GetEngineSubsystem<U{PluginName}Subsystem>();
}
```

---

### 3.5 Slate UI (--slate 시에만)

> `--subsystem`과 함께 사용 시 Editor 모듈(`Source/{PluginName}Editor/`)에 생성
> `--subsystem` 없이 사용 시 단일 모듈(`Source/{PluginName}/`)에 생성

**EditorStyle — `{EditorModule}/Private/Style/{PluginName}EditorStyle.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Styling/SlateStyle.h"

/**
 * {PluginName} 에디터 스타일
 * UE 5.7 Starship Dark 테마 기반 (FStyleColors 와 동일 값)
 * 런타임 호출 가능 시 FStyleColors::Get(EStyleColor::XXX) 우선. 아래 상수는 컴파일 타임 고정값 용도.
 */
class F{PluginName}EditorStyle
{
public:
	static void Initialize();
	static void Shutdown();
	static const ISlateStyle& Get();
	static FName GetStyleSetName();

	// 배경색 (블랙 톤)
	static const FLinearColor BG_Dark;
	static const FLinearColor BG_Panel;
	static const FLinearColor BG_Card;
	static const FLinearColor BG_CardHover;

	// 블루 포인트
	static const FLinearColor Accent;
	static const FLinearColor AccentHover;
	static const FLinearColor AccentDim;
	static const FLinearColor AccentBG;

	// 상태 표시
	static const FLinearColor Status_Good;
	static const FLinearColor Status_Warning;
	static const FLinearColor Status_Error;

	// 텍스트
	static const FLinearColor Text_Primary;
	static const FLinearColor Text_Secondary;

	// 구분선
	static const FLinearColor Separator;

private:
	static TSharedPtr<FSlateStyleSet> StyleInstance;
	static void Create();
};
```

**EditorStyle — `{EditorModule}/Private/Style/{PluginName}EditorStyle.cpp`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#include "Style/{PluginName}EditorStyle.h"
#include "Styling/SlateStyleRegistry.h"
#include "Styling/SlateTypes.h"
#include "Styling/CoreStyle.h"

// 컬러 정의 — UE 5.7 Starship Dark (sRGB HEX → Linear 변환)
// HEX 는 sRGB, FLinearColor 는 Linear — 반드시 FromSRGBColor 사용
const FLinearColor F{PluginName}EditorStyle::BG_Dark       = FLinearColor::FromSRGBColor(FColor(0x1A, 0x1A, 0x1A, 0xFF)); // #1A1A1A Recessed
const FLinearColor F{PluginName}EditorStyle::BG_Panel      = FLinearColor::FromSRGBColor(FColor(0x24, 0x24, 0x24, 0xFF)); // #242424 Panel
const FLinearColor F{PluginName}EditorStyle::BG_Card       = FLinearColor::FromSRGBColor(FColor(0x24, 0x24, 0x24, 0xFF)); // #242424 Panel
const FLinearColor F{PluginName}EditorStyle::BG_CardHover  = FLinearColor::FromSRGBColor(FColor(0x57, 0x57, 0x57, 0xFF)); // #575757 Hover

const FLinearColor F{PluginName}EditorStyle::Accent        = FLinearColor::FromSRGBColor(FColor(0x26, 0xBB, 0xFF, 0xFF)); // #26BBFF AccentBlue
const FLinearColor F{PluginName}EditorStyle::AccentHover   = FLinearColor::FromSRGBColor(FColor(0x0E, 0x86, 0xFF, 0xFF)); // #0E86FF PrimaryHover
const FLinearColor F{PluginName}EditorStyle::AccentDim     = FLinearColor::FromSRGBColor(FColor(0x00, 0x50, 0xA0, 0xFF)); // #0050A0 PrimaryPress
const FLinearColor F{PluginName}EditorStyle::AccentBG      = FLinearColor(Accent.R, Accent.G, Accent.B, 0.15f); // AccentBlue α0.15

const FLinearColor F{PluginName}EditorStyle::Status_Good    = FLinearColor::FromSRGBColor(FColor(0x1F, 0xE4, 0x4B, 0xFF)); // #1FE44B Success
const FLinearColor F{PluginName}EditorStyle::Status_Warning = FLinearColor::FromSRGBColor(FColor(0xFF, 0xB8, 0x00, 0xFF)); // #FFB800 Warning
const FLinearColor F{PluginName}EditorStyle::Status_Error   = FLinearColor::FromSRGBColor(FColor(0xEF, 0x35, 0x35, 0xFF)); // #EF3535 Error

const FLinearColor F{PluginName}EditorStyle::Text_Primary   = FLinearColor::FromSRGBColor(FColor(0xC0, 0xC0, 0xC0, 0xFF)); // #C0C0C0 Foreground
const FLinearColor F{PluginName}EditorStyle::Text_Secondary = FLinearColor::FromSRGBColor(FColor(0x80, 0x80, 0x80, 0xFF)); // #808080 AccentGray

const FLinearColor F{PluginName}EditorStyle::Separator      = FLinearColor::FromSRGBColor(FColor(0x38, 0x38, 0x38, 0xFF)); // #383838 Dropdown

TSharedPtr<FSlateStyleSet> F{PluginName}EditorStyle::StyleInstance = nullptr;

void F{PluginName}EditorStyle::Initialize()
{
	if (!StyleInstance.IsValid())
	{
		Create();
		FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);
	}
}

void F{PluginName}EditorStyle::Shutdown()
{
	if (StyleInstance.IsValid())
	{
		FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
		StyleInstance.Reset();
	}
}

const ISlateStyle& F{PluginName}EditorStyle::Get()
{
	check(StyleInstance.IsValid());
	return *StyleInstance;
}

FName F{PluginName}EditorStyle::GetStyleSetName()
{
	static FName StyleSetName(TEXT("{PluginName}Style"));
	return StyleSetName;
}

void F{PluginName}EditorStyle::Create()
{
	StyleInstance = MakeShareable(new FSlateStyleSet(GetStyleSetName()));

	// 폰트 설정
	const FSlateFontInfo HeaderFont = FCoreStyle::GetDefaultFontStyle("Bold", 18);
	const FSlateFontInfo BodyFont = FCoreStyle::GetDefaultFontStyle("Regular", 12);
	const FSlateFontInfo DetailFont = FCoreStyle::GetDefaultFontStyle("Regular", 10);

	StyleInstance->Set("{PluginName}.Font.Header", HeaderFont);
	StyleInstance->Set("{PluginName}.Font.Body", BodyFont);
	StyleInstance->Set("{PluginName}.Font.Detail", DetailFont);

	// 브러시 등록
	StyleInstance->Set("{PluginName}.Brush.DarkBG", new FSlateColorBrush(BG_Dark));
	StyleInstance->Set("{PluginName}.Brush.PanelBG", new FSlateColorBrush(BG_Panel));
	StyleInstance->Set("{PluginName}.Brush.CardBG", new FSlateColorBrush(BG_Card));
	StyleInstance->Set("{PluginName}.Brush.AccentBG", new FSlateColorBrush(AccentBG));
	StyleInstance->Set("{PluginName}.Brush.Separator", new FSlateColorBrush(Separator));

	// 버튼 스타일
	FButtonStyle DarkButton = FCoreStyle::Get().GetWidgetStyle<FButtonStyle>("Button");
	DarkButton.SetNormal(FSlateColorBrush(BG_Card));
	DarkButton.SetHovered(FSlateColorBrush(AccentDim));
	DarkButton.SetPressed(FSlateColorBrush(Accent));
	DarkButton.SetNormalPadding(FMargin(8.0f, 4.0f));
	DarkButton.SetPressedPadding(FMargin(8.0f, 4.0f));
	StyleInstance->Set("{PluginName}.Button", DarkButton);
}
```

**Panel — `{EditorModule}/Public/UI/S{PluginName}Panel.h`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

/**
 * {PluginName} 메인 패널
 */
class S{PluginName}Panel : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(S{PluginName}Panel) {}
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);
};
```

**Panel — `{EditorModule}/Private/UI/S{PluginName}Panel.cpp`:**

```cpp
// Copyright VP-Studio. All Rights Reserved.

#include "UI/S{PluginName}Panel.h"
#include "Style/{PluginName}EditorStyle.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "{PluginName}"

void S{PluginName}Panel::Construct(const FArguments& InArgs)
{
	ChildSlot
	[
		// 최상위 배경
		SNew(SBorder)
		.BorderImage(FCoreStyle::Get().GetBrush("GenericWhiteBox"))
		.BorderBackgroundColor(F{PluginName}EditorStyle::BG_Dark)
		.Padding(8.0f)
		[
			SNew(SVerticalBox)

			// 헤더
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(0, 0, 0, 8)
			[
				SNew(SBorder)
				.BorderImage(FCoreStyle::Get().GetBrush("GenericWhiteBox"))
				.BorderBackgroundColor(F{PluginName}EditorStyle::BG_Panel)
				.Padding(16.0f, 12.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("Title", "{PluginName}"))
					.Font(FCoreStyle::GetDefaultFontStyle("Bold", 18))
					.ColorAndOpacity(F{PluginName}EditorStyle::Text_Primary)
				]
			]

			// 컨텐츠 영역
			+ SVerticalBox::Slot()
			.FillHeight(1.0f)
			[
				SNew(SBorder)
				.BorderImage(FCoreStyle::Get().GetBrush("GenericWhiteBox"))
				.BorderBackgroundColor(F{PluginName}EditorStyle::BG_Card)
				.Padding(16.0f)
				[
					SNew(STextBlock)
					.Text(LOCTEXT("Placeholder", "여기에 컨텐츠를 구현하세요"))
					.Font(FCoreStyle::GetDefaultFontStyle("Regular", 12))
					.ColorAndOpacity(F{PluginName}EditorStyle::Text_Secondary)
				]
			]
		]
	];
}

#undef LOCTEXT_NAMESPACE
```

**--slate 사용 시 Module.cpp의 SpawnMainTab 변경:**

```cpp
// #include "UI/S{PluginName}Panel.h" 추가
// #include "Style/{PluginName}EditorStyle.h" 추가

// StartupModule()에 추가:
F{PluginName}EditorStyle::Initialize();

// ShutdownModule()에 추가:
F{PluginName}EditorStyle::Shutdown();

// SpawnMainTab 내용 변경:
TSharedRef<SDockTab> ...::SpawnMainTab(const FSpawnTabArgs& Args)
{
	return SNew(SDockTab)
		.TabRole(ETabRole::NomadTab)
		.Label(LOCTEXT("TabLabel", "{PluginName}"))
		[
			SNew(S{PluginName}Panel)
		];
}
```

---

### 3.6 Batch 파일

Batch 스크립트는 UE 엔진 경로를 **Windows 레지스트리에서 자동 탐색**하고, 실패 시 fallback 순서로 해결:

1. 레지스트리 `HKLM\SOFTWARE\EpicGames\Unreal Engine\5.7\InstalledDirectory`
2. 환경변수 `UE_ENGINE_5_7` (있으면)
3. userConfig `ue_engine_5_7_path` 기본값 (`C:\Program Files\Epic Games\UE_5.7`)

**`Batch/Build.bat`:**

```bat
@echo off
REM {PluginName} - 플러그인 빌드
REM UE 5.7 엔진 경로 자동 탐색

set PLUGIN_NAME={PluginName}
set PLUGIN_DIR=%~dp0..

REM 1) 레지스트리에서 UE 5.7 경로 탐색
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\EpicGames\Unreal Engine\5.7" /v "InstalledDirectory" 2^>nul') do set ENGINE_DIR=%%b

REM 2) 실패 시 환경변수
if not defined ENGINE_DIR if defined UE_ENGINE_5_7 set ENGINE_DIR=%UE_ENGINE_5_7%

REM 3) 최종 fallback (userConfig ue_engine_5_7_path 기본값과 동일)
if not defined ENGINE_DIR (
    echo [WARN] UE 5.7 설치 경로를 레지스트리/환경변수에서 못 찾음. 기본 경로 시도...
    set ENGINE_DIR=C:\Program Files\Epic Games\UE_5.7
)

echo 엔진 경로: %ENGINE_DIR%
echo 플러그인: %PLUGIN_DIR%\%PLUGIN_NAME%.uplugin

set UAT="%ENGINE_DIR%\Engine\Build\BatchFiles\RunUAT.bat"

if not exist %UAT% (
    echo [ERROR] RunUAT.bat를 찾을 수 없습니다: %UAT%
    pause
    exit /b 1
)

call %UAT% BuildPlugin -Plugin="%PLUGIN_DIR%\%PLUGIN_NAME%.uplugin" -Package="%PLUGIN_DIR%\Binaries" -TargetPlatforms=Win64
pause
```

**`Batch/Package.bat`:**

```bat
@echo off
REM {PluginName} - 플러그인 패키징
REM UE 5.7 엔진 경로 자동 탐색

set PLUGIN_NAME={PluginName}
set PLUGIN_DIR=%~dp0..
set OUTPUT_DIR=%PLUGIN_DIR%\Package

REM 1) 레지스트리에서 UE 5.7 경로 탐색
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\EpicGames\Unreal Engine\5.7" /v "InstalledDirectory" 2^>nul') do set ENGINE_DIR=%%b

REM 2) 실패 시 환경변수
if not defined ENGINE_DIR if defined UE_ENGINE_5_7 set ENGINE_DIR=%UE_ENGINE_5_7%

REM 3) 최종 fallback
if not defined ENGINE_DIR (
    echo [WARN] UE 5.7 설치 경로를 찾지 못함. 기본 경로 시도...
    set ENGINE_DIR=C:\Program Files\Epic Games\UE_5.7
)

echo 엔진 경로: %ENGINE_DIR%
echo 출력 경로: %OUTPUT_DIR%

set UAT="%ENGINE_DIR%\Engine\Build\BatchFiles\RunUAT.bat"

if not exist %UAT% (
    echo [ERROR] RunUAT.bat를 찾을 수 없습니다: %UAT%
    pause
    exit /b 1
)

call %UAT% BuildPlugin -Plugin="%PLUGIN_DIR%\%PLUGIN_NAME%.uplugin" -Package="%OUTPUT_DIR%" -TargetPlatforms=Win64 -Rocket
pause
```

> Plugin 생성 시 `${ue_engine_5_7_path}` userConfig 값이 설정되어 있으면 Batch 파일의 fallback 경로(3번)를 해당 값으로 **치환 후 작성**. 설정 없으면 기본 `C:\Program Files\Epic Games\UE_5.7` 유지.

---

### 3.7 README.md

```markdown
# {PluginName}

{Description}

## 설치

1. 플러그인 폴더를 UE 프로젝트의 `Plugins/` 디렉토리에 복사
2. UE Editor 실행 → Edit > Plugins → "{PluginName}" 검색 → 활성화
3. Editor 재시작

## 사용법

- **메뉴:** Window > Virtual Production > {PluginName}

## API Reference

(구현 후 작성)

## Changelog

### v0.1.0
- 초기 스캐폴딩 생성
```

---

### 3.8 빈 디렉토리 생성

Bash로 실행:

```bash
mkdir -p "${vpo_plugin_root}/Extra/UE_57/{PluginName}/Content"
mkdir -p "${vpo_plugin_root}/Extra/UE_57/{PluginName}/Resources"
```

- `--subsystem` 없이, `--slate` 없을 때: `Source/{PluginName}/Public/Core/`, `Source/{PluginName}/Public/UI/`, `Source/{PluginName}/Private/Core/`, `Source/{PluginName}/Private/UI/` 도 생성
- `--subsystem` 시: 위 Core/UI 구조를 각 모듈에 맞게 생성

## 4. 후처리

### 4.1 Project 의 plugins.md 레지스트리 업데이트 (Project 책임)

Plugin 이 생성한 새 플러그인은 Project 가 관리하는 **VP 플러그인 레지스트리**에 추가되어야 다른 팀원/에이전트가 인지할 수 있다. 위치:

- Plugin 내장: `${CLAUDE_PLUGIN_ROOT}/agents/vp-agent/.claude/rules/plugins.md` — 표준 VP-Studio 플러그인 7종 등재됨 (참고용)
- Project 책임: Project 가 자체 `.claude/rules/plugins.md` 또는 유사 문서를 보유하면 거기에 새 행 추가

추가할 행 예시:
```markdown
| **{PluginName}** | `Extra/UE_57/{PluginName}/` | {Description} | v0.1.0 개발중 |
```

> Plugin 은 Project 의 rules 파일을 직접 수정하지 않는다. 유저에게 안내만 제공 — Project agent 또는 유저가 직접 반영.

### 4.2 생성 요약 출력

생성된 파일 목록과 다음 단계 안내:

```
✅ {PluginName} 플러그인 생성 완료!

경로: ${vpo_plugin_root}/Extra/UE_57/{PluginName}/

생성된 파일:
  - {PluginName}.uplugin
  - Source/{PluginName}/{PluginName}.Build.cs
  - Source/{PluginName}/Public/{PluginName}Module.h
  - Source/{PluginName}/Private/{PluginName}Module.cpp
  - (--subsystem/--slate 시 추가 파일)
  - Batch/Build.bat
  - Batch/Package.bat
  - README.md

다음 단계:
  1. UE Editor에서 플러그인 활성화
  2. Source/Private/Core/ 에 백엔드 로직 구현
  3. --slate 미사용 시: Source/Private/UI/ 에 UI 구현
  4. Project 의 plugins.md 레지스트리에 새 플러그인 추가 (선택)
```

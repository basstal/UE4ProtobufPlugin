// Copyright Epic Games, Inc. All Rights Reserved.

#include "Protobuf.h"

#include "ProtobufSetting.h"
#include "Misc/BlacklistNames.h"

#if WITH_EDITOR
#include "ISettingsModule.h"
#include "Settings/ProjectPackagingSettings.h"
#include "AssetViewUtils.h"
#include "IContentBrowserDataModule.h"
#include "ContentBrowserDataSubsystem.h"
#include "ContentBrowserFileDataSource.h"
#endif // WITH_EDITOR

#define LOCTEXT_NAMESPACE "FProtobufModule"


DEFINE_LOG_CATEGORY(LogProtobuf)

void FProtobufModule::StartupModule()
{
	RegisterSettings();
#if WITH_EDITOR
	RegisterExcelFileType();
#endif // WITH_EDITOR 
}

void FProtobufModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
}

void FProtobufModule::RegisterExcelFileType()
{
#if WITH_EDITOR

	// Initialize the tick handler
	TickHandle = FTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([this](float DeltaTime)
	{
		QUICK_SCOPE_CYCLE_COUNTER(STAT_FProtobufModule_Tick);
		Tick(DeltaTime);
		return true;
	}));
	
	ContentBrowserFileData::FFileConfigData ExcelFileConfig;
	{
		auto ExcelItemPassesFilter = [](const FName InFilePath, const FString& InFilename, const FContentBrowserDataFilter& InFilter, const bool bIsFile)
		{
			const FContentBrowserDataPackageFilter* PackageFilter = InFilter.ExtraFilters.FindFilter<FContentBrowserDataPackageFilter>();
			if (PackageFilter && PackageFilter->PathBlacklist && PackageFilter->PathBlacklist->HasFiltering())
			{
				return PackageFilter->PathBlacklist->PassesStartsWithFilter(InFilePath, /*bAllowParentPaths*/!bIsFile);
			}

			return true;
		};
		auto GetExcelItemAttribute = [](const FName InFilePath, const FString& InFilename, const bool InIncludeMetaData, const FName InAttributeKey, FContentBrowserItemDataAttributeValue& OutAttributeValue)
		{
			// TODO: Need to way to avoid all this ToString() churn (FPackageNameView?)

			if (InAttributeKey == ContentBrowserItemAttributes::ItemIsDeveloperContent)
			{
				const bool bIsDevelopersFolder = AssetViewUtils::IsDevelopersFolder(InFilePath.ToString());
				OutAttributeValue.SetValue(bIsDevelopersFolder);
				return true;
			}

			if (InAttributeKey == ContentBrowserItemAttributes::ItemIsLocalizedContent)
			{
				const bool bIsLocalizedFolder = FPackageName::IsLocalizedPackage(InFilePath.ToString());
				OutAttributeValue.SetValue(bIsLocalizedFolder);
				return true;
			}

			if (InAttributeKey == ContentBrowserItemAttributes::ItemIsEngineContent)
			{
				const bool bIsEngineFolder = AssetViewUtils::IsEngineFolder(InFilePath.ToString(), /*bIncludePlugins*/true);
				OutAttributeValue.SetValue(bIsEngineFolder);
				return true;
			}

			if (InAttributeKey == ContentBrowserItemAttributes::ItemIsProjectContent)
			{
				const bool bIsProjectFolder = AssetViewUtils::IsProjectFolder(InFilePath.ToString(), /*bIncludePlugins*/true);
				OutAttributeValue.SetValue(bIsProjectFolder);
				return true;
			}

			if (InAttributeKey == ContentBrowserItemAttributes::ItemIsPluginContent)
			{
				const bool bIsPluginFolder = AssetViewUtils::IsPluginFolder(InFilePath.ToString());
				OutAttributeValue.SetValue(bIsPluginFolder);
				return true;
			}

			return false;
		};
		auto ExcelItemPreview = [this](const FName InFilePath, const FString& InFilename)
		{
			// ExecPythonCommand(*InFilename);
			return true;
		};

		auto ExcelItemEdit = [this](const FName InFilePath, const FString& InFilename)
		{
			FString EditorPath = GetDefault<UProtobufUserSetting>()->ExcelExec;
			if (EditorPath.IsEmpty())
			{
				UE_LOG(LogProtobuf, Warning, TEXT("Editor Preferences -> ExcelExec is not set properly, set your exe file path which you prefer edit excel file."))
				return false;
			}
			FPlatformProcess::CreateProc(*EditorPath, *InFilename, true, false, false, nullptr, 0, nullptr, nullptr);
			return true;
		};

		auto ExcelItemCanEdit = [this](const FName InFilePath, const FString& InFilename, FText* OutErrorMsg)
		{
			return true;
		};
		ContentBrowserFileData::FDirectoryActions ExcelDirectoryActions;
		ExcelDirectoryActions.PassesFilter.BindLambda(ExcelItemPassesFilter, false);
		ExcelDirectoryActions.GetAttribute.BindLambda(GetExcelItemAttribute);
		ExcelFileConfig.SetDirectoryActions(ExcelDirectoryActions);
		
		ContentBrowserFileData::FFileActions ExcelFileActions;
		ExcelFileActions.TypeExtension = TEXT("xlsx");
		ExcelFileActions.TypeName = "Excel";
		ExcelFileActions.TypeDisplayName = LOCTEXT("ExcelTypeName", "Excel");
		ExcelFileActions.TypeShortDescription = LOCTEXT("ExcelTypeShortDescription", "Excel");
		ExcelFileActions.TypeFullDescription = LOCTEXT("ExcelTypeFullDescription", "data table created by Microsoft Office Excel");
		// ExcelFileActions.DefaultNewFileName = TEXT("new_excel");
		ExcelFileActions.TypeColor = FColor::Green;
		ExcelFileActions.PassesFilter.BindLambda(ExcelItemPassesFilter, true);
		ExcelFileActions.GetAttribute.BindLambda(GetExcelItemAttribute);
		// ExcelFileActions.Preview.BindLambda(ExcelItemPreview);
		ExcelFileActions.CanEdit.BindLambda(ExcelItemCanEdit);
		ExcelFileActions.Edit.BindLambda(ExcelItemEdit);
		ExcelFileActions.CanCreate.BindLambda([this](const FName /*InDestFolderPath*/, const FString& /*InDestFolder*/, FText* /*OutErrorMsg*/){return false;});
		ExcelFileConfig.RegisterFileActions(ExcelFileActions);
	}
	
	ExcelFileDataSource.Reset(NewObject<UContentBrowserFileDataSource>(GetTransientPackage(), "ExcelData"));
	ExcelFileDataSource->Initialize("/", ExcelFileConfig);

	TArray<FDirectoryPath> ExcelPaths = GetDefault<UProtobufSetting>()->ExcelPaths;
	FString ProjectDir = FPaths::ProjectDir();
	for (const FDirectoryPath& ExcelDirectoryPath : ExcelPaths)
	{
		const FString ExcelPath = FPaths::Combine(ProjectDir, ExcelDirectoryPath.Path);
		const FString ExcelPackagePath = FPackageName::FilenameToLongPackageName(ExcelPath);
		UE_LOG(LogProtobuf, Log, TEXT("ExcelPackagePath : %s"), *ExcelPackagePath);
		UE_LOG(LogProtobuf, Log, TEXT("ExcelPath : %s"), *ExcelPath);
		ExcelFileDataSource->AddFileMount(*ExcelPackagePath, ExcelPath);
	}

#endif // WITH_EDITOR 
}

void FProtobufModule::RegisterSettings() const
{
	UProtobufSetting* Settings = GetMutableDefault<UProtobufSetting>();
	const FString ConfigIniPath = FPaths::SourceConfigDir().Append(TEXT("DefaultProtobuf.ini"));
	Settings->LoadConfig(UProtobufSetting::StaticClass(), *ConfigIniPath);

#if WITH_EDITOR
	if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
	{
		SettingsModule->RegisterSettings("Project",
		                                 "Plugins",
		                                 "Protobuf",
		                                 LOCTEXT("TileSetEditorSettingsName", "Protobuf"),
		                                 LOCTEXT("TileSetEditorSettingsDescription", "Configure the setting of Protobuf plugin."),
		                                 Settings);
	}

	// ** 将excel二进制文件目录同步到打包时需要直接pack的目录中
	UProjectPackagingSettings* PackagingSettings = GetMutableDefault<UProjectPackagingSettings>();
	FString AddPath = Settings->binaries_out.Path;
	if (AddPath.StartsWith(TEXT("Content/")))
	{
		AddPath = AddPath.Replace(TEXT("Content/"), TEXT(""));
	}
	bool bShouldAddPath = true;
	for (auto Directory : PackagingSettings->DirectoriesToAlwaysStageAsUFS)
	{
		if (Directory.Path.Equals(AddPath))
		{
			bShouldAddPath = false;
		}
	}
	if (bShouldAddPath)
	{
		FDirectoryPath DirectoryPath;
		DirectoryPath.Path = AddPath;
		PackagingSettings->DirectoriesToAlwaysStageAsUFS.Add(DirectoryPath);
		PackagingSettings->SaveConfig();
		PackagingSettings->UpdateDefaultConfigFile();
	}
#endif // WITH_EDITOR
}

void FProtobufModule::Tick(const float DeltaSeconds)
{
	if (!bHasTicked)
	{
		bHasTicked = true;

		
#if WITH_EDITOR
		// Activate the Content Browser integration (now that editor subsystems are available)
		if (ExcelFileDataSource)
		{
			UContentBrowserDataSubsystem* ContentBrowserData = IContentBrowserDataModule::Get().GetSubsystem();
			ContentBrowserData->ActivateDataSource("ExcelData");
		}
#endif	// WITH_EDITOR
	}
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FProtobufModule, Protobuf)

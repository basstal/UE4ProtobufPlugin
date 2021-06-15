// Copyright Epic Games, Inc. All Rights Reserved.

#include "Protobuf.h"

#include "ISettingsModule.h"
#include "ProtobufSetting.h"

#if WITH_EDITOR
#include "Settings/ProjectPackagingSettings.h"
#endif // WITH_EDITOR

#define LOCTEXT_NAMESPACE "FProtobufModule"


DEFINE_LOG_CATEGORY(LogProtobuf)

void FProtobufModule::StartupModule()
{
	RegisterSettings();
}

void FProtobufModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
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

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FProtobufModule, Protobuf)

// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "Engine/EngineTypes.h"
#include "Engine/DeveloperSettings.h"
#include "ProtobufSetting.generated.h"
/**
* 
*/
UCLASS(config = Protobuf, defaultconfig, meta = (DisplayName = "Protobuf"))
class UProtobufSetting : public UObject
{
	GENERATED_BODY()
	
public:
#if WITH_EDITOR
	virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif // WITH_EDITOR
	UPROPERTY(config, EditAnywhere, Category = "Setting|In", meta=(DisplayName="Excel源文件在项目中的相对路径"))
	FDirectoryPath excel_root_path;
	UPROPERTY(config, EditAnywhere, Category = "Setting|In", meta=(DisplayName="proto源文件在项目中的相对路径"))
	FDirectoryPath proto_root_path;
	UPROPERTY(config, EditAnywhere, Category = "Setting|Out", meta=(DisplayName="Excel二进制文件在项目中的相对路径"))
	FDirectoryPath binaries_out;
	UPROPERTY(config, EditAnywhere, Category = "Setting|Out", meta=(DisplayName="proto生成的cpp在项目中的相对路径"))
	FDirectoryPath cpp_proto_out;
	UPROPERTY(config, EditAnywhere, Category = "Setting|Out", meta=(DisplayName="ue对应的proto包装类在项目中的相对路径"))
    FDirectoryPath ue_cpp_wrapper_out;

	UPROPERTY(config, EditAnywhere, Category = "Setting", meta=(DisplayName="生成Excel包装类型名的后缀"))
	FString excel_typename_postfix;
	UPROPERTY(config, EditAnywhere, Category = "Setting", meta=(DisplayName="Message生成UE包装类型名的后缀(class)"))
	FString class_typename_postfix;
	UPROPERTY(config, EditAnywhere, Category = "Setting", meta=(DisplayName="Message生成UE包装类型名的后缀(struct)"))
	FString struct_typename_postfix;
	UPROPERTY(config, EditAnywhere, Category = "Setting", meta=(DisplayName="Message默认生成UCLASS，否则默认生成USTRUCT"))
	bool uclass_as_default;
	UPROPERTY(config, EditAnywhere, Category="Setting", meta=(DisplayName="Excel文件夹在项目中的相对路径", ConfigRestartRequired=true))
	TArray<FDirectoryPath> ExcelPaths;
};


UCLASS(config=EditorPerProjectUserSettings)
class UProtobufUserSetting : public UDeveloperSettings
{
	GENERATED_BODY()
public:
	UProtobufUserSetting()
	{
		CategoryName = TEXT("Plugins");
		SectionName = TEXT("Protobuf");
	}
#if WITH_EDITOR
	virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif // WITH_EDITOR

	UPROPERTY(config, EditAnywhere, Category="Setting", meta=(DisplayName="Excel.exe执行程序路径"))
	FString ExcelExec;
};

// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#if WITH_EDITOR
#include "UObject/StrongObjectPtr.h"

class UContentBrowserFileDataSource;
#endif // WITH_EDITOR

DECLARE_LOG_CATEGORY_EXTERN(LogProtobuf, All, Log)

class FProtobufModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
	/**
	 * 将Excel文件类型注册到UE编辑器的ContentBrowser中
	 */
	void RegisterExcelFileType();
	/**
	 * 注册Protobuf插件的相关配置文件，包括将Excel输出数据目录配置到打包直接copy的目录列表中
	 */
	void RegisterSettings() const;
protected:
#if WITH_EDITOR
	TStrongObjectPtr<UContentBrowserFileDataSource> ExcelFileDataSource;
#endif // WITH_EDITOR
	void Tick(const float DeltaSeconds);
	
	FDelegateHandle TickHandle;
	bool bHasTicked = false;
};

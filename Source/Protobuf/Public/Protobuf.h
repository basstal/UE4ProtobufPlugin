// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "UObject/StrongObjectPtr.h"

class UContentBrowserFileDataSource;
DECLARE_LOG_CATEGORY_EXTERN(LogProtobuf, All, Log)

class FProtobufModule : public IModuleInterface
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
	void RegisterExcelFileType();
	void RegisterSettings() const;
protected:
#if WITH_EDITOR
	TStrongObjectPtr<UContentBrowserFileDataSource> ExcelFileDataSource;
#endif // WITH_EDITOR
	void Tick(const float DeltaSeconds);
	
	FDelegateHandle TickHandle;
	bool bHasTicked = false;
};

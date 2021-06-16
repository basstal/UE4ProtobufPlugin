// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "Excel.h"
#include "PBLoaderSubsystem.generated.h"

/**
 * Subsystem控制Excel的加载并缓存已加载的Excel
 */
UCLASS()
class PROTOBUF_API UPBLoaderSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()
public:
	template<typename T>
	T * LoadExcel();
	UFUNCTION()
	UExcel * LoadExcelImpl(UClass * Wrapper);

protected:
	UPROPERTY()
	TMap<FString, UExcel *> LoadedExcels; 
};


template <typename T>
T* UPBLoaderSubsystem::LoadExcel()
{
	return Cast<T>(LoadExcelImpl(T::StaticClass()));
}
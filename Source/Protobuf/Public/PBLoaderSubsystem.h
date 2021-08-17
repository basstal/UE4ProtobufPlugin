// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "Excel.h"
#include "PBLoaderSubsystem.generated.h"

/**
 * Subsystem控制Excel的加载并缓存已加载的Excel
 */
UCLASS()
class PROTOBUF_API UPBLoaderSubsystem : public UEngineSubsystem
{
	GENERATED_BODY()
public:
	template<typename T>
	T * LoadExcel();
	/**
	 * 载入一张表并返回，多次载入只会读取已缓存的内容
	 */
	UFUNCTION(BlueprintCallable)
	UExcel * LoadExcelImpl(TSubclassOf<UExcel> Wrapper);
	/**
	 * 释放全部的缓存内容
	 */
	UFUNCTION(BlueprintCallable)
	void ReleaseAll();
protected:
	void RemovePostfix(FString& PostfixRemovedName);
	UPROPERTY()
	TMap<FName, UExcel *> LoadedExcels; 
};


template <typename T>
T* UPBLoaderSubsystem::LoadExcel()
{
	return Cast<T>(LoadExcelImpl(T::StaticClass()));
}
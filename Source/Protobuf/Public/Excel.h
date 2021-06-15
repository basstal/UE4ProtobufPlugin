// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Excel.generated.h"

/**
 * 抽象一个Excel表
 */
UCLASS()
class PROTOBUF_API UExcel : public UObject
{
	GENERATED_BODY()
protected:
	friend class UPBLoaderSubsystem;
	virtual void Load(TArray<uint8>& Bytes) {}
};

// Fill out your copyright notice in the Description page of Project Settings.
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include <string>
#include <google/protobuf/message.h>
#include "ExcelRow.generated.h"

/**
 * 抽象Excel中每一行数据
 */
UCLASS()
class PROTOBUF_API UExcelRow : public UObject
{
	GENERATED_BODY()
protected:
	virtual void Load(std::string Bytes) {};
	virtual void Load(::google::protobuf::Message * Message) {};
};

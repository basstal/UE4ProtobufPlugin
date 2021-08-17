// Copyright Epic Games, Inc. All Rights Reserved.
#include "PBLoaderSubsystem.h"

#include "Protobuf.h"
#include "ProtobufSetting.h"
#include "Misc/FileHelper.h"

UExcel* UPBLoaderSubsystem::LoadExcelImpl(TSubclassOf<UExcel> Wrapper)
{
	FString ExcelNameStr = Wrapper->GetName();
	RemovePostfix(ExcelNameStr);
	FName ExcelName(ExcelNameStr);
	if (LoadedExcels.Contains(ExcelName))
	{
		return *LoadedExcels.Find(ExcelName);
	}
	
	UExcel* Result = NewObject<UExcel>(Wrapper->GetOuter(), Wrapper);
	const UProtobufSetting& Settings = *GetDefault<UProtobufSetting>();
	const FString ExcelFullPath = FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectDir(), Settings.binaries_out.Path, ExcelNameStr));
	TArray<uint8> Content;
	FFileHelper::LoadFileToArray(Content, *ExcelFullPath);
	if (Content.Num() > 0)
	{
		Result->Load(Content);
	}
	else
	{
		UE_LOG(LogProtobuf, Warning, TEXT("No excel content found at path : %s"), *ExcelFullPath);
	}
	return Result;
}

void UPBLoaderSubsystem::ReleaseAll()
{
	
}

void UPBLoaderSubsystem::RemovePostfix(FString &PostfixRemovedName)
{
	UProtobufSetting * Setting = GetMutableDefault<UProtobufSetting>();
	int32 ChopCount = Setting->excel_typename_postfix.TrimEnd().Len();
	PostfixRemovedName = PostfixRemovedName.LeftChop(ChopCount);
}

#include "PBLoaderSubsystem.h"

#include "Protobuf.h"
#include "ProtobufSetting.h"
#include "Misc/FileHelper.h"

UExcel* UPBLoaderSubsystem::LoadExcelImpl(UClass* Wrapper)
{
	FString ExcelName(Wrapper->GetName().LeftChop(5));
	if (LoadedExcels.Contains(ExcelName))
	{
		return *LoadedExcels.Find(ExcelName);
	}
	
	UExcel* Result = NewObject<UExcel>(Wrapper->GetOuter(), Wrapper);
	const UProtobufSetting& Settings = *GetDefault<UProtobufSetting>();
	const FString ExcelFullPath = FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectDir(), Settings.binaries_out.Path, ExcelName));
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

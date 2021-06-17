#pragma once

#include "ProtobufSetting.h"

#if WITH_EDITOR
void UProtobufUserSetting::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override
{
	Super::PostEditChangeProperty(PropertyChangedEvent);
}

void UProtobufSetting::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override
{
	Super::PostEditChangeProperty(PropertyChangedEvent);
	/** 只截取相对路径 */
	excel_root_path.Path = excel_root_path.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	binaries_out.Path = binaries_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	proto_root_path.Path = proto_root_path.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	cpp_proto_out.Path = cpp_proto_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	ue_cpp_wrapper_out.Path = ue_cpp_wrapper_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));

	TArray<FDirectoryPath> OutExcelPaths;
	for (auto ExcelPath : ExcelPaths)
	{
		FDirectoryPath DirectoryPath;
		DirectoryPath.Path = ExcelPath.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
		OutExcelPaths.Add(DirectoryPath);
	}
	ExcelPaths = OutExcelPaths;
}
#endif // WITH_EDITOR
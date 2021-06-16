// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "ProtobufSetting.generated.h"
/**
* 
*/
UCLASS(config = Protobuf, defaultconfig, meta = (DisplayName = "Protobuf"))
class UProtobufSetting : public UObject
{
	GENERATED_BODY()
	
public:
	// virtual void PostLoad() override;
	virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
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
};
//
// inline void UProtobufSetting::PostLoad()
// {
// 	Super::PostLoad();
// 	UE_LOG(LogProtobuf, Display, TEXT("UProtobufSetting Loaded."));
// 	UE_LOG(LogProtobuf, Display, TEXT("excel_root_path : %s"), *excel_root_path.Path);
// 	UE_LOG(LogProtobuf, Display, TEXT("binaries_out : %s"), *binaries_out.Path);
// 	UE_LOG(LogProtobuf, Display, TEXT("proto_root_path : %s"), *proto_root_path.Path);
// 	UE_LOG(LogProtobuf, Display, TEXT("cpp_proto_out : %s"), *cpp_proto_out.Path);
// 	UE_LOG(LogProtobuf, Display, TEXT("ue_cpp_wrapper_out : %s"), *ue_cpp_wrapper_out.Path);
// }

/**
 * 只截取相对路径
 */
inline void UProtobufSetting::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
	Super::PostEditChangeProperty(PropertyChangedEvent);
	excel_root_path.Path = excel_root_path.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	binaries_out.Path = binaries_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	proto_root_path.Path = proto_root_path.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	cpp_proto_out.Path = cpp_proto_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
	ue_cpp_wrapper_out.Path = ue_cpp_wrapper_out.Path.Replace(*FPaths::ProjectDir(), TEXT(""));
}

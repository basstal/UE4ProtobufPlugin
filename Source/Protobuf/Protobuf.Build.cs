// Copyright Epic Games, Inc. All Rights Reserved.

using System.CodeDom;
using System.IO;
using UnrealBuildTool;

public class Protobuf : ModuleRules
{
	public Protobuf(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		string ThirdPartyPath = Path.GetFullPath(Path.Combine(ModuleDirectory, "../../ThirdParty/protobuf"));
		string IncludePath = Path.Combine(ThirdPartyPath, "include");
		
		// ShadowVariableWarningLevel = WarningLevel.Off;
		if (Target.Platform == UnrealTargetPlatform.Android)
		{
			bEnableUndefinedIdentifierWarnings = false;
		}
		
		PublicIncludePaths.AddRange(new string[]
		{
			IncludePath
		});

		PublicAdditionalLibraries.AddRange(new string[]
		{
			Path.Combine(ThirdPartyPath, "lib/libprotobuf.lib")
		});

		PrivateIncludePaths.AddRange(
			new string[]
			{
				// ... add other private include paths required here ...
			}
		);


		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				// ... add other public dependencies that you statically link with here ...
			}
		);


		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				// ... add private dependencies that you statically link with here ...	
			}
		);

		if (Target.Type == TargetType.Editor)
		{
			PrivateDependencyModuleNames.AddRange(new string[]
			{
				"UnrealEd"
			});
		}


		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
		);
	}
}
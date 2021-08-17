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

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
		);


		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
			}
		);

		if (Target.bBuildEditor == true)
		{
			PrivateDependencyModuleNames.AddRange(new string[]
			{
				"UnrealEd",
				"AssetTools",
				"ContentBrowserData",
				"ContentBrowserFileDataSource",
				"DeveloperSettings"
			});
		}
	}
}
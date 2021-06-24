# UE4ProtobufPlugin

Only support windows for now

Read excel data to UCLASS by Protobuf Message definition

## Example

```cpp
UPBLoaderSubsystem * PBLoader = GEngine->GetEngineSubsystem<UPBLoaderSubsystem>();
UMonsterConfigExcel * Excel = PBLoader->LoadExcel<UMonsterConfigExcel>();
if (Excel)
{
    const FMonsterConfig * MonsterConfigRow = Excel->Get(210705);
    if (MonsterConfigRow)
    {
        UE_LOG(LogTemp, Log, TEXT("MonsterConfigRow->aiRes : %s"), *(MonsterConfigRow->aiRes));
    }
    for(auto ExcelRow : Excel->Rows)
    {
        UE_LOG(LogTemp, Log, TEXT("ExcelRow.id : %d"), ExcelRow.id);
    }
}
UHeroUpgradeExcel * HeroUpgradeExcel = PBLoader->LoadExcel<UHeroUpgradeExcel>();
if (HeroUpgradeExcel)
{
    for (auto Row : HeroUpgradeExcel->Rows)
    {
        for (auto Attr : Row->attr)
        {
            UE_LOG(LogTemp, Log, TEXT("Attr->value : %f"), Attr->value);
        }
    }
}
```

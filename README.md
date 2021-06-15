# UE4ProtobufPlugin

Only support windows for now

Read excel data to UCLASS by Protobuf Message definition

## Example

```cpp
UPBLoaderSubsystem * PBLoader = GetGameInstance()->GetSubsystem<UPBLoaderSubsystem>();
UMonsterConfigExcel * Excel = PBLoader->LoadExcel<UMonsterConfigExcel>();
if (Excel)
{
    UMonsterConfigWrap * MonsterConfigRow = Excel->Get(210705);
    if (MonsterConfigRow)
    {
        UE_LOG(LogTemp, Display, TEXT("MonsterConfigRow->aiRes : %s"), *MonsterConfigRow->aiRes);
    }
    for(UMonsterConfigWrap * ExcelRow : Excel->Rows)
    {
        UE_LOG(LogTemp, Display, TEXT("Row->Data.id() : %d"), ExcelRow->id);
    }
}
UHeroUpgradeExcel * HeroUpgradeExcel = PBLoader->LoadExcel<UHeroUpgradeExcel>();
if (HeroUpgradeExcel)
{
    for (auto Row : HeroUpgradeExcel->Rows)
    {
        for (auto Attr : Row->attr)
        {
            UE_LOG(LogTemp, Display, TEXT("Attr->value : %f"), Attr->value);
        }
    }
}
```

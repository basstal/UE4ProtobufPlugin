h_template = r'''
#pragma once

#include "Excel.h"
#include "ExcelRow.h"

#include "ProtoGen/${module_name}$.pb.h"
${#-----------------------------------------------------}$
${#---------------处理 excel_basic 依赖关系--------------}$
${#-----------------------------------------------------}$
${if len(excels_wrapper) > 0:}$
#include "ProtoGen/excel_basic.pb.h"
${:end-if}$
${#-----------------------------------------------------}$
${#---------------处理 pb import 依赖关系----------------}$
${#-----------------------------------------------------}$
${for pb_import in pb_imports:}$
#include "${pb_import}$${gen_file_postfix}$.h"
${:end-for}$
${if len(enums_wrapper) > 0 or len(classes_wrapper) > 0 or len(excels_wrapper) > 0:}$
#include "${file_basename}$.generated.h"
${:end-if}$

#ifdef _MSC_VER
#pragma warning(disable: 4946)
#endif //_MSC_VER

${from template.template_helper import *}$

${#-----------------------------------------------------}$
${#-----处理 enums_wrapper 生成所有 Enum 的包装-----}$
${#-----------------------------------------------------}$
${for enum_wrapper in enums_wrapper:}$
${enumname = enum_wrapper["enumname"]}$
UENUM(${enum_wrapper["uenum_specifiers"]}$)
enum class E${enumname}$ : uint8
{
	${for enum_value in enum_wrapper['pb_enum_values']:}$
    ${enum_value_name = enum_value.name.replace(f'{enumname}_', '')}$
    ${enum_value_name}$ = ${enum_value.number}$,
    ${:end-for}$
};
${:end-for}$

${#-----------------------------------------------------------}$
${#-----处理 structs_wrapper 生成所有 纯数据的 Message 包装-----}$
${#-----------------------------------------------------------}$
${for struct_wrapper in structs_wrapper:}$
${option_pk_fields = struct_wrapper["option_pk_fields"]}$
${typename_postfix = struct_wrapper["typename_postfix"]}$
USTRUCT(${struct_wrapper["ustruct_specifiers"]}$)
struct F${struct_wrapper["name"]}$${typename_postfix}$
{
    GENERATED_BODY()
public:
    ${for pb_field in struct_wrapper['pb_fields']:}$
    ${#默认BlueprintReadOnly, 如果blueprint_writable的选项为true，则BlueprintReadWrite}$
    ${#TODO:过滤不支持的类型}$
    UPROPERTY(${write('BlueprintReadWrite' if struct_wrapper['blueprint_writable'] else 'BlueprintReadOnly')}$)
    ${write(get_pb_field_ue_type(pb_field, struct_wrapper, uclass_as_default))}$ ${pb_field.name}$;
    ${:end-for}$
};
${:end-for}$

${#-----------------------------------------------------}$
${#-----处理 classes_wrapper 生成所有 Message 的包装-----}$
${#-----------------------------------------------------}$
${for class_wrapper in classes_wrapper:}$
${option_pk_fields = class_wrapper["option_pk_fields"]}$
UCLASS(${class_wrapper["uclass_specifiers"]}$)
class U${class_wrapper["name"]}$${class_wrapper["typename_postfix"]}$ : public UExcelRow
{
    GENERATED_BODY()
public:
    ${#处理友元类声明}$
    ${for friend in class_wrapper["class_friend_classes"]:}$
    friend class U${friend}$;
    ${:end-for}$
    
    UPROPERTY()
    ${if class_wrapper["is_ustruct"]:}$
        ${#ustruct}$
        ${struct_wrapper = class_wrapper["struct_wrapper"]}$
    F${struct_wrapper["name"]}$${struct_wrapper["typename_postfix"]}$ ${write(class_wrapper["name"].lower())}$;
    ${:else:}$
        ${#uclass}$
        ${for pb_field in class_wrapper['pb_fields']:}$
    ${write(get_pb_field_ue_type(pb_field, class_wrapper, uclass_as_default))}$ ${pb_field.name}$;
        ${:end-for}$
    ${:end-if}$
protected:
    virtual void Load(const std::string& Bytes) override;
    virtual void Load(const ::google::protobuf::Message * Message) override;
};
${:end-for}$

${#-----------------------------------------------------}$
${#处理 excels_wrapper 生成有对应 Excel 表的所有 Message 的包装}$
${#-----------------------------------------------------}$
${for excel_wrapper in excels_wrapper:}$
${class_wrapper = excel_wrapper["class_wrapper"]}$
${row_classname = f'U{class_wrapper["name"]}{class_wrapper["typename_postfix"]}'}$
${struct_wrapper = class_wrapper["struct_wrapper"]}$
${row_structname = f'F{struct_wrapper["name"]}{struct_wrapper["typename_postfix"]}'}$
${option_pk_fields = excel_wrapper["option_pk_fields"]}$
${pk_fields_count = len(option_pk_fields)}$
${is_ustruct = excel_wrapper['is_ustruct']}$
UCLASS()
class U${excel_wrapper["excelname"]}$${excel_wrapper["typename_postfix"]}$ : public UExcel
{
	GENERATED_BODY()
public:
    ${#默认BlueprintReadOnly, 如果blueprint_writable的选项为true，则BlueprintReadWrite}$
	UPROPERTY(${write('BlueprintReadWrite' if struct_wrapper['blueprint_writable'] else 'BlueprintReadOnly')}$)
	TArray<${write(f'{row_structname}' if is_ustruct else f'const {row_classname} *')}$> Rows;
protected:
	virtual void Load(TArray<uint8>& Bytes) override;
	

${#仅有一个主键}$
${if pk_fields_count == 1:}$
    ${pk_ue_type = transfor_pk_type(transfor_pb_type_to_ue_type(option_pk_fields[0], excel_wrapper["typename_postfix"], uclass_as_default))}$
    UPROPERTY()
    TMap<${pk_ue_type}$, ${write(f'{row_structname}' if is_ustruct else f'const {row_classname} *')}$> PK_To_Row;
    void LoadPKMap();
public:
    ${#根据主键Get的方法默认BlueprintCallable, 供蓝图使用}$
    UFUNCTION(BlueprintCallable)
    const ${write(f'{row_structname}' if is_ustruct else f'{row_classname} *')}$ Get(${pk_ue_type}$ PKValue) const;

${:end-if}$

${#大于一个主键}$
${if pk_fields_count > 1:}$
${for i in range(0, pk_fields_count):}$
    UPROPERTY()
    ${pk_ue_type = transfor_pk_type(transfor_pb_type_to_ue_type(option_pk_fields[i], excel_wrapper["typename_postfix"], uclass_as_default))}$
    TMap<${write(pk_ue_type)}$, const ${row_classname}$ *> PK${i}$_To_Row;
${:end-for}$
    void LoadPKMapRows();
${:end-if}$
    
};
${:end-for}$
'''

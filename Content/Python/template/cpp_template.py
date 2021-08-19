cpp_template = r'''
#pragma once

${#引用对应的header}$
#include "${module_name}$${gen_file_postfix}$.h"

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


${from template.template_helper import *}$

${#-----------------------------------------------------}$
${#-----处理 classes_wrapper 生成所有 Message 的包装-----}$
${#-----------------------------------------------------}$
${for class_wrapper in classes_wrapper:}$
${option_pk_fields = class_wrapper["option_pk_fields"]}$
${class_name = 'U{0}{1}'.format(class_wrapper["name"], class_wrapper["typename_postfix"])}$

void ${class_name}$::Load(const std::string& Bytes)
{
    ${class_wrapper["name"]}$ PBData;
    PBData.ParseFromString(Bytes);
    Load(&PBData);
}

void ${class_name}$::Load(const ::google::protobuf::Message * Message)
{
    if (auto * PBData = reinterpret_cast<const ${class_wrapper["name"]}$*>(Message))
    {
        ${for pb_field in class_wrapper['pb_fields']:}$
        ${ue_type = get_pb_field_ue_type(pb_field, class_wrapper, uclass_as_default)}$
        ${if ue_type == 'FSoftObjectPath':}$
        ${write(handle_ustruct(pb_field, class_wrapper))}$ = FSoftObjectPath(PBData->${write(pb_field.name.lower())}$().c_str());
        ${:elif ue_type == 'FSoftClassPath':}$
        ${write(handle_ustruct(pb_field, class_wrapper))}$ = FSoftClassPath(PBData->${write(pb_field.name.lower())}$().c_str());
        ${:else:}$
        ${write(transfor_pb_value_to_ue_value(pb_field, '\t'*3, class_wrapper, uclass_as_default))}$
        ${:end-if}$
        ${:end-for}$
    }
}
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
${excel_class_name = 'U{0}{1}'.format(excel_wrapper["excelname"], excel_wrapper["typename_postfix"])}$

void ${excel_class_name}$::Load(TArray<uint8>& Bytes)
{
    Excel PBExcel;
    PBExcel.ParseFromArray(Bytes.GetData(), Bytes.Num());

    for (const std::string& RowContent : PBExcel.rows())
    {
        ${row_classname}$ * AddRow = NewObject<${row_classname}$>();

        AddRow->Load(RowContent);
        ${if is_ustruct:}$
        Rows.Add(CopyTemp(AddRow->${write(excel_wrapper["excelname"].lower())}$));
        ${:else:}$
        Rows.Add(AddRow);
        ${:end-if}$
    }


    ${if pk_fields_count > 0:}$
    LoadPKMap${'' if pk_fields_count == 1 else 'Rows'}$();
    ${:end-if}$
}


${#仅有一个主键}$
${if pk_fields_count == 1:}$
${pk_ue_type = transfor_pk_type(transfor_pb_type_to_ue_type(option_pk_fields[0], excel_wrapper["typename_postfix"], uclass_as_default))}$

void ${excel_class_name}$::LoadPKMap()
{
    for (auto Row : Rows)
    {
        PK_To_Row.Add(Row${write('->' if not is_ustruct else '.')}$${option_pk_fields[0].name}$, Row);
    }
}

const ${write(f'{row_classname}' if not is_ustruct else f'{row_structname}')}$ * ${excel_class_name}$::Get(${pk_ue_type}$ PKValue) const
{
    auto FindResult = PK_To_Row.Find(PKValue);
    if (FindResult)
    {
        return ${write('*' if not is_ustruct else '')}$FindResult;
    }
    return nullptr;
}

${:end-if}$

${#大于一个主键}$
${if pk_fields_count > 1:}$
void ${excel_class_name}$::LoadPKMapRows()
{
    // TODO:多主键处理
}
${:end-if}$

${:end-for}$

'''
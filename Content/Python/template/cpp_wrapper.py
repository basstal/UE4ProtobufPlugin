pb_type_to_ue_type_map = [
    'none',  # [0]
    # ** TODO:double??
    'float',  # [1] TYPE_DOUBLE
    'float',  # [2] TYPE_FLOAT
    'int64',  # [3] TYPE_INT64
    'uint64',  # [4] TYPE_UINT64
    'int32',  # [5] TYPE_INT32
    'uint64',  # [6] TYPE_FIXED64
    'uint32',  # [7] TYPE_FIXED32
    'bool',  # [8] TYPE_BOOL
    'FString',  # [9] TYPE_STRING
    'TODO??deprecated',  # [10] TYPE_GROUP
    'TODO??',  # [11] TYPE_MESSAGE
    'FString',  # [12] TYPE_BYTES
    'uint32',  # [13] TYPE_UINT32
    'TODO??',  # [14] TYPE_ENUM
    'int32',  # [15] TYPE_SFIXED32
    'int64',  # [16] TYPE_SFIXED64
    'int32',  # [17] TYPE_SINT32
    'int64',  # [18] TYPE_SINT64
]


# TODO:前向声明
cpp_wrapper_template = r'''
#pragma once

#include "Excel.h"
#include "ExcelRow.h"

#include "ProtoGen/${module_name}$.pb.h"

#include "${file_basename}$.generated.h"

#ifdef _MSC_VER
#pragma warning(disable: 4946)
#endif //_MSC_VER

${#-----------------------------------------------------}$
${#-----处理 enums_wrapper 生成所有 Enum 的包装-----}$
${#-----------------------------------------------------}$
${for enum_wrapper in enums_wrapper:}$
UENUM()
enum class E${enum_wrapper["enumname"]}$ : int32
{
	${for enum_value in enum_wrapper['pb_enum_values']:}$
    ${enum_value.name}$ = ${enum_value.number}$,
    ${:end-for}$
};
${:end-for}$

${#-----------------------------------------------------}$
${#-----处理 classes_wrapper 的一些帮助函数和数据结构-----}$
${#-----------------------------------------------------}$
${
def transfor_pb_type_to_ue_type(pb_field): 
    # 对于每个字段，将pb类型转换成ue支持的类型
    if pb_field.type == FieldDescriptor.TYPE_ENUM:
        content = f'E{pb_field.enum_type.name}'
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        content = f'U{pb_field.message_type.name}Wrap*'
    else:
        content = pb_type_to_ue_type_map[pb_field.type]
    return content

def wrap_repeated_field(pb_field, content):
    # 如果是Repeated字段则用TArray包装
    if pb_field.label == FieldDescriptor.LABEL_REPEATED:
        return f'TArray<{content}>'
    else:
        return content
}$
${
    # 能够直接转换的值类型
    direct_value_type = [
        FieldDescriptor.TYPE_DOUBLE,
        FieldDescriptor.TYPE_FLOAT,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_UINT64,
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_FIXED64,
        FieldDescriptor.TYPE_FIXED32,
        FieldDescriptor.TYPE_BOOL,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_SFIXED32,
        FieldDescriptor.TYPE_SFIXED64,
        FieldDescriptor.TYPE_SINT32,
        FieldDescriptor.TYPE_SINT64,
    ]
}$
${
    # 对于每个Repeated的字段，将Message的值包装成TArray
def transfor_repeated_value(pb_field, text_format):
    repeated = f'Repeated_{pb_field.name}'

    if pb_field.type == FieldDescriptor.TYPE_STRING or pb_field.type == FieldDescriptor.TYPE_BYTES:
        content = [
            f'google::protobuf::RepeatedPtrField<std::string> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto StrPtr = {repeated}.begin(); StrPtr != {repeated}.end(); ++ StrPtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}std::string value = *StrPtr;{chr(10)}',
            f'{chr(9)}{pb_field.name}.Add(FString(value.c_str()));{chr(10)}',
            f'{chr(125)}'
        ]
    elif pb_field.type in direct_value_type :
        content = [
            f'google::protobuf::RepeatedField<google::protobuf::{pb_type_to_ue_type_map[pb_field.type]}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}google::protobuf::{pb_type_to_ue_type_map[pb_field.type]} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}{pb_field.name}.Add(value);{chr(10)}',
            f'{chr(125)}'
        ]
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        namespace = pb_field.file.package
        wrapname = f'{pb_field.message_type.name}Wrap'
        content = [
            f'google::protobuf::RepeatedPtrField<{namespace}::{pb_field.message_type.name}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}{namespace}::{pb_field.message_type.name} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}U{pb_field.message_type.name}Wrap* {wrapname} = NewObject<U{pb_field.message_type.name}Wrap>();{chr(10)}',
            f'{chr(9)}{wrapname}->Load(&value);{chr(10)}',
            f'{chr(9)}{pb_field.name}.Add({wrapname});{chr(10)}',
            f'{chr(125)}'
        ]
    return text_format.join(content)
}$
${
    # 对于每个字段，将Message的值转换为ue支持的值
def transfor_pb_value_to_ue_value(pb_field, text_format):
    # Repeated字段需要特别处理转换
    if pb_field.label == FieldDescriptor.LABEL_REPEATED:
        return transfor_repeated_value(pb_field, text_format)

    if pb_field.type == FieldDescriptor.TYPE_STRING or pb_field.type == FieldDescriptor.TYPE_BYTES:
        return f'{pb_field.name} = FString(PBData->{pb_field.name.lower()}().c_str())'
    elif pb_field.type == FieldDescriptor.TYPE_ENUM:
        return f'{pb_field.name} = E{pb_field.enum_type.name}(PBData->{pb_field.name.lower()}())'
    else:
        return f'{pb_field.name} = PBData->{pb_field.name.lower()}()'
}$

${#-----------------------------------------------------}$
${#-----处理 classes_wrapper 生成所有 Message 的包装-----}$
${#-----------------------------------------------------}$
${for class_wrapper in classes_wrapper:}$
UCLASS()
class U${class_wrapper["classname"]}$Wrap : public UExcelRow
{
    GENERATED_BODY()
public:
    ${#处理友元类声明}$
    ${for friend in class_wrapper["class_friend_classes"]:}$
    friend class U${friend}$;
    ${:end-for}$
    
    ${for pb_field in class_wrapper['pb_fields']:}$
    UPROPERTY()
    ${#处理是否为uasset}$
    ${if pb_field in class_wrapper['option_uasset_fields']:}$
    FSoftObjectPath ${pb_field.name}$;
    ${:else:}$
    ${write(wrap_repeated_field(pb_field, transfor_pb_type_to_ue_type(pb_field)))}$ ${pb_field.name}$;
    ${:end-if}$
    ${:end-for}$
protected:
    virtual void Load(std::string Bytes) override
    {
        ${class_wrapper["classname"]}$ PBData;
        PBData.ParseFromString(Bytes);
        Load(&PBData);
    }

    virtual void Load(::google::protobuf::Message * Message) override
    {
        ${class_wrapper["classname"]}$ * PBData = reinterpret_cast<${class_wrapper["classname"]}$*>(Message);
        if (PBData)
        {
            ${for pb_field in class_wrapper['pb_fields']:}$
            ${#处理是否为uasset}$
            ${if pb_field in class_wrapper['option_uasset_fields']:}$
            ${pb_field.name}$ = FSoftObjectPath(PBData->${write(pb_field.name.lower())}$().c_str());
            ${:else:}$
            ${write(transfor_pb_value_to_ue_value(pb_field, '\t'*3))}$;
            ${:end-if}$
            ${:end-for}$
        }
    }

};
${:end-for}$

${#-----------------------------------------------------}$
${#处理 excels_wrapper 生成有对应 Excel 表的所有 Message 的包装}$
${#-----------------------------------------------------}$
${for excel_wrapper in excels_wrapper:}$
${row_classname = f'U{excel_wrapper["excelname"]}Wrap'}$
${pk_fields_count = len(excel_wrapper["option_pk_fields"])}$
UCLASS()
class U${excel_wrapper["excelname"]}$Excel : public UExcel
{
	GENERATED_BODY()
public:
	UPROPERTY()
	TArray<${row_classname}$ *> Rows;
    
protected:
	virtual void Load(TArray<uint8>& Bytes) override
	{
		Excel PBExcel;
		PBExcel.ParseFromArray(Bytes.GetData(), Bytes.Num());

		for (std::string RowContent : PBExcel.rows())
		{
			${row_classname}$ * AddRow = NewObject<${row_classname}$>();
	
			AddRow->Load(RowContent);
			Rows.Add(AddRow);
	
		}


        ${if pk_fields_count > 0:}$
        LoadPKMap${'' if pk_fields_count == 1 else 'Rows'}$();
        ${:end-if}$
	}

${#仅有一个主键}$
${if pk_fields_count == 1:}$
    ${pk_ue_type = transfor_pb_type_to_ue_type(excel_wrapper["option_pk_fields"][0])}$
    UPROPERTY()
    TMap<${pk_ue_type}$, ${row_classname}$ *> PK_To_Row;
    void LoadPKMap()
    {
        for ( auto Row : Rows)
        {
            PK_To_Row.Add(Row->${excel_wrapper["option_pk_fields"][0].name}$, Row);
        }
    }
public:
    ${row_classname}$ * Get(${pk_ue_type}$ PKValue)
    {
    	${row_classname}$ ** FindResult = PK_To_Row.Find(PKValue);
    	if (FindResult)
    	{
    		return *FindResult;
    	}
    	return nullptr;
    }

${:end-if}$

${#大于一个主键}$
${if pk_fields_count > 1:}$
${for i in range(0, pk_fields_count):}$
    UPROPERTY()
    TMap<${write(transfor_pb_type_to_ue_type(excel_wrapper["option_pk_fields"][i]))}$, ${row_classname}$ *> PK${i}$_To_Row;
${:end-for}$
    void LoadPKMapRows()
    {
        // TODO:
    }
${:end-if}$
    
};
${:end-for}$

'''

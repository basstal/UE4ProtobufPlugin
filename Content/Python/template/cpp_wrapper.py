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


cpp_wrapper_template = r'''
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
#include "${pb_import}$Wrapper.h"
${:end-for}$
${if len(enums_wrapper) > 0 or len(classes_wrapper) > 0 or len(excels_wrapper) > 0:}$
#include "${file_basename}$.generated.h"
${:end-if}$

#ifdef _MSC_VER
#pragma warning(disable: 4946)
#endif //_MSC_VER

${#-----------------------------------------------------}$
${#-----处理 classes_wrapper 的一些帮助函数和数据结构-----}$
${#-----------------------------------------------------}$
${
def transfor_pb_type_to_ue_type(pb_field, typename_postfix): 
    """
    对于每个字段，将pb类型转换成ue支持的类型
    """
    if pb_field.type == FieldDescriptor.TYPE_ENUM:
        content = f'E{pb_field.enum_type.name}'
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        # 对于含有 ustruct option 的 message 要处理成结构
        is_ustruct = get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
        if not uclass_as_default or is_ustruct:
            content = f'F{pb_field.message_type.name}{typename_postfix}'
        else:
            content = f'U{pb_field.message_type.name}{typename_postfix}*'
    else:
        content = pb_type_to_ue_type_map[pb_field.type]
    return content

def transfor_pk_type(ue_type_str):
    """
    转换为主键类型，接受一个ue_type的str
    """
    if ue_type_str == 'FString':
        return 'FName'
    else:
        return ue_type_str

def wrap_repeated_field(pb_field, content):
    """
    如果是Repeated字段则用TArray包装
    """
    if pb_field.label == FieldDescriptor.LABEL_REPEATED:
        return f'TArray<{content}>'
    else:
        return content

def handle_ustruct(pb_field, class_wrapper):
    is_ustruct = False if 'is_ustruct' not in class_wrapper else class_wrapper['is_ustruct']
    if is_ustruct:
        return f'{class_wrapper["name"].lower()}.{pb_field.name}'
    else:
        return pb_field.name
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
def transfor_repeated_value(pb_field, is_ustruct, classname, typename_postfix, text_format=' '):
    """
    对于每个Repeated的字段，将Message的值包装成TArray
    """
    repeated = f'Repeated_{pb_field.name}'
    field_name = pb_field.name if not is_ustruct else f'{classname.lower()}.{pb_field.name}'
    if pb_field.type == FieldDescriptor.TYPE_STRING or pb_field.type == FieldDescriptor.TYPE_BYTES:
        content = [
            f'google::protobuf::RepeatedPtrField<std::string> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto StrPtr = {repeated}.begin(); StrPtr != {repeated}.end(); ++ StrPtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}std::string value = *StrPtr;{chr(10)}',
            f'{chr(9)}{field_name}.Add(FString(value.c_str()));{chr(10)}',
            f'{chr(125)}'
        ]
    elif pb_field.type in direct_value_type :
        content = [
            f'google::protobuf::RepeatedField<google::protobuf::{pb_type_to_ue_type_map[pb_field.type]}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}google::protobuf::{pb_type_to_ue_type_map[pb_field.type]} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}{field_name}.Add(value);{chr(10)}',
            f'{chr(125)}'
        ]
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        namespace = pb_field.file.package
        temp_name = f'{pb_field.message_type.name}_tmp'
        message_type_is_ustruct = get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
        if not uclass_as_default or message_type_is_ustruct:
            add_content = f'CopyTemp({temp_name}->{pb_field.message_type.name.lower()})'
        else:
            add_content = f'{temp_name}'
        content = [
            f'google::protobuf::RepeatedPtrField<{namespace}::{pb_field.message_type.name}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}{namespace}::{pb_field.message_type.name} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}U{pb_field.message_type.name}{typename_postfix}* {temp_name} = NewObject<U{pb_field.message_type.name}{typename_postfix}>();{chr(10)}',
            f'{chr(9)}{temp_name}->Load(&value);{chr(10)}',
            f'{chr(9)}{field_name}.Add({add_content});{chr(10)}',
            f'{chr(125)}'
        ]
    return text_format.join(content)
}$
${
def transfor_pb_value_to_ue_value(pb_field, text_format, class_wrapper):
    """
    对于每个字段，将Message的值转换为ue支持的值
    Repeated字段需要特别处理转换
    """

    option_pk_fields = class_wrapper['option_pk_fields']
    is_ustruct = class_wrapper['is_ustruct']
    classname = class_wrapper['name']
    typename_postfix = class_wrapper['typename_postfix']

    common_format = ''
    if pb_field.label == FieldDescriptor.LABEL_REPEATED:
        common_format = transfor_repeated_value(pb_field, is_ustruct, classname, typename_postfix, text_format=text_format)
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        content = [
            f'::google::protobuf::Message * {pb_field.name.lower()}Message = const_cast<ActionInputControl *>(&PBData->{pb_field.name.lower()}());{chr(10)}',
        ]
        # 对于含有 ustruct option 的 message 要处理成结构
        message_type_is_ustruct = get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
        if not uclass_as_default or message_type_is_ustruct:
            # 构造一个临时的 包装类型 用于 Load 数据
            temp_name = f'{pb_field.name}_tmp'
            content.extend([
                f'U{pb_field.message_type.name}{typename_postfix} * {temp_name} = NewObject<U{pb_field.message_type.name}{typename_postfix}>();{chr(10)}',
                f'{temp_name}->Load({pb_field.name.lower()}Message);{chr(10)}',
                f'{classname.lower()}.{pb_field.name} = CopyTemp({temp_name}->{pb_field.message_type.name.lower()})'
            ])
        else:
            content.extend([
                f'{pb_field.name} = NewObject<U{pb_field.message_type.name}{typename_postfix}>();{chr(10)}',
                f'{pb_field.name}->Load({pb_field.name.lower()}Message)'
            ])
        common_format = text_format.join(content)
    else:
        if pb_field.type == FieldDescriptor.TYPE_STRING or pb_field.type == FieldDescriptor.TYPE_BYTES:
            if pb_field in option_pk_fields:
                common_format = f'{pb_field.name} = FName(PBData->{pb_field.name.lower()}().c_str())'
            else:
                common_format = f'{pb_field.name} = FString(PBData->{pb_field.name.lower()}().c_str())'
        elif pb_field.type == FieldDescriptor.TYPE_ENUM:
            common_format = f'{pb_field.name} = E{pb_field.enum_type.name}(PBData->{pb_field.name.lower()}())'
        else:
            common_format = f'{pb_field.name} = PBData->{pb_field.name.lower()}()'
        # 内部为USTRUCT结构
        if is_ustruct:
            common_format = f'{classname.lower()}.{common_format}'
    # 最后一行的格式是统一的
    return f'{common_format};{chr(10)}{text_format}'
}$

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
    UPROPERTY()
    ${#处理是否为uasset}$
    ${if pb_field in struct_wrapper['option_uasset_fields']:}$
    FSoftObjectPath ${pb_field.name}$;
    ${:else:}$
    ${ue_type = transfor_pb_type_to_ue_type(pb_field, typename_postfix)}$
    ${ue_type = ue_type if not pb_field in option_pk_fields else transfor_pk_type(ue_type)}$
    ${write(wrap_repeated_field(pb_field, ue_type))}$ ${pb_field.name}$;
    ${:end-if}$
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
        ${#处理是否为uasset}$
        ${if pb_field in class_wrapper['option_uasset_fields']:}$
    FSoftObjectPath ${pb_field.name}$;
        ${:else:}$
        ${ue_type = transfor_pb_type_to_ue_type(pb_field, class_wrapper["typename_postfix"])}$
        ${ue_type = ue_type if not pb_field in option_pk_fields else transfor_pk_type(ue_type)}$
    ${write(wrap_repeated_field(pb_field, ue_type))}$ ${pb_field.name}$;
        ${:end-if}$
        ${:end-for}$
    ${:end-if}$
protected:
    virtual void Load(const std::string& Bytes) override
    {
        ${class_wrapper["name"]}$ PBData;
        PBData.ParseFromString(Bytes);
        Load(&PBData);
    }

    virtual void Load(const ::google::protobuf::Message * Message) override
    {
        if (auto * PBData = reinterpret_cast<const ${class_wrapper["name"]}$*>(Message))
        {
            ${for pb_field in class_wrapper['pb_fields']:}$
            ${#处理是否为uasset}$
            ${if pb_field in class_wrapper['option_uasset_fields']:}$
            ${write(handle_ustruct(pb_field, class_wrapper))}$ = FSoftObjectPath(PBData->${write(pb_field.name.lower())}$().c_str());
            ${:else:}$
            ${write(transfor_pb_value_to_ue_value(pb_field, '\t'*3, class_wrapper))}$
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
	UPROPERTY()
	TArray<${write(f'const {row_classname} *' if not is_ustruct else f'{row_structname}')}$> Rows;
protected:
	virtual void Load(TArray<uint8>& Bytes) override
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
    ${pk_ue_type = transfor_pk_type(transfor_pb_type_to_ue_type(option_pk_fields[0], excel_wrapper["typename_postfix"]))}$
    UPROPERTY()
    TMap<${pk_ue_type}$, ${write(f'const {row_classname} *' if not is_ustruct else f'{row_structname}')}$> PK_To_Row;
    void LoadPKMap()
    {
        for (auto Row : Rows)
        {
            PK_To_Row.Add(Row${write('->' if not is_ustruct else '.')}$${option_pk_fields[0].name}$, Row);
        }
    }
public:
    const ${write(f'{row_classname}' if not is_ustruct else f'{row_structname}')}$ * Get(${pk_ue_type}$ PKValue) const
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
${for i in range(0, pk_fields_count):}$
    UPROPERTY()
    ${pk_ue_type = transfor_pk_type(transfor_pb_type_to_ue_type(option_pk_fields[i], excel_wrapper["typename_postfix"]))}$
    TMap<${write(pk_ue_type)}$, const ${row_classname}$ *> PK${i}$_To_Row;
${:end-for}$
    void LoadPKMapRows()
    {
        // TODO:多主键处理
    }
${:end-if}$
    
};
${:end-for}$
'''

# -----------------------------------------------------
# ----------------------基本定义------------------------
# -----------------------------------------------------

from google.protobuf.descriptor import FieldDescriptor
from pb_helper import pb_helper

pb_type_to_ue_type_map = [
    'none',  # [0]
    # ** NOTE:pb double 转换为UE float 会来带精度损失
    'float',  # [1] TYPE_DOUBLE
    'float',  # [2] TYPE_FLOAT
    'int64',  # [3] TYPE_INT64
    'uint64',  # [4] TYPE_UINT64
    'int32',  # [5] TYPE_INT32
    'uint64',  # [6] TYPE_FIXED64
    'uint32',  # [7] TYPE_FIXED32
    'bool',  # [8] TYPE_BOOL
    'FString',  # [9] TYPE_STRING
    'illegal!!',  # [10] TYPE_GROUP
    'illegal!!',  # [11] TYPE_MESSAGE
    'FString',  # [12] TYPE_BYTES
    'uint32',  # [13] TYPE_UINT32
    'illegal!!',  # [14] TYPE_ENUM
    'int32',  # [15] TYPE_SFIXED32
    'int64',  # [16] TYPE_SFIXED64
    'int32',  # [17] TYPE_SINT32
    'int64',  # [18] TYPE_SINT64
]

predefined_pb_type_to_ue_type = {
    'PB_Vector': 'FVector',
    'PB_Transform': 'FTransform'
}


def pb_vector_transfer(obj_name, field_name, text_format):
    """
    将pb vector message 转换为 FVector 的 cpp 代码

    @obj_name (str)
        被转换的message指针名称

    @field_name (str)
        该message中PB_Vector字段的名称

    @text_format (str)
        格式化Tab
    """
    return text_format.join([
        f'PB_Vector * {field_name} = const_cast<PB_Vector*>(&{obj_name}->{field_name}());{chr(10)}',
        f'FVector {field_name}_tmp({field_name}->x(), {field_name}->y(), {field_name}->z());{chr(10)}',
    ])


def pb_transform_transfer(obj_name, field_name, text_format):
    """
    将pb transform message 转换为 FTransform 的 cpp 代码

    @obj_name (str)
        被转换的message指针名称

    @field_name (str)
        该message中PB_Vector字段的名称

    @text_format (str)
        格式化Tab
    """
    return text_format.join([
        f'PB_Transform * {field_name} = const_cast<PB_Transform*>(&{obj_name}->{field_name}());{chr(10)}',
        pb_vector_transfer(field_name, 'scale3d', text_format),
        pb_vector_transfer(field_name, 'rotation', text_format),
        pb_vector_transfer(field_name, 'translation', text_format),
        f'FTransform {field_name}_tmp(FRotator(rotation_tmp.X, rotation_tmp.Y, rotation_tmp.Z), translation_tmp, scale3d_tmp);{chr(10)}'
    ])


predefined_pb_type_handler = {
    'PB_Vector': pb_vector_transfer,
    'PB_Transform': pb_transform_transfer
}

# -----------------------------------------------------
# -----处理 classes_wrapper 的一些帮助函数和数据结构-----
# -----------------------------------------------------


def transfer_pb_type_to_ue_type(pb_field, typename_postfix, uclass_as_default):
    """
    对于每个字段，将pb类型转换成ue支持的类型
    """
    if pb_field.type == FieldDescriptor.TYPE_ENUM:
        content = f'E{pb_field.enum_type.name}'
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        # 预定义的pb message类型，转成UE类型
        if pb_field.message_type.name in predefined_pb_type_to_ue_type:
            content = f'{predefined_pb_type_to_ue_type[pb_field.message_type.name]}'
        else:
            # 对于含有 ustruct option 的 message 要处理成结构
            is_ustruct = pb_helper.get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
            if not uclass_as_default or is_ustruct:
                content = f'F{pb_field.message_type.name}{typename_postfix}'
            else:
                # FIXME:这里只返回类型，不带指针，同时需要修改所有用到的地方
                content = f'U{pb_field.message_type.name}{typename_postfix}*'
    else:
        content = pb_type_to_ue_type_map[pb_field.type]
    return content


def transfer_pk_type(ue_type_str):
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


def transfer_repeated_value(pb_field, is_ustruct, classname, typename_postfix, uclass_as_default, text_format=' '):
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
            f'{chr(125)};'
        ]
    elif pb_field.type in direct_value_type:
        content = [
            f'google::protobuf::RepeatedField<google::protobuf::{pb_type_to_ue_type_map[pb_field.type]}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}google::protobuf::{pb_type_to_ue_type_map[pb_field.type]} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}{field_name}.Add(value);{chr(10)}',
            f'{chr(125)};'
        ]
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        namespace = pb_field.file.package
        temp_name = f'{pb_field.message_type.name}_tmp'
        message_type_is_ustruct = pb_helper.get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
        if not uclass_as_default or message_type_is_ustruct:
            add_content = f'CopyTemp({temp_name}->{pb_field.message_type.name.lower()})'
        else:
            add_content = f'{temp_name}'

        ue_type = transfer_pb_type_to_ue_type(pb_field, typename_postfix, uclass_as_default)
        content = [
            f'google::protobuf::RepeatedPtrField<{namespace}::{pb_field.message_type.name}> {repeated} = PBData->{pb_field.name.lower()}();{chr(10)}',
            f'for(auto ValuePtr = {repeated}.begin(); ValuePtr != {repeated}.end(); ++ ValuePtr){chr(10)}',
            f'{chr(123)}{chr(10)}',
            f'{chr(9)}{namespace}::{pb_field.message_type.name} value = *ValuePtr;{chr(10)}',
            f'{chr(9)}{ue_type}* {temp_name} = NewObject<{ue_type}>();{chr(10)}',
            f'{chr(9)}{temp_name}->Load(&value);{chr(10)}',
            f'{chr(9)}{field_name}.Add({add_content});{chr(10)}',
            f'{chr(125)};'
        ]
    return text_format.join(content)


def transfer_pb_value_to_ue_value(pb_field, text_format, class_wrapper, uclass_as_default):
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
        common_format = transfer_repeated_value(pb_field, is_ustruct, classname, typename_postfix, uclass_as_default, text_format=text_format)
    elif pb_field.type == FieldDescriptor.TYPE_MESSAGE:
        if pb_field.message_type.name in predefined_pb_type_handler:
            content = [
                predefined_pb_type_handler[pb_field.message_type.name]('PBData', pb_field.name.lower(), text_format),
                f'{classname.lower()}.{pb_field.name} = {pb_field.name}_tmp;',
            ]
            common_format = text_format.join(content)
        else:
            # FIXME: ActionInputControl??这里可能是忘了映射了
            content = [
                f'::google::protobuf::Message * {pb_field.name.lower()}Message = const_cast<ActionInputControl *>(&PBData->{pb_field.name.lower()}());{chr(10)}',
            ]
            # 对于含有 ustruct option 的 message 要处理成结构
            message_type_is_ustruct = pb_helper.get_option_value(pb_field.message_type.GetOptions(), 'ustruct', False) != False
            ue_type = transfer_pb_type_to_ue_type(pb_field, typename_postfix, uclass_as_default)
            if not uclass_as_default or message_type_is_ustruct:
                # 构造一个临时的 包装类型 用于 Load 数据
                temp_name = f'{pb_field.name}_tmp'
                content.extend([
                    f'{ue_type} * {temp_name} = NewObject<{ue_type}>();{chr(10)}',
                    f'{temp_name}->Load({pb_field.name.lower()}Message);{chr(10)}',
                    f'{classname.lower()}.{pb_field.name} = CopyTemp({temp_name}->{pb_field.message_type.name.lower()});'
                ])
            else:
                content.extend([
                    f'{pb_field.name} = NewObject<{ue_type}>();{chr(10)}',
                    f'{pb_field.name}->Load({pb_field.name.lower()}Message);'
                ])
            common_format = text_format.join(content)
    else:
        # 内部为USTRUCT结构
        forehead = f'{classname.lower()}.' if is_ustruct else ''
        if pb_field.type == FieldDescriptor.TYPE_STRING or pb_field.type == FieldDescriptor.TYPE_BYTES:
            if pb_field in option_pk_fields:
                common_format = f'{forehead}{pb_field.name} = FName(PBData->{pb_field.name.lower()}().c_str());'
            else:
                common_format = f'{forehead}{pb_field.name} = FString(PBData->{pb_field.name.lower()}().c_str());'
        elif pb_field.type == FieldDescriptor.TYPE_ENUM:
            common_format = f'{forehead}{pb_field.name} = E{pb_field.enum_type.name}(PBData->{pb_field.name.lower()}());'
        else:
            common_format = f'{forehead}{pb_field.name} = PBData->{pb_field.name.lower()}();'
    # 最后一行的格式是统一的
    return f'{common_format}{chr(10)}{text_format}'


def get_pb_field_ue_type(pb_field, struct_wrapper, uclass_as_default):
    """
    对于每个字段，将pb类型转换为对应的ue类型，其中特殊处理FSoftClassPath、FSoftObjectPath等标记
    """
    if pb_field in struct_wrapper['option_FSoftClassPath_fields']:
        # 处理是否为FSoftClassPath
        return 'FSoftClassPath'
    elif pb_field in struct_wrapper['option_FSoftObjectPath_fields']:
        # 处理是否为FSoftObjectPath
        return 'FSoftObjectPath'
    else:
        typename_postfix = struct_wrapper["typename_postfix"]
        option_pk_fields = struct_wrapper["option_pk_fields"]
        ue_type = transfer_pb_type_to_ue_type(pb_field, typename_postfix, uclass_as_default)
        ue_type = ue_type if not pb_field in option_pk_fields else transfer_pk_type(ue_type)
        return str(wrap_repeated_field(pb_field, ue_type))

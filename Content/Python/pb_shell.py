from pb_helper import pb_helper
import utility as u
import unreal

class pb_shell:    
    def __init__(self, pb_type):
        self.instance = pb_type()
        self.valid = False
        # ** excel_index_to_repeated_index_by_descriptor_field
        # ** 根据descriptor的number，将excel表中的数组下标对应到repeated数组的下标（python数组下标）
        self.exi_to_rpi_by_dscn = {}

    def resolve_value_by_descriptor(self, descriptor_field, value):
        resolved_value = None
        target_type = descriptor_field.type
        
        if target_type is pb_helper.FieldDescriptor.TYPE_STRING or target_type is pb_helper.FieldDescriptor.TYPE_BYTES:
            resolved_value = str(value)
        elif target_type is pb_helper.FieldDescriptor.TYPE_ENUM:
            if type(value) == str:
                enum_type = descriptor_field.enum_type
                try:
                    resolved_value = enum_type.values_by_name[value].number
                except:
                    resolved_value = enum_type.values_by_name["{}_{}".format(enum_type.name, value)].number
            else:
                unreal.log_warning(f"不应该在枚举类型对应的列{descriptor_field.name}填写number类型数据 : {value}")
                resolved_value = int(value)
        else:
            if type(value) == str:
                try:
                    cast_to_float = float(value) if len(value) > 0 else 0
                except:
                    cast_to_float = 0
            else:
                cast_to_float = float(value)
            if target_type in pb_helper.TYPE_INT:
                resolved_value = int(cast_to_float)
            elif target_type is pb_helper.FieldDescriptor.TYPE_FLOAT or target_type is pb_helper.FieldDescriptor.TYPE_DOUBLE:
                resolved_value = cast_to_float
            elif target_type is pb_helper.FieldDescriptor.TYPE_BOOL:
                resolved_value = (int(cast_to_float)) != 0

        return resolved_value

    def write_field_value(self, pb_field_excel_ref, value, sub_instance=None):
        first = pb_field_excel_ref[0]
        name = first[0]
        excel_index = first[1]

        instance = sub_instance or self.instance
        if len(name) <= 0:
            return
        if value is None:
            instance.ClearField(name)
            return

        self.valid = True
        descriptor_field = pb_helper.get_descriptor_field(instance, name)
        if descriptor_field is not None:
            if descriptor_field.label == pb_helper.FieldDescriptor.LABEL_REPEATED:
                if excel_index is None:
                    unreal.log_warning("descriptor_field : {} need a repeated field assigning !".format(descriptor_field))
                    return
                # ** repeated
                repeated_field = getattr(self.instance, name)
                if repeated_field is None:
                    unreal.log_warning('{} field in {} is None?'.format(name, self.instance))
                if descriptor_field.type == pb_helper.FieldDescriptor.TYPE_MESSAGE:
                    if descriptor_field.number in self.exi_to_rpi_by_dscn:
                        reflection = self.exi_to_rpi_by_dscn[descriptor_field.number]
                    else:
                        reflection = {}
                        self.exi_to_rpi_by_dscn[descriptor_field.number] = reflection
                    # ** get defaults
                    if excel_index not in reflection:
                        # ** reflection with a new repeated message index
                        repeated_field.add()
                        reflection[excel_index] = len(repeated_field) - 1

                    sub_instance = repeated_field[reflection[excel_index]]

                    self.write_field_value(pb_field_excel_ref[1:], value, sub_instance)
                else:
                    attr_value_instance = self.resolve_value_by_descriptor(descriptor_field, value)
                    repeated_field.append(attr_value_instance)
            else:
                resolved_value = self.resolve_value_by_descriptor(descriptor_field, value)
                setattr(instance, name, resolved_value)
        else:
            unreal.log_warning("{} is not a member of {}. 可以在表中删除该列，或将该列的第二行字段名改为空以屏蔽该警告。".format(name, type(self.instance)))
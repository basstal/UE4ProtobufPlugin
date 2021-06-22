import sys
import os
import importlib

import utility as u

from unreal_import_switch import unreal


from google.protobuf.descriptor import FieldDescriptor


class pb_helper:
    """
    记录Python生成的pb模块
    """
    loaded_modules = None

    TYPE_INT = [
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_SINT32,
        FieldDescriptor.TYPE_SINT64,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_UINT64,
    ]

    FieldDescriptor = FieldDescriptor

    @staticmethod
    def get_pb_path():
        python_pb_out = os.path.normpath(os.path.join(unreal.Paths.project_intermediate_dir(), 'pb'))
        return python_pb_out

    @staticmethod
    def load_modules():
        pb_helper.loaded_modules = []

        pb_root_path = pb_helper.get_pb_path()
        for dirpath, _, _ in os.walk(pb_root_path):
            sys.path.append(dirpath)

        for file_path in u.get_files(pb_root_path, ["*_pb2.py"]):
            filename_without_ext = os.path.splitext(os.path.split(file_path)[1])[0]
            module_name = "{}".format(filename_without_ext)
            importlib.import_module(module_name)
            # unreal.log(f"loaded module : {module_name}")
            pb_helper.loaded_modules.append(module_name)

    @staticmethod
    def get_descriptor_field(instance, member):
        for field in type(instance).DESCRIPTOR.fields:
            if field.name == member:
                return field

    @staticmethod
    def get_type_with_module(type_name):
        if pb_helper.loaded_modules is None:
            pb_helper.load_modules()

        pb_type, result_module = None, None
        # unreal.log(len(pb_helper.loaded_modules))
        for loaded_module in pb_helper.loaded_modules:
            # unreal.log(f" try find {type_name} in {loaded_module}")
            try:
                module = sys.modules[loaded_module]
                pb_type = getattr(module, type_name)
                # unreal.log(f'result : {str(pb_type)}')
                if pb_type is not None:
                    result_module = loaded_module
                    break
            except:
                continue
        
        return pb_type, result_module
import sys
import os
import importlib

import utility as u
import unreal

from google.protobuf.descriptor import FieldDescriptor


class pb_helper:
    # ** 记录Python生成的pb模块
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
            module = importlib.import_module(module_name)
            pb_helper.loaded_modules.append(module)

    @staticmethod
    def get_descriptor_field(instance, member):
        for field in type(instance).DESCRIPTOR.fields:
            if field.name == member:
                return field

    @staticmethod
    def get_type_with_module(type_name):
        if pb_helper.loaded_modules is None:
            pb_helper.load_modules()

        pb_type = None
        for module in pb_helper.loaded_modules:
            try:
                pb_type = getattr(module, type_name)
                if pb_type is not None:
                    break
            except:
                pass
        return pb_type, module
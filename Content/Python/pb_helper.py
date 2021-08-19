import sys
import os
import importlib
import configparser
import re

import utility as u

from unreal_import_switch import unreal


class pb_helper:
    """
    记录Python生成的pb模块
    """
    loaded_modules = None

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

    @staticmethod
    def load_protobuf_preference():
        """
        载入Protobuf配置文件
        """
        project_config_dir = unreal.Paths.project_config_dir()

        preferences_file_path = os.path.join(project_config_dir, "DefaultProtobuf.ini")
        if not os.path.exists(preferences_file_path):
            unreal.log_error(f'Config file don\'t exist at path {preferences_file_path}')
            return

        config = configparser.ConfigParser()
        config.read(preferences_file_path)
        if '/Script/Protobuf.ProtobufSetting' in config:
            return config['/Script/Protobuf.ProtobufSetting']
            
    @staticmethod
    def get_path_from_preference(preference, path_key):
        """
        从配置中获取指定路径，并转化为UE工程路径

        @preference (dict())
        配置
        @path_key (str)
        获取对应字段名
        """
        preference_path = None if path_key not in preference else preference[path_key]
        pattern = re.compile(r'\(Path="(.*)"\)')
        match_result = pattern.match(preference_path)
        return os.path.abspath(os.path.normpath(os.path.join(unreal.Paths.project_dir(), match_result.group(1))))

    @staticmethod
    def get_option_value(options, target_option, default=''):
        """
        从options结构中获得target_option的值，如果找不到返回空字符串

        @options (object)
        options字段，是DESCRIPTOR中的一个结构，详情见 google.protobuf.descriptor.FieldDescriptor

        @target_option (str)
        option名称，参考options_ext.proto定义
        
        @default (str)
        找不到时需要返回的默认值
        """
        for option_field_descriptor, option_field_value in options.ListFields():
            if option_field_descriptor.name == target_option:
                return option_field_value
        return default

import os
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'fake_unreal':
    # ** NOTE:构造一个假的unreal模块，供没有启动引擎的情况下调用
    import utility as u
    class unreal:
        def log(message):
            u.info(message)

        def log_warning(message):
            u.warning(message)


        def log_error(message):
            u.error(message)


        class Paths:
            @staticmethod
            def project_intermediate_dir():
                return os.path.join(unreal.Paths.project_dir(), 'Intermediate')

            @staticmethod
            def project_content_dir():
                return os.path.join(unreal.Paths.project_dir(), 'Content')

            @staticmethod
            def project_dir():
                return os.path.realpath(os.path.join(os.path.split(__file__)[0], '../../../../'))

            @staticmethod
            def project_config_dir():
                return os.path.join(unreal.Paths.project_dir(), 'Config')

            @staticmethod
            def project_plugins_dir():
                return os.path.join(unreal.Paths.project_dir(), 'Plugins')

else:
    import unreal as unreal
import pb_helper
import pb_shell
import protobuf
import template.cpp_wrapper
import unreal
import time as t
import sys
import importlib


def reload_modules():
    importlib.reload(protobuf)
    importlib.reload(template.cpp_wrapper)
    importlib.reload(pb_shell)
    importlib.reload(pb_helper)
    # unreal.log(type(sys.modules))
    pending_modules = []
    for module_name  in sys.modules:
        if module_name.endswith('_pb2'):
            if module_name.replace('_pb2', '') in protobuf.exclude_proto_names():
                continue
            pending_modules.append(module_name)

    for module_name in pending_modules:
        module = sys.modules[module_name]
        importlib.reload(module)
        # del(sys.modules[module_name])


reload_modules()
if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == 'all':
        start = t.time()
        protobuf.generate_all()
        unreal.log(f'protobuf.generate_all finished in {t.time() - start} seconds')
else:
    start = t.time()
    protobuf.generate_excel_bin()
    unreal.log(f'protobuf.generate_excel_bin finished in {t.time() - start} seconds')

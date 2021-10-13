import pb_helper
import pb_shell
import protobuf
import template.cpp_template
import template.h_template
import template.template_helper
import unreal
import time as t
import sys
import importlib


def reload_modules():
    importlib.reload(protobuf)
    importlib.reload(template.template_helper)
    importlib.reload(template.cpp_template)
    importlib.reload(template.h_template)
    importlib.reload(pb_shell)
    importlib.reload(pb_helper)
    # unreal.log(type(sys.modules))
    pending_modules = []
    for module_name  in sys.modules:
        if module_name.endswith('_pb2'):
            if module_name.replace('_pb2', '') in pb_helper.exclude_proto_names():
                continue
            pending_modules.append(module_name)

    for module_name in pending_modules:
        module = sys.modules[module_name]
        try:
            importlib.reload(module)
        except:
            None
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

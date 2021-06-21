import pb_shell
import protobuf
import template.cpp_wrapper
import unreal
import time as t
import sys
import importlib

# ** Debug uesage
# for name in sys.modules:
#     unreal.log(f"{name!r} already in sys.modules")

# xlsx_pb2 = None
# if 'xlsx_pb2' in sys.modules:
#     xlsx_pb2 = sys.modules['xlsx_pb2']
# importlib.reload(protobuf)
# importlib.reload(template.cpp_wrapper)
# importlib.reload(pb_shell)
# if xlsx_pb2:
#     importlib.reload(xlsx_pb2)

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

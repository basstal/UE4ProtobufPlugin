import sys
sys.argv.append('fake_unreal')

import time as t
import protobuf
from unreal_import_switch import unreal


start = t.time()
protobuf.generate_all()
unreal.log(f'protobuf.generate_all finished in {t.time() - start} seconds')
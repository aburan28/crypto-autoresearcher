#!/usr/bin/env python3
"""Build pinned BL/rho and independent endpoint-recycling candidate; no scientific runs."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--sanitize',action='store_true');p.add_argument('--development',action='store_true');a=p.parse_args()
r=Path(__file__).resolve().parent
for f in json.loads((r/'vendor-source.json').read_text())['files']:
 assert hashlib.sha256((r/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
a.output.resolve().parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='endpoint-reuse-build-') as tmp:
 instrumentation=['-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if a.sanitize else []
 defs=['-DER_DEVELOPMENT_API'] if a.development else []
 objects=[]
 for name in ['rng_instrumentation.c','baseline_inspection.c','candidate/endpoint_reuse.c','vendor/src/rho.c','vendor/src/util.c','vendor/src/modarith.c']:
  obj=Path(tmp)/(Path(name).stem+'.o');objects.append(str(obj))
  subprocess.run(['gcc','-std=gnu11','-O2',*instrumentation,*defs,'-Wall','-Wextra','-Werror','-pthread','-include',str(r/'rng_instrumentation.h'),'-I'+str(r/'vendor/include'),'-I'+str(r/'vendor/src'),'-I'+str(r/'candidate'),'-c',str(r/name),'-o',str(obj)],check=True)
 subprocess.run(['g++','-std=c++20','-O2',*instrumentation,*defs,'-Wall','-Wextra','-Wpedantic','-Werror','-Wconversion','-Wshadow','-pthread','-isystem',str(r/'vendor/include'),str(r/'endpoint_reuse.cpp'),*objects,'-lm','-o',str(a.output.resolve())],check=True)
print(a.output.resolve())

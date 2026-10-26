#!/usr/bin/env python3
"""Build unchanged upstream C algorithms plus the shared-arithmetic C++ adapter."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--sanitize',action='store_true')
a=p.parse_args();here=Path(__file__).resolve().parent;output=a.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='baseline-build-') as temporary:
    objects=[]
    extra=['-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if a.sanitize else ['-O2']
    for source in ['rho','precomp','util','modarith']:
        obj=Path(temporary)/(source+'.o');objects.append(str(obj))
        subprocess.run(['gcc','-std=gnu11',*extra,'-Wall','-Wextra','-Werror','-pthread','-I'+str(here/'vendor/include'),'-I'+str(here/'vendor/src'),'-c',str(here/'vendor/src'/f'{source}.c'),'-o',str(obj)],check=True)
    subprocess.run(['g++','-std=c++20',*extra,'-Wall','-Wextra','-Wconversion','-Werror','-pthread','-I'+str(here/'vendor/include'),str(here/'baselines.cpp'),*objects,'-lm','-o',str(output)],check=True)
print(output)

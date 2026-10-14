"""Compact native point measurements. All generator/start scalars are public."""
import ctypes
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent


def build(target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    command=['cc','-O3','-shared','-fPIC',str(HERE/'engine.c'),'-o',str(target),'-lcrypto','-Wall','-Wextra','-Wno-deprecated-declarations']
    result=subprocess.run(command,capture_output=True,text=True)
    (target.parent/(target.name+'.build.json')).write_text(json.dumps({'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
    if result.returncode:raise RuntimeError(result.stderr)
    return target


def seed_for(*parts):return hashlib.sha256('|'.join(map(str,parts)).encode()).digest()


class Engine:
    def __init__(self,library):
        self.lib=ctypes.CDLL(str(library))
        self.lib.windows.argtypes=[ctypes.c_char_p]*6+[ctypes.c_int,ctypes.c_uint64,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint64,ctypes.c_uint64]+[ctypes.c_char_p]*5+[ctypes.c_void_p]*6
        self.lib.windows.restype=ctypes.c_int

    def sample(self,curve,step,named,count,metric,threshold,start_seed,gen_seed,directory,retain_full=False,max_event_frames=None,event_limit_bytes=32*1024**2):
        directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);cohorts=3 if named else 1;width=(curve['p'].bit_length()+7)//8
        bits=np.zeros((count,cohorts,32),dtype=np.uint8);scores=np.zeros((count,cohorts,3),dtype=np.uint32)
        scalars=np.zeros((count,width),dtype=np.uint8);hashes=ctypes.create_string_buffer(cohorts*32)
        counters=(ctypes.c_uint64*2)();checks=ctypes.c_uint64()
        paths=[directory/'events.frames',directory/'witness.frames',directory/'coordinates.raw' if retain_full else None]
        parameters=[curve[k] for k in ('p','A','B','N')]+list(step)
        status=self.lib.windows(*[str(v).encode() for v in parameters],named,count,metric,threshold,count if max_event_frames is None else max_event_frames,event_limit_bytes,start_seed,gen_seed,
                 *[str(p).encode() if p else None for p in paths],bits.ctypes.data,scores.ctypes.data,scalars.ctypes.data,hashes,ctypes.byref(counters),ctypes.byref(checks))
        if status!=1:
            error=ArithmeticError(f'Compact point engine refused/failed with code {status}; partial frame files preserved')
            error.native_code=status;error.counter_consumed=list(counters);error.oncurve_checks=checks.value
            raise error
        return {'bits':bits,'scores':scores,'public_scalars':scalars,'coordinate_sha256':[hashes.raw[i*32:(i+1)*32].hex() for i in range(cohorts)],
                'counter_consumed':list(counters),'oncurve_checks':checks.value}

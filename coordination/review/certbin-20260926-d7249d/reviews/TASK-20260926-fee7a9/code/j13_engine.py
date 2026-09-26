"""J13: run the PINNED engine (crypto_autoresearcher.gf2 at the archive commit, tree ==
934bee5's) UNCHANGED on given systems. Input: a JSONL of {key, E_hex}; or instance keys.
Records M_3, M_4 (macaulay_closure) and W_4 (w_closure), want_cert=False, plus build_info.
Usage: j13_engine.py <worktree_src> <codedir> <input.jsonl> <out.jsonl>"""
import sys, json, time, os, hashlib
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from crypto_autoresearcher.gf2 import closure, kernels
from crypto_autoresearcher.gf2 import _native
from rtlib19 import decode_E_hex
inp, outp = sys.argv[3], sys.argv[4]
C3 = closure.Closure(20, 3, 19); C4 = closure.Closure(20, 4, 19)
fo = open(outp, 'w')
first = True
for line in open(inp):
    r = json.loads(line)
    eqs = [sorted(s) for s in decode_E_hex(r['E_hex'])]
    t0 = time.time()
    m3, _ = C3.macaulay_closure(eqs, want_cert=False)
    m4, _ = C4.macaulay_closure(eqs, want_cert=False)
    w4, _ = C4.w_closure(eqs, want_cert=False)
    rec = {'key': r['key'], 'M_3': m3, 'M_4': m4, 'W_4': w4, 'seconds': round(time.time() - t0, 3)}
    if first:
        rec['build_info'] = dict(_native.build_info)
        rec['backend'] = kernels.backend() if callable(getattr(kernels, 'backend', None)) else str(getattr(kernels, 'backend', None))
        rec['engine_file_sha256'] = {f: hashlib.sha256(open(os.path.join(sys.argv[1], 'crypto_autoresearcher/gf2', f), 'rb').read()).hexdigest()
                                     for f in sorted(os.listdir(os.path.join(sys.argv[1], 'crypto_autoresearcher/gf2'))) if f.endswith(('.py', '.c'))}
        first = False
    fo.write(json.dumps(rec) + '\n'); fo.flush()

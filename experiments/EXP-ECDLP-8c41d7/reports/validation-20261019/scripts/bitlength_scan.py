#!/usr/bin/env python3
"""Bit-length scan of the msolve 0.6.5 crash on the SAME construction (committed code, patched prime only).

For each prime in a list (all p = 3 mod 4 with 2^L | p+1), rebuild the m=4 dense B system (S_5 + four dense
degree-2^L fibre polynomials) with the committed launcher and run `msolve -g 2 -t 1` with a short timeout.
Outcome classes: ok (solved), rc-11 (segfault), timeout (still running = read the input and computed).
Informational on timing.  usage: bitlength_scan.py <L> <inst> <timeout> <outjsonl> p1 p2 ...
"""
import hashlib, importlib, json, os, sys, tempfile
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7")
bm = importlib.import_module("block_order_m4")
bog = bm.bog
pkm = bog.pkm
L, inst, to, outp = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
primes = [int(x) for x in sys.argv[5:]]
plan = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/trial-plan.json"))
seed = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{inst}".encode()).hexdigest()[:12], 16)
kind = "planted" if inst < 4 else "random"
rec = []
def fake_run_ms(vars_, polys, p, extra, timeout):
    if all(v.startswith("x") for v in vars_) and not extra:      # B_ms only
        path = bog.msg.write_input(vars_, p, polys)
        st, wall, log = bog.msg.run_msolve(["-f", path, "-o", path + ".gb", "-g", "2", "-v", "2", "-t", "1"], to)
        for f in (path, path + ".gb"):
            if os.path.exists(f):
                os.unlink(f)
        rec.append(dict(p=p, bits=p.bit_length(), L=L, status=st, wall_s=wall))
    return dict(status="skipped"), None
bog.run_ms = fake_run_ms
for p in primes:
    assert p % 4 == 3 and p % (2 ** L) == 2 ** L - 1, p
    pkm.find_prime = lambda m, L_, p=p: p
    n0 = len(rec)
    for (ii, kk) in ((inst, kind), (4, "random"), (5, "random")):
        sd = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{ii}".encode()).hexdigest()[:12], 16)
        try:
            bog.run_instance(dict(m=4, L=L, inst=ii, kind=kk, seed=sd, timeout=to, arms=["B_ms"]))
            break
        except IndexError:   # empty factor base for a planted target (generation artefact, not a solver event)
            continue
    if len(rec) == n0:
        rec.append(dict(p=p, bits=p.bit_length(), L=L, status="no_instance"))
    rec[-1]["inst_used"] = ii
    print(json.dumps(rec[-1]), flush=True)
    with open(outp, "a") as fh:
        fh.write(json.dumps(rec[-1]) + "\n")

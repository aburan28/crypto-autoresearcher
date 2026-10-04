#!/usr/bin/env python3
"""J8 (1) -- TASK-20260924-d95e70. Confirm the trivial-syzygy count at D = 4
BY CONSTRUCTION, not by formula:
  Koszul  (i < j): sum_{m in supp f_j} row(m, i) + sum_{m in supp f_i} row(m, j) = 0
  field   (i)    : sum_{m in supp f_i} row(m, i) + row(1, i) = 0   (f_i * f_i = f_i)
For each system: build M_4 (rows mu*f_k, deg mu <= 2), verify each of the 153
vectors is a left-kernel vector (XOR of its rows is 0), compute their rank, and
compare with the left-kernel dimension 2924 - rank(M_4). If rank(trivial) =
153 = 2924 - rank(M_4), the trivial syzygies SPAN the left kernel (the system is
"semi-regular at D = 4" in the plan's sense).

Systems: 3 random dense quadratic systems (random.Random(1..3), every monomial
of degree <= 2 iid Bernoulli(1/2)); the first 5 N-AFF62 and first 5 N-F262
instances and 5 U62 instances (E_hex from the run's instance-sets.json, decoded
with my own implementation of the documented convention; the convention is
validated on every U62 instance used by comparing with my own descent).
Also: support audit of all 124 null instances (every monomial is bilinear
v_i v_{9+j}, linear, or constant?)."""
import json
import os
import random
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j7-mechanism"))
import rtlib as R  # noqa: E402

RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
SRC = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"

EQ_MONS = []
for d in range(3):
    EQ_MONS.extend(combinations(range(18), d))
EQ_MASKS = [sum(1 << i for i in m) for m in EQ_MONS]
assert len(EQ_MASKS) == 172


def decode(hexes):
    out = []
    for h in hexes:
        v = int(h, 16)
        out.append(frozenset(EQ_MASKS[j] for j in range(172) if (v >> j) & 1))
    return out


def analyse(sp, fs):
    mus = sp.multipliers(2)
    assert len(mus) == 172
    rows = []
    for mu in mus:
        for k in range(17):
            p = set()
            for m in fs[k]:
                p ^= {mu | m}
            rows.append(sp.to_int(p))
    ech = R.Echelon()
    for r in rows:
        ech.add(r)
    rank = ech.rank()
    idx = {mu: a for a, mu in enumerate(mus)}

    def rid(mu, k):
        return idx[mu] * 17 + k
    syz = []
    for i in range(17):
        for j in range(i + 1, 17):
            v = 0
            for m in fs[j]:
                v ^= 1 << rid(m, i)
            for m in fs[i]:
                v ^= 1 << rid(m, j)
            syz.append(v)
    for i in range(17):
        v = 0
        for m in fs[i]:
            v ^= 1 << rid(m, i)
        v ^= 1 << rid(0, i)
        syz.append(v)
    in_kernel = 0
    for v in syz:
        acc = 0
        x = v
        while x:
            b = x.bit_length() - 1
            acc ^= rows[b]
            x ^= 1 << b
        in_kernel += (acc == 0)
    se = R.Echelon()
    for v in syz:
        se.add(v)
    return {"rank_M4": rank, "left_kernel_dim": len(rows) - rank, "trivial_constructed": len(syz),
            "trivial_in_left_kernel": in_kernel, "trivial_rank": se.rank(),
            "trivial_span_left_kernel": se.rank() == len(rows) - rank,
            "nontrivial_syzygies": (len(rows) - rank) - se.rank(),
            "fall_profile_M4": ech.dims_by_deg(sp.coldeg, 4)}


def main():
    sp = R.Space(range(18), 4)
    iset = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]
    B = json.load(open(os.path.join(SRC, "curve.json")))["B"]
    out = {"task": "TASK-20260924-d95e70", "joint": "J8 (1)", "systems": []}
    for sd in (1, 2, 3):
        rng = random.Random(sd)
        fs = [frozenset(m for m in EQ_MASKS if rng.getrandbits(1)) for _ in range(17)]
        r = analyse(sp, fs)
        r.update({"system": f"random dense quadratic, random.Random({sd})"})
        out["systems"].append(r)
        print(r, flush=True)
    for sname in ("N-AFF62", "N-F262", "U62"):
        for inst in iset[sname][:5]:
            fs = decode(inst["E_hex"])
            r = {"system": inst["key"]}
            if sname == "U62":
                r["decode_equals_own_descent"] = (fs == R.descent(B, inst["archived"]["x_R"]))
            r.update(analyse(sp, fs))
            out["systems"].append(r)
            print(r, flush=True)
    # support audit of all null instances
    def kind(m):
        a = bin(m & 0x1FF).count("1")
        b = bin(m >> 9).count("1")
        if a + b <= 1:
            return "const_or_linear"
        if a == 1 and b == 1:
            return "bilinear"
        return "pure_block_quadratic"
    audit = {}
    for sname in ("N-AFF62", "N-F262", "U62", "S62", "C20"):
        cnt = {}
        for inst in iset[sname]:
            for f in decode(inst["E_hex"]):
                for m in f:
                    k = kind(m)
                    cnt[k] = cnt.get(k, 0) + 1
        audit[sname] = cnt
    out["support_audit_all_instances"] = audit
    print(audit)
    json.dump(out, open(os.path.join(HERE, "syzygy.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

"""J10 O4 construction (TASK-20260926-c58e87), EXACTLY as review-plan proves_too_much.objects O4
fixes it. NO ENGINE CALL in this script (own code only: j10-ptm/rtlib.py).

  seed 2026092689101; g = numpy.random.Generator(numpy.random.PCG64(seed)); numpy 2.4.6.
  (1) basis: b = g.integers(0, 2**17, size=9); reject and redraw while the nine are
      F_2-dependent or all have degree < 9 (every rejection logged).
  (2) x_1 = sum_{j<9} v_j b_j, x_2 = sum_{j<9} v_{9+j} b_j; E'_S3(x_R) = multilinearized
      coordinate expansion of S_3(x_1, x_2, x_R) over V' (rtlib.descent with this basis).
  (3) U', S'_L by object.union_support with E'_S3 in place of E_S3 (E'^0 = E'_S3(0),
      E'^j = E'_S3(t^j) xor E'^0); S'_L = U' cap columns 0..18, row-major.
  (4) slots 0..19 = the 20 lowest-idx U62 x_R in the slot order of instance_sets.xr144
      (U62 listed order, ascending idx; RC-1 instance-sets.json).
  (5) the same generator continues: per attempt bits = g.integers(0, 2, size=|S'_L|) placed
      row-major on S'_L over E'_S3(x_R)'s quadratic columns (all other columns 0..18 zero);
      identity draw (== E'_S3(x_R)) rejected; duplicate of an already-kept system of this
      arm rejected (frozen keep_rule; compared by exact E); then s by exhaustive 2^18
      evaluation; keep the first s = 0 (unsat) and the first s >= 1 (sat); stop when both
      are filled; at most 256 attempts (a = 0..255) per slot, else EXHAUSTED for the role.
  E_sha256 here = sha256 of json.dumps(list of lowercase hex rows, bit j = column j) --
  this script's own convention (the specification does not fix the hash input).
Usage: python3 o4_build.py <worktree> <outdir>
"""
import gzip
import json
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

wt, outdir = sys.argv[1], sys.argv[2]
SEED = 2026092689101
t0 = time.time()
assert np.__version__ == "2.4.6", np.__version__
g = np.random.Generator(np.random.PCG64(SEED))


def independent(vals):
    ech = {}
    for x in vals:
        while x:
            hb = x.bit_length() - 1
            if hb in ech:
                x ^= ech[hb]
            else:
                ech[hb] = x
                break
        if x == 0:
            return False
    return True


basis_log = []
while True:
    b = [int(x) for x in g.integers(0, 2 ** 17, size=9)]
    dep = not independent(b)
    lowdeg = all(x < (1 << 9) for x in b)
    rec = {"draw": len(basis_log), "b": b, "dependent": dep, "all_deg_lt_9": lowdeg,
           "accepted": not dep and not lowdeg}
    basis_log.append(rec)
    if rec["accepted"]:
        break
basis = basis_log[-1]["b"]

U = R.union_support(basis)
SL = R.S_L_positions(U)
support = {"basis": basis, "U_row_sizes": [int(U[k].sum()) for k in range(17)],
           "S_L_size": len(SL), "S_L_row_sizes": [sum(1 for (k, c) in SL if k == kk) for kk in range(17)],
           "U_bilinear_all_81_per_row": [bool(all(U[k, c] for c in R.BILINEAR_COLS)) for k in range(17)],
           "U_nonbilinear_quadratic_cols": int(sum(U[k, c] for k in range(17) for c in R.QUAD_COLS if c not in set(R.BILINEAR_COLS))),
           "U_linear_all_18_per_row": [bool(all(U[k, c] for c in range(1, 19))) for k in range(17)],
           "U_const_per_row": [int(U[k, 0]) for k in range(17)]}

d = json.load(open(f"{wt}/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"))
u62 = d["sets"]["U62"]
assert [r["idx"] for r in u62] == sorted(r["idx"] for r in u62)
slots = [{"slot": i, "set": "U62", "idx": u62[i]["idx"], "x_R": u62[i]["archived"]["x_R"]} for i in range(20)]

attempts = []
kept = []
descents = []
kept_bytes = set()
for sl in slots:
    xr = sl["x_R"]
    Ed = R.descent(xr, basis)
    descents.append({"slot": sl["slot"], "idx": sl["idx"], "x_R": xr, "E_hex": R.E_to_hex(Ed),
                     "E_sha256": R.E_sha(Ed)})
    base = Ed.copy()
    base[:, :19] = 0  # keep only the quadratic columns
    need = {"unsat": None, "sat": None}
    for a in range(256):
        bits = g.integers(0, 2, size=len(SL))
        E = base.copy()
        for (k, c), bit in zip(SL, bits):
            E[k, c] = int(bit)
        key = E.tobytes()
        rec = {"slot": sl["slot"], "attempt": a, "E_sha256": R.E_sha(E)}
        if np.array_equal(E, Ed):
            rec.update(s=None, outcome="rejected_identity")
        elif key in kept_bytes:
            rec.update(s=None, outcome="rejected_duplicate")
        else:
            sol = R.solutions(E)
            s = len(sol)
            rec["s"] = s
            role = "unsat" if s == 0 else "sat"
            if need[role] is None:
                need[role] = a
                rec["outcome"] = f"kept_{role}"
                kept_bytes.add(key)
                kept.append({"key": f"N-CONV-VR:{sl['slot']}:{role}", "slot": sl["slot"], "idx": sl["idx"],
                             "x_R": xr, "role": role, "attempt": a, "E_hex": R.E_to_hex(E),
                             "E_sha256": R.E_sha(E), "s": s, "solutions": sol if s else []})
            else:
                rec["outcome"] = "discarded"
        attempts.append(rec)
        if need["unsat"] is not None and need["sat"] is not None:
            break
    for role in ("unsat", "sat"):
        if need[role] is None:
            kept.append({"key": f"N-CONV-VR:{sl['slot']}:{role}", "slot": sl["slot"], "role": role,
                         "EXHAUSTED": "cap"})

# descents' own s (the S_3 descent over V' at each slot)
for dd in descents:
    E = R.hex_to_E(dd["E_hex"])
    sol = R.solutions(E)
    dd["s"] = len(sol)
    dd["solutions"] = sol

with gzip.open(f"{outdir}/o4-generation-log.jsonl.gz", "wt") as fh:
    for rec in attempts:
        fh.write(json.dumps(rec) + "\n")
json.dump({"seed": SEED, "numpy": np.__version__, "basis_draws": basis_log, "support": support,
           "slots": slots}, open(f"{outdir}/o4-basis-and-support.json", "w"), indent=1)
json.dump({"kept": kept, "descents": descents}, open(f"{outdir}/o4-systems.json", "w"))
summ = {"basis_rejections": len(basis_log) - 1, "basis": basis, "S_L_size": len(SL),
        "attempts": len(attempts),
        "rejected_identity": sum(1 for r in attempts if r["outcome"] == "rejected_identity"),
        "rejected_duplicate": sum(1 for r in attempts if r["outcome"] == "rejected_duplicate"),
        "kept": sum(1 for k in kept if "EXHAUSTED" not in k),
        "exhausted": [k["key"] for k in kept if "EXHAUSTED" in k],
        "unsat_fraction_among_evaluated": None,
        "descent_s": [dd["s"] for dd in descents],
        "seconds": round(time.time() - t0, 1)}
ev = [r for r in attempts if r.get("s") is not None]
summ["unsat_fraction_among_evaluated"] = [sum(1 for r in ev if r["s"] == 0), len(ev)]
json.dump(summ, open(f"{outdir}/o4-build-summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
print(json.dumps(support, indent=1)[:1500])

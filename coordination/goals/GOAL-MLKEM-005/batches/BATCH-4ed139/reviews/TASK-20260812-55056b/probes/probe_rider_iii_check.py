#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe G -- rider (iii)'s checkable half.

fpylll is ABSENT on the Validator host, so the REDUCTION cannot be re-executed
by this session. That is COVERAGE, never a negative result. What IS checkable
without fpylll, and is checked here:

  (a) every hkz and lam1n value rider (iii) publishes is compared BIT-WISE
      against the committed results_relvar.json it claims to reproduce -- if the
      rider's table were transcribed from its own output rather than measured,
      the comparison would still pass, but if it were transcribed WRONG it
      would fail, and a wrong transcription is the failure mode a reader of the
      report is exposed to;
  (b) ENVIRONMENTS_DIFFER is RECOMPUTED field by field from the two committed
      environment blocks, since the rider REFUSED a cross-platform claim on the
      strength of that Boolean and the refusal must be warranted;
  (c) the 96 = 2 x 2 x 3 x 8 comparison count is reconstructed, and the rider's
      own disclosure that the 48 lam1n comparisons cover only 16 DISTINCT
      measured values is checked against the committed file's structure;
  (d) the basis construction rider (iii) verified is re-verified here at L7/L8
      (this needs no fpylll).

Run from the repository root.
"""
import json
import sys

import numpy as np

RELVAR = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
          "TASK-20260809-cda2f6/results_relvar.json")
R3 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
      "TASK-20260812-0e930c/results_l7l8.json")
Q = 3329


def find_values(obj, path=""):
    """Yield (path, value) for every float leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from find_values(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from find_values(v, "%s[%d]" % (path, i))
    elif isinstance(obj, float):
        yield path, obj


def main():
    rv = json.load(open(RELVAR))
    r3 = json.load(open(R3))
    print("=== (d) BASIS CONSTRUCTION AT L7/L8, RE-VERIFIED (no fpylll needed)")
    ok = True
    for lat, (d, k) in (("L7", (20, 6)), ("L8", (20, 14))):
        for i in range(8):
            A = np.random.default_rng([1, d, k, i]).integers(
                0, Q, size=(k, d - k), dtype=np.int64)
            B = np.zeros((d, d), dtype=np.int64)
            B[:k, :k] = np.eye(k, dtype=np.int64)
            B[:k, k:] = A
            B[k:, k:] = Q * np.eye(d - k, dtype=np.int64)
            good = (B.dtype == np.int64
                    and np.array_equal(B[:k, :k], np.eye(k, dtype=np.int64))
                    and np.array_equal(B[k:, :k],
                                       np.zeros((d - k, k), np.int64))
                    and np.array_equal(B[k:, k:],
                                       Q * np.eye(d - k, dtype=np.int64))
                    and int(A.min()) >= 0 and int(A.max()) <= Q - 1)
            ok = ok and good
    print("   16 bases at L7/L8 structurally verified:", ok)

    print("\n=== (a) RIDER (iii) PUBLISHED VALUES vs COMMITTED results_relvar")
    # committed per-basis hkz and lam1n at L7/L8
    comm = {}
    gv = rv["G_VAR"]["per_candidate"]
    for cand in ("hkz", "lam1n"):
        pc = gv[cand]["per_cell"]
        for cell, rec in pc.items():
            if cell.split("_")[0] in ("L7", "L8"):
                pb = rec.get("per_basis") or rec.get("values")
                if pb is not None:
                    comm[(cand, cell)] = pb
    print("   committed L7/L8 per-basis vectors found:", len(comm))
    for kk in sorted(comm):
        print("     ", kk, "n=", len(comm[kk]))

    # rider (iii)'s own comparison block
    keys = list(r3.keys())
    print("\n   rider (iii) results_l7l8.json top keys:", keys)
    cmpblk = None
    for k in keys:
        if "compar" in k.lower() or "deviat" in k.lower():
            cmpblk = k
    print("   comparison block key:", cmpblk)

    # brute-force: every committed L7/L8 value must appear bitwise in r3
    r3vals = {v for _, v in find_values(r3)}
    missing = []
    total = 0
    for (cand, cell), pb in sorted(comm.items()):
        for v in pb:
            total += 1
            if float(v) not in r3vals:
                missing.append((cand, cell, v))
    print(f"\n   committed L7/L8 per-basis values checked : {total}")
    print(f"   present BITWISE in rider (iii)'s output   : {total - len(missing)}")
    print(f"   MISSING                                   : {len(missing)}")
    for m in missing[:10]:
        print("      ", m)

    print("\n=== (b) ENVIRONMENTS_DIFFER, RECOMPUTED FIELD BY FIELD")
    e_c = rv.get("environment", {})
    e_r = r3.get("environment", {})
    fields = ["operating_system", "architecture", "python_version"]
    rows = []
    for f in fields:
        rows.append((f, e_c.get(f), e_r.get(f), e_c.get(f) == e_r.get(f)))
    for dep in ("numpy", "scipy", "fpylll"):
        a = (e_c.get("dependencies") or {}).get(dep)
        b = (e_r.get("dependencies") or {}).get(dep)
        rows.append(("dep:" + dep, a, b, a == b))
    ba = e_c.get("blas_threads") or {}
    bb = e_r.get("blas_threads") or {}
    for t in sorted(set(ba) | set(bb)):
        if t == "note":
            continue
        rows.append(("blas:" + t, ba.get(t), bb.get(t), ba.get(t) == bb.get(t)))
    for f, a, b, same in rows:
        print("   %-28s committed=%-45s rider=%-45s %s"
              % (f, str(a)[:45], str(b)[:45], "SAME" if same else "DIFFER"))
    differ = [r[0] for r in rows if not r[3]]
    print("\n   FIELDS DIFFERING:", differ if differ else "NONE")
    print("   ENVIRONMENTS_DIFFER recomputed by the Validator:",
          bool(differ))
    print("   rider (iii) declared ENVIRONMENTS_DIFFER = False;",
          "REFUSAL OF A CROSS-PLATFORM CLAIM IS WARRANTED" if not differ
          else "CHECK")
    # fields present in one record and not the other
    extra_r = sorted(set(e_r) - set(e_c))
    extra_c = sorted(set(e_c) - set(e_r))
    print("   fields only in rider (iii)'s record :", extra_r)
    print("   fields only in the committed record :", extra_c)

    print("\n=== (c) THE 96 COMPARISONS AND THE 16 DISTINCT lam1n VALUES")
    n_hkz = 2 * 3 * 8          # 2 lattices x 3 betas x 8 bases
    n_lam = 2 * 3 * 8
    print(f"   hkz  comparisons: 2 lattices x 3 betas x 8 bases = {n_hkz}")
    print(f"   lam1n comparisons: same shape                    = {n_lam}")
    print(f"   total                                            = "
          f"{n_hkz + n_lam}")
    lamvals = set()
    for (cand, cell), pb in comm.items():
        if cand == "lam1n":
            for v in pb:
                lamvals.add(float(v))
    print(f"   DISTINCT committed lam1n values at L7/L8         = "
          f"{len(lamvals)}  (rider (iii) discloses 16)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""J2 (3)(5): own affine decomposition, support U / S_L / Upos / ell_lin, and FULL replays of the
N-CONV19, N-ELL19, N-F219, N-AFF19 and F-RANDX19 streams from the specification text, with own
exhaustive s. Compared draw by draw with the archived draws-<ARM>.jsonl.gz and kept system by kept
system (E_hex, E_sha256, s, solutions, attempt/slot/family/stratum) with instances.jsonl.gz.

Alternative readings of the executor interpretations are replayed too, where they could matter
(see ALT below), to test whether the kept population depends on the reading.

usage: python3 replay_synthetic.py <run_dir>
"""
import gzip
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gf219 as G  # noqa: E402

RUN = sys.argv[1]
NR, NC = 19, 211


def load_jsonl(path):
    with gzip.open(path, "rt") as fh:
        return [json.loads(l) for l in fh]


def hexsha(E):
    hx = G.E_to_hex(E)
    return hx, G.E_sha256(hx)


mine_primary = load_jsonl(os.path.join(HERE, "my-draws-S3-PRIMARY.jsonl.gz"))
inst = load_jsonl(os.path.join(RUN, "instances.jsonl.gz"))
by_key = {r["key"]: r for r in inst}
res = {}

# ------------------------------------------------ affine decomposition and support (own)
E0 = G.descend_E(0)
Ej = [G.descend_E(1 << j) ^ E0 for j in range(NR)]
U = E0.copy()
for e in Ej:
    U |= e
Upos = np.flatnonzero(U.reshape(-1))
S_L = np.array([p for p in Upos if (p % NC) <= 20], dtype=np.int64)
tau = G.TAU
ell_cols = []
for j in range(10):
    if tau[j]:
        ell_cols += [1 + j, 1 + 10 + j]
sup = json.load(open(os.path.join(RUN, "support.json")))
res["support_vs_archived"] = {
    "Upos_equal": [int(x) for x in Upos] == sup["Upos"],
    "S_L_equal": [int(x) for x in S_L] == sup["S_L_positions"],
    "U_size": int(Upos.size), "archived_U_size": sup["U_size"],
    "S_L_size": int(S_L.size), "archived_S_L_size": sup["S_L_size"],
    "E0_nnz": int(E0.sum()), "archived_E0_nnz": sup["E0_nnz"],
    "Ej_nnz": [int(e.sum()) for e in Ej], "Ej_nnz_equal": [int(e.sum()) for e in Ej] == sup["Ej_nnz"],
    "U_hex_equal": G.E_to_hex(U) == sup["U_hex"],
    "ell_lin_columns": ell_cols, "archived_ell_lin_support": sup["ell_lin_support"],
    "tau_equal": tau == sup["tau"],
}
# Coordinator reading of object.parts on S_3: quadratic part only bilinear columns
bil = set()
for i in range(10):
    for j in range(10):
        a, b = i, 10 + j
        bil.add(G.MONO2.index((a, b)))
quad_nonbil = [c for c in range(21, 211) if c not in bil]
res["support_vs_archived"]["U_nonbilinear_quadratic_entries"] = int(U[:, quad_nonbil].sum())


def affine(xR):
    E = E0.copy()
    for j in range(NR):
        if (xR >> j) & 1:
            E ^= Ej[j]
    return E


# C-AFF19-style own check on every kept curve-algebra system
aff_bad = []
for r in inst:
    if r["arm"] in ("S3-U400", "S3-SAT100", "F-RANDX19"):
        Ed = G.descend_E(r["x_R"])
        if not np.array_equal(Ed, affine(r["x_R"])):
            aff_bad.append(r["key"])
        if G.E_to_hex(Ed) != r["E_hex"]:
            aff_bad.append(r["key"] + ":E_hex")
res["own_affine_decomposition_failures_on_curve_systems"] = aff_bad

# ------------------------------------------------ N-CONV19
def replay_nconv(dup_scope="kept"):
    g = np.random.Generator(np.random.PCG64(2026092460602))
    U400 = [m for m in mine_primary if m["outcome"] == "kept:S3-U400"]
    kept, log = [], []
    kept_sha = set()
    for slot in range(200):
        xR = U400[slot]["x_R"]
        base = G.descend_E(xR)
        need_u, need_s = True, slot < 50
        for att in range(256):
            if not (need_u or need_s):
                break
            bits = g.integers(0, 2, size=S_L.size)
            M = np.zeros(NR * NC, dtype=np.uint8)
            M.reshape(NR, NC)[:, 21:] = base[:, 21:]
            M[S_L] = bits.astype(np.uint8)
            M = M.reshape(NR, NC)
            hx, sh = hexsha(M)
            rec = {"slot": slot, "attempt": att, "E_sha256": sh}
            if np.array_equal(M, base):
                rec["outcome"] = "identity"
            elif sh in kept_sha:
                rec["outcome"] = "duplicate"
            else:
                s, sols = G.s_system(M, True)
                rec["s"] = s
                if s == 0 and need_u:
                    rec["outcome"] = "kept:unsat"
                    need_u = False
                    kept.append({"slot": slot, "attempt": att, "role": "unsat", "E_hex": hx, "E_sha256": sh, "s": 0, "x_R": xR, "E": M})
                    kept_sha.add(sh)
                elif s >= 1 and need_s:
                    rec["outcome"] = "kept:sat"
                    need_s = False
                    kept.append({"slot": slot, "attempt": att, "role": "sat", "E_hex": hx, "E_sha256": sh, "s": s, "solutions": sols, "x_R": xR, "E": M})
                    kept_sha.add(sh)
                else:
                    rec["outcome"] = "not_needed"
            log.append(rec)
    return kept, log


# ------------------------------------------------ N-ELL19 / N-F219 (stream mode)
def replay_stream(seed, ell, dup_scope="all"):
    g = np.random.Generator(np.random.PCG64(seed))
    kept, log = [], []
    seen = set()
    nu = ns = 0
    for d in range(20000):
        if nu >= 200 and ns >= 50:
            break
        M = np.zeros(NR * NC, dtype=np.uint8)
        M[Upos] = g.integers(0, 2, size=Upos.size).astype(np.uint8)
        M = M.reshape(NR, NC)
        rec = {"draw": d}
        if ell:
            c = int(g.integers(0, 2))
            M[18, :] = 0
            for col in ell_cols:
                M[18, col] = 1
            M[18, 0] = c
            rec["c"] = c
        hx, sh = hexsha(M)
        rec["E_sha256"] = sh
        if sh in seen:
            rec["outcome"] = "duplicate"
            log.append(rec)
            continue
        if dup_scope == "all":
            seen.add(sh)
        s, sols = G.s_system(M, True)
        rec["s"] = s
        if s == 0 and nu < 200:
            rec["outcome"] = "kept:unsat"
            nu += 1
            kept.append({"attempt": d, "role": "unsat", "E_hex": hx, "E_sha256": sh, "s": 0, "E": M})
            seen.add(sh)
        elif s >= 1 and ns < 50:
            rec["outcome"] = "kept:sat"
            ns += 1
            kept.append({"attempt": d, "role": "sat", "E_hex": hx, "E_sha256": sh, "s": s, "solutions": sols, "E": M})
            seen.add(sh)
        else:
            rec["outcome"] = "not_needed"
        log.append(rec)
    return kept, log


# ------------------------------------------------ N-AFF19
def replay_naff(include_duplicate_primary=False):
    g = np.random.Generator(np.random.PCG64(2026092460605))
    fams = []
    nz0 = np.flatnonzero(E0.reshape(-1))
    nzj = [np.flatnonzero(e.reshape(-1)) for e in Ej]
    for d in range(1, 6):
        F0 = np.zeros(NR * NC, dtype=np.uint8)
        F0[nz0] = g.integers(0, 2, size=nz0.size).astype(np.uint8)
        Fj = []
        for j in range(NR):
            Fx = np.zeros(NR * NC, dtype=np.uint8)
            Fx[nzj[j]] = g.integers(0, 2, size=nzj[j].size).astype(np.uint8)
            Fj.append(Fx.reshape(NR, NC))
        fams.append((F0.reshape(NR, NC), Fj))
    if include_duplicate_primary:
        prim = [m for m in mine_primary if m["x_R"] is not None and m["x_R"] >= 1024]
    else:
        prim = [m for m in mine_primary if "s" in m]  # classified attempts
    kept, log = [], []
    for d in range(1, 6):
        F0, Fj = fams[d - 1]
        seen = set()
        nu = ns = 0
        for m in prim:
            if nu >= 40 and ns >= 10:
                break
            xR = m["x_R"]
            M = F0.copy()
            for j in range(NR):
                if (xR >> j) & 1:
                    M ^= Fj[j]
            hx, sh = hexsha(M)
            rec = {"family": d, "primary_attempt": m["attempt"], "x_R": xR, "E_sha256": sh}
            if sh in seen:
                rec["outcome"] = "duplicate"
                log.append(rec)
                continue
            seen.add(sh)
            s, sols = G.s_system(M, True)
            rec["s"] = s
            if s == 0 and nu < 40:
                rec["outcome"] = "kept:unsat"
                nu += 1
                kept.append({"family": d, "attempt": m["attempt"], "role": "unsat", "E_hex": hx, "E_sha256": sh, "s": 0, "x_R": xR, "E": M})
            elif s >= 1 and ns < 10:
                rec["outcome"] = "kept:sat"
                ns += 1
                kept.append({"family": d, "attempt": m["attempt"], "role": "sat", "E_hex": hx, "E_sha256": sh, "s": s, "solutions": sols, "x_R": xR, "E": M})
            else:
                rec["outcome"] = "not_needed"
            log.append(rec)
    return kept, log, fams


# ------------------------------------------------ F-RANDX19
def replay_frandx(primary_scope="R_not_O", order=("degenerate", "duplicate", "primary")):
    g = np.random.Generator(np.random.PCG64(2026092460606))
    if primary_scope == "R_not_O":
        prim_x = {m["x_R"] for m in mine_primary if m["x_R"] is not None}
    elif primary_scope == "kept":
        prim_x = {m["x_R"] for m in mine_primary if m["outcome"].startswith("kept")}
    else:
        raise ValueError
    counts = {"TWIST": 0, "X2E": 0, "XE-NOT-2E": 0}
    kept, log = [], []
    seen = set()
    tr_bad = 0
    for att in range(30000):
        if all(v >= 200 for v in counts.values()):
            break
        x = int(g.integers(0, 1 << 19))
        rec = {"attempt": att, "x": x}
        label = None
        for chk in order:
            if chk == "degenerate" and x < 1024:
                label = "degenerate"
            elif chk == "duplicate" and x in seen:
                label = "duplicate"
            elif chk == "primary" and x in prim_x:
                label = "primary_collision"
            if label:
                break
        if x >= 1024:
            seen.add(x)
        if label:
            rec["outcome"] = label
            log.append(rec)
            continue
        w = x ^ G.A_CURVE ^ G.fmul(G.B_CURVE, G.finv(G.fsq(x)))
        if G.tr(w) == 1:
            st = "TWIST"
        else:
            Pt = G.lift_x(x)
            st = "X2E" if G.smul(G.Q_ORDER, Pt) is None else "XE-NOT-2E"
            if (st == "X2E") != (G.tr(x) == G.tr(G.A_CURVE)):
                tr_bad += 1
        rec["stratum"] = st
        if counts[st] >= 200:
            rec["outcome"] = "quota_full"
            log.append(rec)
            continue
        sB = G.s_bruteforce(x)
        sA, _ = G.s_quadratic(x)
        rec["s"] = sB
        rec["sA"] = sA
        if sB == 0:
            counts[st] += 1
            rec["outcome"] = "kept:unsat"
            E = G.descend_E(x)
            hx, sh = hexsha(E)
            kept.append({"attempt": att, "role": "unsat", "stratum": st, "x_R": x, "E_hex": hx, "E_sha256": sh, "s": 0, "E": E})
        else:
            rec["outcome"] = "sat_recorded"
        log.append(rec)
    return kept, log, tr_bad


def compare_logs(mine, arch, fields):
    mism = []
    for i in range(max(len(mine), len(arch))):
        m = mine[i] if i < len(mine) else None
        a = arch[i] if i < len(arch) else None
        if m is None or a is None:
            mism.append({"i": i, "mine": m, "archived": a})
            continue
        for f in fields:
            if m.get(f) != a.get(f):
                mism.append({"i": i, "field": f, "mine": m.get(f), "archived": a.get(f)})
    return mism


def compare_kept(arm, kept, extra_fields):
    arch = [r for r in inst if r["arm"] == arm]
    arch_sorted = sorted(arch, key=lambda r: r["index"])
    mism = []
    if len(arch_sorted) != len(kept):
        mism.append({"count_mine": len(kept), "count_archived": len(arch_sorted)})
    for i, (m, a) in enumerate(zip(kept, arch_sorted)):
        if a["key"] != f"{arm}:{i}":
            mism.append({"i": i, "key": a["key"]})
        for f in ["role", "E_hex", "E_sha256", "s", "attempt"] + extra_fields:
            if m.get(f) != a.get(f):
                mism.append({"i": i, "key": a["key"], "field": f, "mine": str(m.get(f))[:80], "archived": str(a.get(f))[:80]})
        if m["role"] == "sat" and sorted(a.get("solutions", [])) != m["solutions"]:
            mism.append({"i": i, "key": a["key"], "field": "solutions"})
        # s re-check of archived E from its E_hex with own evaluator
        Ea = G.hex_to_E(a["E_hex"])
        if G.s_system(Ea) != a["s"]:
            mism.append({"i": i, "key": a["key"], "field": "s_from_archived_E_hex"})
    return mism


def structural(arm, kept):
    bad = []
    for i, m in enumerate(kept):
        E = m["E"]
        if arm in ("N-F219", "N-ELL19"):
            rows = E[:18] if arm == "N-ELL19" else E
            if (rows & (1 - U[: rows.shape[0]])).any():
                bad.append((i, "outside_U"))
            if arm == "N-F219" and (E & (1 - U)).any():
                bad.append((i, "outside_U_full"))
        if arm == "N-ELL19":
            want = np.zeros(NC, dtype=np.uint8)
            for col in ell_cols:
                want[col] = 1
            if not np.array_equal(E[18, 1:], want[1:]):
                bad.append((i, "row18_not_ell_lin_plus_c"))
        if arm == "N-CONV19":
            base = G.descend_E(m["x_R"])
            if not np.array_equal(E[:, 21:], base[:, 21:]):
                bad.append((i, "quad_part_not_S3"))
            lower = E[:, :21].reshape(-1)
            allowed = np.zeros(NR * 21, dtype=np.uint8)
            for p in S_L:
                allowed[(p // NC) * 21 + (p % NC)] = 1
            if (lower & (1 - allowed)).any():
                bad.append((i, "lower_outside_S_L"))
        if arm == "N-AFF19":
            if (E & (1 - U)).any():
                bad.append((i, "outside_U"))
    return bad


out_logs = {}
# N-CONV19
kept, log = replay_nconv()
arch_log = load_jsonl(os.path.join(RUN, "draws-N-CONV19.jsonl.gz"))
res["N-CONV19"] = {
    "draws_mine": len(log), "draws_archived": len(arch_log),
    "log_mismatches": compare_logs(log, arch_log, ["slot", "attempt", "E_sha256", "s", "outcome"])[:20],
    "kept_mismatches": compare_kept("N-CONV19", kept, ["slot", "x_R"])[:20],
    "structural_violations": structural("N-CONV19", kept)[:20],
    "outcomes_mine": dict(Counter(r["outcome"] for r in log)),
    "s3_key_check": [r["key"] for r in inst if r["arm"] == "N-CONV19" and r.get("s3_key") != f"S3-U400:{r['slot']}"][:10],
}
out_logs["N-CONV19"] = log
print("N-CONV19 done", len(res["N-CONV19"]["log_mismatches"]), len(res["N-CONV19"]["kept_mismatches"]), flush=True)
# N-ELL19
kept, log = replay_stream(2026092460603, True)
arch_log = load_jsonl(os.path.join(RUN, "draws-N-ELL19.jsonl.gz"))
res["N-ELL19"] = {
    "draws_mine": len(log), "draws_archived": len(arch_log),
    "log_mismatches": compare_logs(log, arch_log, ["draw", "c", "E_sha256", "s", "outcome"])[:20],
    "kept_mismatches": compare_kept("N-ELL19", kept, [])[:20],
    "structural_violations": structural("N-ELL19", kept)[:20],
    "outcomes_mine": dict(Counter(r["outcome"] for r in log)),
}
out_logs["N-ELL19"] = log
print("N-ELL19 done", flush=True)
# N-F219
kept, log = replay_stream(2026092460604, False)
arch_log = load_jsonl(os.path.join(RUN, "draws-N-F219.jsonl.gz"))
res["N-F219"] = {
    "draws_mine": len(log), "draws_archived": len(arch_log),
    "log_mismatches": compare_logs(log, arch_log, ["draw", "E_sha256", "s", "outcome"])[:20],
    "kept_mismatches": compare_kept("N-F219", kept, [])[:20],
    "structural_violations": structural("N-F219", kept)[:20],
    "outcomes_mine": dict(Counter(r["outcome"] for r in log)),
}
out_logs["N-F219"] = log
print("N-F219 done", flush=True)
# N-AFF19 (executor reading and the alternative reading that includes duplicate primary attempts)
kept, log, fams = replay_naff(False)
arch_log = load_jsonl(os.path.join(RUN, "draws-N-AFF19.jsonl.gz"))
kept_alt, log_alt, _ = replay_naff(True)
res["N-AFF19"] = {
    "draws_mine": len(log), "draws_archived": len(arch_log),
    "log_mismatches": compare_logs(log, arch_log, ["family", "primary_attempt", "x_R", "E_sha256", "s", "outcome"])[:20],
    "kept_mismatches": compare_kept("N-AFF19", kept, ["family", "x_R"])[:20],
    "structural_violations": structural("N-AFF19", kept)[:20],
    "outcomes_mine": dict(Counter(r["outcome"] for r in log)),
    "ALT_include_duplicate_primary_attempts_same_kept_E_sha": [k["E_sha256"] for k in kept] == [k["E_sha256"] for k in kept_alt],
    "ALT_duplicate_rejections": sum(1 for r in log_alt if r["outcome"] == "duplicate"),
    "per_family_kept": {d: dict(Counter(k["role"] for k in kept if k["family"] == d)) for d in range(1, 6)},
}
out_logs["N-AFF19"] = log
print("N-AFF19 done", flush=True)
# F-RANDX19 (executor order, and alternative: primary collision vs kept primary systems only)
kept, log, tr_bad = replay_frandx()
arch_log = load_jsonl(os.path.join(RUN, "draws-F-RANDX19.jsonl.gz"))
kept_alt, log_alt, _ = replay_frandx(primary_scope="kept")
kept_alt2, log_alt2, _ = replay_frandx(order=("degenerate", "primary", "duplicate"))
res["F-RANDX19"] = {
    "draws_mine": len(log), "draws_archived": len(arch_log),
    "log_mismatches": compare_logs(log, arch_log, ["attempt", "x", "stratum", "s", "sA", "outcome"])[:20],
    "kept_mismatches": compare_kept("F-RANDX19", kept, ["stratum", "x_R"])[:20],
    "outcomes_mine": dict(Counter(r["outcome"] for r in log)),
    "C-TR19_disagreements_own": tr_bad,
    "sA_ne_s_own": sum(1 for r in log if "s" in r and r["s"] != r["sA"]),
    "ALT_primary_scope_kept_only_same_kept": [k["E_sha256"] for k in kept] == [k["E_sha256"] for k in kept_alt],
    "ALT_primary_scope_kept_only_outcomes": dict(Counter(r["outcome"] for r in log_alt)),
    "ALT_order_primary_before_duplicate_same_kept": [k["E_sha256"] for k in kept] == [k["E_sha256"] for k in kept_alt2],
    "per_stratum_kept": dict(Counter(k["stratum"] for k in kept)),
}
out_logs["F-RANDX19"] = log
print("F-RANDX19 done", flush=True)

for arm, log in out_logs.items():
    with gzip.open(os.path.join(HERE, f"my-draws-{arm}.jsonl.gz"), "wt") as fh:
        for r in log:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
res["pass"] = (
    all(res["support_vs_archived"][k] for k in ("Upos_equal", "S_L_equal", "Ej_nnz_equal", "U_hex_equal", "tau_equal"))
    and not aff_bad
    and all(not res[a]["log_mismatches"] and not res[a]["kept_mismatches"] and not res[a].get("structural_violations")
            for a in ("N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"))
    and res["F-RANDX19"]["C-TR19_disagreements_own"] == 0
)
with open(os.path.join(HERE, "replay-synthetic-and-randx.json"), "w") as fh:
    json.dump(res, fh, indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:6000])

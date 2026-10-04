#!/usr/bin/env python3
"""TASK-20260923-7a2cd4 -- blind re-derivation driver (joint J6 of
REVIEW-CERTBIN-20260923-c51f07). Written from
experiments/EXP-CERTBIN-4e92d7/specification.yaml alone.

ONE INVOCATION WITHOUT --dev = ONE FULL PASS over the 105 inputs (BR-6).
It writes <out>/<name> (default rederivation.json) and then <out>/<seal>
(sha256 + UTC time), refusing to overwrite either.

--dev replaces the blind inputs by synthetic instances from this task's own dev
seed, writes NOTHING, and prints a summary: it is not a pass over the inputs.
"""
import argparse
import datetime
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gf2n as F           # noqa: E402
import curve as Cv         # noqa: E402
import oracles as O        # noqa: E402
import stats as St         # noqa: E402
import system as S         # noqa: E402
import selftests as ST     # noqa: E402
from ambiguities import AMBIGUITIES  # noqa: E402

TASK = "TASK-20260923-7a2cd4"
INPUT_PATH = "coordination/review/certbin-20260923-c51f07/blind/blind-inputs.json"
SPEC_PATH = "experiments/EXP-CERTBIN-4e92d7/specification.yaml"
WRITE_SCOPE = "coordination/review/certbin-20260923-c51f07/reviews/TASK-20260923-7a2cd4/"
DEV_SEED = 0xDE7A2C
N_DIRECT_REPLAY_TARGETS = 20
GRANS = ("T_rank", "T_set", "T_strict", "T_ops")

# Q7 readings of the spec's `curve` + `seeds` blocks, DECLARED BEFORE ANY DRAW.
Q7_READINGS = {
    "R1_primary": "per draw: A = rng.integers(0, 2**17); B = rng.integers(0, 2**17) (two scalar calls, "
                  "default int64); a draw with B == 0 is rejected and counted; accept the first (A, B) "
                  "with #E = h*q, h in {2, 4}, q prime",
    "R2": "per draw: A = rng.integers(0, 2**17); B = rng.integers(1, 2**17) (B != 0 by construction); "
          "same acceptance rule",
    "R3": "per draw: (A, B) = rng.integers(0, 2**17, size=2); B == 0 rejected and counted; same acceptance rule",
}
S_CURVE = 20260923101                      # spec seeds.S_curve (used ONLY for optional Q7)
Q7_MAX_DRAWS = 20000


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def sha256b(b):
    return hashlib.sha256(b).hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def log(msg):
    print(f"[{utcnow()}] {msg}", flush=True)


# ------------------------------------------------------------------ Q7 ------
def q7_regenerate(reading, seed=S_CURVE):
    rng = np.random.Generator(np.random.PCG64(seed))
    rej_B0 = rej_order = 0
    for draw in range(1, Q7_MAX_DRAWS + 1):
        if reading == "R1_primary":
            A = int(rng.integers(0, 1 << 17))
            B = int(rng.integers(0, 1 << 17))
        elif reading == "R2":
            A = int(rng.integers(0, 1 << 17))
            B = int(rng.integers(1, 1 << 17))
        else:
            A, B = (int(v) for v in rng.integers(0, 1 << 17, size=2))
        if B == 0:
            rej_B0 += 1
            continue
        order = Cv.Curve(A, B).order()
        split = Cv.cofactor_split(order)
        if split is None:
            rej_order += 1
            continue
        return {"A": A, "B": B, "order": order, "h": split[0], "q": split[1], "draws": draw,
                "rejected_B_zero": rej_B0, "rejected_order": rej_order}
    return {"A": None, "B": None, "draws": Q7_MAX_DRAWS, "rejected_B_zero": rej_B0,
            "rejected_order": rej_order, "note": "no acceptance within cap"}


# ------------------------------------------------------------ instances -----
def process_instance(shape, B, xR, keep_ops):
    tm = {}
    t = time.time()
    coef = S.descend(B, xR)
    tm["descend"] = time.time() - t
    t = time.time()
    sA, _ = O.s_route_A(B, xR)
    tm["route_A"] = time.time() - t
    t = time.time()
    vB = O.values_route_B(coef)
    sB = int(np.count_nonzero(vB == 0))
    tm["route_B"] = time.time() - t
    t = time.time()
    vC = O.values_route_C(B, xR)
    sC = int(np.count_nonzero(vC == 0))
    values_equal = bool(np.array_equal(vB, vC))
    tm["route_C"] = time.time() - t
    degenerate = xR < 512
    arm = "degenerate" if degenerate else ("sat" if sB >= 1 else "unsat")
    t = time.time()
    M = S.macaulay(shape, S.equations(coef))
    tm["macaulay"] = time.time() - t
    t = time.time()
    cp = S.column_pass(M, shape.C, keep_ops=keep_ops)
    tm["column_pass"] = time.time() - t
    t = time.time()
    leads, Z = S.row_pass(M)
    tm["row_pass"] = time.time() - t
    T_rank, T_set, T_strict = S.traces(cp, Z)
    rank = T_rank
    piv_rows = {p for p, _ in cp["steps"]}
    rec = {
        "x_R": xR,
        "degenerate": degenerate,
        "s_route_A_rootfinding": sA,
        "s_route_B_exhaustive_descended": sB,
        "s_route_C_direct_field_enumeration": sC,
        "routes_agree": sA == sB == sC,
        "descended_values_equal_direct_S3_on_all_2^18": values_equal,
        "arm": arm,
        "D4": {
            "rank": rank,
            "Z_size": len(Z),
            "one_in_R": (shape.C - 1) in set(T_set[0]),
            "check_pivotcols_equal_rowpass_leads": T_set[0] == leads,
            "check_Z_size_equals_R_minus_rank": len(Z) == shape.R - rank,
            "check_Z_equals_complement_of_pivot_rows": Z == [i for i in range(shape.R) if i not in piv_rows],
            "residual_nonzero_unused_rows": cp["residual_nonzero_unused_rows"],
            "zero_rows_in_M4": int(np.count_nonzero(~M.any(axis=1))),
            "sum_X": cp["sumX"],
            "sha256": {
                "T_rank": S.sha(T_rank),
                "T_set": S.sha(T_set),
                "T_strict": S.sha(T_strict),
                "T_ops": cp["T_ops_sha256"],
            },
        },
        "timing_s": {k: round(v, 4) for k, v in tm.items()},
    }
    mem = {"coef": coef, "M": M, "T_set": T_set, "T_strict": T_strict, "ops": cp["ops"], "Z": Z}
    return rec, mem


def affine_parts(B):
    E0 = S.descend(B, 0)
    Ej = [S.coef_xor(S.descend(B, 1 << j), E0) for j in range(17)]
    return E0, Ej


def affine_check(coef, E0, Ej, xR):
    acc = dict(E0)
    for j in range(17):
        if (xR >> j) & 1:
            acc = S.coef_xor(acc, Ej[j])
    return acc == coef


# ------------------------------------------------------------------ main ----
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--input-commit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="rederivation.json")
    ap.add_argument("--seal", default="seal.txt")
    ap.add_argument("--pass-number", type=int, default=1)
    ap.add_argument("--dev", action="store_true")
    a = ap.parse_args()
    t_start = time.time()
    started = utcnow()

    out_json = os.path.join(a.out, a.name)
    out_seal = os.path.join(a.out, a.seal)
    if not a.dev and (os.path.exists(out_json) or os.path.exists(out_seal)):
        sys.exit(f"refusing to overwrite {out_json} / {out_seal}")

    # ---------------------------------------------------------- inputs ---
    spec_bytes = open(os.path.join(a.repo, SPEC_PATH), "rb").read()
    provenance = {
        "specification": {
            "path": SPEC_PATH,
            "sha256_working_tree": sha256b(spec_bytes),
            "git_blob_at_HEAD": git(a.repo, "rev-parse", f"HEAD:{SPEC_PATH}").decode().strip(),
            "git_blob_at_input_commit": git(a.repo, "rev-parse", f"{a.input_commit}:{SPEC_PATH}").decode().strip(),
        },
        "worktree_HEAD": git(a.repo, "rev-parse", "HEAD").decode().strip(),
    }
    porcelain = git(a.repo, "status", "--porcelain", "--untracked-files=all").decode().splitlines()
    provenance["dirty_paths_outside_write_scope"] = [
        l for l in porcelain if not l[3:].strip('"').startswith(WRITE_SCOPE)]
    if a.dev:
        rng = np.random.Generator(np.random.PCG64(DEV_SEED))
        A_, B_ = 12345, 67891
        inputs = {"curve": {"A": A_, "B": B_},
                  "references": [{"label": f"DEV-{i}", "x_R": int(rng.integers(512, 1 << 17))} for i in range(5)],
                  "targets": [{"position": i, "x_R": int(v)} for i, v in
                              enumerate([int(rng.integers(512, 1 << 17)) for _ in range(6)] + [0, 77], start=1)],
                  "D": [4]}
        provenance["input"] = {"dev": True}
    else:
        raw = git(a.repo, "show", f"{a.input_commit}:{INPUT_PATH}")
        inputs = json.loads(raw)
        provenance["input"] = {
            "path": INPUT_PATH,
            "read_via": f"git show {a.input_commit}:{INPUT_PATH}",
            "commit": a.input_commit,
            "git_blob": git(a.repo, "rev-parse", f"{a.input_commit}:{INPUT_PATH}").decode().strip(),
            "sha256": sha256b(raw),
            "bytes": len(raw),
            "input_commit_is_ancestor_of_worktree_HEAD": subprocess.run(
                ["git", "-C", a.repo, "merge-base", "--is-ancestor", a.input_commit, "HEAD"]).returncode == 0,
        }
        fld = inputs["field"]
        assert fld["n"] == 17 and fld["modulus"].replace(" ", "") == "t^17+t^3+1", fld
        assert inputs["m"] == 2 and inputs["l"] == 9 and 4 in inputs["D"], inputs
    A, B = int(inputs["curve"]["A"]), int(inputs["curve"]["B"])
    log(f"inputs loaded: {len(inputs['references'])} references, {len(inputs['targets'])} targets")

    env = {
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "byteorder": sys.byteorder,
        "cpu_count": os.cpu_count(),
        "code_sha256": {fn: sha256b(open(os.path.join(HERE, fn), "rb").read())
                        for fn in sorted(os.listdir(HERE)) if fn.endswith(".py")},
    }
    try:
        import mpmath
        env["mpmath"] = mpmath.__version__
    except Exception:  # pragma: no cover
        env["mpmath"] = None

    # ------------------------------------------------------- self-tests ---
    t = time.time()
    selftests, order, split = ST.run_all(A, B)
    t_self = time.time() - t
    all_pass = all(r["passed"] for r in selftests)
    log(f"self-tests: {'ALL PASS' if all_pass else 'FAILURE'} ({t_self:.1f}s)")

    result = {
        "schema": "certbin.rederivation.v1",
        "task_id": TASK,
        "review_id": "REVIEW-CERTBIN-20260923-c51f07",
        "joint": "J6",
        "pass_number": a.pass_number,
        "command": "python3 -B " + " ".join(sys.argv),
        "started_utc": started,
        "provenance": provenance,
        "environment": env,
        "ambiguities": AMBIGUITIES,
        "conventions": {
            "indices": "0-based; row index = idx(mu)*17 + k; column index = position in descending degrevlex, constant last",
            "trace_encoding": "json.dumps(obj, separators=(',', ':')), sha256 of UTF-8 bytes; T_rank = int; "
                              "T_set = [[sorted pivot cols],[sorted Z_D]]; T_strict = [[p,c],...]; T_ops = [[p,c,[sorted X]],...]",
            "assignment": "u in [0, 2^18): v_i = bit i of u; x_1 = u & 511, x_2 = u >> 9; field element bit j = coefficient of t^j",
            "degenerate": "x_R < 512 (x_R in V, including 0)",
            "arm": "degenerate if x_R in V; else sat iff s >= 1; else unsat",
        },
        "self_tests": {"seed": ST.SELFTEST_SEED, "all_passed": all_pass, "seconds": round(t_self, 2),
                       "results": selftests},
    }

    if not all_pass:
        result["stopped"] = "self-test failure (BR-2): no quantity computed"
        return finish(a, result, out_json, out_seal, t_start)

    shape = S.Shape(4)
    result["shape_D4"] = {"R_4": shape.R, "C_4": shape.C, "words_per_row": shape.W}
    E0, Ej = affine_parts(B)

    # ------------------------------------------------- per-instance pass ---
    refs = [(r["label"], int(r["x_R"])) for r in inputs["references"]]
    tgts = [(str(t_["position"]), int(t_["x_R"])) for t_ in inputs["targets"]]
    recs, mems = {}, {}
    for kind, items in (("ref", refs), ("tgt", tgts)):
        for key, xR in items:
            rec, mem = process_instance(shape, B, xR, keep_ops=(kind == "ref"))
            rec["affine_decomposition_exact"] = affine_check(mem["coef"], E0, Ej, xR)
            recs[(kind, key)] = rec
            if kind == "tgt":
                mem = {"T_set": mem["T_set"], "T_strict": mem["T_strict"], "Z": mem["Z"], "M": mem["M"]}
            mems[(kind, key)] = mem
            log(f"{kind} {key}: x_R={xR} arm={rec['arm']} s(A,B,C)=({rec['s_route_A_rootfinding']},"
                f"{rec['s_route_B_exhaustive_descended']},{rec['s_route_C_direct_field_enumeration']}) "
                f"rank={rec['D4']['rank']} |Z|={rec['D4']['Z_size']}")

    ref_keys = [k for k, _ in refs]
    tgt_keys = [k for k, _ in tgts]
    R_, C_ = shape.R, shape.C

    # ------------------------------------------------------------ Q1, Q2 ---
    def q1(rec):
        return {"x_R": rec["x_R"], "degenerate": rec["degenerate"],
                "s_route_A_rootfinding": rec["s_route_A_rootfinding"],
                "s_route_B_exhaustive_descended": rec["s_route_B_exhaustive_descended"],
                "s_route_C_direct_field_enumeration": rec["s_route_C_direct_field_enumeration"],
                "routes_agree": rec["routes_agree"], "arm": rec["arm"]}

    def q2(rec):
        return {"rank_4": rec["D4"]["rank"], "Z_4_size": rec["D4"]["Z_size"], "one_in_R4": rec["D4"]["one_in_R"]}

    result["Q1"] = {"references": {k: q1(recs[("ref", k)]) for k in ref_keys},
                    "targets": {k: q1(recs[("tgt", k)]) for k in tgt_keys}}
    disagreements = [f"{kind}:{k}" for (kind, k), r in recs.items() if not r["routes_agree"]]
    result["Q1"]["route_disagreements"] = disagreements
    result["Q2"] = {"references": {k: q2(recs[("ref", k)]) for k in ref_keys},
                    "targets": {k: q2(recs[("tgt", k)]) for k in tgt_keys}}

    # ---------------------------------------------------------------- Q3 ---
    def eq_content(g, kt, kr):
        mt, mr = mems[kt], mems[kr]
        if g == "T_rank":
            return recs[kt]["D4"]["rank"] == recs[kr]["D4"]["rank"]
        if g == "T_set":
            return mt["T_set"] == mr["T_set"]
        if g == "T_strict":
            return mt["T_strict"] == mr["T_strict"]
        raise ValueError(g)

    ops_confirmations = []

    def eq_ops(kt, kr):
        same_hash = recs[kt]["D4"]["sha256"]["T_ops"] == recs[kr]["D4"]["sha256"]["T_ops"]
        if not same_hash:
            return False
        # confirm content on equal hash: re-run the target's solver keeping ops
        ops_t = mems[kt].get("ops")
        if ops_t is None:
            ops_t = S.column_pass(mems[kt]["M"], shape.C, keep_ops=True)["ops"]
        same = [list(o) for o in ops_t] == [list(o) for o in mems[kr]["ops"]]
        ops_confirmations.append({"pair": [kt[1], kr[1]], "content_equal": same})
        return same

    nesting_violations = []
    match = {}
    for kt_key in tgt_keys + ref_keys:
        kind = "tgt" if kt_key in tgt_keys and ("tgt", kt_key) in recs else "ref"
        kt = (kind, kt_key)
        row = {}
        for kr_key in ref_keys:
            kr = ("ref", kr_key)
            flags = {g: eq_content(g, kt, kr) for g in ("T_rank", "T_set", "T_strict")}
            flags["T_ops"] = eq_ops(kt, kr) if kt != kr else True
            # hash-level agreement with content (for the three content-compared granularities)
            for g in ("T_rank", "T_set", "T_strict"):
                if flags[g] != (recs[kt]["D4"]["sha256"][g] == recs[kr]["D4"]["sha256"][g]):
                    nesting_violations.append({"pair": [kt_key, kr_key], "problem": f"hash/content disagree at {g}"})
            if (flags["T_ops"] and not flags["T_strict"]) or (flags["T_strict"] and not flags["T_set"]) or \
               (flags["T_set"] and not flags["T_rank"]):
                nesting_violations.append({"pair": [kt_key, kr_key], "flags": flags})
            row[kr_key] = flags
        match[f"{kind}:{kt_key}"] = row

    result["Q3"] = {
        "hashes": {"references": {k: recs[("ref", k)]["D4"]["sha256"] for k in ref_keys},
                   "targets": {k: recs[("tgt", k)]["D4"]["sha256"] for k in tgt_keys}},
        "match_flags_target_vs_reference": {k: match[f"tgt:{k}"] for k in tgt_keys},
        "match_flags_reference_vs_reference": {k: match[f"ref:{k}"] for k in ref_keys},
        "T_ops_equal_hash_content_confirmations": ops_confirmations,
        "nesting_or_hash_content_violations": nesting_violations,
        "reference_content": {k: {"T_strict": mems[("ref", k)]["T_strict"], "T_set": mems[("ref", k)]["T_set"]}
                              for k in ref_keys},
    }

    # ---------------------------------------------------------------- Q4 ---
    q4 = {}
    for k in ref_keys:
        rec = recs[("ref", k)]
        rank = rec["D4"]["rank"]
        npiv = len(mems[("ref", k)]["T_set"][0])
        zs = rec["D4"]["Z_size"]
        ops_strict = rec["D4"]["sum_X"]
        ops_full = C_ * R_
        ops_set = npiv * (R_ - zs)
        sav_strict = Fraction(ops_full, ops_strict) if ops_strict else None
        sav_set = Fraction(ops_full, ops_set) if ops_set else None
        ident = Fraction(C_ * R_, rank * rank) if rank else None
        q4[k] = {
            "R_4": R_, "C_4": C_,
            "ops_masked_full": ops_full,
            "ops_strict": ops_strict,
            "saving_strict": float(sav_strict) if sav_strict is not None else None,
            "saving_strict_exact": [sav_strict.numerator, sav_strict.denominator] if sav_strict is not None else None,
            "pivot_cols": npiv,
            "R_minus_Z": R_ - zs,
            "ops_set": ops_set,
            "saving_set": float(sav_set) if sav_set is not None else None,
            "saving_set_exact": [sav_set.numerator, sav_set.denominator] if sav_set is not None else None,
            "identity_saving_set_eq_C4R4_over_rank4_sq": (sav_set == ident) if sav_set is not None else None,
            "unit": "one full-row XOR (C_4 bits)",
        }
    result["Q4"] = q4

    # ---------------------------------------------------------------- Q5 ---
    unsat_refs = [k for k in ref_keys if recs[("ref", k)]["arm"] == "unsat"]
    pool = [k for k in tgt_keys if recs[("tgt", k)]["arm"] == "unsat"]
    n = len(pool)
    q5 = {"unsat_references": unsat_refs, "n_nondegenerate_unsat_targets": n,
          "nondegenerate_unsat_target_positions": pool, "per_reference": {}}
    for kr in unsat_refs:
        per = {}
        for g in ("T_rank", "T_set", "T_strict", "T_ops"):
            cnt = sum(1 for kt in pool if match[f"tgt:{kt}"][kr][g])
            per[g] = {"count": cnt, "n": n, "retention": (cnt / n) if n else None,
                      "clopper_pearson_95": St.clopper_pearson(cnt, n) if n else None}
        per["note"] = "T_ops is reported in addition to the three granularities Q5 asks for"
        q5["per_reference"][kr] = per
    result["Q5"] = q5

    # ---------------------------------------------------------------- Q6 ---
    t = time.time()
    blocks = [S.macaulay(shape, S.equations(E0))] + [S.macaulay(shape, S.equations(Ej[j])) for j in range(17)]
    # linearity of M_D in E: M(E(r)) == M(E0) ^ sum r_j M(Ej), checked on every instance
    lin_fail = []
    for (kind, key), mem in mems.items():
        xR = recs[(kind, key)]["x_R"]
        acc = blocks[0].copy()
        for j in range(17):
            if (xR >> j) & 1:
                acc ^= blocks[1 + j]
        if not np.array_equal(acc, mem["M"]):
            lin_fail.append(f"{kind}:{key}")
    q6 = {"macaulay_linearity_failures": lin_fail, "per_reference": {}}
    direct_targets = [k for k in tgt_keys if recs[("tgt", k)]["arm"] != "degenerate"][:N_DIRECT_REPLAY_TARGETS]
    for kr in unsat_refs:
        ops = mems[("ref", kr)]["ops"]
        e = S.replay(blocks, ops)
        a0 = e[:, 0].astype(int).tolist()
        avec = [int(sum(int(e[k, 1 + j]) << j for j in range(17))) for k in range(e.shape[0])]
        r_ref = recs[("ref", kr)]["x_R"]

        def ek(k, r):
            return a0[k] ^ (bin(avec[k] & r).count("1") & 1)

        self_affine = all(ek(k, r_ref) == 1 for k in range(len(ops)))
        self_direct = bool(np.all(S.replay([mems[("ref", kr)]["M"]], ops)[:, 0] == 1))
        direct_mismatch = {}
        for kt in direct_targets:
            ed = S.replay([mems[("tgt", kt)]["M"]], ops)[:, 0].astype(int).tolist()
            r_t = recs[("tgt", kt)]["x_R"]
            bad = [k for k in range(len(ops)) if ed[k] != ek(k, r_t)]
            if bad:
                direct_mismatch[kt] = bad[:10]
        nz = [k for k in range(len(ops)) if avec[k] != 0]
        K_exact = len(nz)
        K_rank = S.gf2_rank_ints([avec[k] for k in nz])
        first = []
        basis_so_far = []
        for k in nz:
            before = S.gf2_rank_ints(basis_so_far)
            after = S.gf2_rank_ints(basis_so_far + [avec[k]])
            if len(first) < 64:
                first.append({"k": k, "a_k0": a0[k], "a_k": avec[k], "increases_rank": after > before})
            basis_so_far.append(avec[k])
            if len(first) >= 64:
                break
        zero_linear = [k for k in range(len(ops)) if avec[k] == 0]
        q6["per_reference"][kr] = {
            "steps": len(ops),
            "K_exact": K_exact,
            "K_rank": K_rank,
            "first_64_nonzero": first,
            "steps_with_a_k_zero": len(zero_linear),
            "a_k0_values_where_a_k_zero": sorted(set(a0[k] for k in zero_linear)),
            "check_affine_formula_at_reference_r_gives_all_ones": self_affine,
            "check_direct_self_replay_all_ones": self_direct,
            "check_direct_replay_equals_affine_formula": {
                "targets": direct_targets, "mismatches": direct_mismatch, "passed": not direct_mismatch},
            "full_affine_forms": {"a_k0": a0, "a_k": avec,
                                  "encoding": "a_k bit j = coefficient of r_j (E^j block); k = 0-based op-log step"},
        }
    q6["seconds"] = round(time.time() - t, 2)
    result["Q6"] = q6

    # ---------------------------------------------------------------- Q7 ---
    t = time.time()
    q7 = {"readings": Q7_READINGS, "numpy": np.__version__, "S_curve": S_CURVE,
          "extracted": {"A": A, "B": B, "order": order,
                        "cofactor_split_h_q": list(split) if split else None,
                        "meets_acceptance_rule": split is not None},
          "results": {}}
    for rd in Q7_READINGS:
        r = q7_regenerate(rd, seed=(DEV_SEED if a.dev else S_CURVE))
        r["equals_extracted"] = (r["A"] == A and r["B"] == B)
        q7["results"][rd] = r
    q7["seconds"] = round(time.time() - t, 2)
    result["Q7"] = q7

    # ------------------------------------------------------ bookkeeping ---
    result["instance_records"] = {"references": {k: recs[("ref", k)] for k in ref_keys},
                                  "targets": {k: recs[("tgt", k)] for k in tgt_keys}}
    checks = {
        "all_routes_agree": not disagreements,
        "all_descended_values_equal_direct_S3": all(r["descended_values_equal_direct_S3_on_all_2^18"] for r in recs.values()),
        "all_affine_decomposition_exact": all(r["affine_decomposition_exact"] for r in recs.values()),
        "all_pivotcols_equal_rowpass_leads": all(r["D4"]["check_pivotcols_equal_rowpass_leads"] for r in recs.values()),
        "all_Z_size_equals_R_minus_rank": all(r["D4"]["check_Z_size_equals_R_minus_rank"] for r in recs.values()),
        "all_Z_equals_complement_of_pivot_rows": all(r["D4"]["check_Z_equals_complement_of_pivot_rows"] for r in recs.values()),
        "all_residual_unused_rows_zero": all(r["D4"]["residual_nonzero_unused_rows"] == 0 for r in recs.values()),
        "no_nesting_or_hash_content_violation": not nesting_violations,
        "macaulay_linear_in_E_on_every_instance": not lin_fail,
        "q6_checks_all_pass": all(v["check_affine_formula_at_reference_r_gives_all_ones"]
                                  and v["check_direct_self_replay_all_ones"]
                                  and v["check_direct_replay_equals_affine_formula"]["passed"]
                                  for v in q6["per_reference"].values()),
    }
    result["internal_checks"] = checks
    result["counts"] = {
        "references": len(ref_keys), "targets": len(tgt_keys),
        "arms_targets": {arm: sum(1 for k in tgt_keys if recs[("tgt", k)]["arm"] == arm)
                         for arm in ("unsat", "sat", "degenerate")},
        "arms_references": {k: recs[("ref", k)]["arm"] for k in ref_keys},
    }
    result["gaps"] = []
    if not unsat_refs:
        result["gaps"].append("Q5/Q6: no reference classified unsatisfiable")
    return finish(a, result, out_json, out_seal, t_start)


def finish(a, result, out_json, out_seal, t_start):
    result["timing"] = {"wall_seconds": round(time.time() - t_start, 2),
                        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}
    result["finished_utc"] = utcnow()
    blob = json.dumps(result, indent=1).encode("utf-8")
    if a.dev:
        slim = {k: result[k] for k in ("self_tests", "internal_checks", "counts", "timing") if k in result}
        slim["self_tests"] = {"all_passed": result["self_tests"]["all_passed"]}
        if "Q4" in result:
            slim["Q4"] = result["Q4"]
            slim["Q5"] = result["Q5"]
            slim["Q6"] = {k: {kk: (vv if kk != "full_affine_forms" else "...") for kk, vv in v.items()
                              if kk != "first_64_nonzero"} | {"first_5": v["first_64_nonzero"][:5]}
                          for k, v in result["Q6"]["per_reference"].items()}
            slim["Q3_ref_vs_ref"] = result["Q3"]["match_flags_reference_vs_reference"]
            slim["Q7_dev_seed_mechanics"] = result["Q7"]
        print(json.dumps(slim, indent=1))
        print("dev: bytes that would be written:", len(blob))
        return 0
    with open(out_json, "xb") as fh:           # 'x' = refuse to overwrite
        fh.write(blob)
    digest = sha256b(open(out_json, "rb").read())
    with open(out_seal, "x") as fh:
        fh.write(f"sha256 {digest}  {os.path.basename(out_json)}\n")
        fh.write(f"sealed_utc {utcnow()}\n")
        fh.write(f"task {TASK} pass {a.pass_number}\n")
    log(f"wrote {out_json} sha256={digest}; sealed in {out_seal}")
    return 0 if result["self_tests"]["all_passed"] else 2


if __name__ == "__main__":
    sys.exit(main())

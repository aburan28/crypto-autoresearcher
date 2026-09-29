#!/usr/bin/env python3
"""Arms A (n=6, seed 760706), B (n=8, seed 760708), C (n=10, seed 760710),
and the arm-B determinism re-run (IV-7), for EXP-ECRANK-76a70d.

Frozen protocol fields (specification.yaml): seeded b-tuples (b_1 = 0,
b_2 = 1, b_3..b_n distinct integers in [-20,20]); class patterns from ONE
k=3 coset of the committed support {-1,2,3,5,7,11,13} (>= 3 distinct cosets
per arm, separate seeded b-streams, C6); fibration sampling: fix 5 of the n
r-coordinates in a seeded sub-box of height H, solve the remaining n-5
diagonal quadratic system exactly (unique y-solution; Bezout candidates are
the 2^(n-5) sign choices; rationality checked exactly via rational_square);
exact C4 degeneracy filter; nested boxes H in {10^2, 10^3, 10^4}; stopping
rules 1.0e8 counted exact ops OR 7200 s wall, whichever first, exhaustion
reported as exhaustion (inert); checkpointing per contract cadence.

Implementation choices (recorded, never a protocol change):
  IC-13  8 draws per b-tuple (the declared per-b budget: "<= 8 fibration
         draws"); H schedule per draw index: [10^2 x3, 10^3 x3, 10^4 x2]
         (near-equal exposure per decade for the log-log slope fit; counts
         reported per level and cumulatively).
  IC-15  stream derivation: cosets drawn from random.Random(arm_seed) over
         the canonically sorted eligible-coset list; stream j uses
         random.Random(arm_seed*100 + j); b-tuples, class choices, dpat
         shuffles, and fibration sub-box draws all come from the stream rng
         in a fixed call order (determinism re-run compares the resulting
         instance list bit-for-bit).
  IC-16  class pattern: n/2 distinct member values of the arm's coset,
         redrawn (bounded) until sign-mixed (HEUR-1 scope: mixed signs);
         pattern [d,d,...] shuffled onto the b-indices.
  IC-17  per-b ops are monitored against the declared 10^4/b derivation;
         an overrun is recorded as an event, the binding stop is the global
         1.0e8 cap (stopping_rules).
  IC-18  minimal-model dedup (C6) via the committed canonical short-form
         key of the base-class model; isomorphic-but-distinct-key pairs are
         flagged, not merged.

Observations only; interprets nothing; changes no status.
"""

import argparse
import json
import os
import random
import sys
import time
import traceback
from fractions import Fraction as Fr

import ecrank_engine as E
import certify76 as C
import run_common as RC

ARMS = {
    "A": {"n": 6, "seed": 760706, "n_b": 1000},
    "B": {"n": 8, "seed": 760708, "n_b": 10000},
    "C": {"n": 10, "seed": 760710, "n_b": 10000},
}
H_SCHEDULE = [100, 100, 100, 1000, 1000, 1000, 10000, 10000]
S_IDX = [0, 1, 2, 3, 4]
OPS_CAP = int(1.0e8)
WALL_CAP = 7200.0
PER_B_DECLARED_OPS = 10 ** 4
CKPT_B_INTERVAL = 500
B_INTS = sorted(set(range(-20, 21)) - {0, 1})


def canon_key_of_instance(inst, ec):
    """C6 dedup key: committed stdlib short-form conversion (verbatim
    coset_structure.short_model_from_ainvs) of the base-class model, then
    the engine's exact canonical representative under (u^4 A, u^6 B).
    Disclosed adaptation: the committed pipeline's PARI ellminimalmodel is
    banned by this contract's stdlib-only solver constraint (IC-8)."""
    s = [Fr(c) for c in inst["s"]]
    d1 = sorted({int(d) for d in inst["d_pattern"]})[0]
    qd = [c / Fr(d1) for c in s]
    deg = len(s) - 1
    if deg == 3:
        ainv, _imgs = E.cubic_to_weierstrass(qd, [])
    else:
        b_first = Fr(inst["b"][0])
        r_first = Fr(inst["r"][0])
        route = C.quartic_route(qd, b_first, r_first)
        ainv = route["ainv"]
    AB = E.short_model_from_ainvs(ainv)
    return E.canonical_short_key(AB), AB


def run_arm(arm, run_id, replay_of=None):
    cfg = ARMS[arm]
    n, seed, n_b = cfg["n"], cfg["seed"], cfg["n_b"]
    params = {
        "run_kind": "arm_%s%s" % (arm, "_determinism_rerun" if replay_of else ""),
        "arm": arm, "n": n, "arm_seed": seed, "n_b_declared": n_b,
        "H_schedule_per_draw": H_SCHEDULE,
        "draws_per_b": len(H_SCHEDULE),
        "S_fixed_indices": S_IDX, "T_solved_indices": list(range(5, n)),
        "classes_per_instance": n // 2,
        "per_b_declared_ops": PER_B_DECLARED_OPS,
        "replay_of": replay_of,
        "implementation_choices": ["IC-13", "IC-15", "IC-16", "IC-17", "IC-18"],
    }
    run_dir, header, t0 = RC.open_run(run_id, sys.argv, params)
    E.start_counting()
    ec, digest = E.load_exact_certify(RC.REPO_ROOT)
    assert digest == E.EXACT_CERTIFY_SHA

    cosets = E.eligible_cosets()
    rng_arm = random.Random(seed)
    coset_ids = rng_arm.sample(range(len(cosets)), 3)
    arm_cosets = [cosets[i] for i in coset_ids]

    per_stream = []
    found = []          # instance records (certified or not)
    level_counts = {100: 0, 1000: 0, 10000: 0}       # per-level found
    cumulative = {100: 0, 1000: 0, 10000: 0}         # cumulative found
    exhaustion = None
    events = []
    blind_inputs = []
    ck = E.Checkpointer(os.path.join(run_dir, "checkpoints"))
    cert_dir = os.path.join(RC.REPO_ROOT, RC.EXP_DIR, "certificates", run_id)

    base_b = n_b // 3
    extra = n_b % 3
    stream_sizes = [base_b + (1 if j < extra else 0) for j in range(3)]

    def state():
        return {"ops": E.ops_count(), "wall": round(time.monotonic() - t0, 2),
                "streams_completed": [st["b_done"] for st in per_stream],
                "found": len(found), "level_counts": level_counts,
                "exhaustion": exhaustion}

    try:
        for j, coset in enumerate(arm_cosets):
            rng_j = random.Random(seed * 100 + j)
            values = [E.class_value(m) for m in coset["members"]]
            st = {"stream": j, "coset_index": coset_ids[j],
                  "coset_m0": coset["m0"], "coset_V": list(coset["V"]),
                  "coset_values": values, "b_total": stream_sizes[j],
                  "b_done": 0, "draws": 0, "solves_ok": 0, "square_ok": 0,
                  "build_ok": 0, "reject_reasons": {}, "solve_reasons": {},
                  "class_attempts_hist": {}, "found": 0,
                  "local_solvability": None}
            per_stream.append(st)
            blind_taken = 0
            for bi in range(stream_sizes[j]):
                ops_b0 = E.ops_count()
                b_rest = rng_j.sample(B_INTS, n - 2)
                b = [Fr(0), Fr(1)] + [Fr(x) for x in b_rest]
                k = n // 2
                attempts = 0
                chosen = None
                while attempts < 1000:
                    attempts += 1
                    cand = rng_j.sample(values, k)
                    if any(v < 0 for v in cand) and any(v > 0 for v in cand):
                        chosen = cand
                        break
                if chosen is None:
                    st["reject_reasons"]["class_mix_failure"] = \
                        st["reject_reasons"].get("class_mix_failure", 0) + 1
                    st["b_done"] += 1
                    continue
                st["class_attempts_hist"][attempts] = \
                    st["class_attempts_hist"].get(attempts, 0) + 1
                dpat = []
                for v in chosen:
                    dpat += [v, v]
                rng_j.shuffle(dpat)
                if blind_taken < 3:
                    blind_inputs.append({
                        "stream": j, "b_index": bi,
                        "b": [str(x) for x in b], "d_pattern": dpat,
                        "quantity_statements": [
                            "left kernel of W(b): all c in Q^n with "
                            "sum_i c_i b_i^t = 0 for t = 0..4 (reduced basis)",
                            "delta interpolant: delta(b_i) = d_i, degree <= n-1",
                        ]})
                    blind_taken += 1
                gamma = E.vandermonde_kernel(b)
                gamma_d = [[g[i] * Fr(dpat[i]) for i in range(n)]
                           for g in gamma]
                if arm == "A":
                    ls = E.local_solvability(gamma_d[0])
                    rec = {"stream": j, "b_index": bi,
                           "real_place": ls["real_place"],
                           "obstruction": ls["obstruction"],
                           "n_primes_no_witness": sum(
                               1 for v in ls["primes"].values()
                               if v["status"] == "no_constructive_witness")}
                    st.setdefault("local_solvability_list", []).append(rec)
                for jd, H in enumerate(H_SCHEDULE):
                    st["draws"] += 1
                    rS = {i: E.draw_rational(rng_j, H) for i in S_IDX}
                    y, reason = E.solve_draw(gamma_d, S_IDX,
                                             list(range(5, n)), rS)
                    if y is None:
                        st["solve_reasons"][reason] = \
                            st["solve_reasons"].get(reason, 0) + 1
                        continue
                    st["solves_ok"] += 1
                    roots = [E.rational_square(y[t]) for t in range(5, n)]
                    if any(rt is None or rt == 0 for rt in roots):
                        continue
                    st["square_ok"] += 1
                    r = [rS[i] for i in S_IDX] + roots
                    inst, why = E.build_instance(b, dpat, r, n)
                    if inst is None:
                        st["reject_reasons"][why] = \
                            st["reject_reasons"].get(why, 0) + 1
                        continue
                    st["build_ok"] += 1
                    st["found"] += 1
                    level_counts[H] += 1
                    for HL in cumulative:
                        if H <= HL:
                            cumulative[HL] += 1
                    rec = {"stream": j, "b_index": bi, "draw_index": jd,
                           "H_level": H, "instance": RC.inst_json(inst),
                           "canonical_instance": RC.canon_instance_key(inst)}
                    if not replay_of:
                        cert = C.certify_instance(inst, coset, ec)
                        cpath = RC.write_json(os.path.join(
                            cert_dir,
                            "inst-s%d-b%05d-d%d.json" % (j, bi, jd)), cert)
                        ce_table = {}
                        for dstr, cd in cert.get("classes", {}).items():
                            d = int(dstr)
                            if d != cert.get("base_class"):
                                ce_table[dstr] = (cd["n_forced_points"]
                                                  - cd["certified_Fl_within_class"])
                        rec["certificate"] = {
                            "path": os.path.relpath(cpath, RC.REPO_ROOT),
                            "verdict": cert["verdict"],
                            "aggregate_total": cert["aggregate_total"],
                            "eig_units": cert["eig_units"],
                            "fl_units": cert["fl_units"],
                            "route": cert["route"],
                            "errors_strict": cert["errors_strict"],
                            "withholds": cert["withholds"],
                            "c_e_nontrivial_classes": ce_table,
                        }
                    found.append(rec)
                ops_b = E.ops_count() - ops_b0
                if ops_b > PER_B_DECLARED_OPS:
                    events.append({"event": "per_b_ops_over_declared",
                                   "stream": j, "b_index": bi,
                                   "ops": ops_b})
                st["b_done"] += 1
                if E.ops_count() >= OPS_CAP:
                    exhaustion = {"kind": "counted_ops_cap",
                                  "ops": E.ops_count(),
                                  "stream": j, "b_index": bi}
                    break
                if time.monotonic() - t0 >= WALL_CAP:
                    exhaustion = {"kind": "wall_cap",
                                  "wall": round(time.monotonic() - t0, 2),
                                  "stream": j, "b_index": bi}
                    break
                ck.maybe(state)
                if st["b_done"] % CKPT_B_INTERVAL == 0:
                    ck.flush(state, "b_interval_s%d_b%d" % (j, st["b_done"]))
            if exhaustion:
                break
        ck.flush(state, "final")

        # C6 dedup: distinct minimal models via committed canonical keys
        dedup = {"n_found_records": len(found), "distinct_keys": 0,
                 "key_groups": {}, "isomorphic_flags": [],
                 "adaptation_note": "committed stdlib short-model conversion "
                                    "(coset_structure.py verbatim) + exact "
                                    "canonical scaling key; PARI "
                                    "ellminimalmodel banned by the "
                                    "contract's stdlib-only solver"}
        if found:
            keys = {}
            abs_ = {}
            for rec in found:
                try:
                    key, AB = canon_key_of_instance(rec["instance"], ec)
                except Exception as exc:
                    key, AB = ("key_error:%s" % exc, None)
                keys.setdefault(key, []).append(
                    {"stream": rec["stream"], "b_index": rec["b_index"],
                     "draw_index": rec["draw_index"]})
                if AB is not None:
                    abs_[key] = AB
            dedup["distinct_keys"] = len(keys)
            dedup["key_groups"] = {str(k)[:64]: v for k, v in keys.items()}
            kl = list(abs_)
            for ii in range(len(kl)):
                for jj in range(ii + 1, len(kl)):
                    try:
                        if E.curves_isomorphic(abs_[kl[ii]], abs_[kl[jj]]):
                            dedup["isomorphic_flags"].append(
                                [str(kl[ii])[:40], str(kl[jj])[:40]])
                    except Exception:
                        pass

        raw = {
            "parameters": params,
            "arm_cosets": [{"stream": j, "coset_index": coset_ids[j],
                            "m0": c["m0"], "V": list(c["V"]),
                            "values": [E.class_value(m) for m in c["members"]]}
                           for j, c in enumerate(arm_cosets)],
            "streams": per_stream,
            "found_instances": found,
            "level_counts_per_H": level_counts,
            "cumulative_counts_per_H": cumulative,
            "dedup_C6": dedup,
            "exhaustion": exhaustion,
            "events": events,
            "blind_rederivation_inputs_C3": blind_inputs,
            "ops_counted_total": E.ops_count(),
        }
        if replay_of:
            orig = json.load(open(os.path.join(RC.REPO_ROOT, replay_of)))
            orig_list = [r["canonical_instance"]
                         for r in orig["found_instances"]]
            new_list = [r["canonical_instance"] for r in found]
            oh = __import__("hashlib").sha256(
                json.dumps(orig_list, sort_keys=True).encode()).hexdigest()
            nh = __import__("hashlib").sha256(
                json.dumps(new_list, sort_keys=True).encode()).hexdigest()
            match = (oh == nh)
            diff = {
                "orig_path": replay_of, "orig_sha256": oh, "rerun_sha256": nh,
                "bit_for_bit_match": match,
                "orig_n": len(orig_list), "rerun_n": len(new_list),
                "first_divergence": None,
                "IV7_fired": not match,
                "note": "certification intentionally not re-run on the "
                        "determinism re-run: IV-7 compares the instance list",
            }
            if not match:
                for idx in range(max(len(orig_list), len(new_list))):
                    a = orig_list[idx] if idx < len(orig_list) else None
                    bb = new_list[idx] if idx < len(new_list) else None
                    if a != bb:
                        diff["first_divergence"] = {
                            "index": idx,
                            "orig": (a or "")[:400],
                            "rerun": (bb or "")[:400]}
                        break
            raw["determinism_IV7"] = diff
            with open(os.path.join(run_dir, "determinism-diff.txt"), "w") as f:
                f.write(json.dumps(diff, indent=1, sort_keys=True))
            status = "completed"
            reason = ("determinism re-run: instance list bit-for-bit "
                      "MATCH" if match else
                      "determinism re-run: DIVERGENCE (IV-7 fired)")
        elif exhaustion:
            status = "completed_exhausted_%s" % exhaustion["kind"]
            reason = ("budget exhaustion (%s) after %d found; completed "
                      "prefix preserved; exhaustion is inert (rules 3/5)"
                      % (exhaustion["kind"], len(found)))
        else:
            status = "completed"
            reason = ("full pre-registered sample executed: %d b-tuples, "
                      "%d found instances" % (
                          sum(st["b_done"] for st in per_stream), len(found)))
        RC.finalize_run(run_dir, header, t0, status, reason, raw)
        print(json.dumps({"run_id": run_id, "status": status,
                          "reason": reason, "found": len(found),
                          "level_counts": level_counts,
                          "ops": E.ops_count()}, indent=1))
        return 0
    except Exception:
        tb = traceback.format_exc()
        raw = {"exception_traceback": tb, "ops_counted_total": E.ops_count(),
               "found_so_far": len(found), "streams": per_stream}
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "exception during run (rule 3/5: asserts nothing "
                        "about the hypothesis)", raw)
        print(tb)
        return 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=list(ARMS))
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--replay-of", default=None,
                    help="repo-relative path of the original raw-result.json")
    a = ap.parse_args()
    return run_arm(a.arm, a.run_id, a.replay_of)


if __name__ == "__main__":
    sys.exit(main())

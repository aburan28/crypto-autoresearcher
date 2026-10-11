#!/usr/bin/env python3
"""J2 (6): replay of one certificate back-trace across the iteration
boundary, TASK-20260924-c83b05.

Instance (declared): the lowest-idx U62 instance, whose archived W_4 record
has 1 first in W^(1) (an iteration-1 refutation).

The op logs are not archived (only the flat certificates are), so they are
REGENERATED with the archived engine's own elimination routine
(impl/closure.echelon) on the archived instance, level by level exactly as
Closure._w_closure builds its stacks (level 0 = M_4; level 1 = [echelon basis
of W^(0) in lead order; v_j * (rows whose low lead is new), j-major]). The
REPLAY is the validator's own code:
  (1) level 1: a boolean membership vector walked backwards over the log
      (step k: if an odd number of the target rows received pivot p_k, toggle
      p_k) -> the set T1 of ORIGINAL level-1 stack rows whose XOR is the row
      "1"; checked by XORing those rows in the validator's own polynomial
      representation (must equal exactly 1);
  (2) the iteration boundary: each row of T1 is either a level-0 basis row
      (multiplier 1) or v_j * (a level-0 row) (multiplier v_j); grouped by
      multiplier with XOR (symmetric difference) semantics;
  (3) level 0: the same backward walk, separately for each multiplier's
      target set -> original M_4 rows (mu, k); each level-0 target row is
      checked to equal the XOR of its traced M_4 rows;
  (4) the pushed multiplier: pair (m | mu, k) with XOR parity -> C_replay;
  (5) C_replay compared with the archived certificate of certificates.jsonl.gz
      (exact equality of the sorted pair lists), and sum mu * f_k evaluated
      with own arithmetic on the own-decoded system.
Output: j2-constructions/backtrace_replay_results.json
"""
import gzip
import json
import os
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402


def backward(nrows, ps, Xs, targets):
    """own replay: returns the set of ORIGINAL row indices whose XOR equals the
    XOR of the FINAL states of `targets`."""
    inT = np.zeros(nrows, dtype=bool)
    for t in targets:
        inT[t] = not inT[t]
    for k in range(len(ps) - 1, -1, -1):
        X = Xs[k]
        if X.size and (int(np.count_nonzero(inT[X])) & 1):
            p = int(ps[k])
            inT[p] = not inT[p]
    return set(int(x) for x in np.flatnonzero(inT))


def main():
    t0 = time.time()
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    it = min(inst["sets"]["U62"], key=lambda x: x["idx"])
    key = it["key"]
    arch_rec = None
    for line in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"):
        r = json.loads(line)
        if r["key"] == key and r["closure"] == "W_4":
            arch_rec = r
    arch_cert = None
    for line in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt"):
        c = json.loads(line)
        if c["key"] == key and c["closure"] == "W_4":
            arch_cert = c
    assert arch_rec["one_first_iteration"] == 1
    sys.path.insert(0, IMPL)
    from closure import Closure, echelon
    from instances import E_from_hex, eqs_of
    cl = Closure(18, 4, 17)
    eqs_eng = eqs_of(E_from_hex(it["E_hex"]))
    eqs_own = oa.eqs_from_hex(it["E_hex"])
    sp = oa.Space(18, 4)

    def own_rows(packed):
        d = cl.unpack(packed)
        return [sp.poly(int(cl.col_mask[c]) for c in np.flatnonzero(row)) for row in d]

    # ---- level 0 (regenerated log)
    M0 = cl.build_M(eqs_eng)
    M0_orig_own = own_rows(M0)
    ps0, cs0, Xs0 = echelon(M0, cl.C, keep_log=True)
    order = np.argsort(cs0, kind="stable")
    prow = ps0[order]
    leads = cs0[order]
    basis = M0[prow]
    low = cl.col_deg[leads] <= 3
    new = np.flatnonzero(low)                   # iteration 0 -> 1: every low row is new
    nb, nnew = len(prow), len(new)
    P = cl.products(basis[new])
    M1 = np.concatenate([basis, P])
    M1_orig_own = own_rows(M1)
    ps1, cs1, Xs1 = echelon(M1, cl.C, keep_log=True)
    const_col = cl.C - 1
    assert const_col in set(cs1.tolist())
    pstar = int(ps1[np.flatnonzero(cs1 == const_col)[0]])
    # ---- (1) level-1 backward replay
    T1 = backward(M1.shape[0], ps1, Xs1, [pstar])
    x = 0
    for r in T1:
        x ^= M1_orig_own[r]
    level1_xor_is_1 = (x == 1)                # own position 0 = constant monomial
    # ---- (2) boundary: group by multiplier
    by_mult = {}
    n_basis_rows, n_product_rows = 0, 0
    for r in T1:
        if r < nb:
            pr, m = int(prow[r]), 0
            n_basis_rows += 1
        else:
            j, f = divmod(r - nb, nnew)
            pr, m = int(prow[new[f]]), 1 << j
            n_product_rows += 1
        s = by_mult.setdefault(m, set())
        s ^= {pr}
    # ---- (3) level-0 backward replay per multiplier, with the per-row check
    M0_final_own = own_rows(M0)                  # final states after the level-0 echelon
    pairs = {}
    rows_checked, rows_ok = 0, 0
    for m, targets in by_mult.items():
        for t in targets:                       # per-row check of the level-0 trace
            orig = backward(M0.shape[0], ps0, Xs0, [t])
            y = 0
            for r in orig:
                y ^= M0_orig_own[r]
            rows_checked += 1
            rows_ok += (y == M0_final_own[t])
        orig = backward(M0.shape[0], ps0, Xs0, sorted(targets))
        for r in orig:
            mu, k = cl.row_pair(r)
            kk = (m | mu, k)                    # (4) pushed multiplier
            pairs[kk] = pairs.get(kk, 0) ^ 1
    C_replay = sorted(kk for kk, p in pairs.items() if p)
    C_replay_json = sorted([[i for i in range(18) if (mu >> i) & 1], k] for mu, k in C_replay)
    C_arch = sorted(arch_cert["C"])
    # ---- (5) own evaluation
    acc = {}
    for mu, k in C_replay:
        for mm in eqs_own[k]:
            z = mu | mm
            acc[z] = acc.get(z, 0) ^ 1
    ssum = sorted(z for z, p in acc.items() if p)
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J2", "construction": "certificate back-trace replay",
           "key": key, "archived_one_first_iteration": arch_rec["one_first_iteration"],
           "level0": {"rows": int(M0.shape[0]), "rank": int(len(ps0)), "low_rows_new": int(nnew)},
           "level1": {"stack_rows": int(M1.shape[0]), "archived_stack_rows": arch_rec["stack_rows_per_iteration"][1],
                      "rank": int(len(ps1)), "pstar": pstar,
                      "traced_original_rows": len(T1), "of_which_level0_basis_rows": n_basis_rows,
                      "of_which_vj_products": n_product_rows,
                      "xor_of_traced_rows_is_exactly_1": level1_xor_is_1},
           "boundary": {"distinct_multipliers": len(by_mult),
                        "multiplier_degrees": sorted(set(bin(m).count("1") for m in by_mult))},
           "level0_per_row_trace_checks": {"checked": rows_checked, "ok": rows_ok},
           "C_replay_size": len(C_replay_json), "C_archived_size": len(C_arch),
           "C_replay_equals_archived": C_replay_json == C_arch,
           "C_replay_max_deg_mu": max(len(p[0]) for p in C_replay_json),
           "own_sum_mu_f_k": ssum, "own_sum_is_exactly_1": ssum == [0],
           "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
           "wall_seconds": round(time.time() - t0, 1)}
    json.dump(res, open(os.path.join(HERE, "backtrace_replay_results.json"), "w"), indent=1)
    print(json.dumps(res))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-VAR2 -- THE LEAD PRODUCER MEASUREMENT.

TASK-20260812-56b9da / BATCH-4ed139 / GOAL-MLKEM-005.  Role: executor.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

WHAT THIS IS.  An implementation of G-VAR2 exactly as PREREG-1
(tasks/TASK-20260812-34b86c/prereg.md) section 3 freezes it -- VAR-S (3.1), the
degenerate-scale rule with BOTH readings (3.2), VAR-F (3.3), the conjunction and
tau_var = 1e-3 (3.4) -- validated against the two committed fixtures F0
(probe_nullroute.py) and F1 (probe_gvar_family.py) of section 4, with V_evade
scored through the same criterion (section 5), the graded guard of 6.1 and the
could-not-fail arrangements of 6.2/6.3/6.4 MEASURED rather than cited.

THE FROZEN TEXT IS NOT AMENDED HERE.  Where this producer believes a clause is
under-specified, the clause is implemented AS WRITTEN and the objection is
reported in report_gvar2.md.

PROVENANCE OF THE ARITHMETIC ROUTES.  probe_nullroute.py is IMPORTED, not
transcribed: its fixed_unimodular, fixed_isometry, bit_identical, make_A and
logdet_routes are used directly.  This file's family-parametrised route function
is checked for BIT-IDENTICAL agreement with the committed probe's own
logdet_routes at every F0 lattice and basis, and the agreement is reported.
probe_gvar_family.py is likewise imported for its moduli()/build_basis() so that
F1 is the committed fixture's F1 and not a re-reading of it.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out results_gvar2.json

WRITES exactly one file: the --out path.  No git write, no commit.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()

# ------------------------------------------------------------------ constants
# PREREG-1 2.1, transcribed from the frozen text
Q = 3329
LOGQ = math.log(Q)
N_BASES = 8
TAU_REL = 0.10
S_X = 1.0
TAU_VAR = 1e-3

# PREREG-1 2.2, carried verbatim from BATCH-9e3584 prereg 1.2/1.3
LATTICES = OrderedDict([
    ("L1", (100, 30)), ("L2", (100, 70)),
    ("L4", (140, 40)), ("L5", (140, 100)),
    ("L7", (20, 6)), ("L8", (20, 14)),
    ("L9", (30, 9)), ("L10", (30, 21)),
    ("L11", (40, 12)), ("L12", (40, 28)),
])
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
             20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}

# PREREG-1 6.1 -- the frozen lambda grid
LAMBDA_GRID = [0.0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0]

ROUTES6 = ["R0_closed_form", "R1_slogdet", "R2_QR_of_BT", "R3_slogdet_of_UB",
           "R4_gram_half_slogdet", "R5_slogdet_of_BH_ambient_isometry"]

def _repo_root():
    """Resolved from THIS FILE's own location so the script is re-executable
    from any working directory; overridable by GVAR2_REPO_ROOT."""
    env = os.environ.get("GVAR2_REPO_ROOT")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return os.path.abspath(".")


REPO = _repo_root()
P_PROBE_N = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
          "TASK-20260809-444fe7/probes/probe_nullroute.py")
P_PROBE_N_OUT = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
          "TASK-20260809-444fe7/probes/probe_nullroute_output.json")
P_PROBE_F = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
          "reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.py")
P_PROBE_F_OUT = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
          "reviews-wave2/TASK-20260812-aadafd/probes/probe_gvar_family.json")
P_RELVAR = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
          "TASK-20260809-cda2f6/results_relvar.json")
P_PREREG1 = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-34b86c/prereg.md")

INPUT_FILES = OrderedDict([
    ("prereg1", P_PREREG1),
    ("probe_nullroute.py", P_PROBE_N),
    ("probe_nullroute_output.json", P_PROBE_N_OUT),
    ("probe_gvar_family.py", P_PROBE_F),
    ("probe_gvar_family.json", P_PROBE_F_OUT),
    ("results_relvar.json", P_RELVAR),
])


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)          # module-level only; main() NOT called
    return mod


PROBE_N = load_module(P_PROBE_N, "probe_nullroute_committed")
PROBE_F = load_module(P_PROBE_F, "probe_gvar_family_committed")

# ------------------------------------------------------- families (PREREG-1 2.3)
# name -> (seed_prefix, modulus mode)
FAMILIES = OrderedDict([
    ("F0",        (1, "const_q")),
    ("F1",        (1, "q_plus_i")),
    ("F0|fib_s2", (2, "const_q")),
    ("F1|fib_s2", (2, "q_plus_3_fixed")),
    ("F0|fib_s3", (3, "const_q")),
    ("F1|fib_s3", (3, "q_plus_3_fixed")),
    ("F0|fib_s4", (4, "const_q")),
    ("F1|fib_s4", (4, "q_plus_3_fixed")),
])
# PREREG-1 3.3: the fibre sub-family of a scored family.  s2 is the primary
# fibre family; s3 and s4 are the AM-10 replicates.
FIBRE_OF = {"F0": ["F0|fib_s2", "F0|fib_s3", "F0|fib_s4"],
            "F1": ["F1|fib_s2", "F1|fib_s3", "F1|fib_s4"]}
SCORED_FAMILIES = ["F0", "F1"]


def make_A_seed(d, k, q, i, seed_prefix):
    """PREREG-1 2.3.  seed_prefix 1 is the committed A of BOTH fixtures; 2, 3, 4
    are the new fibre draws."""
    rng = np.random.default_rng([seed_prefix, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def moduli(d, k, i, mode):
    m = np.full(d - k, Q, dtype=np.int64)
    if mode == "q_plus_i":
        m[0] = Q + i
    elif mode == "q_plus_3_fixed":
        m[0] = Q + 3
    return m


def build_basis_fam(d, k, i, family):
    seed_prefix, mode = FAMILIES[family]
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A_seed(d, k, Q, i, seed_prefix)
    B[k:, k:] = np.diag(moduli(d, k, i, mode))
    return B


def structural_check_and_exact_absdet(B, d, k, m):
    """|det B| for B = [[I_k, A],[0, diag(m)]] is prod(m) EXACTLY.  The block
    structure is verified entrywise here, so the exact determinant is a
    verified consequence of the verified structure rather than an assumption."""
    ok = (np.array_equal(B[:k, :k], np.eye(k, dtype=np.int64))
          and np.array_equal(B[k:, :k], np.zeros((d - k, k), dtype=np.int64))
          and np.array_equal(B[k:, k:], np.diag(m)))
    ad = 1
    for v in m.tolist():
        ad *= int(v)
    return bool(ok), ad


# --------------------------------------------------- the six arithmetic routes
def logdet_routes_fam(B, d, k, m, family):
    """PREREG-1 2.5.  R1..R5 are functions of B alone and are the committed
    probe's own expressions.  R0 is the exact closed form of THIS family's
    determinant: (d-k) log q in a constant-q family, sum_j log m_j otherwise,
    labelled R0_closed_form_of_family there."""
    out = OrderedDict()
    if np.all(m == Q):
        out["R0_closed_form"] = float((d - k) * LOGQ)
        r0_label = "R0_closed_form"
    else:
        out["R0_closed_form"] = float(np.sum(np.log(m.astype(np.float64))))
        r0_label = "R0_closed_form_of_family"
    Bf = B.astype(np.float64)
    _, la = np.linalg.slogdet(Bf)
    out["R1_slogdet"] = float(la)
    _, R = np.linalg.qr(Bf.T)
    out["R2_QR_of_BT"] = float(np.sum(np.log(np.abs(np.diag(R)))))
    U = PROBE_N.fixed_unimodular(d)                       # IMPORTED
    _, la3 = np.linalg.slogdet((U @ B).astype(np.float64))
    out["R3_slogdet_of_UB"] = float(la3)
    G = (B @ B.T).astype(np.float64)
    _, la4 = np.linalg.slogdet(G)
    out["R4_gram_half_slogdet"] = float(0.5 * la4)
    H = PROBE_N.fixed_isometry(d)                         # IMPORTED
    _, la5 = np.linalg.slogdet(Bf @ H)
    out["R5_slogdet_of_BH_ambient_isometry"] = float(la5)
    return out, r0_label


def raw_gso_logs(B):
    """CARRIED VERBATIM from BATCH-9e3584 measure_relvar.py.  NO reduction."""
    _, R = np.linalg.qr(B.astype(np.float64).T)
    dg = np.abs(np.diag(R))
    return np.log(dg), float(np.sum(np.log(dg)))


def x_rawtail_of(loggs, logdet, d, beta):
    """CARRIED VERBATIM from BATCH-9e3584 measure_relvar.py."""
    return float(np.mean(loggs[d - beta:]) - logdet / d)


bit_identical = PROBE_N.bit_identical                      # IMPORTED


def sd_mean(vals):
    a = np.asarray(vals, dtype=float)
    return (float(a.std(ddof=1)) if a.size > 1 else 0.0), float(a.mean())


# ---------------------------------------------------------------- G-VAR2 core
def var_s_from_cells(cellstats):
    """PREREG-1 3.1 + 3.2.  cellstats: {lattice: {beta: {'s':..,'m':..}}}.
    Returns per-cell dicts carrying s_c, m_c, R_{d,k}, D_c, the frozen verdict
    and the NAIVE reading's verdict beside it."""
    out = OrderedDict()
    for lat, per_beta in cellstats.items():
        means = [v["m"] for v in per_beta.values()]
        R = float(max(means) - min(means)) if means else 0.0
        for beta, v in per_beta.items():
            s = float(v["s"])
            degenerate = (R == 0.0)
            if degenerate:
                verdict = "scale_degenerate"
                D = None
                naive_D = float("inf") if s > 0.0 else float("nan")
                naive = "ADMIT" if s > 0.0 else "REFUSE_or_undefined_0_over_0"
            else:
                D = s / R
                verdict = "ADMIT" if D >= TAU_VAR else "REFUSE"
                naive_D = D
                naive = verdict
            rec = OrderedDict([
                ("lattice", lat), ("beta", beta),
                ("s_c", s), ("m_c", float(v["m"])),
                ("spread_max_minus_min", v.get("spread")),
                ("bit_identical", v.get("bit_identical")),
                ("R_d_k", R), ("D_c", D),
                ("VAR_S", verdict),
                ("naive_reading_D_c",
                 (None if naive_D != naive_D else
                  ("+inf" if naive_D == float("inf") else naive_D))),
                ("naive_reading_VAR_S", naive),
            ])
            out["%s_b%s" % (lat, beta)] = rec
    return out


def var_f_from_cells(fibstats):
    """PREREG-1 3.3.  Same statistic, same threshold, with the identical
    scale_degenerate handling -- at a scale_degenerate fibre cell non-constancy
    is decided by the carried bit_identical() test.  BOTH statistics reported."""
    out = OrderedDict()
    for lat, per_beta in fibstats.items():
        means = [v["m"] for v in per_beta.values()]
        R = float(max(means) - min(means)) if means else 0.0
        for beta, v in per_beta.items():
            s = float(v["s"])
            bid = v.get("bit_identical")
            if R == 0.0:
                D = None
                verdict = "PASS" if (bid is False) else "FAIL"
                basis = "bit_identity_at_scale_degenerate_fibre_cell"
            else:
                D = s / R
                verdict = "PASS" if D >= TAU_VAR else "FAIL"
                basis = "scaled_dispersion"
            out["%s_b%s" % (lat, beta)] = OrderedDict([
                ("lattice", lat), ("beta", beta),
                ("s_c_fib", s), ("m_c_fib", float(v["m"])),
                ("R_d_k_fib", R), ("D_c_fib", D),
                ("bit_identical", bid),
                ("n_distinct_ieee754_values_over_8_bases", v.get("n_distinct")),
                ("fibre_seed_prefix", v.get("seed_prefix")),
                ("VAR_F", verdict), ("decided_by", basis),
            ])
    return out


def gvar2(var_s_rec, var_f_rec):
    """PREREG-1 3.4."""
    if var_f_rec is None:
        return "UNCOVERED_VAR_F_NOT_COMPUTABLE"
    s_ok = var_s_rec["VAR_S"] in ("ADMIT", "scale_degenerate")
    f_ok = var_f_rec["VAR_F"] == "PASS"
    return "ADMIT" if (s_ok and f_ok) else "REFUSE"


# ------------------------------------------------------- prereg 2.6 (F0 table)
def prereg_2_6_from_probe_n():
    """probe_nullroute.py keeps its transcription of the notarized BATCH-9e3584
    prereg 2.6 table inside main(), so it is EXTRACTED from the committed source
    by literal evaluation of that assignment rather than re-transcribed here."""
    import ast
    tree = ast.parse(open(P_PROBE_N).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "PREREG_2_6":
                    return ast.literal_eval(node.value)
    raise RuntimeError("PREREG_2_6 not found in the committed probe_nullroute.py")


PREREG_2_6 = prereg_2_6_from_probe_n()
# probe_gvar_family.py carries its own independent transcription of the same
# notarized table, keyed differently; the two committed copies are compared.
PREREG_2_6_F = PROBE_F.PREREG_X_NULL
TABLE_AGREEMENT = {
    "n_entries_probe_nullroute": sum(len(v) for v in PREREG_2_6.values()),
    "n_entries_probe_gvar_family": len(PREREG_2_6_F),
    "the_two_committed_transcriptions_agree_exactly": all(
        PREREG_2_6[lat][beta] == PREREG_2_6_F[(lat, beta)]
        for lat in PREREG_2_6 for beta in PREREG_2_6[lat]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["task_id"] = "TASK-20260812-56b9da"
    R["batch_id"] = "BATCH-4ed139"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "executor"
    R["object"] = "G-VAR2 as frozen by PREREG-1 section 3"
    R["claim_tier"] = "toy"
    R["status_of_this_measurement"] = (
        "PRODUCER MEASUREMENT under the frozen PREREG-1. Observations only. It "
        "declares no hypothesis supported or refuted, validates no heuristic, "
        "and changes no research status. CLAIM TIER TOY: nothing here bears on "
        "ML-KEM security, any FIPS 203 parameter set, any attack cost or any "
        "cost model.")
    R["certificate"] = {
        "kind": "none",
        "reason": "pure measurement run: no discrete-log solve and no "
                  "factor-base relation is claimed or produced. The run's own "
                  "internal re-verifications (import agreement, fibre "
                  "determinant guard, RC/RD rawtail agreement, prereg 2.6 "
                  "reproduction) are instrument checks, not certificates."}
    R["environment"] = {
        "python": platform.python_version(), "numpy": np.__version__,
        "platform": platform.platform(), "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
    }
    try:
        import fpylll                                        # noqa: F401
        R["environment"]["fpylll"] = fpylll.__version__
    except Exception as e:
        R["environment"]["fpylll"] = (
            "ABSENT (%s). INFRASTRUCTURE SIGNAL, AGENTS.md rule 5 and PREREG-1 "
            "7.4: route RD is UNAVAILABLE for lam1n and hkz on this host. This "
            "is NEVER a fixture failure and NEVER negative mathematical "
            "evidence." % e.__class__.__name__)
    try:
        R["git_revision"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip()
        R["git_dirty_paths"] = subprocess.run(
            ["git", "-C", REPO, "status", "--porcelain"], capture_output=True,
            text=True, check=True).stdout.strip().splitlines()
    except Exception as e:
        R["git_revision"] = "UNAVAILABLE: %s" % e
        R["git_dirty_paths"] = None
    # ---- the notarized contract, verified rather than asserted
    NOTARIZING = "8d72f2c03"
    rel_prereg = os.path.relpath(P_PREREG1, REPO)
    pv = OrderedDict()
    try:
        pv["sha256_working_tree"] = sha256_file(P_PREREG1)
        side = os.path.join(os.path.dirname(P_PREREG1), "prereg_sha256.txt")
        pv["sidecar_text"] = (open(side).read().strip()
                              if os.path.exists(side) else None)
        blob = subprocess.run(["git", "-C", REPO, "show",
                               "%s:%s" % (NOTARIZING, rel_prereg)],
                              capture_output=True, check=True).stdout
        pv["sha256_notarized_blob"] = hashlib.sha256(blob).hexdigest()
        pv["working_tree_equals_notarized_blob"] = (
            pv["sha256_working_tree"] == pv["sha256_notarized_blob"])
        parent = subprocess.run(["git", "-C", REPO, "rev-parse",
                                 "%s^" % NOTARIZING], capture_output=True,
                                text=True, check=True).stdout.strip()
        at_parent = subprocess.run(["git", "-C", REPO, "cat-file", "-e",
                                    "%s:%s" % (parent, rel_prereg)],
                                   capture_output=True)
        pv["absent_at_the_notarizing_commit_parent"] = at_parent.returncode != 0
        pv["notarizing_commit"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", NOTARIZING], capture_output=True,
            text=True, check=True).stdout.strip()
        pv["notarizing_commit_parent"] = parent
        pv["is_ancestor_of_HEAD"] = subprocess.run(
            ["git", "-C", REPO, "merge-base", "--is-ancestor", NOTARIZING,
             "HEAD"], capture_output=True).returncode == 0
        pv["files_changed_by_the_notarizing_commit"] = subprocess.run(
            ["git", "-C", REPO, "show", "--name-only", "--format=", NOTARIZING],
            capture_output=True, text=True,
            check=True).stdout.strip().splitlines()
    except Exception as e:
        pv["ERROR"] = "%s: %s" % (e.__class__.__name__, e)
    R["prereg_verification"] = pv
    R["inputs_sha256"] = OrderedDict(
        (k, sha256_file(v)) for k, v in INPUT_FILES.items())
    R["input_paths"] = OrderedDict(
        (k, os.path.relpath(v, REPO)) for k, v in INPUT_FILES.items())
    R["frozen_constants"] = {"q": Q, "N_BASES": N_BASES, "tau_rel": TAU_REL,
                             "s_X": S_X, "tau_var": TAU_VAR,
                             "lambda_grid": LAMBDA_GRID}
    R["seeds"] = {
        "A_draws": "np.random.default_rng([seed_prefix, d, k, i]); seed_prefix "
                   "1 = F0/F1 (committed), 2 = primary fibre, 3 and 4 = AM-10 "
                   "fibre replicates",
        "fixed_unimodular_U": "np.random.default_rng([424242, d]) via the "
                              "IMPORTED probe_nullroute.fixed_unimodular",
        "fixed_isometry_H": "np.random.default_rng([313131, d]) via the "
                            "IMPORTED probe_nullroute.fixed_isometry",
        "other_randomness": "none; no sampling, no shuffling, no timing-"
                            "dependent branch"}
    R["route_provenance"] = {
        "probe_nullroute.py": "IMPORTED as a module (not transcribed); its "
                              "fixed_unimodular, fixed_isometry, bit_identical "
                              "and logdet_routes are used directly",
        "probe_gvar_family.py": "IMPORTED as a module; its moduli() and "
                                "build_basis() are used for the F0/F1 "
                                "cross-check below",
        "raw_gso_logs / x_rawtail_of": "TRANSCRIBED VERBATIM from BATCH-9e3584 "
                                       "measure_relvar.py (route RD for rawtail "
                                       "needs no reduction)"}

    # =================================================== 0. build every family
    print("[0] building bases and evaluating routes ...")
    LD = {}          # (family, lat, i) -> {route: logdet}
    A00 = {}         # (family, lat, i) -> A[0,0]
    ABSDET = {}      # (family, lat, i) -> exact |det B| (python int)
    STRUCT_OK = True
    R0LABEL = {}
    for family in FAMILIES:
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                B = build_basis_fam(d, k, i, family)
                m = moduli(d, k, i, FAMILIES[family][1])
                ok, ad = structural_check_and_exact_absdet(B, d, k, m)
                STRUCT_OK = STRUCT_OK and ok
                ABSDET[(family, lat, i)] = ad
                A00[(family, lat, i)] = int(B[0, k])
                lr, lbl = logdet_routes_fam(B, d, k, m, family)
                LD[(family, lat, i)] = lr
                R0LABEL[family] = lbl
    R["block_structure_verified_entrywise_everywhere"] = bool(STRUCT_OK)
    R["R0_label_by_family"] = dict(R0LABEL)

    # ------------------------------------------------ import-agreement check
    agree = OrderedDict()
    worst = 0.0
    n_bitid = 0
    n_tot = 0
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            B = PROBE_N.build_basis(d, k, Q, i)              # committed builder
            ref = PROBE_N.logdet_routes(B, d, k)             # committed routes
            mine = LD[("F0", lat, i)]
            for r in ROUTES6:
                n_tot += 1
                if float(ref[r]).hex() == float(mine[r]).hex():
                    n_bitid += 1
                worst = max(worst, abs(ref[r] - mine[r]))
    agree["n_route_values_compared"] = n_tot
    agree["n_bit_identical_to_the_committed_probe"] = n_bitid
    agree["max_abs_difference"] = worst
    # and that the committed F1 builder agrees with this file's F1
    f1_ok = True
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            f1_ok = f1_ok and np.array_equal(
                PROBE_F.build_basis(d, k, i, "F1"), build_basis_fam(d, k, i, "F1"))
            f1_ok = f1_ok and np.array_equal(
                PROBE_F.build_basis(d, k, i, "F0"), build_basis_fam(d, k, i, "F0"))
    agree["F0_and_F1_bases_identical_to_the_committed_probe_gvar_family_builder"] = bool(f1_ok)
    R["import_agreement_with_the_committed_fixtures"] = agree

    # --------------------------------- guards: F1 moduli, fibre determinants
    mono = [int(moduli(20, 6, i, "q_plus_i")[0]) for i in range(N_BASES)]
    R["guard_F1_moduli_strictly_increase_in_i"] = {
        "m_i[0] over i": mono,
        "strictly_increasing": bool(all(b > a for a, b in zip(mono, mono[1:])))}

    fib_guard = OrderedDict()
    FIB_GUARD_OK = True
    for family in FAMILIES:
        if "|fib" not in family:
            continue
        per_lat = OrderedDict()
        for lat in LATTICES:
            dets = [ABSDET[(family, lat, i)] for i in range(N_BASES)]
            ok = len(set(dets)) == 1
            FIB_GUARD_OK = FIB_GUARD_OK and ok
            # also the float log|det| bit-identity through R1, reported
            r1 = [LD[(family, lat, i)]["R1_slogdet"] for i in range(N_BASES)]
            per_lat[lat] = {
                "abs_det_bit_identical_across_8_bases": bool(ok),
                "n_distinct_exact_abs_det": len(set(dets)),
                "abs_det_decimal_digits": len(str(dets[0])),
                "R1_slogdet_bit_identical_across_8_bases": bool(bit_identical(r1)),
            }
        fib_guard[family] = per_lat
    R["fibre_guard_abs_det_bit_identical"] = fib_guard
    R["FIBRE_GUARD_HOLDS_EVERYWHERE"] = bool(FIB_GUARD_OK)
    print("    fibre determinant guard holds everywhere: %s" % FIB_GUARD_OK)
    if not FIB_GUARD_OK or not STRUCT_OK:
        R["INSTRUMENT_FAILURE"] = (
            "PREREG-1 6.4: the fibre family failed to hold |det B_i| fixed "
            "across the 8 bases, or the block structure did not verify. The "
            "run claims nothing.")
        with open(args.out, "w") as fh:
            json.dump(R, fh, indent=1)
        print("INSTRUMENT FAILURE -- see %s" % args.out)
        return 3

    # =============================== 1. determinant-only candidates, 6 routes
    def cand_value(cand, ld, a00, d, beta, lam=None):
        xn = (beta / d) * (1.0 / d) * ld
        if cand == "X_null":
            return xn
        if cand == "rdet":
            return math.exp(ld / d)
        if cand == "V_evade":
            return xn + 1e-9 * a00 / Q
        if cand == "X_lambda":
            return xn + lam * a00 / Q
        raise KeyError(cand)

    def stats_for(cand, route, family, lam=None):
        """cellstats keyed lattice -> beta -> {s, m, spread, bit_identical,
        n_distinct}"""
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per_beta = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = [cand_value(cand, LD[(family, lat, i)][route],
                                   A00[(family, lat, i)], d, beta, lam)
                        for i in range(N_BASES)]
                s, m = sd_mean(vals)
                per_beta[beta] = {
                    "s": s, "m": m,
                    "spread": float(max(vals) - min(vals)),
                    "bit_identical": bool(bit_identical(vals)),
                    "n_distinct": len({float(v).hex() for v in vals}),
                    "seed_prefix": FAMILIES[family][0]}
            out[lat] = per_beta
        return out

    DET_CANDS = ["X_null", "rdet", "V_evade"]
    DECLARED_ARGS = {
        "X_null": "d, k, beta, q, abs(det B)",
        "rdet": "d, abs(det B)",
        "V_evade": "d, k, beta, q, abs(det B), A[0,0]",
        "X_lambda": "d, k, beta, q, abs(det B), A[0,0]",
        "rawtail": "d, k, beta, q, raw GSO profile",
        "hkz": "d, k, beta, q, HKZ-reduced GSO profile",
        "lam1n": "d, k, q, GSO profile (+ beta if any)",
    }
    FIBRE_NUISANCE = {
        "X_null": "abs(det B)", "rdet": "abs(det B)",
        "V_evade": "abs(det B), A[0,0]", "X_lambda": "abs(det B), A[0,0]",
        "rawtail": "d, k, beta, q, abs(det B)",
        "hkz": "d, k, beta, q, abs(det B)",
        "lam1n": "d, k, beta, q, abs(det B)",
    }

    print("[1] scoring determinant-only candidates through six routes ...")
    PROF = OrderedDict()      # "cand|route|family" -> profile block
    for cand in DET_CANDS:
        for route in ROUTES6:
            for family in SCORED_FAMILIES:
                vs = var_s_from_cells(stats_for(cand, route, family))
                fib_primary = FIBRE_OF[family][0]
                vf_all = OrderedDict()
                for fibfam in FIBRE_OF[family]:
                    vf_all[fibfam] = var_f_from_cells(
                        stats_for(cand, route, fibfam))
                vf = vf_all[fib_primary]
                cells = OrderedDict()
                for ck in vs:
                    g = gvar2(vs[ck], vf[ck])
                    cells[ck] = OrderedDict([
                        ("VAR_S", vs[ck]), ("VAR_F", vf[ck]),
                        ("G_VAR2", g),
                        ("VAR_F_replicates", {
                            f: {"VAR_F": vf_all[f][ck]["VAR_F"],
                                "s_c_fib": vf_all[f][ck]["s_c_fib"],
                                "D_c_fib": vf_all[f][ck]["D_c_fib"],
                                "bit_identical": vf_all[f][ck]["bit_identical"],
                                "seed_prefix": vf_all[f][ck]["fibre_seed_prefix"]}
                            for f in FIBRE_OF[family]}),
                    ])
                verds = [c["G_VAR2"] for c in cells.values()]
                PROF["%s|%s|%s" % (cand, route, family)] = OrderedDict([
                    ("candidate", cand), ("route", route), ("family", family),
                    ("declared_arguments", DECLARED_ARGS[cand]),
                    ("fibre_family_primary", fib_primary),
                    ("fibre_nuisance_held_fixed", FIBRE_NUISANCE[cand]),
                    ("n_cells_scored", len(cells)),
                    ("n_ADMIT", sum(1 for v in verds if v == "ADMIT")),
                    ("n_REFUSE", sum(1 for v in verds if v == "REFUSE")),
                    ("n_UNCOVERED", sum(1 for v in verds
                                        if v.startswith("UNCOVERED"))),
                    ("per_cell", cells),
                ])

    # ================================== 2. rawtail / hkz / lam1n (RC and RD)
    print("[2] scoring rawtail (RC, RD) and hkz / lam1n (RC only) ...")
    relvar = json.load(open(P_RELVAR))
    RC = relvar["G_VAR"]["per_candidate"]

    def rc_cellstats(cand):
        out = OrderedDict()
        for cell, v in RC[cand]["per_cell"].items():
            lat, b = cell.rsplit("_b", 1)
            out.setdefault(lat, OrderedDict())[int(b)] = {
                "s": v["float_sd"], "m": v["mean"],
                "spread": float(v["max"] - v["min"]),
                "bit_identical": v["bit_identical"], "n_distinct": None,
                "seed_prefix": 1}
        return out

    # RD for rawtail: reduction-free raw GSO, all families
    RAW = {}
    for family in FAMILIES:
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                B = build_basis_fam(d, k, i, family)
                RAW[(family, lat, i)] = raw_gso_logs(B)

    def rawtail_cellstats(family):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per_beta = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = []
                for i in range(N_BASES):
                    lg, ld = RAW[(family, lat, i)]
                    vals.append(x_rawtail_of(lg, ld, d, beta))
                s, m = sd_mean(vals)
                per_beta[beta] = {"s": s, "m": m,
                                  "spread": float(max(vals) - min(vals)),
                                  "bit_identical": bool(bit_identical(vals)),
                                  "n_distinct": len({float(v).hex()
                                                     for v in vals}),
                                  "seed_prefix": FAMILIES[family][0]}
            out[lat] = per_beta
        return out

    # RC/RD agreement on rawtail in F0 (consistency check, AM-15(a))
    rd_f0 = rawtail_cellstats("F0")
    rc_rt = rc_cellstats("rawtail")
    dmax_sd = dmax_mean = 0.0
    ncmp = 0
    for lat in rc_rt:
        for beta in rc_rt[lat]:
            ncmp += 1
            dmax_sd = max(dmax_sd, abs(rc_rt[lat][beta]["s"] - rd_f0[lat][beta]["s"]))
            dmax_mean = max(dmax_mean,
                            abs(rc_rt[lat][beta]["m"] - rd_f0[lat][beta]["m"]))
    R["consistency_rawtail_RC_vs_RD_in_F0"] = {
        "cells_compared": ncmp, "max_abs_diff_in_between_basis_sd": dmax_sd,
        "max_abs_diff_in_cell_mean": dmax_mean,
        "note": "route RD for rawtail is the committed measure_relvar.py raw-GSO "
                "path carried verbatim and uses NO reduction; this is a "
                "CONSISTENCY CHECK under AM-15(a), not a prediction."}

    # rawtail through RC (VAR-S only; the fibre is not available in the
    # committed file) and through RD (VAR-S and VAR-F)
    for family in SCORED_FAMILIES:
        # -- RC exists only for F0 (the committed family)
        if family == "F0":
            vs = var_s_from_cells(rc_rt)
            cells = OrderedDict((ck, OrderedDict([
                ("VAR_S", vs[ck]), ("VAR_F", None),
                ("G_VAR2", "UNCOVERED_VAR_F_NOT_COMPUTABLE"),
                ("uncovered_reason",
                 "route RC is a committed per-cell summary of the scored family "
                 "only; BATCH-9e3584 computed no fibre family, so VAR-F cannot "
                 "be evaluated through RC. Declared coverage limit (PREREG-1 "
                 "7.4), not a result."),
            ])) for ck in vs)
            PROF["rawtail|RC|F0"] = OrderedDict([
                ("candidate", "rawtail"), ("route", "RC_committed_values"),
                ("family", "F0"), ("declared_arguments", DECLARED_ARGS["rawtail"]),
                ("fibre_family_primary", None),
                ("fibre_nuisance_held_fixed", FIBRE_NUISANCE["rawtail"]),
                ("n_cells_scored", len(cells)),
                ("n_ADMIT", 0), ("n_REFUSE", 0), ("n_UNCOVERED", len(cells)),
                ("n_VAR_S_ADMIT", sum(1 for c in cells.values()
                                      if c["VAR_S"]["VAR_S"] == "ADMIT")),
                ("per_cell", cells)])
        vs = var_s_from_cells(rawtail_cellstats(family))
        fibp = FIBRE_OF[family][0]
        vf_all = OrderedDict((f, var_f_from_cells(rawtail_cellstats(f)))
                             for f in FIBRE_OF[family])
        vf = vf_all[fibp]
        cells = OrderedDict()
        for ck in vs:
            cells[ck] = OrderedDict([
                ("VAR_S", vs[ck]), ("VAR_F", vf[ck]),
                ("G_VAR2", gvar2(vs[ck], vf[ck])),
                ("VAR_F_replicates", {
                    f: {"VAR_F": vf_all[f][ck]["VAR_F"],
                        "s_c_fib": vf_all[f][ck]["s_c_fib"],
                        "D_c_fib": vf_all[f][ck]["D_c_fib"],
                        "bit_identical": vf_all[f][ck]["bit_identical"],
                        "seed_prefix": vf_all[f][ck]["fibre_seed_prefix"]}
                    for f in FIBRE_OF[family]})])
        verds = [c["G_VAR2"] for c in cells.values()]
        PROF["rawtail|RD_rawgso|%s" % family] = OrderedDict([
            ("candidate", "rawtail"),
            ("route", "RD_rawgso_no_reduction"),
            ("route_note",
             "PREREG-1 2.5 declares routes RC and RD for rawtail. RD is written "
             "there as 'recomputation through the FROZEN HKZ pipeline at d <= 40 "
             "only, fpylll pinned at 0.6.4'. rawtail is computed inside that "
             "frozen pipeline from the RAW, UNREDUCED basis (measure_relvar.py "
             "raw_gso_logs + x_rawtail_of) and uses no reduction and no fpylll, "
             "so this recomputation is available on this host and at every d. "
             "This is reported as an observation about the frozen text, NOT as "
             "an amendment to it: the RC route is reported unchanged beside it, "
             "and a reviewer who reads RD as strictly requiring fpylll should "
             "read this row as UNCOVERED."),
            ("family", family), ("declared_arguments", DECLARED_ARGS["rawtail"]),
            ("fibre_family_primary", fibp),
            ("fibre_nuisance_held_fixed", FIBRE_NUISANCE["rawtail"]),
            ("n_cells_scored", len(cells)),
            ("n_ADMIT", sum(1 for v in verds if v == "ADMIT")),
            ("n_REFUSE", sum(1 for v in verds if v == "REFUSE")),
            ("n_UNCOVERED", sum(1 for v in verds if v.startswith("UNCOVERED"))),
            ("per_cell", cells)])

    for cand in ("lam1n", "hkz"):
        vs = var_s_from_cells(rc_cellstats(cand))
        cells = OrderedDict((ck, OrderedDict([
            ("VAR_S", vs[ck]), ("VAR_F", None),
            ("G_VAR2", "UNCOVERED_VAR_F_NOT_COMPUTABLE"),
            ("uncovered_reason",
             "VAR-F needs the candidate evaluated on the fibre families of "
             "PREREG-1 2.3, which requires the frozen HKZ pipeline. fpylll is "
             "ABSENT on this host (route RD unavailable) and BATCH-9e3584 "
             "computed no fibre family, so route RC cannot supply it either. "
             "INFRASTRUCTURE SIGNAL + declared coverage limit (PREREG-1 7.4); "
             "NEVER a fixture failure and never negative evidence."),
        ])) for ck in vs)
        PROF["%s|RC|F0" % cand] = OrderedDict([
            ("candidate", cand), ("route", "RC_committed_values"),
            ("family", "F0"), ("declared_arguments", DECLARED_ARGS[cand]),
            ("fibre_family_primary", None),
            ("fibre_nuisance_held_fixed", FIBRE_NUISANCE[cand]),
            ("n_cells_scored", len(cells)),
            ("n_cells_declared_in_family", 38),
            ("n_cells_NOT_COMPUTED_in_the_committed_file",
             38 - len(cells)),
            ("not_computed_reason",
             "d > 40 exceeds the frozen reduction bound (BATCH-9e3584 prereg "
             "2.13); declared in advance, neither a zero nor a pass nor a fail"),
            ("n_ADMIT", 0), ("n_REFUSE", 0), ("n_UNCOVERED", len(cells)),
            ("n_VAR_S_ADMIT", sum(1 for c in cells.values()
                                  if c["VAR_S"]["VAR_S"] == "ADMIT")),
            ("n_VAR_S_scale_degenerate",
             sum(1 for c in cells.values()
                 if c["VAR_S"]["VAR_S"] == "scale_degenerate")),
            ("per_cell", cells)])
        PROF["%s|RD_frozen_HKZ|F0" % cand] = OrderedDict([
            ("candidate", cand), ("route", "RD_frozen_HKZ_pipeline"),
            ("family", "F0"), ("n_cells_scored", 0),
            ("n_UNCOVERED", 38),
            ("uncovered_reason",
             "fpylll ABSENT on this host: route RD could not be run at any "
             "cell. INFRASTRUCTURE SIGNAL (AGENTS.md rule 5, PREREG-1 7.4). "
             "Nothing is estimated or substituted for it."),
            ("per_cell", {})])

    R["per_cell_profiles"] = PROF

    # ===================================== 3. FIXTURE F0 and FIXTURE F1
    print("[3] adjudicating the two fixtures ...")

    def block(cand, route, family):
        return PROF.get("%s|%s|%s" % (cand, route, family))

    f0 = OrderedDict()
    f0_refusal_half_ok = True
    for cand in ("X_null", "rdet"):
        rows = OrderedDict()
        for route in ROUTES6:
            b = block(cand, route, "F0")
            verds = [c["G_VAR2"] for c in b["per_cell"].values()]
            ok = all(v == "REFUSE" for v in verds)
            f0_refusal_half_ok = f0_refusal_half_ok and ok
            rows[route] = {
                "target": "REFUSED",
                "n_cells_covered": len(verds), "n_cells_declared": 38,
                "coverage": "%d/38" % len(verds),
                "n_REFUSE": sum(1 for v in verds if v == "REFUSE"),
                "n_ADMIT": sum(1 for v in verds if v == "ADMIT"),
                "TARGET_MET_AT_EVERY_COVERED_CELL": bool(ok)}
        f0[cand] = rows
    admitted_half = OrderedDict()
    for key in ("rawtail|RC|F0", "rawtail|RD_rawgso|F0", "lam1n|RC|F0",
                "lam1n|RD_frozen_HKZ|F0", "hkz|RC|F0", "hkz|RD_frozen_HKZ|F0"):
        b = PROF[key]
        verds = [c["G_VAR2"] for c in b["per_cell"].values()]
        admitted_half[key] = {
            "target": "ADMITTED",
            "n_cells_covered_for_the_FULL_G_VAR2_verdict":
                sum(1 for v in verds if not v.startswith("UNCOVERED")),
            "n_cells_with_a_VAR_S_value": len(verds),
            "n_cells_declared": 38,
            "n_ADMIT": sum(1 for v in verds if v == "ADMIT"),
            "n_REFUSE": sum(1 for v in verds if v == "REFUSE"),
            "n_UNCOVERED": sum(1 for v in verds if v.startswith("UNCOVERED"))
                           + (38 - len(verds)),
            "TARGET_MET_AT_EVERY_COVERED_CELL":
                (all(v == "ADMIT" for v in verds) if verds and
                 all(not v.startswith("UNCOVERED") for v in verds) else None)}
    f0_admit_full = [k for k, v in admitted_half.items()
                     if v["TARGET_MET_AT_EVERY_COVERED_CELL"] is True]
    f0_admit_uncov = [k for k, v in admitted_half.items()
                      if v["TARGET_MET_AT_EVERY_COVERED_CELL"] is None]
    f0_admit_fail = [k for k, v in admitted_half.items()
                     if v["TARGET_MET_AT_EVERY_COVERED_CELL"] is False]
    F0_VERDICT = ("FAIL" if (not f0_refusal_half_ok or f0_admit_fail)
                  else ("PASS" if not f0_admit_uncov else "PARTIAL"))
    R["FIXTURE_F0"] = {
        "declared_target_behaviour": "PREREG-1 4.1: all six routes to X_null "
                                     "REFUSED, all six to rdet REFUSED, "
                                     "lam1n / hkz / rawtail ADMITTED",
        "refusal_half_per_candidate_per_route": f0,
        "refusal_half_TARGET_MET_EVERYWHERE": bool(f0_refusal_half_ok),
        "admitted_half_per_candidate_per_route": admitted_half,
        "admitted_half_fully_covered_and_met": f0_admit_full,
        "admitted_half_uncovered": f0_admit_uncov,
        "admitted_half_target_missed": f0_admit_fail,
        "R2_OUT_1_F0_VERDICT": F0_VERDICT,
        "verdict_basis":
            "PREREG-1 4.1 + 7.4: the determinant-only half needs no reduction "
            "and is fully scorable here, so its verdict is binding; the "
            "ADMITTED half is reported at its ACTUAL coverage."}

    f1 = OrderedDict()
    f1_ok = True
    for cand in ("X_null", "rdet"):
        rows = OrderedDict()
        for route in ROUTES6:
            b = block(cand, route, "F1")
            verds = [c["G_VAR2"] for c in b["per_cell"].values()]
            ok = (len(verds) == 38) and all(v == "REFUSE" for v in verds)
            f1_ok = f1_ok and ok
            rows[route] = {
                "target": "REFUSED",
                "n_cells_covered": len(verds), "coverage": "%d/38" % len(verds),
                "n_REFUSE": sum(1 for v in verds if v == "REFUSE"),
                "n_ADMIT": sum(1 for v in verds if v == "ADMIT"),
                "TARGET_MET_AT_ALL_38_CELLS": bool(ok)}
        f1[cand] = rows
    R["FIXTURE_F1"] = {
        "declared_target_behaviour": "PREREG-1 4.2 / AM-17(b): X_null REFUSED "
                                     "and rdet REFUSED in F1, at every one of "
                                     "the 38 cells, for every declared route",
        "per_candidate_per_route": f1,
        "R2_OUT_2_F1_VERDICT": "PASS" if f1_ok else "FAIL",
        "declared_scope_limit":
            "lam1n, hkz and rawtail are NOT SCORED in F1 and no target "
            "behaviour is declared for them there (PREREG-1 4.2). Their absence "
            "is a declared scope limit and is never reported as a failure. "
            "rawtail's F1 row is computed and reported here for information "
            "only and enters no F1 verdict."}
    R["FIXTURE_F1_rawtail_information_only"] = {
        "n_ADMIT": PROF["rawtail|RD_rawgso|F1"]["n_ADMIT"],
        "n_REFUSE": PROF["rawtail|RD_rawgso|F1"]["n_REFUSE"],
        "note": "information only; PREREG-1 4.2 declares no target for it and "
                "it enters no verdict."}

    # ===================================== 4. P-V1 -- VAR-S ALONE on V_evade
    print("[4] P-V1: VAR-S alone on V_evade over F0 ...")
    pv1 = OrderedDict()
    pv1_holds = True
    for route in ROUTES6:
        b = block("V_evade", route, "F0")
        vs = [c["VAR_S"] for c in b["per_cell"].values()]
        admits = [v for v in vs if v["VAR_S"] == "ADMIT"]
        maxD = max([v["D_c"] for v in vs if v["D_c"] is not None] or [None])
        sds = [v["s_c"] for v in vs]
        pv1_holds = pv1_holds and not admits
        pv1[route] = {
            "n_cells": len(vs),
            "n_VAR_S_REFUSE": sum(1 for v in vs if v["VAR_S"] == "REFUSE"),
            "n_VAR_S_ADMIT": len(admits),
            "n_scale_degenerate": sum(1 for v in vs
                                      if v["VAR_S"] == "scale_degenerate"),
            "max_D_c": maxD, "tau_var": TAU_VAR,
            "max_between_basis_sd": max(sds), "min_between_basis_sd": min(sds)}
    R["P_V1"] = {
        "statement": "VAR-S alone REFUSES V_evade at every scored F0 cell "
                     "(PREREG-1 5)",
        "falsifier": "VAR-S admits V_evade at any scored cell (D_c >= tau_var)",
        "class": "CONSISTENCY CHECK (AM-15(a)), declared in advance in PREREG-1 "
                 "5; it does not count toward this batch's empirical content",
        "adjudicated_on": "VAR-S ALONE, all six declared routes, all 38 F0 cells",
        "per_route": pv1,
        "R2_OUT_3_P_V1": "HOLDS" if pv1_holds else "FALSIFIED"}
    R["V_evade_FULL_G_VAR2_verdict_reported_separately_and_is_not_P_V1"] = {
        route: {"family": fam,
                "n_ADMIT": block("V_evade", route, fam)["n_ADMIT"],
                "n_REFUSE": block("V_evade", route, fam)["n_REFUSE"]}
        for route in ROUTES6 for fam in ["F0"]}

    # ===================================== 5. graded guard (PREREG-1 6.1)
    print("[5] graded guard over the frozen lambda grid ...")
    guard = OrderedDict()
    n_cross = 0
    n_cells_guard = 0
    for route in ROUTES6:
        per_cell = OrderedDict()
        prof = {lam: var_s_from_cells(stats_for("X_lambda", route, "F0", lam))
                for lam in LAMBDA_GRID}
        for ck in prof[0.0]:
            lam_star = None
            row = []
            for lam in LAMBDA_GRID:
                rec = prof[lam][ck]
                row.append({"lambda": lam, "D_c": rec["D_c"],
                            "VAR_S": rec["VAR_S"], "s_c": rec["s_c"]})
                if lam_star is None and rec["VAR_S"] == "ADMIT":
                    lam_star = lam
            per_cell[ck] = {"crossing_amplitude_lambda_star": lam_star,
                            "profile": row}
            if route == ROUTES6[1]:
                n_cells_guard += 1
                if lam_star is not None:
                    n_cross += 1
        guard[route] = {
            "n_cells": len(per_cell),
            "n_cells_crossing": sum(1 for v in per_cell.values()
                                    if v["crossing_amplitude_lambda_star"]
                                    is not None),
            "lambda_star_values": sorted(
                {v["crossing_amplitude_lambda_star"] for v in per_cell.values()},
                key=lambda x: (x is None, x)),
            "per_cell": per_cell}
    crossed_anywhere = any(g["n_cells_crossing"] > 0 for g in guard.values())
    majority = all(g["n_cells_crossing"] * 2 > g["n_cells"]
                   for g in guard.values())
    R["GRADED_GUARD"] = {
        "lambda_grid": LAMBDA_GRID,
        "note": "lambda = 0 is X_null itself; lambda = 1e-9 is V_evade",
        "per_route": guard,
        "P_G1_crossed_somewhere_at_a_majority_of_cells_every_route":
            bool(majority),
        "crossed_anywhere_in_the_grid": bool(crossed_anywhere),
        "R2_OUT_4": "crossing-amplitude profile reported per cell per route",
        "R2_OUT_V_FIRES": bool(not crossed_anywhere),
        "R2_OUT_V_meaning":
            "PREREG-1 6.1: if the guard does not cross anywhere in the grid, "
            "VAR-S is dead at this scale and EVERY G-VAR2 verdict in this batch "
            "is VOID, both fixtures included."}

    # =========================== 6. scale-degenerate disclosure (R2-OUT-5)
    print("[6] scale-degenerate disclosure ...")
    sd_disc = OrderedDict()
    for key, b in PROF.items():
        rows = []
        for ck, c in b.get("per_cell", {}).items():
            v = c.get("VAR_S")
            if v and v["VAR_S"] == "scale_degenerate":
                rows.append({"cell": ck, "d_k": "%s" % v["lattice"],
                             "s_c": v["s_c"], "R_d_k": v["R_d_k"],
                             "frozen_reading": "scale_degenerate "
                                               "(NOT a pass, NOT a fail)",
                             "naive_reading_D_c": v["naive_reading_D_c"],
                             "naive_reading_VAR_S": v["naive_reading_VAR_S"],
                             "G_VAR2_under_the_frozen_reading": c["G_VAR2"]})
        if rows:
            sd_disc[key] = {"n_scale_degenerate_cells": len(rows), "cells": rows}
    R["R2_OUT_5_scale_degenerate_disclosure"] = {
        "rule": "PREREG-1 3.2. FROZEN READING BINDING: R_{d,k} == 0 gives "
                "scale_degenerate, which is NOT a pass and NOT a fail, and the "
                "cell's G-VAR2 verdict is then decided by VAR-F alone. The "
                "NAIVE reading (s/0 = +inf -> ADMIT) is reported beside it at "
                "every such cell.",
        "by_block": sd_disc,
        "summary_candidates_with_scale_degenerate_cells": sorted(
            {PROF[k]["candidate"] for k in sd_disc}),
        "naive_versus_frozen_by_block": OrderedDict(
            (k, {"n_scale_degenerate": v["n_scale_degenerate_cells"],
                 "n_naive_reading_ADMIT": sum(
                     1 for c in v["cells"]
                     if c["naive_reading_VAR_S"] == "ADMIT"),
                 "n_naive_reading_REFUSE_or_undefined": sum(
                     1 for c in v["cells"]
                     if c["naive_reading_VAR_S"] != "ADMIT"),
                 "n_G_VAR2_ADMIT_under_the_frozen_reading": sum(
                     1 for c in v["cells"]
                     if c["G_VAR2_under_the_frozen_reading"] == "ADMIT"),
                 "n_G_VAR2_REFUSE_under_the_frozen_reading": sum(
                     1 for c in v["cells"]
                     if c["G_VAR2_under_the_frozen_reading"] == "REFUSE")})
            for k, v in sd_disc.items()),
    }

    # =========================== 7. could-not-fail arrangements, MEASURED
    print("[7] could-not-fail arrangements, measured in both directions ...")
    xnull_f0_sd = [c["VAR_S"]["s_c"]
                   for c in block("X_null", "R0_closed_form", "F0")["per_cell"].values()]
    xnull_f0_sd_r1 = [c["VAR_S"]["s_c"]
                      for c in block("X_null", "R1_slogdet", "F0")["per_cell"].values()]
    hkz_vs = [c["VAR_S"] for c in PROF["hkz|RC|F0"]["per_cell"].values()]
    rawtail_vs = [c["VAR_S"] for c in
                  PROF["rawtail|RD_rawgso|F0"]["per_cell"].values()]
    varf_pass_blocks = OrderedDict()
    for key, b in PROF.items():
        n_pass = sum(1 for c in b.get("per_cell", {}).values()
                     if c.get("VAR_F") and c["VAR_F"]["VAR_F"] == "PASS")
        if n_pass:
            varf_pass_blocks[key] = n_pass
    R["COULD_NOT_FAIL_MEASURED"] = {
        "6.2_could_not_FIRE": {
            "arrangement": "the criterion could never refuse anything (tau_var "
                           "= 0, or D_c >= tau_var everywhere by construction)",
            "measured": {
                "X_null_F0_R0_between_basis_sd_distribution": {
                    "n": len(xnull_f0_sd), "min": min(xnull_f0_sd),
                    "max": max(xnull_f0_sd),
                    "n_exactly_zero": sum(1 for v in xnull_f0_sd if v == 0.0)},
                "X_null_F0_R1_between_basis_sd_distribution": {
                    "n": len(xnull_f0_sd_r1), "min": min(xnull_f0_sd_r1),
                    "max": max(xnull_f0_sd_r1),
                    "n_exactly_zero": sum(1 for v in xnull_f0_sd_r1
                                          if v == 0.0)},
                "n_REFUSE_verdicts_in_this_run": sum(
                    b.get("n_REFUSE", 0) for b in PROF.values())},
            "WE_ARE_IN_IT": bool(sum(b.get("n_REFUSE", 0)
                                     for b in PROF.values()) == 0)},
        "6.3_could_not_PASS": {
            "arrangement": "the criterion could never admit anything (tau_var "
                           "above every real candidate's dispersion)",
            "measured": {
                "hkz_RC_max_D_c": max([v["D_c"] for v in hkz_vs
                                       if v["D_c"] is not None] or [None]),
                "hkz_RC_max_between_basis_sd": max(v["s_c"] for v in hkz_vs),
                "rawtail_RD_max_D_c": max([v["D_c"] for v in rawtail_vs
                                           if v["D_c"] is not None] or [None]),
                "n_ADMIT_verdicts_in_this_run": sum(
                    b.get("n_ADMIT", 0) for b in PROF.values()),
                "n_VAR_S_ADMIT_cells_in_this_run": sum(
                    1 for b in PROF.values()
                    for c in b.get("per_cell", {}).values()
                    if c.get("VAR_S") and c["VAR_S"]["VAR_S"] == "ADMIT")},
            "WE_ARE_IN_IT": bool(sum(b.get("n_ADMIT", 0)
                                     for b in PROF.values()) == 0)},
        "6.4_could_not_fail_on_the_FIBRE_clause": {
            "could_not_FAIL_direction": {
                "arrangement": "if every fibre family held X constant for every "
                               "candidate, VAR-F would refuse everything and the "
                               "clause would be a constant",
                "blocks_with_at_least_one_VAR_F_PASS": varf_pass_blocks,
                "n_blocks_with_a_VAR_F_PASS": len(varf_pass_blocks),
                "WE_ARE_IN_IT": bool(len(varf_pass_blocks) == 0),
                "note": "X_gso_k is rider (ii)'s object (TASK-20260812-4b8ede) "
                        "and is NOT scored here; the live check is satisfied "
                        "here by the candidates listed above or not at all."},
            "could_not_PASS_direction": {
                "arrangement": "if a fibre family failed to hold the nuisance "
                               "argument fixed, VAR-F would pass everything",
                "guard": "abs(det B_i) bit-identical across all 8 bases at every "
                         "fibre family and every lattice, ASSERTED AND PRINTED",
                "GUARD_HOLDS_EVERYWHERE": bool(FIB_GUARD_OK),
                "WE_ARE_IN_IT": bool(not FIB_GUARD_OK)}},
        "6.5_AM_16_f": "N/A with its reason (PREREG-1 6.5): this batch "
                       "estimates no standard error and applies no variance "
                       "decomposition."}

    # =========================== 8. P-R26 -- prereg 2.6 reproduction
    print("[8] P-R26 consistency check ...")
    p26 = OrderedDict()
    for route in ROUTES6:
        n_ok = n_tot = 0
        worst26 = 0.0
        for lat, (d, k) in LATTICES.items():
            for beta in BETA_GRID[d]:
                want = PREREG_2_6[lat][beta]
                for i in range(N_BASES):
                    got = (beta / d) * (1.0 / d) * LD[("F0", lat, i)][route]
                    n_tot += 1
                    worst26 = max(worst26, abs(round(got, 6) - want))
                    n_ok += int(round(got, 6) == want)
        p26[route] = {"cells_x_bases": n_tot,
                      "n_reproducing_to_6_decimals": n_ok,
                      "max_abs_deviation_after_rounding": worst26}
    # the definitional through-the-matrix route is R1 (slogdet of B)
    defroute = "R1_slogdet"
    cells_ok = 0
    for lat, (d, k) in LATTICES.items():
        for beta in BETA_GRID[d]:
            want = PREREG_2_6[lat][beta]
            vals = [(beta / d) * (1.0 / d) * LD[("F0", lat, i)][defroute]
                    for i in range(N_BASES)]
            cells_ok += int(all(round(v, 6) == want for v in vals))
    R["P_R26"] = {
        "statement": "definitional (through-the-matrix) X_null reproduces the "
                     "notarized BATCH-9e3584 prereg 2.6 table at 38 of 38 F0 "
                     "cells to 6 decimals",
        "class": "CONSISTENCY CHECK (AM-15(a)); reported, not counted as "
                 "empirical content",
        "definitional_route": defroute,
        "n_cells_reproducing_at_all_8_bases": cells_ok,
        "n_cells_declared": 38,
        "VERDICT": "HOLDS" if cells_ok == 38 else "DOES_NOT_HOLD",
        "per_route_cellsxbases": p26,
        "table_provenance": "extracted by literal evaluation from the committed "
                            "probe_nullroute.py (transcribed there from the "
                            "notarized BATCH-9e3584 prereg 2.6)",
        "two_committed_transcriptions_compared": TABLE_AGREEMENT}

    # =========================== 9. prediction register rows this task owns
    R["PREDICTION_REGISTER_ROWS_OWNED_BY_THIS_TASK"] = {
        "n_items_in_PREREG_1_section_9": 8,
        "n_OPEN_at_notarization": 8,
        "owned_here": {
            "P-F0": {"class": "PREDICTION",
                     "open_at_notarization": True,
                     "outcome": ("MET on the refusal half at every covered cell"
                                 if f0_refusal_half_ok else
                                 "NOT MET on the refusal half"),
                     "admitted_half": {"fully_covered_and_met": f0_admit_full,
                                       "uncovered": f0_admit_uncov,
                                       "target_missed": f0_admit_fail}},
            "P-F1": {"class": "PREDICTION", "open_at_notarization": True,
                     "outcome": "MET at all 38 cells, all six routes"
                                if f1_ok else "NOT MET"},
            "P-G1": {"class": "MUST-PASS GUARD", "open_at_notarization": True,
                     "outcome": "guard crosses within the grid at a majority of "
                                "cells on every route" if majority else
                                ("guard crosses somewhere but not at a majority "
                                 "of cells on every route" if crossed_anywhere
                                 else "NO CROSSING ANYWHERE -- R2-OUT-V FIRES")},
            "P-V1": {"class": "CONSISTENCY CHECK (AM-15(a))",
                     "open_at_notarization": True,
                     "outcome": "HOLDS" if pv1_holds else "FALSIFIED"},
            "P-R26": {"class": "CONSISTENCY CHECK (AM-15(a))",
                      "open_at_notarization": True,
                      "outcome": "HOLDS" if cells_ok == 38 else "DOES_NOT_HOLD"},
        },
        "not_owned_here": {
            "P-FR1": "rider (ii), TASK-20260812-4b8ede",
            "P-C1": "rider (i), TASK-20260812-78a6e3",
            "P-L1": "rider (iii), TASK-20260812-0e930c"},
        "empirical_content_note": "PREREG-1 9: five predictions (P-F0, P-F1, "
                                  "P-FR1, P-C1, P-L1), two consistency checks "
                                  "(P-V1, P-R26) which are NOT counted, and one "
                                  "must-pass guard (P-G1)."}

    # =========================== 10. termination branch (PREREG-1 7)
    partial = bool(f0_admit_uncov) or ("ABSENT" in str(R["environment"]["fpylll"]))
    if not crossed_anywhere:
        branch = "R2-OUT-V (VOID)"
        clause = ("PREREG-1 6.1: 'if the guard does not cross anywhere in the "
                  "grid, VAR-S is dead at this scale and every G-VAR2 verdict "
                  "in this batch is VOID, both fixtures included.'")
    elif F0_VERDICT == "FAIL":
        branch = "T-F0FAIL" + ("-PARTIAL" if partial else "")
        clause = ("PREREG-1 7.3: 'FIRES WHEN: F0 FAILS at one or more covered "
                  "cells or routes -- whatever F1 does.'")
    elif R["FIXTURE_F1"]["R2_OUT_2_F1_VERDICT"] == "FAIL":
        branch = "T-F1FAIL" + ("-PARTIAL" if partial else "")
        clause = ("PREREG-1 7.2: 'FIRES WHEN: F0 PASSES and F1 FAILS at one or "
                  "more cells or routes.'")
    else:
        branch = "T-PASS" + ("-PARTIAL" if partial else "")
        clause = ("PREREG-1 7.1: 'FIRES WHEN: F0 PASSES at full coverage and F1 "
                  "PASSES at all 38 cells for all declared routes, and the "
                  "guard crossed.' with PREREG-1 7.4: 'the branch that fires is "
                  "reported with the suffix -PARTIAL' when any declared cell, "
                  "route or candidate is uncovered.")
    R["TERMINATION"] = {
        "read_off": "R2-OUT-1 and R2-OUT-2 under R2-OUT-V's precedence, and "
                    "nowhere else (PREREG-1 10)",
        "R2_OUT_1_F0": F0_VERDICT,
        "R2_OUT_2_F1": R["FIXTURE_F1"]["R2_OUT_2_F1_VERDICT"],
        "R2_OUT_V_fires": bool(not crossed_anywhere),
        "BRANCH": branch,
        "clause": clause,
        "partial_suffix_reason":
            ("route RD is uncovered for lam1n and hkz (fpylll ABSENT: "
             "INFRASTRUCTURE SIGNAL), and the full G-VAR2 verdict on the "
             "ADMITTED half is uncovered wherever VAR-F cannot be evaluated. "
             "PREREG-1 7.4: T-PASS-PARTIAL does NOT license C3 to proceed "
             "behind the instrument." if partial else None)}

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    try:
        import resource
        R["peak_rss_mb"] = round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    except Exception as e:
        R["peak_rss_mb"] = "UNAVAILABLE: %s" % e
    R["what_this_measurement_does_NOT_establish"] = [
        "It declares no hypothesis supported, rejected or closed, and no "
        "heuristic validated or refuted. Those are Reviewer and Coordinator "
        "acts.",
        "It makes no admissibility claim about any candidate observable. "
        "PREREG-1 3.5: passing G-VAR2 carries NO claim that an observable "
        "carries lattice information.",
        "It says nothing about the gate's REFUSAL side or any false-refusal "
        "rate (C-2(b) stands).",
        "It revalidates nothing scored under G-VAR's predecessor, rescores "
        "BATCH-a44d08 in no respect, and retires AM-3 in no respect.",
        "The G-VAR refusal is cited ONLY as conditional on the frozen family F0.",
        "CLAIM TIER TOY: nothing bears on ML-KEM security, any FIPS 203 "
        "parameter set, any attack cost or any cost model, and no number "
        "transports to beta = 606, d = 1420 or any other parameter set by "
        "extrapolation, analogy or any other route.",
    ]

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1)
        fh.write("\n")

    # ------------------------------------------------------------- human print
    print("=" * 78)
    print("G-VAR2 -- LEAD PRODUCER MEASUREMENT (TASK-20260812-56b9da) -- TOY")
    print("=" * 78)
    print("fpylll: %s" % R["environment"]["fpylll"])
    print("block structure verified entrywise everywhere: %s" % STRUCT_OK)
    print("FIBRE GUARD |det B_i| bit-identical across 8 bases everywhere: %s"
          % FIB_GUARD_OK)
    print("import agreement with committed probe_nullroute.logdet_routes: "
          "%d/%d bit-identical, max abs diff %.3e"
          % (agree["n_bit_identical_to_the_committed_probe"],
             agree["n_route_values_compared"], agree["max_abs_difference"]))
    print("\nF0 refusal half (target REFUSED), per candidate per route:")
    for cand, rows in f0.items():
        for route, v in rows.items():
            print("  %-8s %-34s cov %-6s REFUSE %2d ADMIT %2d  met=%s"
                  % (cand, route, v["coverage"], v["n_REFUSE"], v["n_ADMIT"],
                     v["TARGET_MET_AT_EVERY_COVERED_CELL"]))
    print("\nF0 admitted half (target ADMITTED):")
    for k, v in admitted_half.items():
        print("  %-28s VAR-S cells %2d  full-verdict cells %2d  ADMIT %2d "
              "REFUSE %2d UNCOV %2d met=%s"
              % (k, v["n_cells_with_a_VAR_S_value"],
                 v["n_cells_covered_for_the_FULL_G_VAR2_verdict"],
                 v["n_ADMIT"], v["n_REFUSE"], v["n_UNCOVERED"],
                 v["TARGET_MET_AT_EVERY_COVERED_CELL"]))
    print("\nF1 (target REFUSED at all 38 cells):")
    for cand, rows in f1.items():
        for route, v in rows.items():
            print("  %-8s %-34s cov %-6s REFUSE %2d ADMIT %2d  met=%s"
                  % (cand, route, v["coverage"], v["n_REFUSE"], v["n_ADMIT"],
                     v["TARGET_MET_AT_ALL_38_CELLS"]))
    print("\nP-V1 (VAR-S alone on V_evade, F0): %s" % R["P_V1"]["R2_OUT_3_P_V1"])
    for route, v in pv1.items():
        print("  %-34s REFUSE %2d ADMIT %2d  max D_c %s  max sd %.3e"
              % (route, v["n_VAR_S_REFUSE"], v["n_VAR_S_ADMIT"],
                 v["max_D_c"], v["max_between_basis_sd"]))
    print("\nGraded guard: crossed anywhere = %s, majority every route = %s"
          % (crossed_anywhere, majority))
    for route, g in guard.items():
        print("  %-34s crossing cells %2d/%2d  lambda* values %s"
              % (route, g["n_cells_crossing"], g["n_cells"],
                 g["lambda_star_values"]))
    print("\nscale_degenerate blocks: %s"
          % {k: v["n_scale_degenerate_cells"] for k, v in sd_disc.items()})
    print("\nP-R26: %s (%d/38 cells reproduce at all 8 bases)"
          % (R["P_R26"]["VERDICT"], cells_ok))
    print("\nR2-OUT-1 F0 = %s   R2-OUT-2 F1 = %s   R2-OUT-V fires = %s"
          % (F0_VERDICT, R["FIXTURE_F1"]["R2_OUT_2_F1_VERDICT"],
             not crossed_anywhere))
    print("TERMINATION BRANCH: %s" % branch)
    print("\nwrote %s in %.2f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

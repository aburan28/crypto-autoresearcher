"""One cell of EXP-ICEX-aaccfc protocol v2. Cell kinds:

  primary       m = 5 interval factor base: stage 1 (batched B0 sieve, uniform
                collector), stage 2 (alpha2 2-sum scan, 256 held-out points),
                stage 3 (rank tracking, SGE + Lanczos, kernel fixing, 16
                descents), known-false scrambled-relation control.
  null_randfb   C-6 matched null: random-x factor base of the interval size;
                the same attempt stream, stage 1 + stage-3 LA; yield and cost.
  stage_cost    m in {6, 8}, B_m = ceil(p^(1/m)): stage 1 to the same rank rule,
                stage 2 scan and stage-3 LA; no descents (OQ-7).
  rho           C-6 baseline, 64 targets.

Charged cost (C-5 complete cost) = stage 1 (factor-base construction, forward
table build once, every attempt's R_j = a_j G + b_j Q, every B0 query incl.
failed ones, relation extraction) + stage 3 (collector rank tracking, SGE,
Lanczos, back-substitution) + all descent attempts. Stage 2 and the controls
are measured separately and are not part of the complete cost. Peak RSS of
the cell process is recorded after every stage.

Verification (uncharged, verify.py arithmetic): every relation and descent
decomposition by point arithmetic; every factor-base log x_i by x_i G = P_i;
k by k G = Q; every descent by k_t G = Q_t. A failed identity is a procedure
defect (spec stopping rule 1) and stops the cell.
"""

from __future__ import annotations

import time

import common
import la
from arith import Cost, Curve, Fp
from b0 import (ForwardTable, b0_query, extract_relation, interval_fb, random_fb, rss_bytes,
                terms_to_row, two_sum_scan, verify_relation)
from verify import O, VCurve

DEFAULT_MAX_ATTEMPTS = 5_000_000
DEFAULT_MAX_DESCENT_ATTEMPTS = 1_000_000


class ProcedureDefect(RuntimeError):
    pass


class Incomplete(RuntimeError):
    """Machine-protection cap reached: infrastructure incompletion, never evidence."""


class NamespaceRefused(RuntimeError):
    """Frozen-namespace cell requested outside an admitted driver run (AMD-20260929-5a84eb FX-4)."""


# Set only by cellrun.run_task after its admission guard accepts a frozen-namespace task.
FROZEN_ADMITTED = False


# v4b A-1: the only smoke-namespace path allowed to evaluate a frozen fixture is
# the in-process unit tests (tests/conftest.py, test_charging, test_controls,
# test_fxa), which call these functions directly and persist nothing.
TESTS_NS_PREFIX = common.SMOKE_NS + "|tests"


def _ns_guard(ns, fx=None):
    if ns == common.FROZEN_NS and not FROZEN_ADMITTED:
        raise NamespaceRefused(f"namespace {ns!r} is frozen; only cellrun.py under an admitted driver run may use it")
    if (fx is not None and common.is_smoke_ns(ns) and not str(ns).startswith(TESTS_NS_PREFIX)
            and common.is_frozen_fixture(fx)):
        raise NamespaceRefused(f"frozen fixture in smoke namespace {ns!r}: only the in-process unit-test "
                               f"namespace {TESTS_NS_PREFIX}* may evaluate it")


def _pt(P):
    return None if P is O else list(P)


class AttemptLog:
    """Columnar per-attempt receipt (attempt index = position): membership as a
    '0'/'1' string, charged group operations per attempt, and the probe count,
    which B0's full scan makes identical for every attempt of a cell (checked).
    Units of attempt j = 13 * pt_ops[j] + probes_each (no other op is charged
    in an attempt; checked). Hits are listed for member attempts only."""

    def __init__(self):
        self.bits, self.pt_ops, self.hits = [], [], []
        self.probes_each = None
        self.n = self.n_failed = 0

    def append(self, j, res, d):
        if j != self.n:
            raise ProcedureDefect(f"attempt log index {j} != {self.n}")
        if d["mul"] or d["inv"] or d["la_mul"] or d["la_inv"]:
            raise ProcedureDefect(f"attempt {j} charged non-point field/LA ops")
        if self.probes_each is None:
            self.probes_each = d["probes"]
        elif d["probes"] != self.probes_each:
            raise ProcedureDefect(f"attempt {j} probe count {d['probes']} != {self.probes_each}")
        ops = d["pt_add"] + d["pt_dbl"]
        if d["units"] != common.UNIT_POINT_ADD * ops + common.UNIT_PROBE * d["probes"]:
            raise ProcedureDefect(f"attempt {j} units do not decompose")
        self.bits.append("1" if res["member"] else "0")
        self.pt_ops.append(ops)
        if res["member"]:
            self.hits.append([j, res["n_hits"], res["units_to_first_hit"]])
        else:
            self.n_failed += 1
        self.n += 1

    def as_dict(self):
        return {"member_bits": "".join(self.bits), "pt_ops": self.pt_ops, "probes_each": self.probes_each,
                "hits": self.hits, "encoding": "columnar; index = attempt j; units_j = 13*pt_ops[j] + probes_each"}


def target_k(fx, ns):
    return common.uniform(common.lab(ns, "target", fx["bits"], fx["seed"]), fx["N"])


def attempt_ab(fx, ns, j):
    return common.uniform_pair(common.lab(ns, "attempt", fx["bits"], fx["seed"], j), fx["N"])


def lanczos_dlabel(fx, ns, fbkind):
    q = fx["N"]

    def d(t, i):
        return 1 + common.uniform(common.lab(ns, "lanczos", fx["bits"], fx["seed"], fbkind, t, i), q - 1)
    return d


# ------------------------------------------------------------------ stage 1
def collect(fx, ns, fb, table, Q, m, max_attempts, log_fn=print, attempt_limit=None):
    """Uniform collector: attempts j = 0, 1, ... until rank L + 1 of the
    (classes, Q) system and then EXCESS_ROWS further relations."""
    q = fx["N"]
    L = fb.L
    G = tuple(fx["G"])
    s1 = Cost()
    rank_cost = Cost()
    rank_log = []
    tracker = la.RankTracker(L + 1, q, rank_cost, rank_log)
    F = Fp(fx["p"], s1)
    curve = Curve(F, fx["a"], fx["b"])
    relations = []
    log = AttemptLog()
    excess = 0
    j = 0
    limit = attempt_limit if attempt_limit is not None else max_attempts
    while True:
        if j >= limit:
            raise Incomplete(f"attempt cap {limit} reached at rank {tracker.rank}/{L + 1}, excess {excess}")
        a, b = attempt_ab(fx, ns, j)
        snap = s1.snapshot()
        R = curve.add(curve.mul(a, G), curve.mul(b, Q))
        res = b0_query(fx, fb, table, R, m, s1)
        if res["member"]:
            terms = extract_relation(fx, fb, table, res["first"], s1)
            if not verify_relation(fx, fb, R, terms, m):
                raise ProcedureDefect(f"relation at attempt {j} fails point-arithmetic verification")
            row = terms_to_row(terms, L, q)
            row[L] = (-b) % q
            full_before = tracker.rank == L + 1
            tracker.add(row)
            if full_before:
                excess += 1
            relations.append({"j": j, "a": a, "b": b, "R": _pt(R), "terms": terms, "row": row})
        log.append(j, res, s1.delta(snap))
        j += 1
        if tracker.rank == L + 1 and excess >= common.EXCESS_ROWS:
            break
    return {"attempts": log.as_dict(), "n_attempts": log.n, "n_failed": log.n_failed, "relations": relations,
            "stage1_attempt_cost": s1.as_dict(), "rank_cost": rank_cost.as_dict(), "rank_log": rank_log,
            "rank": tracker.rank}


def la_solve(fx, ns, fb, relations, fbkind, row_key="row"):
    q = fx["N"]
    L = fb.L
    cost = Cost()
    log = []
    rows = [r[row_key] for r in relations]
    rhs = [r["a"] for r in relations]
    t0 = time.time()
    try:
        x, info = la.solve(rows, rhs, L + 1, q, cost, log, lanczos_dlabel(fx, ns, fbkind))
        err = None
    except la.LAFailure as e:
        x, info, err = None, None, str(e)
    return {"x": x, "info": info, "error": err, "cost": cost.as_dict(), "log": log,
            "seconds": round(time.time() - t0, 4)}


def verify_logs(fx, fb, x, Q) -> dict:
    """Uncharged: x_i G = P_i for every class and x_Q G = Q."""
    if x is None:
        return {"all_ok": False, "reason": "no solution"}
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    fb_ok = [vc.mul(x[i], G) == tuple(fb.points[i]) for i in range(fb.L)]
    q_ok = vc.mul(x[fb.L], G) == (Q if Q is O else tuple(Q))
    return {"all_ok": all(fb_ok) and q_ok, "fb_logs_ok": sum(fb_ok), "fb_logs_total": fb.L, "k_ok": q_ok}


# ------------------------------------------------------------------ stage 2
def stage2(fx, ns, fb, n_heldout):
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    signed = [(i, s, P if s > 0 else vc.neg(P)) for i, P in enumerate(fb.points) for s in (1, -1)]
    per = []
    agree = 0
    total = Cost()
    for i in range(n_heldout):
        hk = common.uniform(common.lab(ns, "heldout", fx["bits"], fx["seed"], i), fx["N"])
        S = vc.mul(hk, G)
        c = Cost()
        r = two_sum_scan(fx, fb, S, c)
        brute = sorted((i1, s1, i2, s2) for i1, s1, P1 in signed for i2, s2, P2 in signed
                       if vc.add(P1, P2) == S)
        ok = sorted(r["pairs"]) == brute
        agree += ok
        per.append({"i": i, "units": c.units(), "n_pairs": r["n_pairs"], "agrees_brute_force": ok})
        for k, v in c.as_dict().items():
            if k not in ("units", "units_fieldlevel"):
                setattr(total, k, getattr(total, k) + v)
    units = [p["units"] for p in per]
    return {"n_heldout": n_heldout, "L": fb.L, "B": fb.B, "per_point": per,
            "mean_units": sum(units) / len(units) if units else None,
            "min_units": min(units) if units else None, "max_units": max(units) if units else None,
            "total_cost": total.as_dict(), "agreement_with_brute_force": agree, "peak_rss_bytes": rss_bytes()}


# ------------------------------------------------------------------ descents
def descents(fx, ns, fb, table, x, n_desc, max_attempts, m=5):
    q = fx["N"]
    G = tuple(fx["G"])
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    total = Cost()
    out = []
    for t in range(n_desc):
        kt = common.uniform(common.lab(ns, "descent", fx["bits"], fx["seed"], t), q)
        Qt = vc.mul(kt, G)
        c = Cost()
        F = Fp(fx["p"], c)
        curve = Curve(F, fx["a"], fx["b"])
        att = AttemptLog()
        found = None
        for i in range(max_attempts):
            r = common.uniform(common.lab(ns, "descent_r", fx["bits"], fx["seed"], t, i), q)
            snap = c.snapshot()
            R = curve.add(Qt, curve.mul(r, G))
            res = b0_query(fx, fb, table, R, m, c)
            if res["member"]:
                terms = extract_relation(fx, fb, table, res["first"], c)
                if not verify_relation(fx, fb, R, terms, m):
                    raise ProcedureDefect(f"descent {t} attempt {i} decomposition fails verification")
                khat = (sum(s * x[idx] for idx, s in terms) - r) % q
                found = {"i": i, "r": r, "terms": terms, "k_hat": khat}
            att.append(i, res, c.delta(snap))
            if found:
                break
        if not found:
            raise Incomplete(f"descent {t}: attempt cap {max_attempts}")
        ok = vc.mul(found["k_hat"], G) == Qt
        if not ok:
            raise ProcedureDefect(f"descent {t}: k_t G != Q_t")
        out.append({"t": t, "k_t": kt, "Q_t": _pt(Qt), "attempts": att.n, "attempt_log": att.as_dict(),
                    "units": c.units(), "verified": ok, **found})
        for k, v in c.as_dict().items():
            if k not in ("units", "units_fieldlevel"):
                setattr(total, k, getattr(total, k) + v)
    return {"targets": out, "cost": total.as_dict(), "n_verified": sum(o["verified"] for o in out),
            "peak_rss_bytes": rss_bytes()}


# ------------------------------------------------------------------ known-false
def scramble(fx, ns, relations, fbkind, L):
    """C-6 known-false: permute the factor-base coefficient vectors across rows
    (a_j, b_j stay with their rows). Fisher-Yates by '<ns>|scramble|...|<i>';
    if the permuted rows equal the originals the draw is advanced (at most 64
    times) so the control is never the identity."""
    q = fx["N"]
    n = len(relations)
    fbparts = [{k: v for k, v in r["row"].items() if k != L} for r in relations]
    for attempt in range(64):
        perm = list(range(n))
        for i in range(n - 1, 0, -1):
            jj = common.uniform(common.lab(ns, "scramble", fx["bits"], fx["seed"], fbkind, f"{attempt}.{i}"), i + 1)
            perm[i], perm[jj] = perm[jj], perm[i]
        if any(fbparts[perm[i]] != fbparts[i] for i in range(n)):
            break
    rows = []
    for i, r in enumerate(relations):
        row = dict(fbparts[perm[i]])
        row[L] = r["row"][L]
        rows.append({"a": r["a"], "row_scrambled": row})
    return perm, attempt, rows


def known_false(fx, ns, fb, relations, Q):
    perm, attempt, rows = scramble(fx, ns, relations, "interval_scramble", fb.L)
    sol = la_solve(fx, ns, fb, rows, "interval_scramble", row_key="row_scrambled")
    ver = verify_logs(fx, fb, sol["x"], Q)
    return {"permutation": perm, "permutation_redraws": attempt,
            "rows_changed": sum(1 for i in range(len(perm)) if perm[i] != i),
            "la_error": sol["error"], "la_cost": sol["cost"],
            "log_verification_all_ok": ver["all_ok"], "verification": ver,
            "control_passed": not ver["all_ok"]}


# ------------------------------------------------------------------ cells
def _sum_units(*costs):
    return sum(c["units"] for c in costs)


def run_primary(fx, ns, n_descents=common.N_DESCENTS, n_heldout=common.N_HELDOUT,
                max_attempts=DEFAULT_MAX_ATTEMPTS, max_descent_attempts=DEFAULT_MAX_DESCENT_ATTEMPTS,
                m=common.M_PRIMARY, log_fn=print):
    _ns_guard(ns, fx)
    t0 = time.time()
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    k = target_k(fx, ns)
    Q = vc.mul(k, tuple(fx["G"]))
    fb = interval_fb(fx, m)
    rss_fb = rss_bytes()
    table = ForwardTable(fx, fb)
    rss_table = rss_bytes()
    col = collect(fx, ns, fb, table, Q, m, max_attempts)
    rss_s1 = rss_bytes()
    stage1_cost = {"fb_construction": fb.cost, "forward_table": table.cost,
                   "attempts": col["stage1_attempt_cost"]}
    stage1_units = _sum_units(fb.cost, table.cost, col["stage1_attempt_cost"])
    log_fn(f"[{common.fixture_id(fx)} primary] stage1 attempts={col['n_attempts']} "
           f"relations={len(col['relations'])} L={fb.L}")
    sol = la_solve(fx, ns, fb, col["relations"], "interval")
    if sol["error"]:
        raise ProcedureDefect(f"stage 3 LA failed on the true relations: {sol['error']}")
    ver = verify_logs(fx, fb, sol["x"], Q)
    if not ver["all_ok"]:
        raise ProcedureDefect(f"stage 3 logs fail verification: {ver}")
    ref = la.gauss_reference([r["row"] for r in col["relations"]], [r["a"] for r in col["relations"]],
                             fb.L + 1, fx["N"])
    rss_s3 = rss_bytes()
    stage3_units = _sum_units(col["rank_cost"], sol["cost"])
    desc = descents(fx, ns, fb, table, sol["x"], n_descents, max_descent_attempts, m=m)
    desc_units = desc["cost"]["units"]
    rss_desc = rss_bytes()
    s2 = stage2(fx, ns, fb, n_heldout)
    kf = known_false(fx, ns, fb, col["relations"], Q)
    if not kf["control_passed"]:
        raise ProcedureDefect("known-false control: scrambled relations passed log verification")
    complete = stage1_units + stage3_units + desc_units
    return {
        "kind": "primary", "fixture": fx, "fixture_id": common.fixture_id(fx), "namespace": ns, "m": m,
        "factor_base": fb.summary(),
        "forward_table": {"size": table.size, "n_pairs": table.n_pairs, "cost": table.cost},
        "target": {"k": k, "Q": _pt(Q)},
        "stage1": {"n_attempts": col["n_attempts"], "n_failed_attempts": col["n_failed"],
                   "n_relations": len(col["relations"]), "cost": stage1_cost, "units": stage1_units,
                   "attempt_log": col["attempts"], "relations": col["relations"],
                   "peak_rss_bytes": rss_s1, "peak_rss_after_fb": rss_fb, "peak_rss_after_table": rss_table},
        "stage3": {"rank_tracking_cost": col["rank_cost"], "rank_log": col["rank_log"],
                   "la_cost": sol["cost"], "la_log": sol["log"], "la_info": sol["info"],
                   "units": stage3_units, "logs": sol["x"], "k_recovered": sol["x"][fb.L],
                   "log_verification": ver, "agrees_dense_reference": ref == sol["x"],
                   "peak_rss_bytes": rss_s3},
        "descents": {**desc, "units": desc_units, "n_descents": n_descents},
        "stage2_alpha2": s2,
        "known_false": kf,
        "complete_units": complete,
        "complete_units_components": {"stage1": stage1_units, "stage3": stage3_units, "descents": desc_units},
        "amortized_units_per_target": complete / (1 + n_descents),
        "peak_rss_bytes": rss_bytes(), "seconds": round(time.time() - t0, 3),
    }


def run_null_randfb(fx, ns, max_attempts=DEFAULT_MAX_ATTEMPTS, m=common.M_PRIMARY, log_fn=print):
    _ns_guard(ns, fx)
    t0 = time.time()
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    k = target_k(fx, ns)
    Q = vc.mul(k, tuple(fx["G"]))
    ifb = interval_fb(fx, m)
    fb = random_fb(fx, ns, ifb.L, ifb.B)
    table = ForwardTable(fx, fb)
    col = collect(fx, ns, fb, table, Q, m, max_attempts)
    rss_s1 = rss_bytes()
    stage1_units = _sum_units(fb.cost, table.cost, col["stage1_attempt_cost"])
    sol = la_solve(fx, ns, fb, col["relations"], "random_x")
    ver = verify_logs(fx, fb, sol["x"], Q)
    if sol["error"] or not ver["all_ok"]:
        raise ProcedureDefect(f"null LA/log verification failed: {sol['error']} {ver}")
    log_fn(f"[{common.fixture_id(fx)} null_randfb] attempts={col['n_attempts']} L={fb.L}")
    return {
        "kind": "null_randfb", "fixture": fx, "fixture_id": common.fixture_id(fx), "namespace": ns, "m": m,
        "factor_base": fb.summary(), "interval_L": ifb.L,
        "forward_table": {"size": table.size, "n_pairs": table.n_pairs, "cost": table.cost},
        "stage1": {"n_attempts": col["n_attempts"],
                   "n_failed_attempts": col["n_failed"],
                   "n_relations": len(col["relations"]),
                   "relation_yield": len(col["relations"]) / col["n_attempts"],
                   "cost": {"fb_construction": fb.cost, "forward_table": table.cost,
                            "attempts": col["stage1_attempt_cost"]},
                   "units": stage1_units, "attempt_log": col["attempts"], "relations": col["relations"],
                   "peak_rss_bytes": rss_s1},
        "stage3": {"rank_tracking_cost": col["rank_cost"], "rank_log": col["rank_log"], "la_cost": sol["cost"],
                   "la_log": sol["log"], "units": _sum_units(col["rank_cost"], sol["cost"]),
                   "log_verification": ver, "peak_rss_bytes": rss_bytes()},
        "peak_rss_bytes": rss_bytes(), "seconds": round(time.time() - t0, 3),
    }


def run_stage_cost(fx, ns, m, n_heldout=common.N_HELDOUT, max_attempts=DEFAULT_MAX_ATTEMPTS, log_fn=print):
    _ns_guard(ns, fx)
    t0 = time.time()
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    k = target_k(fx, ns)
    Q = vc.mul(k, tuple(fx["G"]))
    fb = interval_fb(fx, m)
    table = ForwardTable(fx, fb)
    col = collect(fx, ns, fb, table, Q, m, max_attempts)
    rss_s1 = rss_bytes()
    stage1_units = _sum_units(fb.cost, table.cost, col["stage1_attempt_cost"])
    sol = la_solve(fx, ns, fb, col["relations"], f"interval_m{m}")
    ver = verify_logs(fx, fb, sol["x"], Q)
    if sol["error"] or not ver["all_ok"]:
        raise ProcedureDefect(f"m={m} LA/log verification failed: {sol['error']} {ver}")
    s2 = stage2(fx, ns, fb, n_heldout)
    log_fn(f"[{common.fixture_id(fx)} stage_cost m={m}] attempts={col['n_attempts']} L={fb.L}")
    return {
        "kind": f"stage_cost_m{m}", "fixture": fx, "fixture_id": common.fixture_id(fx), "namespace": ns, "m": m,
        "factor_base": fb.summary(),
        "forward_table": {"size": table.size, "n_pairs": table.n_pairs, "cost": table.cost},
        "stage1": {"n_attempts": col["n_attempts"],
                   "n_failed_attempts": col["n_failed"],
                   "n_relations": len(col["relations"]),
                   "cost": {"fb_construction": fb.cost, "forward_table": table.cost,
                            "attempts": col["stage1_attempt_cost"]},
                   "units": stage1_units, "attempt_log": col["attempts"], "relations": col["relations"],
                   "peak_rss_bytes": rss_s1},
        "stage3": {"rank_tracking_cost": col["rank_cost"], "rank_log": col["rank_log"], "la_cost": sol["cost"],
                   "la_log": sol["log"], "units": _sum_units(col["rank_cost"], sol["cost"]),
                   "log_verification": ver, "peak_rss_bytes": rss_bytes()},
        "stage2_alpha2": s2,
        "peak_rss_bytes": rss_bytes(), "seconds": round(time.time() - t0, 3),
    }


def run_rho_cell(fx, ns, n_targets=common.N_RHO_TARGETS, log_fn=print):
    import rho
    _ns_guard(ns, fx)
    t0 = time.time()
    r = rho.run_rho(fx, ns, n_targets)
    bad = [x["t"] for x in r["targets"] if not x.get("solved") or not x.get("k_true_matches")]
    if bad:
        raise ProcedureDefect(f"rho targets unsolved/mismatched: {bad}")
    log_fn(f"[{common.fixture_id(fx)} rho] targets={n_targets}")
    return {"kind": "rho", "fixture": fx, "fixture_id": common.fixture_id(fx), "namespace": ns, **r,
            "peak_rss_bytes": rss_bytes(), "seconds": round(time.time() - t0, 3)}

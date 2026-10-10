"""EXP-PFDR-0b3699 analysis (TASK-20261002-8a6b8a).  Imports NO crypto_autoresearcher module.

Subcommands (AR-2; writer table of required_artifacts.per_run_data):

  p0         RA-03: P0X-A (CC-1..CC-3 recount of the archived EXP-PFDR-011cd0 R12 TT4 random-arm
             and known-null counts, compared as integers, AR-4 included), G-FRESH, rho1_hat_b and
             D_plan from the P0 inputs by path and field, the G-NB-R simulation of the single cell
             (t_A_plan, powers at kappa 1.10 and 1.097, contrast power), the P0 RULE, predicted
             X_rel and U_A at kappa = 1, K_plant_b and S, the height-screen list, the jobs, the
             design stops -> design.json, power.json, p0x-a-report.json.
  checks     RA-04 after the merge: verify_rows.py by path (--out /dev/stdout, parsed in memory)
             -> row-verify.json; G4, G7, G-CURVE, G-REL, G7-OFFSET, PC-R-iii -> checks-report.json.
             Per-check pass, per-instance PASS/FAIL and mismatch keys only (stopping_rules [5]).
  calibrate  RA-05: null arms only (lines filtered by arm name before any parse;
             arm-read-log.json): rho1_hat_b, D_b, G-NB-R t_A, permutation null t_perm, t_dec,
             t_Delta, PC-NULL-R, H1c dispersion, predicted X_rel, U-coverage -> calibration.json,
             arm-read-log.json, view-map.json.
  unmask     RA-06: refuses unless calibration.json matches the pinned sha256; every declared
             metric, the outcome id -> analysis.json, cells.jsonl, view-map.json.

The relation recount follows the CC-1..CC-3 clauses of EXP-PFDR-011cd0 counting_conventions
and shares no code with harvest.py.  The simulation rule of analysis.upper_bound_U_A is
implemented from its text.  Nothing here interprets a result beyond the frozen outcome table.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict

import numpy as np

REPO = "/home/user/crypto-autoresearcher"
EXP = "EXP-PFDR-0b3699"
EXPDIR = f"experiments/{EXP}"
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
TOKEN = 0x0B3699
VERIFY_ROWS = "experiments/EXP-PFDR-011cd0/verify_rows.py"

ARCH_JOBS = "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs"
ARCH_CAL = "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-calibrate/calibration.json"
ARCH_ANA = "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-analysis/analysis.json"
ARCH_DESIGN = "experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"
LOCALISE = ("coordination/review/pfdr-011cd0-20261002/reviews/TASK-20261002-87ffc4/attacks/j6/out/"
            "smallx-tt4-localise.json")
SIZING = ("coordination/review/pfdr-011cd0-20261002/reviews/TASK-20261002-87ffc4/attacks/j6/out/"
          "replication-sizing.json")
REDTEAM = "coordination/review/pfdr-011cd0-20261002/reviews/TASK-20261002-87ffc4/red-team-report.yaml"

NULL_ARMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub")
RANDOMS = NULL_ARMS[:3]
STRUCT_ARMS = ("subgroup", "small_x", "planted_sub", "small_x_offset")
FAMILY_ARMS = ("subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
               "known_null_sub", "planted_sub", "small_x_offset")
RUNGS = (30, 32)
DECLARED_N = 3400
C0 = 2010
C_MAX = 9999
JOB_CURVES = 100
MULTIPLIERS = (1.0, 1.25, 1.5, 2.0)
KAPPA_TARGET = 1.15
KAPPA_POWER = 1.10
KAPPA_POWER_OBS = 1.097
RHO_D_UPPER = 1.307
D_PLAN_FACTOR = 1.2
ALPHA_ONE_SIDED = 0.01
X_GRID = [round(1.00 + 0.01 * i, 2) for i in range(31)]
COVERAGE_KAPPAS = (1.00, 1.10, 1.15)
COVERAGE_FLOOR = 0.945
FAMILIES = 5
PROD_REPS = 20000
PROD_DESIGNS = 4000
CHUNK = 200
HEIGHT_FRACTION_STOP = 0.01
PACKAGE_GUARD_BYTES = 1.0 * 1024 ** 3

# ------------------------------------------------------------------------------------------
# io


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def absp(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def rel(p: str) -> str:
    return os.path.relpath(absp(p), REPO)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(absp(path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class ViewMap:
    """Every file a step reads, by repository-relative path and sha256 (AR-2 (4))."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def note(self, path: str) -> str:
        p = absp(path)
        self.files[rel(p)] = sha256(p)
        return p

    def as_list(self) -> list[dict]:
        return [{"path": k, "sha256": v} for k, v in sorted(self.files.items())]


def read_jsonl(path: str):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def iter_lines(path: str):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield line


def write_json(path: str, obj, indent: int | None = 1) -> str:
    p = absp(path)
    if os.path.exists(p):
        raise SystemExit(f"refusing: {rel(p)} exists (records are immutable)")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        json.dump(obj, fh, indent=indent, default=_json_default)
    return sha256(p)


def write_jsonl(path: str, recs) -> str:
    p = absp(path)
    if os.path.exists(p):
        raise SystemExit(f"refusing: {rel(p)} exists (records are immutable)")
    with open(p, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r, default=_json_default) + "\n")
    return sha256(p)


def _json_default(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def load_yaml(path: str):
    import yaml
    return yaml.safe_load(open(absp(path)))


def ikey(bits, curve, m, arm, mode) -> str:
    return json.dumps([bits, curve, m, arm, mode])


def row_m(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


# ------------------------------------------------------------------------------------------
# CC-1 .. CC-3 relation recount (written from the clauses; shares no code with harvest.py)

_KCOORD = 10 ** 12      # kcoef coordinate: after every base index
_RCOORD = 10 ** 12 + 1  # rhs coordinate: after kcoef


def _row_vector(h: dict, N: int) -> dict:
    """A star row as the integer vector (c_1..c_|F|, kcoef, rhs), reduced mod N."""
    v: dict = {}
    for i, c in h["coeffs"]:
        c %= N
        if c:
            v[int(i)] = (v.get(int(i), 0) + c) % N
    v = {i: c for i, c in v.items() if c}
    if h["kcoef"] % N:
        v[_KCOORD] = h["kcoef"] % N
    if h["rhs"] % N:
        v[_RCOORD] = h["rhs"] % N
    return v


def _difference(u: dict, w: dict, N: int) -> dict:
    d = dict(u)
    for i, c in w.items():
        x = (d.get(i, 0) - c) % N
        if x:
            d[i] = x
        else:
            d.pop(i, None)
    return d


def _monic(v: dict, N: int):
    """CC-1: multiply by the inverse mod N of the first nonzero coordinate (base indices
    ascending, then kcoef, then rhs).  None for the zero vector (a formal duplicate)."""
    if not v:
        return None
    items = sorted(v.items())
    inv = pow(items[0][1], -1, N)
    return tuple((i, c * inv % N) for i, c in items)


def _sign_only(v: dict, N: int):
    """CC-1b: the lexicographically smaller of v and -v mod N (coordinates in CC-1 order)."""
    items = sorted(v.items())
    neg = tuple((i, (-c) % N) for i, c in items)
    pos = tuple(items)
    return min(pos, neg, key=lambda t: [c for _, c in t])


def recount_class(hrows: list[dict], N: int, cls: str, keep_keys: bool = False) -> dict:
    """CC-1..CC-3 for one (instance, class, scope = whole table).

    x-groups are the star rows sharing their first element.  The pair (1, j) carries row_j;
    for TT the pair (i, j), 2 <= i < j, carries row_j - row_i; TB pairs are the (base, tail)
    star pairs only (implementation-notes PDI-3).  CC-2: the formal basis of every arm of
    this experiment is empty, so every nonzero relation is nonformal."""
    groups: dict = {}
    for h in hrows:
        if h["class"] != cls:
            continue
        gid = json.dumps(h["elements"][0], sort_keys=True)
        groups.setdefault(gid, []).append(_row_vector(h, N))
    mult: dict = {}
    sign: set = set()
    star: set = set()
    pairs = zero = 0
    for rows in groups.values():
        for j, rj in enumerate(rows):
            rels = [rj]
            if cls != "TB":
                rels += [_difference(rj, ri, N) for ri in rows[:j]]
            for idx, r in enumerate(rels):
                pairs += 1
                key = _monic(r, N)
                if key is None:
                    zero += 1
                    continue
                mult[key] = mult.get(key, 0) + 1
                sign.add(_sign_only(r, N))
                if idx == 0:
                    star.add(key)
    hist = Counter(mult.values())
    out = {"relations_distinct": len(mult), "relations_distinct_sign": len(sign),
           "relations_nonformal": len(mult), "R_star": len(star),
           "multiplicity_histogram": {str(k): hist[k] for k in sorted(hist)},
           "relation_pairs": pairs, "relation_pairs_zero": zero,
           "star_groups": len(groups),
           "star_groups_with_ge2_star_rows": sum(1 for g in groups.values() if len(g) >= 2)}
    if keep_keys:
        out["keys"] = set(mult)
    return out


def planted_tt_keys(fb_params: dict, N: int) -> list:
    out = []
    for r in fb_params.get("planted_relations") or []:
        if r["class"] == "TT":
            out.append(_monic({int(i): s % N for i, s in zip(r["indices"], r["signs"])}, N))
    return out


# ------------------------------------------------------------------------------------------
# model means and NB machinery

def mu_model(s: int, N: int) -> float:
    """L1 first moment with generic multiplicity 3 (L2): T (T - 1) / (3 N), T = s^2 (PDI-1)."""
    T = s * s
    return T * (T - 1) / (3 * N)


def nb_draw(rng, mean, D: float, size):
    """Per-curve count with the given mean and index of dispersion D (D = 1: Poisson)."""
    if D <= 1.0 + 1e-12:
        return rng.poisson(mean, size=size)
    return rng.negative_binomial(np.asarray(mean) / (D - 1.0), 1.0 / D, size=size)


class Model:
    """Curves of the simulated design, ordered by rung, with null means m_j and D per rung.

    parts: disjoint curve sets, each within one rung: (rung, name, boolean mask).  Every
    simulated total is drawn and accumulated per part (implementation-notes PDI-5)."""

    def __init__(self, rung: np.ndarray, m: np.ndarray, D: dict, parts: list):
        self.rung = rung
        self.m = m.astype(float)
        self.D = {int(b): float(v) for b, v in D.items()}
        self.parts = parts
        self.P = np.zeros((len(m), len(parts)))
        for k, (_, _, mask) in enumerate(parts):
            self.P[mask, k] = 1.0
        self.part_rung = [int(b) for b, _, _ in parts]
        self.msum = self.m @ self.P
        self.slices = {}
        for b in sorted(set(int(x) for x in rung)):
            idx = np.nonzero(rung == b)[0]
            assert idx.size and np.all(np.diff(idx) == 1), "curves must be ordered by rung"
            self.slices[b] = slice(int(idx[0]), int(idx[-1]) + 1)

    def part_index(self, names) -> list[int]:
        return [k for k, (_, nm, _) in enumerate(self.parts) if nm in names]


def triples_for(n_arms: int) -> list[tuple]:
    if n_arms == 3:
        return [(0, 1, 2)]
    return [tuple(a for a in range(4) if a != e) for e in range(4)]


def make_bank(model: Model, R: int, n_arms: int, seed_seq) -> dict:
    """R replicates of per-curve null draws of n_arms arms (r0, r1, r2[, kn]); per part:
    totals T[r, part, arm] and 6 x sum of ddof-1 variances S6[r, part, triple]."""
    rng = np.random.default_rng(seed_seq)
    nparts = len(model.parts)
    T = np.zeros((R, nparts, n_arms))
    trip = triples_for(n_arms)
    S6 = np.zeros((R, nparts, len(trip)))
    n = len(model.m)
    for c0 in range(0, R, CHUNK):
        B = min(CHUNK, R - c0)
        X = np.empty((B, n, n_arms), dtype=np.int64)
        for b, sl in model.slices.items():
            mm = model.m[sl][None, :, None]
            X[:, sl, :] = nb_draw(rng, np.broadcast_to(mm, (B, sl.stop - sl.start, n_arms)),
                                  model.D[b], (B, sl.stop - sl.start, n_arms))
        Xf = X.astype(float)
        T[c0:c0 + B] = np.einsum("bna,nk->bka", Xf, model.P)
        for t, tr in enumerate(trip):
            Y = Xf[:, :, list(tr)]
            six = 3.0 * (Y * Y).sum(axis=2) - Y.sum(axis=2) ** 2
            S6[c0:c0 + B, :, t] = six @ model.P
    return {"T": T, "S6": S6, "n_arms": n_arms, "R": R}


def cell_from_bank(bank: dict, parts: list[int], struct_arm: int | None, CX=None):
    """z, kappa, SE per replicate of a pseudo-cell over `parts`.  struct_arm: the bank arm
    scored as structured (its triple is the other three); None: CX (array) scored against the
    randoms r0..r2."""
    T, S6 = bank["T"][:, parts, :].sum(axis=1), bank["S6"][:, parts, :].sum(axis=1)
    if bank["n_arms"] == 3:
        CR = T[:, :3].sum(axis=1) / 3.0
        S2 = S6[:, 0] / 6.0
    else:
        e = 3 if struct_arm is None else struct_arm
        others = [a for a in range(4) if a != e]
        CR = T[:, others].sum(axis=1) / 3.0
        S2 = S6[:, e] / 6.0
        if struct_arm is not None:
            CX = T[:, struct_arm]
    V = np.maximum(S2, CR)
    SD = np.sqrt(4.0 * V / 3.0)
    z = (CX - CR) / SD
    with np.errstate(divide="ignore", invalid="ignore"):
        kap = CX / CR
        se = SD / CR
    return z, kap, se, CR, V


def rand_parts_stats(bank: dict, parts: list[int]):
    """C_R and V of the randoms r0..r2 over parts."""
    T, S6 = bank["T"][:, parts, :].sum(axis=1), bank["S6"][:, parts, :].sum(axis=1)
    CR = T[:, :3].sum(axis=1) / 3.0
    S2 = (S6[:, 0] if bank["n_arms"] == 3 else S6[:, 3]) / 6.0
    return CR, np.maximum(S2, CR)


def struct_totals(rng, model: Model, R: int, kappa: float, mode: str, parts: list[int],
                  rho_upper: float = RHO_D_UPPER) -> np.ndarray:
    """Structured-arm total over `parts` per replicate, by the analysis.upper_bound_U_A
    SIMULATION RULE: null draw from G-NB-R; kappa > 1: plus a Poisson-planted excess
    ((kappa - 1) m) or, mode compound, the arm drawn with mean kappa m and dispersion
    rho_upper x D; kappa = 1: the null draw as drawn; kappa < 1: Binomial(null draw, kappa).
    Drawn per rung over the union of the rung's parts (sums of NB with common p; PDI-5)."""
    out = np.zeros(R)
    by_rung: dict = {}
    for k in parts:
        by_rung[model.part_rung[k]] = by_rung.get(model.part_rung[k], 0.0) + float(model.msum[k])
    for b in sorted(by_rung):
        msum = by_rung[b]
        if msum <= 0:
            continue
        D = model.D[b]
        if mode == "compound" and kappa > 1:
            out += nb_draw(rng, kappa * msum, rho_upper * D, R)
            continue
        null = nb_draw(rng, msum, D, R)
        if kappa > 1:
            out += null + rng.poisson((kappa - 1.0) * msum, R)
        elif kappa == 1:
            out += null
        else:
            out += rng.binomial(null, kappa)
    return out


def fam_seq(f: int) -> list:
    """Children of SeedSequence([0x0b3699, f]): [bank, struct, xrel, cov_designs, cov_bounds,
    obs_bound, contrast, spare]."""
    return np.random.SeedSequence([TOKEN, f]).spawn(8)


SEQ_NAMES = ["bank", "struct", "xrel", "cov_designs", "cov_bounds", "obs_bound", "contrast", "spare"]


def q_bounds_at(stats: list, model: Model, parts: list[int], kappa_hat: float, rngs: list,
                R: int) -> tuple[float, float]:
    """(q_lo, q_abs): family-averaged 0.05 quantile of signed dev and 0.95 quantile of |dev|,
    dev = (kappa* - kappa_hat) / SE*, under G-NB-R with the structured arm at kappa_hat."""
    qlo, qab = [], []
    for f, (CR, V) in enumerate(stats):
        A = struct_totals(rngs[f], model, R, kappa_hat, "poisson", parts)
        se = np.sqrt(4.0 * V / 3.0) / CR
        dev = (A / CR - kappa_hat) / se
        qlo.append(float(np.quantile(dev, 0.05)))
        qab.append(float(np.quantile(np.abs(dev), 0.95)))
    return float(np.mean(qlo)), float(np.mean(qab))


def synth_designs(model: Model, parts: list[int], kappas, n_designs: int, seq) -> dict:
    """n_designs synthetic designs: per-curve randoms r0..r2 (shared across kappas, common
    random numbers) and the structured total at each kappa.  Returns kappa_hat, SE per kappa."""
    s_rand, s_struct = seq.spawn(2)
    rng = np.random.default_rng(s_struct)
    rb = make_bank(model, n_designs, 3, s_rand)
    CR, V = rand_parts_stats(rb, parts)
    out = {}
    for kap in kappas:
        A = struct_totals(rng, model, n_designs, kap, "poisson", parts)
        out[kap] = {"kappa_hat": A / CR, "se": np.sqrt(4.0 * V / 3.0) / CR}
    return out


def coverage(banks: list, model: Model, parts: list[int], kappas, n_designs: int, R: int) -> dict:
    """One-sided coverage of the signed-quantile bound and of the |dev| bound, each design's
    own bound computed by the analysis.upper_bound_U_A rule (PDI-6)."""
    per_fam = n_designs // FAMILIES
    stats = [rand_parts_stats(bk, parts) for bk in banks]
    res = {k: {"signed": [], "absdev": [], "bounds_signed": []} for k in kappas}
    for f in range(FAMILIES):
        seqs = fam_seq(f)
        syn = synth_designs(model, parts, kappas, per_fam, seqs[3])
        brng = [np.random.default_rng(s) for s in
                [fam_seq(g)[4].spawn(FAMILIES)[f] for g in range(FAMILIES)]]
        for kap in kappas:
            kh, se = syn[kap]["kappa_hat"], syn[kap]["se"]
            for i in range(per_fam):
                qlo, qab = q_bounds_at(stats, model, parts, float(kh[i]), brng, R)
                u_s = kh[i] - qlo * se[i]
                u_a = kh[i] + qab * se[i]
                res[kap]["signed"].append(bool(u_s >= kap))
                res[kap]["absdev"].append(bool(u_a >= kap))
                res[kap]["bounds_signed"].append(float(u_s))
    out = {}
    for kap in kappas:
        bs = np.array(res[kap]["bounds_signed"])
        out[f"{kap:.2f}"] = {"designs": len(bs),
                             "coverage_signed": float(np.mean(res[kap]["signed"])),
                             "coverage_absdev": float(np.mean(res[kap]["absdev"])),
                             "U_signed_median": float(np.median(bs)),
                             "U_signed_q05": float(np.quantile(bs, 0.05)),
                             "U_signed_q95": float(np.quantile(bs, 0.95)),
                             "U_signed_fraction_le_1.15": float(np.mean(bs <= KAPPA_TARGET))}
    return out


def x_rel(banks: list, model: Model, parts: list[int], t: float, R: int, D_rho: float) -> dict:
    out = {}
    for mode in ("poisson", "compound"):
        powers = {}
        for kap in X_GRID:
            hits = 0
            for f, bank in enumerate(banks):
                rng = np.random.default_rng(fam_seq(f)[2].spawn(len(X_GRID) * 2)[
                    X_GRID.index(kap) * 2 + (mode == "compound")])
                CR, V = rand_parts_stats(bank, parts)
                A = struct_totals(rng, model, R, kap, mode, parts, D_rho)
                hits += int(np.sum((A - CR) / np.sqrt(4.0 * V / 3.0) > t))
            powers[f"{kap:.2f}"] = hits / (R * len(banks))
        first = next((k for k in X_GRID if powers[f"{k:.2f}"] >= 0.5), None)
        out[mode] = {"X_rel": first if first is not None else "X_rel > 1.30", "power_grid": powers}
    vals = [out[m]["X_rel"] for m in ("poisson", "compound")]
    out["X_rel"] = ("X_rel > 1.30" if any(isinstance(v, str) for v in vals) else max(vals))
    out["rule"] = ("smallest kappa on 1.00..1.30 (step 0.01) with simulated P(z > t) >= 0.5; "
                   "Poisson- and compound-planted (A dispersion 1.307 x D); the larger reported; "
                   "'X_rel > 1.30' when no grid point reaches 0.5")
    return out


def quant_avg(values_per_family: list[np.ndarray], q: float) -> tuple[float, list[float]]:
    per = [float(np.quantile(v, q)) for v in values_per_family]
    return float(np.mean(per)), per


# ------------------------------------------------------------------------------------------
# p0 (RA-03)

def p0x_a(vm: ViewMap, jobs_dir: str, arch_cal: dict, rungs) -> dict:
    """P0X-A (and AR-4): integer recount of the archived R12 TT4 random-arm and known-null
    relation counts at 30 and 32 bits."""
    counts: dict = defaultdict(dict)      # (bits, curve) -> arm -> n
    status: dict = defaultdict(dict)
    Ns: dict = {}
    files = []
    sub_family = ("subgroup", "small_x") + NULL_ARMS
    for b in rungs:
        names = sorted(n for n in os.listdir(absp(jobs_dir)) if n.startswith(f"4-b{b}-c"))
        for name in names:
            jd = os.path.join(absp(jobs_dir), name)
            rp = vm.note(os.path.join(jd, "rows.jsonl.gz"))
            hp = vm.note(os.path.join(jd, "harvest-rows.jsonl.gz"))
            files.append(rel(jd))
            for r in read_jsonl(rp):
                if r.get("mode") == "table" and row_m(r) == 4 and r.get("arm") in sub_family:
                    status[(r["bits"], r["curve"])][r["arm"]] = r.get("status")
                    Ns[(r["bits"], r["curve"])] = r["N"]
            by_inst: dict = defaultdict(list)
            for h in read_jsonl(hp):
                if h["arm"] in NULL_ARMS and h["m"] == 4 and h["mode"] == "table":
                    by_inst[(h["bits"], h["curve"], h["arm"])].append(h)
            for (bits, c, arm), hs in by_inst.items():
                counts[(bits, c)][arm] = recount_class(hs, Ns[(bits, c)], "TT")["relations_nonformal"]
    used = sorted(k for k, st in status.items()
                  if all(st.get(a) == "completed_valid" for a in sub_family))
    three_CR = six_s2 = CA = 0
    for k in used:
        n = [counts[k].get(a, 0) for a in RANDOMS]
        three_CR += sum(n)
        six_s2 += 3 * sum(x * x for x in n) - sum(n) ** 2
        CA += counts[k].get("known_null_sub", 0)
    cell = arch_cal["PC_NULL"]["known_null_band_cells"]["known_null_sub|TT4|band"]
    arch = {"3xC_R": round(3 * cell["C_R"]), "6xsum_s2": round(6 * cell["sum_s2"]),
            "C_A": round(cell["C_A"])}
    mine = {"3xC_R": three_CR, "6xsum_s2": six_s2, "C_A": CA}
    pairs = {k: {"recount": mine[k], "archived_rounded": arch[k], "equal": mine[k] == arch[k]}
             for k in arch}
    return {"gate": "P0X-A", "pass": all(p["equal"] for p in pairs.values()),
            "rule": ("analyze_a.py CC-1..CC-3 recount of the archived R12 TT4 random-arm and known-null "
                     "counts at 30 and 32 bits; 3 x C_R, 6 x sum_s2 (P0X-A) and C_A (AR-4) compared as "
                     "integers, archived values rounded to the nearest integer; no float compared"),
           "integer_pairs": pairs,
           "archived_values_as_read": {"C_R": cell["C_R"], "sum_s2": cell["sum_s2"], "C_A": cell["C_A"],
                                       "curves_used": cell.get("curves_used")},
           "curves_used": len(used),
           "curves_used_by_rung": {str(b): sum(1 for k in used if k[0] == b) for b in rungs},
           "rule_curves": "curves whose SUB-family arms (subgroup, small_x, r0, r1, r2, known_null_sub) are all completed_valid (CC-6)",
           "job_dirs_read": files}


def cmd_p0(a) -> int:
    t_start = time.time()
    vm = ViewMap()
    out_dir = absp(a.out_dir)
    fixture = a.fixture
    if not fixture and (a.reps < PROD_REPS or a.designs < PROD_DESIGNS):
        raise SystemExit("replicates below the frozen minimum outside --fixture")
    curves_all = list(read_jsonl(vm.note(a.curves)))
    arch_cal = json.load(open(vm.note(a.arch_calibration)))
    arch_ana = json.load(open(vm.note(a.arch_analysis)))
    arch_design = json.load(open(vm.note(a.arch_design)))
    localise = json.load(open(vm.note(a.localise)))
    sizing = json.load(open(vm.note(a.sizing)))
    redteam = load_yaml(vm.note(a.redteam))
    started = now()
    # -- P0 inputs by path and field
    groups = {tuple(g["key"]): g for g in arch_cal["generators"]["G-NB-R"]["groups"]}
    a_curves = {(c["bits"], c["curve"]): c for c in arch_design["curves"]}
    rho1, D_in, inputs_read = {}, {}, {}
    for b in a.rungs:
        g = groups[("SUB", "TT", 4, b)]
        mus = [mu_model(a_curves[(b, c)]["sizes"]["4"]["s_sub"], a_curves[(b, c)]["N"]) for c in g["curves"]]
        rho1[b] = float(sum(g["mj"]) / sum(mus))
        D_in[b] = float(g["D"])
        inputs_read[f"G-NB-R[SUB,TT,4,{b}]"] = {"D": g["D"], "sum_mj": float(sum(g["mj"])),
                                                 "curves": len(g["curves"]),
                                                 "sum_mu_model_011cd0_curves": float(sum(mus))}
    D_plan = max(D_in.values()) * D_PLAN_FACTOR
    sx = arch_ana["A_INT"]["small_x|TT4|band"]
    inputs_read["A_INT[small_x|TT4|band]"] = {"SE": sx["SE"], "q_one_sided_095": sx["q"]["q_one_sided_095"],
                                              "upper95_one_sided": sx["upper95_one_sided"],
                                              "kappa_rel": sx["kappa_rel"]}
    inputs_read["localise C_R"] = {str(b): localise[f"small_x|{b}"]["C_R"] for b in a.rungs}
    inputs_read["sizing"] = {k: sizing["cells"]["small_x|TT4|band"].get(k) for k in
                             ("curves_power0.8_at_1.100_alpha_0.01_single_test",
                              "curves_power0.9_at_1.100_alpha_0.01_single_test")}
    inputs_read["red_team J4 d_dispersion"] = redteam["red_team_report"]["joints"]["J4"]["computation"]["d_dispersion"]
    # -- P0X-A
    p0x = p0x_a(vm, a.arch_jobs, arch_cal, a.rungs)
    p0x["created_at"] = now()
    design_stop = []
    if not p0x["pass"]:
        design_stop.append("P0X-A failed")
    # -- candidate curves -> declared and final n
    by_rung = {b: [c for c in curves_all if c["bits"] == b] for b in a.rungs}
    for b in a.rungs:
        by_rung[b].sort(key=lambda c: c["curve"])
        cs = [c["curve"] for c in by_rung[b]]
        if cs != list(range(a.c0, a.c0 + len(cs))):
            raise SystemExit(f"curves.jsonl.gz rung {b} is not the contiguous range from c0")
    arch_pab = {(c["p"], c["a"], c["b"]) for c in arch_design["curves"]}
    rule_evals = []
    chosen = None
    power_detail = {}
    if p0x["pass"]:
        for mult in MULTIPLIERS:
            n_b = int(round(a.declared_n * mult))
            if any(n_b > len(by_rung[b]) for b in a.rungs):
                raise SystemExit("candidate curves do not cover the multiplier")
            ev, ctx = p0_evaluate(by_rung, a.rungs, n_b, rho1, D_plan, a.reps)
            rule_evals.append({"multiplier": mult, "n_b": n_b, **{k: ev[k] for k in (
                "t_A_plan", "t_Delta_plan", "power_1.10", "power_contrast", "meets")}})
            power_detail[f"{mult}"] = ev
            if ev["meets"] or mult == MULTIPLIERS[-1]:
                chosen = (mult, n_b, not ev["meets"])
                final_ctx = (ev, ctx)
                break
    else:
        chosen = (1.0, a.declared_n, False)
    mult, n_b, unattainable = chosen
    final = {b: by_rung[b][:n_b] for b in a.rungs}
    # -- G-FRESH on the final design
    fresh_bad_range = [[c["bits"], c["curve"]] for b in a.rungs for c in final[b]
                       if not (C0 <= c["curve"] <= C_MAX)]
    fresh_bad_pab = [[c["bits"], c["curve"]] for b in a.rungs for c in final[b]
                     if (c["p"], c["a"], c["b"]) in arch_pab]
    g_fresh = {"gate": "G-FRESH", "pass": not fresh_bad_range and not fresh_bad_pab,
               "range_violations": fresh_bad_range, "pab_collisions": fresh_bad_pab,
               "compared_against": rel(a.arch_design), "archived_curves": len(arch_pab)}
    if not g_fresh["pass"]:
        design_stop.append("G-FRESH failed")
    # -- final-n evaluation with predictions
    final_eval = None
    if p0x["pass"]:
        final_eval = p0_predict(*final_ctx, a.reps, a.designs)
    # -- planted, height screen, K_plant, S
    planted_errors = [[c["bits"], c["curve"], c["planted"]["error"]] for b in a.rungs for c in final[b]
                      if not c["planted"]["ok"]]
    if planted_errors:
        design_stop.append("planted_sub cannot plant on some curve (ValueError)")
    height = {str(b): [c["curve"] for c in final[b] if c["height_screen_hits"]] for b in a.rungs}
    for b in a.rungs:
        if len(height[str(b)]) > HEIGHT_FRACTION_STOP * n_b:
            design_stop.append(f"height-screen list exceeds 1% of rung {b}'s curves")
    mu_loc = {b: localise[f"small_x|{b}"]["C_R"] / localise[f"small_x|{b}"]["curves"] for b in a.rungs}
    K_plant = {str(b): int(round(0.15 * n_b * mu_loc[b])) for b in a.rungs}
    S = {}
    for b in a.rungs:
        cs = [c["curve"] for c in final[b]]
        S[str(b)] = sorted(random.Random(f"plant-target|EXP-PFDR-0b3699|{b}").sample(cs, n_b)[:K_plant[str(b)]])
    # -- jobs
    jobs = []
    for b in a.rungs:
        for c0 in range(a.c0, a.c0 + n_b, JOB_CURVES):
            k = min(JOB_CURVES, a.c0 + n_b - c0)
            jobs.append({"job": f"4-b{b}-c{c0}", "bits": b, "c0": c0, "curves": k,
                         "arms": list(FAMILY_ARMS)})
    # -- expected disk and CPU (modeled)
    inst = len(FAMILY_ARMS) * n_b * len(a.rungs)
    disk = {"bytes_modeled": inst * 1500 + 5e7, "per_instance_bytes_modeled": 1500,
            "label": ("modeled, not measured: about 0.5 kB per instance for each of census rows, "
                      "harvest rows + staircases, bases samples (specification budget.expected_disk), "
                      "plus 50 MB for checks and analysis outputs")}
    if disk["bytes_modeled"] > PACKAGE_GUARD_BYTES:
        design_stop.append("expected package exceeds 1.0 GB")
    cpu = {"cpu_seconds_modeled": inst * 0.089 * 1.0,
           "label": "modeled, not measured: 0.089 CPU s per instance (EXP-PFDR-011cd0 R12 rate, specification budget)"}
    curves_out = []
    for b in a.rungs:
        for c in final[b]:
            curves_out.append({k: c[k] for k in ("bits", "curve", "p", "a", "b", "N", "P", "size0", "F_sub",
                                                 "s_sub", "subgroup_d", "mu_model", "x0", "offset_bound")}
                              | {"height_screened": bool(c["height_screen_hits"]),
                                 "planted_n_tt": c["planted"]["n_tt"]})
    design = {
        "what": "EXP-PFDR-0b3699 P0 design (RA-03)", "created_at": now(), "started_at": started,
        "rungs": list(a.rungs),
        "fixture": fixture, "writer": "analyze_a.py p0",
        "declared_n_b": a.declared_n, "final_n_b": n_b, "multiplier": mult,
        "rule_raised": mult != 1.0, "target_unattainable_by_design": unattainable,
        "rule_evaluations": rule_evals,
        "rho1_hat_b": {str(b): rho1[b] for b in a.rungs},
        "D_in_b": {str(b): D_in[b] for b in a.rungs}, "D_plan": D_plan,
        "t_A_plan": final_eval["t_A_plan"] if final_eval else None,
        "t_Delta_plan": final_eval["t_Delta_plan"] if final_eval else None,
        "predicted_powers": ({k: final_eval[k] for k in ("power_1.10", "power_1.097", "power_contrast")}
                             if final_eval else None),
        "predicted_X_rel": final_eval["X_rel"] if final_eval else None,
        "predicted_U_A_at_kappa_1": final_eval["U_A_at_1"] if final_eval else None,
        "gaussian_planning_figures": {"curves_power0.8_at_1.100_alpha_0.01_single_test": 5244,
                                      "curves_power0.9_at_1.100_alpha_0.01_single_test": 6801,
                                      "label": "replication-sizing.json, Gaussian approximation; planning only"},
        "simulated_requirement": {"pooled_curves": 2 * n_b, "multiplier": mult,
                                  "meets_both_targets": not unattainable},
        "K_plant_b": K_plant, "mu_b_localise": {str(b): mu_loc[b] for b in a.rungs},
        "S": S, "height_screen": height,
        "height_screen_rule": "x * v mod p in [-2^12, 2^12] for some v in 1..16; curve dropped from M and the contrast only",
        "planted_errors": planted_errors,
        "x0_rule": "random.Random(f'fb-smallx-offset|{p}|{a}|{b}|{s_sub}|{c + 9000}').randrange(p // 2) + p // 4 (design_a.py)",
        "curves": curves_out, "jobs": jobs,
        "expected_disk": disk, "expected_cpu": cpu,
        "G-FRESH": g_fresh, "P0X-A_pass": p0x["pass"],
        "design_stop": design_stop,
        "inputs_read": inputs_read, "view_map": vm.as_list(),
        "simulation": {"generator": "G-NB-R at the design curves: means rho1_hat_b x mu_model(j), dispersion D_plan",
                       "families": FAMILIES, "reps_per_family": a.reps, "designs": a.designs,
                       "seed_rule": "SeedSequence([0x0b3699, family]).spawn(8) children " + str(SEQ_NAMES)},
    }
    power = {"what": "EXP-PFDR-0b3699 P0 power (RA-03)", "created_at": now(), "fixture": fixture,
             "writer": "analyze_a.py p0", "evaluations": power_detail, "final": final_eval,
             "note": ("powers at kappa 1.097 are recorded with no target attached (power_analysis.target); "
                      "powers at a post-selection estimate overstate power at the truth")}
    os.makedirs(out_dir, exist_ok=True)
    write_json(os.path.join(out_dir, "p0x-a-report.json"), p0x)
    write_json(os.path.join(out_dir, "power.json"), power)
    dsha = write_json(os.path.join(out_dir, "design.json"), design)
    print(json.dumps({"P0X-A": p0x["pass"], "G-FRESH": g_fresh["pass"], "final_n_b": n_b,
                      "multiplier": mult, "unattainable": unattainable, "design_stop": design_stop,
                      "design_sha256": dsha, "seconds": round(time.time() - t_start, 1)}))
    return 0 if not design_stop else 1


def p0_model(by_rung: dict, rungs, n_b: int, rho1: dict, D: float, adm_exclude: set) -> Model:
    rung, m, parts = [], [], []
    for b in rungs:
        for c in by_rung[b][:n_b]:
            rung.append(b)
            m.append(rho1[b] * c["mu_model"])
    rung = np.array(rung)
    curves = [(b, c["curve"]) for b in rungs for c in by_rung[b][:n_b]]
    adm = np.array([k not in adm_exclude for k in curves])
    for b in rungs:
        parts.append((b, f"b{b}_adm", (rung == b) & adm))
        parts.append((b, f"b{b}_rest", (rung == b) & ~adm))
    return Model(rung, np.array(m), {b: D for b in rungs}, parts)


def p0_evaluate(by_rung, rungs, n_b, rho1, D_plan, R) -> tuple[dict, dict]:
    excl = {(b, c["curve"]) for b in rungs for c in by_rung[b][:n_b] if c["height_screen_hits"]}
    model = p0_model(by_rung, rungs, n_b, rho1, D_plan, excl)
    allp = list(range(len(model.parts)))
    admp = model.part_index({f"b{b}_adm" for b in rungs})
    banks, zA, zD = [], [], []
    for f in range(FAMILIES):
        seqs = fam_seq(f)
        bank = make_bank(model, R, 3, seqs[0])
        banks.append(bank)
        rng = np.random.default_rng(seqs[1])
        A = struct_totals(rng, model, R, 1.0, "poisson", allp)
        CR, V = rand_parts_stats(bank, allp)
        zA.append((A - CR) / np.sqrt(4 * V / 3))
        Aa = struct_totals(rng, model, R, 1.0, "poisson", admp)
        Ma = struct_totals(rng, model, R, 1.0, "poisson", admp)
        CRa, Va = rand_parts_stats(bank, admp)
        zD.append((Aa - Ma) / np.sqrt(2 * Va))
    tA, tA_f = quant_avg(zA, 1 - ALPHA_ONE_SIDED)
    tD, tD_f = quant_avg(zD, 0.95)

    def power(kappa, mode):
        hits = 0
        for f, bank in enumerate(banks):
            rng = np.random.default_rng(fam_seq(f)[6].spawn(8)[
                {("poisson", KAPPA_POWER): 0, ("compound", KAPPA_POWER): 1,
                 ("poisson", KAPPA_POWER_OBS): 2, ("compound", KAPPA_POWER_OBS): 3}[(mode, kappa)]])
            CR, V = rand_parts_stats(bank, allp)
            A = struct_totals(rng, model, R, kappa, mode, allp)
            hits += int(np.sum((A - CR) / np.sqrt(4 * V / 3) > tA))
        return hits / (R * FAMILIES)

    p110 = {"poisson": power(KAPPA_POWER, "poisson"), "compound": power(KAPPA_POWER, "compound")}
    p110["governing"] = min(p110["poisson"], p110["compound"])
    p1097 = {"poisson": power(KAPPA_POWER_OBS, "poisson"), "compound": power(KAPPA_POWER_OBS, "compound")}
    p1097["governing"] = min(p1097["poisson"], p1097["compound"])
    p1097["target"] = None
    hits = 0
    for f, bank in enumerate(banks):
        rng = np.random.default_rng(fam_seq(f)[6].spawn(8)[4])
        Aa = struct_totals(rng, model, R, KAPPA_POWER, "poisson", admp)
        Ma = struct_totals(rng, model, R, 1.0, "poisson", admp)
        CRa, Va = rand_parts_stats(bank, admp)
        hits += int(np.sum((Aa - Ma) / np.sqrt(2 * Va) > tD))
    pc = hits / (R * FAMILIES)
    ev = {"n_b": n_b, "pooled_curves": len(model.m),
          "t_A_plan": tA, "t_A_plan_per_family": tA_f, "t_A_plan_spread": max(tA_f) - min(tA_f),
          "t_Delta_plan": tD, "t_Delta_plan_per_family": tD_f,
          "power_1.10": p110, "power_1.097": p1097,
          "power_contrast": {"kappa_A": KAPPA_POWER, "kappa_M": 1.0, "power": pc,
                             "M_admitted_curves": int(sum(model.P[:, admp].sum(axis=0)))},
          "meets": p110["governing"] >= 0.90 and pc >= 0.80,
          "expected_C_R_model": float(model.m.sum())}
    return ev, {"banks": banks, "model": model, "allp": allp, "tA": tA}


def p0_predict(ev: dict, ctx: dict, R: int, n_designs: int) -> dict:
    ev = dict(ev)
    ev["X_rel"] = x_rel(ctx["banks"], ctx["model"], ctx["allp"], ctx["tA"], R, RHO_D_UPPER)
    ev["X_rel"]["threshold"] = "t_A_plan (pre-data; t_perm does not exist before data)"
    cov = coverage(ctx["banks"], ctx["model"], ctx["allp"], (1.00,), n_designs, R)
    ev["U_A_at_1"] = {"rule": "analysis.upper_bound_U_A applied to synthetic null designs (PDI-6)",
                      **cov["1.00"]}
    return ev


# ------------------------------------------------------------------------------------------
# checks (RA-04)

def run_verify_rows(run_dir: str) -> dict:
    """verify_rows.py unmodified, by path, --out /dev/stdout; stdout captured in memory; only
    the whitelisted fields are kept, the trailing summary line is discarded."""
    r = subprocess.run([PY, absp(VERIFY_ROWS), "--run-dir", rel(run_dir), "--out", "/dev/stdout"],
                       cwd=REPO, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    rep, _ = json.JSONDecoder().raw_decode(r.stdout.lstrip())
    keep = {k: rep.get(k) for k in ("gate", "pass", "run_dir", "sample_rule", "sampled_instances",
                                    "bases_records_checked", "harvest_files_sha256", "verifier",
                                    "verifier_sha256", "imports", "imports_subset_of_declared_and_stdlib")}
    bad_base = {json.dumps(f["key"][:4]) for f in rep.get("failures", []) if len(f["key"]) == 4}
    per = {}
    for k, v in rep.get("per_instance", {}).items():
        kk = json.loads(k)
        ok = v.get("failed") == 0 and json.dumps(kk[:4]) not in bad_base
        per[k] = "PASS" if ok else "FAIL"
    keep["per_instance"] = per
    keep["failures"] = [{"key": f["key"], "class": f.get("class")} for f in rep.get("failures", [])]
    keep["exit_code"] = r.returncode
    keep["stderr_tail"] = r.stderr[-2000:] if r.stderr.strip() else None
    del rep
    return keep


def legendre_ok(x: int, a: int, b: int, p: int) -> bool:
    rhs = (x * x * x + a * x + b) % p
    return rhs != 0 and pow(rhs, (p - 1) // 2, p) == 1


def set_rungs(design: dict) -> None:
    global RUNGS
    RUNGS = tuple(int(b) for b in design.get("rungs", RUNGS))


def gt(x, t) -> bool:
    return x is not None and x == x and t is not None and t == t and x > t


def cmd_checks(a) -> int:
    rd = absp(a.run_dir)
    vm = ViewMap()
    design = json.load(open(vm.note(a.design)))
    set_rungs(design)
    dcur = {(c["bits"], c["curve"]): c for c in design["curves"]}
    mr = json.load(open(vm.note(os.path.join(rd, "merge-report.json"))))
    rows = {}
    for r in read_jsonl(vm.note(os.path.join(rd, "rows.jsonl.gz"))):
        rows[ikey(r["bits"], r["curve"], row_m(r), r["arm"], r["mode"])] = r
    vm.note(VERIFY_ROWS)
    vr = run_verify_rows(rd)
    write_json(os.path.join(rd, "row-verify.json"), vr)
    per: dict = defaultdict(dict)
    fails: dict = defaultdict(list)

    def mark(check, key, ok, field=None, extra=None):
        per[key][check] = "PASS" if ok else "FAIL"
        if not ok:
            k = json.loads(key)
            fails[check].append({"check": check, "run": "RUN-PFDR-0b3699-table", "bits": k[0],
                                 "c": k[1], "m": k[2], "arm": k[3], "mode": k[4],
                                 "field": field, **(extra or {})})

    # G4, G7, G-CURVE on every canonical row
    for key, r in rows.items():
        st = r.get("status")
        if st != "completed_valid":
            per[key]["status"] = st
            if st == "invalid":
                mark("G4", key, False, "status invalid")
            continue
        h = r["harvest"]
        g4 = True
        for cname in ("TT", "TB", "SS"):
            s = h[cname]["at_stop"]
            if s["cert_fail"] != 0 or s["cert_pass"] != s["rows_emitted"]:
                g4 = False
                mark("G4", key, False, f"{cname}.cert_fail/cert_pass/rows_emitted")
        if g4:
            mark("G4", key, True)
        chk = r.get("checks") or {}
        if r["arm"] in ("subgroup", "planted_sub"):
            bad = [k for k, v in chk.items() if v is False]
            need = (["G7_subgroup_x_pow_d_eq_coset_pow_d"] if r["arm"] == "subgroup" else
                    ["G7_planted_relations_hold", "G7_planted_x_distinct", "G7_planted_points_on_curve",
                     "G7_planted_size_eq_s_sub"])
            missing = [k for k in need if k not in chk]
            ok7 = not bad and not missing
            mark("G7", key, ok7, ",".join(bad + missing) or None)
        dc = dcur.get((r["bits"], r["curve"]))
        okc = dc is not None and all(r.get(k) == dc[k] for k in ("p", "a", "b", "N")) and r.get("P") == dc["P"]
        if okc:
            mark("G-CURVE", key, True)
        else:
            flds = ["design entry"] if dc is None else [k for k in ("p", "a", "b", "N", "P") if r.get(k) != dc[k]]
            mark("G-CURVE", key, False, ",".join(flds))
    # G-REL and PC-R-iii from the retained harvest rows
    hmap = mr["harvest_rows_map"]
    by_file: dict = defaultdict(set)
    for k, v in hmap.items():
        if k in rows and rows[k].get("status") == "completed_valid" and v.get("harvest_rows_file"):
            by_file[v["harvest_rows_file"]].add(k)
    seen_keys = set()
    for f, keyset in sorted(by_file.items()):
        grouped: dict = defaultdict(list)
        for h in read_jsonl(vm.note(f)):
            k = ikey(h["bits"], h["curve"], h["m"], h["arm"], h["mode"])
            if k in keyset:
                grouped[k].append(h)
        for k in sorted(keyset):
            seen_keys.add(k)
            r = rows[k]
            hs = grouped.get(k, [])
            N = r["N"]
            okrel = True
            for cname in ("TT", "TB", "SS"):
                s = r["harvest"][cname]["at_stop"]
                if "relations_distinct" not in s:
                    continue
                rc = recount_class(hs, N, cname, keep_keys=(cname == "TT"))
                for fld in ("relations_distinct", "relations_distinct_sign", "relations_nonformal",
                            "R_star", "multiplicity_histogram"):
                    if rc[fld] != s[fld]:
                        okrel = False
                        mark("G-REL", k, False, f"{cname}.{fld}")
                if cname == "TT" and r["arm"] == "planted_sub":
                    vs = planted_tt_keys(r.get("fb_params") or {}, N)
                    okp = bool(vs) and all(v in rc["keys"] for v in vs)
                    if (r.get("fb_params") or {}).get("n_tt") != 1:
                        okp = False
                        mark("PC-R-iii", k, False, "n_tt (one TT plant per curve)")
                    elif okp:
                        mark("PC-R-iii", k, True)
                    else:
                        mark("PC-R-iii", k, False, "planted TT monic vector")
            if okrel:
                mark("G-REL", k, True)
    for k, r in rows.items():
        if r.get("status") == "completed_valid" and k not in seen_keys:
            mark("G-REL", k, False, "harvest_rows_file")
            if r["arm"] == "planted_sub":
                mark("PC-R-iii", k, False, "harvest_rows_file")
    # G7-OFFSET on the sampled small_x_offset bases
    bases = {}
    for bf in sorted({v["bases_file"] for v in mr["bases_map"].values()}):
        for brec in read_jsonl(vm.note(bf)):
            if brec["arm"] == "small_x_offset":
                bases[(brec["bits"], brec["curve"])] = brec
    for key, r in rows.items():
        if r["arm"] != "small_x_offset" or r["curve"] % 10 != 0 or r.get("status") != "completed_valid":
            continue
        dc = dcur[(r["bits"], r["curve"])]
        brec = bases.get((r["bits"], r["curve"]))
        fl = []
        if (r.get("fb_params") or {}).get("x0") != dc["x0"]:
            fl.append("x0")
        if brec is None:
            fl.append("bases record")
        else:
            p, aa, bb = brec["p"], brec["a"], brec["b"]
            xs, x = [], dc["x0"]
            while len(xs) < dc["s_sub"]:
                if legendre_ok(x, aa, bb, p):
                    xs.append(x)
                x += 1
            if [pt[0] for pt in brec["points"]] != xs:
                fl.append("points (first s_sub liftable x >= x0)")
            if any(pt[1] == 0 or (pt[1] * pt[1] - (pt[0] ** 3 + aa * pt[0] + bb)) % p for pt in brec["points"]):
                fl.append("points (y != 0, on curve)")
        mark("G7-OFFSET", key, not fl, ",".join(fl) or None)
    # G4-R from verify_rows
    for k, v in vr["per_instance"].items():
        mark("G4-R", k, v == "PASS", None if v == "PASS" else "row identity / base points")
    checks = {}
    for check in ("G4", "G4-R", "G7", "G-CURVE", "G-REL", "G7-OFFSET", "PC-R-iii"):
        evaluated = sum(1 for d in per.values() if check in d)
        checks[check] = {"pass": (not fails[check]) and evaluated > 0 and (check != "G4-R" or vr["pass"]),
                         "instances_evaluated": evaluated, "mismatch_keys": fails[check][:5000]}
    instances_by_status = Counter(r.get("status") for r in rows.values())
    rep = {"gate": "RA-04 checks", "pass": all(c["pass"] for c in checks.values()),
           "created_at": now(), "writer": "analyze_a.py checks", "run_dir": rel(rd),
           "blinding_note": ("stopping_rules [5]: per-check pass, per-instance PASS/FAIL and mismatch keys only; "
                             "no relation count, row count, total, kappa or z"),
           "instance_counts_by_status": dict(instances_by_status),
           "checks": checks, "per_instance": dict(per), "view_map": vm.as_list()}
    write_json(os.path.join(rd, "checks-report.json"), rep)
    print(json.dumps({"checks_pass": rep["pass"], **{c: v["pass"] for c, v in checks.items()}}))
    return 0 if rep["pass"] else 1


# ------------------------------------------------------------------------------------------
# shared by calibrate and unmask

ARM_RE = re.compile(r'"arm": "([A-Za-z0-9_]+)"')


def line_arm(line: str) -> str | None:
    arms = set(ARM_RE.findall(line))
    return arms.pop() if len(arms) == 1 else None


def curve_sets(design: dict, mr: dict) -> dict:
    """CC-6 from keys only: a curve is used for the family iff every family arm has a
    completed_valid canonical row; M admitted iff used and not height-screened."""
    bad = set()
    for st, keys in (mr.get("non_valid_keys") or {}).items():
        for k in keys:
            bad.add((k[0], k[1]))
    for k in mr.get("missing_keys") or []:
        bad.add((k[0], k[1]))
    hs = {(int(b), c) for b, cs in design["height_screen"].items() for c in cs}
    used, adm, excluded = {}, {}, {}
    for b in RUNGS:
        cs = [c["curve"] for c in design["curves"] if c["bits"] == b]
        used[b] = [c for c in cs if (b, c) not in bad]
        adm[b] = [c for c in used[b] if (b, c) not in hs]
        excluded[str(b)] = sorted(c for c in cs if (b, c) in bad)
    return {"used": used, "adm": adm, "cc6_excluded": excluded,
            "height_screened": {str(b): sorted(c for (bb, c) in hs if bb == b) for b in RUNGS}}


def build_model(design: dict, sets: dict, rho1: dict, D: dict) -> tuple[Model, list]:
    dcur = {(c["bits"], c["curve"]): c for c in design["curves"]}
    rung, m, order, parts = [], [], [], []
    for b in RUNGS:
        for c in sets["used"][b]:
            rung.append(b)
            m.append(rho1[b] * dcur[(b, c)]["mu_model"])
            order.append((b, c))
    rung = np.array(rung)
    admset = {(b, c) for b in RUNGS for c in sets["adm"][b]}
    adm = np.array([k in admset for k in order])
    for b in RUNGS:
        parts.append((b, f"b{b}_adm", (rung == b) & adm))
        parts.append((b, f"b{b}_rest", (rung == b) & ~adm))
    return Model(rung, np.array(m), D, parts), order


def null_counts(rd: str, mr: dict, vm: ViewMap, read_log: dict | None, all_arms: bool) -> tuple[dict, dict]:
    """Per-instance TT and TB recount from the harvest rows, and the census rows parsed.
    all_arms False (RA-05): lines are filtered by arm name before any parse; only null-arm
    lines are parsed (I-A7)."""
    want = set(NULL_ARMS) if not all_arms else None
    rows = {}
    rp = vm.note(os.path.join(rd, "rows.jsonl.gz"))
    parsed = Counter()
    skipped_structured = False
    for line in iter_lines(rp):
        arm = line_arm(line)
        if want is not None and arm not in want:
            skipped_structured = True
            continue
        r = json.loads(line)
        parsed[r["arm"]] += 1
        rows[ikey(r["bits"], r["curve"], row_m(r), r["arm"], r["mode"])] = r
    if read_log is not None:
        read_log["files"].append({"path": rel(rp), "sha256": sha256(rp), "kind": "census rows",
                                  "parsed_lines_by_arm": dict(parsed),
                                  "structured_lines_skipped_unparsed": skipped_structured})
    files = sorted({v["harvest_rows_file"] for k, v in mr["harvest_rows_map"].items()
                    if v.get("harvest_rows_file")})
    grouped: dict = defaultdict(list)
    for f in files:
        p = vm.note(f)
        parsed = Counter()
        skipped_structured = False
        for line in iter_lines(p):
            arm = line_arm(line)
            if want is not None and arm not in want:
                skipped_structured = True
                continue
            h = json.loads(line)
            parsed[h["arm"]] += 1
            grouped[ikey(h["bits"], h["curve"], h["m"], h["arm"], h["mode"])].append(h)
        if read_log is not None:
            read_log["files"].append({"path": rel(p), "sha256": sha256(p), "kind": "harvest rows",
                                      "parsed_lines_by_arm": dict(parsed),
                                      "structured_lines_skipped_unparsed": skipped_structured})
    counts = {}
    for k, r in rows.items():
        if r.get("status") != "completed_valid":
            continue
        hs = grouped.get(k, [])
        counts[k] = {"TT": recount_class(hs, r["N"], "TT", keep_keys=all_arms),
                     "TB": recount_class(hs, r["N"], "TB")}
    return rows, counts


def table_null(sets: dict, counts: dict) -> tuple[list, np.ndarray]:
    order, Y = [], []
    for b in RUNGS:
        for c in sets["used"][b]:
            order.append((b, c))
            Y.append([counts[ikey(b, c, 4, arm, "table")]["TT"]["relations_nonformal"] for arm in NULL_ARMS])
    return order, np.array(Y, dtype=np.int64)


def cc8(CX: float, Yr: np.ndarray) -> dict:
    """CC-8 of one cell: Yr (curves x 3) the triple's counts."""
    CR = Yr.sum() / 3.0
    s2 = Yr.var(axis=1, ddof=1).sum() if len(Yr) else 0.0
    V = max(s2, CR)
    SD = math.sqrt(4.0 * V / 3.0) if V > 0 else float("nan")
    return {"C_X": float(CX), "C_R": float(CR), "sum_s2": float(s2), "V": float(V), "SD_null": SD,
            "kappa_rel": (CX / CR) if CR else None, "z": (CX - CR) / SD if SD == SD and SD > 0 else None,
            "SE": SD / CR if CR else None, "curves": int(len(Yr))}


def make_banks(model: Model, R: int) -> list:
    return [make_bank(model, R, 4, fam_seq(f)[0]) for f in range(FAMILIES)]


def calib_core(model: Model, order: list, Y: np.ndarray, R: int, banks: list) -> dict:
    """G-NB-R t_A, permutation-null t_perm, t_dec, t_Delta, PC-NULL-R joint law."""
    allp = list(range(len(model.parts)))
    admp = model.part_index({f"b{b}_adm" for b in RUNGS})
    zA = [cell_from_bank(bk, allp, 3)[0] for bk in banks]
    tA, tA_f = quant_avg(zA, 0.99)
    tA999, _ = quant_avg(zA, 0.999)
    # permutation null on the real null-arm counts (PDI-4)
    tot = Y.sum(axis=1)
    X0 = Y.astype(float)
    Rs = (tot[:, None] - Y).astype(float)
    S6 = np.zeros_like(X0)
    for e in range(4):
        o = Y[:, [a for a in range(4) if a != e]].astype(float)
        S6[:, e] = 3 * (o * o).sum(axis=1) - o.sum(axis=1) ** 2
    zP = []
    for f in range(FAMILIES):
        rng = np.random.default_rng(np.random.SeedSequence([TOKEN, 100 + f]))
        zs = np.empty(R)
        for c0 in range(0, R, CHUNK):
            B = min(CHUNK, R - c0)
            e = rng.integers(0, 4, size=(B, len(Y)))
            cols = np.arange(len(Y))[None, :]
            CX = X0[cols, e].sum(1)
            CR = Rs[cols, e].sum(1) / 3
            S2 = S6[cols, e].sum(1) / 6
            V = np.maximum(S2, CR)
            zs[c0:c0 + B] = (CX - CR) / np.sqrt(4 * V / 3)
        zP.append(zs)
    tP, tP_f = quant_avg(zP, 0.99)
    t_dec = max(tA, tP)
    allA, allP = np.concatenate(zA), np.concatenate(zP)
    # t_Delta: two independent pseudo-structured arms on the M-admitted curves
    zD = []
    for f, bk in enumerate(banks):
        rng = np.random.default_rng(fam_seq(f)[6])
        Aa = struct_totals(rng, model, R, 1.0, "poisson", admp)
        Ma = struct_totals(rng, model, R, 1.0, "poisson", admp)
        CRa, Va = rand_parts_stats(bk, admp)
        zD.append((Aa - Ma) / np.sqrt(2 * Va))
    tD, tD_f = quant_avg(zD, 0.95)
    # PC-NULL-R joint law (four null pseudo-cells)
    Ks, means = [], []
    for bk in banks:
        Z = np.stack([cell_from_bank(bk, allp, e)[0] for e in range(4)], axis=1)
        Ks.append((Z > t_dec).sum(axis=1))
        means.append(Z.mean(axis=1))
    Kall, Mall = np.concatenate(Ks), np.concatenate(means)
    m_lo, m_lo_f = quant_avg(means, 0.005)
    m_hi, m_hi_f = quant_avg(means, 0.995)
    return {"t_A": tA, "t_A_per_family": tA_f, "t_A_spread": max(tA_f) - min(tA_f),
            "t_A_0999": tA999, "t_perm": tP, "t_perm_per_family": tP_f,
            "t_perm_spread": max(tP_f) - min(tP_f), "t_dec": t_dec,
            "t_dec_source": "t_perm" if tP > tA else "t_A",
            "rate_perm_null_above_t_A": float(np.mean(allP > tA)),
            "rate_G-NB-R_above_t_perm": float(np.mean(allA > tP)),
            "t_Delta": tD, "t_Delta_per_family": tD_f,
            "pc_null_joint": {"K_null_distribution": {str(k): float(np.mean(Kall == k)) for k in range(5)},
                              "mean_z_interval_99": [m_lo, m_hi],
                              "mean_z_interval_per_family": [m_lo_f, m_hi_f]},
            "_K_all": Kall}


def observed_null_cells(order: list, Y: np.ndarray, t_dec: float) -> dict:
    out = {}
    names = ["r0_as_structured", "r1_as_structured", "r2_as_structured", "known_null_sub"]
    for e, nm in enumerate(names):
        others = [a for a in range(4) if a != e]
        band = cc8(Y[:, e].sum(), Y[:, others])
        rung = {}
        for b in RUNGS:
            idx = [i for i, (bb, _) in enumerate(order) if bb == b]
            rung[str(b)] = cc8(Y[idx, e].sum(), Y[np.ix_(idx, others)])
        out[nm] = {"band": band, "per_rung": rung}
    return out


def disp_ci(order, Y, seq, R) -> dict:
    """H1c TT m = 4 dispersion clause: pooled within-curve relation dispersion of r0..r2
    (sum s_j^2 / sum nbar_j) with a curve-cluster bootstrap 99% interval."""
    Yr = Y[:, :3].astype(float)
    s2 = Yr.var(axis=1, ddof=1)
    nbar = Yr.mean(axis=1)
    D = s2.sum() / nbar.sum() if nbar.sum() else float("nan")
    rng = np.random.default_rng(seq)
    rungs = np.array([b for b, _ in order])
    reps = np.empty(R)
    for c0 in range(0, R, CHUNK):
        B = min(CHUNK, R - c0)
        num = np.zeros(B)
        den = np.zeros(B)
        for b in RUNGS:
            idx = np.nonzero(rungs == b)[0]
            pick = idx[rng.integers(0, len(idx), size=(B, len(idx)))]
            num += s2[pick].sum(axis=1)
            den += nbar[pick].sum(axis=1)
        reps[c0:c0 + B] = num / den
    lo, hi = float(np.quantile(reps, 0.005)), float(np.quantile(reps, 0.995))
    return {"D_pooled": float(D), "interval_99": [lo, hi], "bootstrap_reps": R,
            "method": "curve-cluster bootstrap within rung, percentile 99% interval",
            "interval_inside_[0.8,1.25]": bool(lo >= 0.8 and hi <= 1.25),
            "interval_entirely_outside_[0.8,1.25]": bool(hi < 0.8 or lo > 1.25)}


# ------------------------------------------------------------------------------------------
# calibrate (RA-05)

def cmd_calibrate(a) -> int:
    t0 = time.time()
    if not a.fixture and (a.reps < PROD_REPS or a.designs < PROD_DESIGNS):
        raise SystemExit("replicates below the frozen minimum outside --fixture")
    vm = ViewMap()
    rd = absp(a.table_dir)
    out = absp(a.out_dir)
    design = json.load(open(vm.note(a.design)))
    set_rungs(design)
    if a.design_sha256 and sha256(a.design) != a.design_sha256:
        raise SystemExit("design.json sha256 differs from the pinned value")
    mr = json.load(open(vm.note(os.path.join(rd, "merge-report.json"))))
    read_log = {"rule": "lines filtered by arm name (fixed-pattern scan) before any JSON parse; only "
                        "random_sub_r0, random_sub_r1, random_sub_r2, known_null_sub lines parsed",
                "files": []}
    started = now()
    rows, counts = null_counts(rd, mr, vm, read_log, all_arms=False)
    if any(json.loads(k)[3] not in NULL_ARMS for k in rows):
        raise SystemExit("I-A7: a non-null arm was parsed")
    sets = curve_sets(design, mr)
    order, Y = table_null(sets, counts)
    dcur = {(c["bits"], c["curve"]): c for c in design["curves"]}
    rho1, D, Dhat = {}, {}, {}
    for b in RUNGS:
        idx = [i for i, (bb, _) in enumerate(order) if bb == b]
        Yr = Y[idx][:, :3].astype(float)
        nbar = Yr.mean(axis=1)
        mus = np.array([dcur[order[i]]["mu_model"] for i in idx])
        rho1[b] = float(nbar.sum() / mus.sum())
        Dhat[b] = float(Yr.var(axis=1, ddof=1).sum() / nbar.sum()) if nbar.sum() else float("nan")
        D[b] = max(Dhat[b], 1.0)
    model, morder = build_model(design, sets, rho1, D)
    assert morder == order
    banks = make_banks(model, a.reps)
    core = calib_core(model, order, Y, a.reps, banks)
    obs = observed_null_cells(order, Y, core["t_dec"])
    K_obs = sum(1 for v in obs.values() if v["band"]["z"] is not None and v["band"]["z"] > core["t_dec"])
    Kall = core.pop("_K_all")
    pK = float(np.mean(Kall >= K_obs))
    mean_z = float(np.mean([v["band"]["z"] for v in obs.values()]))
    lo, hi = core["pc_null_joint"]["mean_z_interval_99"]
    pc_null = {"gate": "PC-NULL-R", "K_observed": K_obs, "P_K_null_ge_K": pK,
               "criterion_i": pK >= 0.01, "mean_z_observed": mean_z, "mean_z_interval_99": [lo, hi],
               "criterion_ii": lo <= mean_z <= hi, "pass": pK >= 0.01 and lo <= mean_z <= hi,
               "observed_cells": obs,
               "per_rung_null_z_reported_never_gating": {nm: {b: v["per_rung"][b]["z"] for b in v["per_rung"]}
                                                         for nm, v in obs.items()}}
    allp = list(range(len(model.parts)))
    xr = x_rel(banks, model, allp, core["t_dec"], a.reps, RHO_D_UPPER)
    cov = coverage(banks, model, allp, COVERAGE_KAPPAS, a.designs, a.reps)
    signed_ok = all(cov[f"{k:.2f}"]["coverage_signed"] >= COVERAGE_FLOOR for k in COVERAGE_KAPPAS)
    h1c = disp_ci(order, Y, np.random.SeedSequence([TOKEN, 200]).spawn(4)[0], a.reps)
    null_table = [{"bits": b, "curve": c, **{arm: int(Y[i, j]) for j, arm in enumerate(NULL_ARMS)}}
                  for i, (b, c) in enumerate(order)]
    n_used = {str(b): len(sets["used"][b]) for b in RUNGS}
    cal = {
        "what": "EXP-PFDR-0b3699 calibration (RA-05; null arms only)", "created_at": now(),
        "started_at": started, "writer": "analyze_a.py calibrate", "fixture": a.fixture,
        "design_sha256": sha256(a.design), "design_final_n_b": design["final_n_b"],
        "curves_used": n_used, "cc6_excluded": sets["cc6_excluded"],
        "M_admitted": {str(b): len(sets["adm"][b]) for b in RUNGS},
        "height_screened": sets["height_screened"],
        "rho1_hat_b": {str(b): rho1[b] for b in RUNGS}, "D_hat_b": {str(b): Dhat[b] for b in RUNGS},
        "D_b": {str(b): D[b] for b in RUNGS},
        **core, "PC-NULL-R": pc_null,
        "predicted_X_rel": xr | {"threshold": "t_dec", "n": n_used},
        "U_coverage": {"by_kappa": cov, "floor": COVERAGE_FLOOR,
                       "signed_quantile_governs": signed_ok,
                       "governing_bound": "signed quantile" if signed_ok else "quantile of |dev| (EXP-PFDR-011cd0 A-INT)"},
        "H1c_TT4_dispersion": h1c,
        "H4_readings": {"known_null_z": obs["known_null_sub"]["band"]["z"], "PC-NULL-R_pass": pc_null["pass"],
                        "t_perm_above_t_A_0999": core["t_perm"] > core["t_A_0999"]},
        "simulation": {"generator": "G-NB-R: per curve NB(mean rho1_hat_b x mu_model(j), variance D_b x mean)",
                       "families": FAMILIES, "reps_per_family": a.reps, "designs_per_kappa": a.designs,
                       "chunk": CHUNK,
                       "seeds": {"family": "SeedSequence([0x0b3699, f]).spawn(8) -> " + str(SEQ_NAMES),
                                 "permutation": "SeedSequence([0x0b3699, 100 + f])",
                                 "bootstrap": "SeedSequence([0x0b3699, 200]).spawn(4)[0] (H1c)"}},
        "null_table": null_table,
    }
    cal["declared_metrics"] = {k: cal[k] for k in ("t_A", "t_A_spread", "t_A_0999", "t_perm", "t_dec",
                                                    "t_Delta", "rate_perm_null_above_t_A",
                                                    "rate_G-NB-R_above_t_perm", "rho1_hat_b", "D_b")}
    cal["declared_metrics"].update({"PC-NULL-R_pass": pc_null["pass"], "PC-NULL-R_K": K_obs,
                                    "PC-NULL-R_P_K": pK, "predicted_X_rel": xr["X_rel"],
                                    "U_coverage_signed": {k: v["coverage_signed"] for k, v in cov.items()},
                                    "U_coverage_absdev": {k: v["coverage_absdev"] for k, v in cov.items()},
                                    "H1c_D_pooled": h1c["D_pooled"], "H1c_interval_99": h1c["interval_99"]})
    os.makedirs(out, exist_ok=True)
    csha = write_json(os.path.join(out, "calibration.json"), cal)
    write_json(os.path.join(out, "arm-read-log.json"), read_log)
    write_json(os.path.join(out, "view-map.json"), {"step": "RA-05 calibrate", "files": vm.as_list()})
    print(json.dumps({"calibration_sha256": csha, "t_A": core["t_A"], "t_perm": core["t_perm"],
                      "t_dec": core["t_dec"], "t_Delta": core["t_Delta"], "PC-NULL-R": pc_null["pass"],
                      "seconds": round(time.time() - t0, 1)}))
    return 0


# ------------------------------------------------------------------------------------------
# unmask (RA-06)

def top10_share(per_curve_x: np.ndarray, nbar: np.ndarray) -> float | None:
    d = per_curve_x - nbar
    tot = d.sum()
    if tot <= 0:
        return None
    return float(np.sort(d)[::-1][:10].sum() / tot)


def poisson_sf(k: int, mu: float) -> float:
    """P(Poisson(mu) >= k)."""
    if k <= 0:
        return 1.0
    term = math.exp(-mu)
    cdf = term
    for i in range(1, k):
        term *= mu / i
        cdf += term
    return max(0.0, 1.0 - cdf)


def disp_robust(xA: np.ndarray, Yr: np.ndarray, rungs: np.ndarray, seq, R: int) -> dict:
    """rho = D_A_hat / D_R_hat (red team J4 d), curve-cluster bootstrap 95% interval."""
    def stat(idx):
        x, y = xA[idx], Yr[idx]
        nbar = y.mean(axis=1)
        s2 = y.var(axis=1, ddof=1)
        CR = nbar.sum()
        kh = x.sum() / CR
        d = x - nbar
        DA = (((d - (kh - 1) * nbar) ** 2).sum() - (s2 / 3).sum()) / CR
        DR = s2.sum() / CR
        return DA / DR
    allidx = np.arange(len(xA))
    rho = float(stat(allidx))
    rng = np.random.default_rng(seq)
    reps = np.empty(R)
    groups = [np.nonzero(rungs == b)[0] for b in RUNGS]
    for i in range(R):
        idx = np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups])
        reps[i] = stat(idx)
    return {"rho": rho, "interval_95": [float(np.quantile(reps, 0.025)), float(np.quantile(reps, 0.975))],
            "bootstrap_reps": R, "method": "curve-cluster bootstrap within rung, percentile"}


def cmd_unmask(a) -> int:
    t0 = time.time()
    if not a.fixture and a.reps < PROD_REPS:
        raise SystemExit("replicates below the frozen minimum outside --fixture")
    vm = ViewMap()
    calp = absp(a.calibration)
    if sha256(calp) != a.calibration_sha256:
        raise SystemExit("REFUSING: calibration.json does not match the pinned sha256")
    if not a.fixture:
        notes = open(absp(f"{EXPDIR}/implementation-notes.yaml")).read()
        if f"calibration_json" not in notes or a.calibration_sha256 not in notes:
            raise SystemExit("REFUSING: the calibration.json sha256 is not pinned in implementation-notes.yaml")
    cal = json.load(open(vm.note(calp)))
    rd = absp(a.table_dir)
    out = absp(a.out_dir)
    design = json.load(open(vm.note(a.design)))
    set_rungs(design)
    if sha256(a.design) != cal["design_sha256"]:
        raise SystemExit("design.json differs from the one calibration.json used")
    mr = json.load(open(vm.note(os.path.join(rd, "merge-report.json"))))
    started = now()
    rows, counts = null_counts(rd, mr, vm, None, all_arms=True)
    sets = curve_sets(design, mr)
    order, Y = table_null(sets, counts)
    if [[b, c, *[int(v) for v in Y[i]]] for i, (b, c) in enumerate(order)] != \
            [[r["bits"], r["curve"], *[r[arm] for arm in NULL_ARMS]] for r in cal["null_table"]]:
        raise SystemExit("null table differs from calibration.json")
    dcur = {(c["bits"], c["curve"]): c for c in design["curves"]}
    rho1 = {int(b): v for b, v in cal["rho1_hat_b"].items()}
    D = {int(b): v for b, v in cal["D_b"].items()}
    model, _ = build_model(design, sets, rho1, D)
    banks = make_banks(model, a.reps)
    allp = list(range(len(model.parts)))
    admp = model.part_index({f"b{b}_adm" for b in RUNGS})
    zA_null = [cell_from_bank(bk, allp, 3)[0] for bk in banks]
    tA_check, _ = quant_avg(zA_null, 0.99)
    if tA_check != cal["t_A"]:
        raise SystemExit("regenerated G-NB-R bank does not reproduce calibration.json t_A")
    t_dec, t_Delta = cal["t_dec"], cal["t_Delta"]
    # per-curve counts of every arm on the used curves
    S = {(int(b), c) for b, cs in design["S"].items() for c in cs}

    def arm_counts(arm, cls="TT"):
        return np.array([counts[ikey(b, c, 4, arm, "table")][cls]["relations_nonformal"] for (b, c) in order],
                        dtype=np.int64)

    unmatched = {}
    for arm in STRUCT_ARMS:
        unmatched[arm] = [[b, c] for (b, c) in order
                          if rows[ikey(b, c, 4, arm, "table")]["fb_size"] != dcur[(b, c)]["s_sub"]]
    x = {arm: arm_counts(arm) for arm in FAMILY_ARMS}
    pt = []
    pt_removed_ok = True
    for i, (b, c) in enumerate(order):
        k = ikey(b, c, 4, "planted_sub", "table")
        keys = counts[k]["TT"]["keys"]
        vs = planted_tt_keys(rows[k]["fb_params"], rows[k]["N"])
        if (b, c) in S:
            pt.append(len(keys))
        else:
            rem = keys - set(vs)
            pt_removed_ok &= len(rem) == len(keys) - len(set(vs))
            pt.append(len(rem))
    x["planted_target"] = np.array(pt, dtype=np.int64)
    Yr = Y[:, :3]
    rungs = np.array([b for b, _ in order])
    adm_mask = np.array([(b, c) in {(bb, cc) for bb in RUNGS for cc in sets["adm"][bb]} for (b, c) in order])
    um = {(b, c) for b, c in unmatched["small_x_offset"]}
    adm_mask &= np.array([(b, c) not in um for (b, c) in order])

    def null_p(z, parts):
        zs = np.concatenate([cell_from_bank(bk, parts, 3)[0] for bk in banks])
        return float(np.mean(zs >= z)) if z is not None else None

    def cell(arm, mask=None, parts=None):
        msk = np.ones(len(order), bool) if mask is None else mask
        um_arm = {(b, c) for b, c in unmatched.get(arm, [])}
        msk = msk & np.array([(b, c) not in um_arm for (b, c) in order])
        res = cc8(x[arm][msk].sum(), Yr[msk])
        res["calibrated_p"] = null_p(res["z"], parts if parts is not None else allp)
        res["per_rung"] = {}
        for b in RUNGS:
            mb = msk & (rungs == b)
            r = cc8(x[arm][mb].sum(), Yr[mb])
            r["calibrated_p"] = null_p(r["z"], model.part_index({f"b{b}_adm", f"b{b}_rest"}) if mask is None
                                       else model.part_index({f"b{b}_adm"}))
            res["per_rung"][str(b)] = r
        return res

    cells = {}
    for arm in ("small_x", "subgroup", "planted_sub", "planted_target", "known_null_sub"):
        cells[arm] = cell(arm)
    cells["small_x_offset"] = cell("small_x_offset", adm_mask, admp)
    # primary
    A = cells["small_x"]
    zA, kh, SE = A["z"], A["kappa_rel"], A["SE"]
    bound_rngs = [np.random.default_rng(s) for s in [fam_seq(f)[5] for f in range(FAMILIES)]]
    qlo, qab = q_bounds_at([rand_parts_stats(bk, allp) for bk in banks], model, allp, kh,
                           bound_rngs, a.reps)
    U_signed = kh - qlo * SE
    U_abs = kh + qab * SE
    covs = cal["U_coverage"]["by_kappa"]
    thin = kh < 1
    lab_s = ("one-sided 95% (signed quantile; kappa_hat < 1, binomial thinning), simulated coverage "
             if thin else "one-sided 95% (signed quantile), simulated coverage ")
    lab_a = ("quantile of |dev|; kappa_hat < 1, binomial thinning, simulated one-sided coverage "
             if thin else "quantile of |dev|, simulated one-sided coverage ")
    cov_s = {k: v["coverage_signed"] for k, v in covs.items()}
    cov_a = {k: v["coverage_absdev"] for k, v in covs.items()}
    signed_gov = cal["U_coverage"]["signed_quantile_governs"]
    U_gov = U_signed if signed_gov else U_abs
    Xr = cal["predicted_X_rel"]["X_rel"]
    # M and contrast on the M-admitted curves
    M = cells["small_x_offset"]
    mA = cc8(x["small_x"][adm_mask].sum(), Yr[adm_mask])
    VD = max(Yr[adm_mask].var(axis=1, ddof=1).sum() if adm_mask.any() else 0.0, Yr[adm_mask].sum() / 3)
    zD = ((x["small_x"][adm_mask].sum() - x["small_x_offset"][adm_mask].sum()) / math.sqrt(2 * VD)
          if VD > 0 else None)
    # controls
    K_plant = sum(1 for k in S if k in set(order))
    PT = cells["planted_target"]
    pcrt_i = gt(PT["z"], t_dec)
    pcrt_ii = abs((PT["C_X"] - PT["C_R"]) - K_plant) <= 4 * PT["SD_null"]
    pcrd = gt(cells["planted_sub"]["z"], t_dec)
    # gates from the earlier reports
    gate_reports = {}
    for g in a.gate_report or []:
        rep = json.load(open(vm.note(g)))
        gate_reports[rel(g)] = rep.get("pass")
    gate_reports["design.json G-FRESH"] = design["G-FRESH"]["pass"]
    if a.junit:
        import xml.etree.ElementTree as ET
        root_ = ET.parse(vm.note(a.junit)).getroot()
        suites = [root_] if root_.tag == "testsuite" else list(root_)
        tests = sum(int(x.get("tests", 0)) for x in suites)
        bad = sum(int(x.get("failures", 0)) + int(x.get("errors", 0)) for x in suites)
        gate_reports[rel(a.junit) + " (G-T)"] = tests > 0 and bad == 0
    invalid_gates = [g for g, ok in gate_reports.items() if ok is not True]
    keep80 = {str(b): len(sets["used"][b]) / design["final_n_b"] for b in RUNGS}
    madm80 = {str(b): int(adm_mask[rungs == b].sum()) / design["final_n_b"] for b in RUNGS}
    pcnull = cal["PC-NULL-R"]["pass"]

    def outcome(z_a):
        if invalid_gates or not pt_removed_ok:
            return "O-A-INVALID"
        if not pcnull or not pcrt_i or not pcrt_ii or not pcrd or any(v < 0.8 for v in keep80.values()):
            return "O-A-UNCAL"
        rep_ = gt(z_a, t_dec)
        m_ok = all(v >= 0.8 for v in madm80.values())
        if rep_:
            if m_ok and gt(M["z"], t_dec):
                return "O-A2"
            ks_ = [A["per_rung"][str(b)]["kappa_rel"] for b in RUNGS]
            if (all(gt(k_, 1.0) for k_ in ks_) and m_ok and M["z"] is not None and not gt(M["z"], t_dec)
                    and gt(zD, t_Delta)):
                return "O-A1"
            return "O-A1b"
        xr_ok = (not isinstance(Xr, str)) and Xr <= KAPPA_TARGET
        if U_gov <= KAPPA_TARGET and xr_ok:
            return "O-A3"
        return "O-A4"

    out_id = outcome(zA)
    bseq = np.random.SeedSequence([TOKEN, 200]).spawn(4)
    dr_A = disp_robust(x["small_x"].astype(float), Yr.astype(float), rungs, bseq[1], a.reps)
    dr_M = (disp_robust(x["small_x_offset"][adm_mask].astype(float), Yr[adm_mask].astype(float),
                        rungs[adm_mask], bseq[2], a.reps) if adm_mask.sum() > 1 else None)
    V_rob = A["V"] * max(1.0, dr_A["interval_95"][1])
    zA_rob = (A["C_X"] - A["C_R"]) / math.sqrt(4 * V_rob / 3)
    out_rob = outcome(zA_rob)
    flag = out_rob != out_id
    outcome_id = out_id + (" dispersion-sensitive" if flag else "")
    # tail checks and secondaries
    nbar = Yr.mean(axis=1)
    mcal = model.m
    tails = {}
    for arm in ("small_x", "small_x_offset"):
        msk = np.ones(len(order), bool) if arm == "small_x" else adm_mask
        xs = x[arm]
        tails[arm] = {
            "per_curve_histogram": dict(Counter(int(v) for v in xs[msk])),
            "zero_count_curves": int((xs[msk] == 0).sum()),
            "curves_with_count_ge_3": [[order[i][0], order[i][1], int(xs[i])] for i in range(len(order))
                                       if msk[i] and xs[i] >= 3],
            "poisson_tail_lt_1e-4": [[order[i][0], order[i][1], int(xs[i]), poisson_sf(int(xs[i]), float(mcal[i]))]
                                     for i in range(len(order)) if msk[i] and poisson_sf(int(xs[i]), float(mcal[i])) < 1e-4],
            "top10_share_of_excess": top10_share(xs[msk].astype(float), nbar[msk])}
    tails["randoms_histogram"] = {arm: dict(Counter(int(v) for v in Y[:, j])) for j, arm in enumerate(RANDOMS)}
    tails["null_pseudo_cells_top10_share"] = {
        nm: top10_share(Y[:, e].astype(float), Y[:, [q for q in range(4) if q != e]].mean(axis=1))
        for e, nm in enumerate(["r0", "r1", "r2", "known_null_sub"])}
    tb = {arm: int(sum(counts[ikey(b, c, 4, arm, "table")]["TB"]["relations_nonformal"] for (b, c) in order))
          for arm in FAMILY_ARMS}
    sign_counts = {arm: int(sum(counts[ikey(b, c, 4, arm, "table")]["TT"]["relations_distinct_sign"]
                                for (b, c) in order)) for arm in FAMILY_ARMS}
    mult_hist = {}
    for arm in FAMILY_ARMS:
        hcount = Counter()
        for (b, c) in order:
            for kk, v in counts[ikey(b, c, 4, arm, "table")]["TT"]["multiplicity_histogram"].items():
                hcount[kk] += v
        mult_hist[arm] = dict(sorted(hcount.items(), key=lambda t: int(t[0])))
    inf_rank = {arm: int(sum(rows[ikey(b, c, 4, arm, "table")]["harvest"]["TT"]["at_stop"]["informative_rank"]
                             for (b, c) in order)) for arm in FAMILY_ARMS}
    rstar = {arm: int(sum(counts[ikey(b, c, 4, arm, "table")]["TT"]["R_star"] for (b, c) in order))
             for arm in FAMILY_ARMS}
    perf = {}
    for arm in FAMILY_ARMS:
        secs = [rows[ikey(b, c, 4, arm, "table")].get("seconds", 0.0) for (b, c) in order]
        ents = [rows[ikey(b, c, 4, arm, "table")]["table_entries"] for (b, c) in order]
        rss = [rows[ikey(b, c, 4, arm, "table")]["harvest"].get("worker_maxrss_bytes", 0) for (b, c) in order]
        perf[arm] = {"seconds_median": float(np.median(secs)), "seconds_max": float(np.max(secs)),
                     "table_entries_median": float(np.median(ents)), "worker_maxrss_bytes_max": int(np.max(rss))}
    unexpected = []
    if not gt(zA, t_dec) and gt(M["z"], t_dec):
        unexpected.append("U-1: z_M > t_dec with z_A <= t_dec")
    if zA is not None and zA < -t_dec:
        unexpected.append("U-2: z_A < -t_dec (deficit)")
    if gt(cells["subgroup"]["z"], t_dec):
        unexpected.append("U-3: subgroup pooled z > t_dec")
    for arm, cc in cells.items():
        for b, r in cc["per_rung"].items():
            if r["z"] is not None and abs(r["z"]) > t_dec:
                unexpected.append(f"U-4: per-rung |z| > t_dec: {arm} rung {b}")
    for nm, v in cal["PC-NULL-R"]["observed_cells"].items():
        for b, r in v["per_rung"].items():
            if r["z"] is not None and abs(r["z"]) > t_dec:
                unexpected.append(f"U-4: per-rung |z| > t_dec: null pseudo-cell {nm} rung {b}")
    ana = {
        "what": "EXP-PFDR-0b3699 analysis (RA-06)", "created_at": now(), "started_at": started,
        "writer": "analyze_a.py unmask", "fixture": a.fixture,
        "calibration_sha256": a.calibration_sha256, "design_sha256": sha256(a.design),
        "bank_check": {"t_A_regenerated": tA_check, "equals_calibration": True},
        "outcome_id": outcome_id, "outcome_without_dispersion_flag": out_id,
        "outcome_with_dispersion_robust_z": out_rob,
        "primary": {"cell": "small_x|TT4|band", **{k: A[k] for k in ("C_X", "C_R", "V", "SD_null", "kappa_rel",
                                                                     "z", "SE", "curves", "calibrated_p")},
                    "C_A": A["C_X"], "t_A": cal["t_A"], "t_perm": cal["t_perm"], "t_dec": t_dec,
                    "z_A_gt_t_dec": gt(zA, t_dec),
                    "U_A_signed": U_signed, "U_A_signed_label": lab_s + str(cov_s),
                    "U_A_absdev": U_abs, "U_A_absdev_label": lab_a + str(cov_a),
                    "q_lo": qlo, "q_abs095": qab,
                    "U_A_governing": U_gov, "U_A_governing_bound": "signed quantile" if signed_gov else "quantile of |dev|",
                    "achieved_X_rel": Xr, "X_rel_detail": cal["predicted_X_rel"],
                    "kappa_hat_lt_1_reading": "no excess detected (never read as kappa_rel < 1)" if thin else None},
        "mutation": {"cell": "small_x_offset|TT4|band (M-admitted curves)",
                     **{k: M[k] for k in ("C_X", "C_R", "V", "SD_null", "kappa_rel", "z", "SE", "curves",
                                          "calibrated_p")},
                     "z_M_gt_t_dec": gt(M["z"], t_dec), "M_admitted_fraction_of_design_n_b": madm80,
                     "unmatched_size": unmatched["small_x_offset"],
                     "height_screened": sets["height_screened"]},
        "contrast": {"z_Delta": zD, "t_Delta": t_Delta, "z_Delta_gt_t_Delta": gt(zD, t_Delta),
                     "C_A_admitted": float(x["small_x"][adm_mask].sum()),
                     "C_M_admitted": float(x["small_x_offset"][adm_mask].sum()), "V_admitted": VD,
                     "small_x_on_admitted_curves": mA},
        "controls": {"PC-NULL-R": {"pass": pcnull, "source": "calibration.json"},
                     "PC-R-T": {"i_z_gt_t_dec": pcrt_i, "ii_within_4SD_of_K_plant": pcrt_ii,
                                "K_plant_realised": K_plant, "K_plant_design": design["K_plant_b"],
                                "C_planted_target_minus_C_R": PT["C_X"] - PT["C_R"], "SD_null": PT["SD_null"],
                                "pass": pcrt_i and pcrt_ii},
                     "PC-R-D": {"z": cells["planted_sub"]["z"], "pass": pcrd},
                     "planted_vector_exact_removal_ok": pt_removed_ok},
        "gates_read": gate_reports, "invalidating_gates_failed": invalid_gates,
        "small_x_kept_fraction_of_design_n_b": keep80,
        "cells": cells,
        "per_rung_small_x_sign": {b: (A["per_rung"][b]["kappa_rel"] or 0) - 1 for b in A["per_rung"]},
        "dispersion_robustness": {"rho_A": dr_A, "rho_M": dr_M, "z_A_with_V_scaled": zA_rob,
                                  "V_scale": max(1.0, dr_A["interval_95"][1]),
                                  "dispersion_sensitive": flag},
        "tail_checks": tails,
        "secondary": {"TB_counts": tb, "TT_sign_only_counts_CC-1b": sign_counts,
                      "TT_multiplicity_histograms": mult_hist, "TT_informative_rank_sum": inf_rank,
                      "TT_R_star_sum": rstar, "per_instance_performance": perf,
                      "H1c_TT4_dispersion": cal["H1c_TT4_dispersion"], "H4_readings": cal["H4_readings"],
                      "A-INT_absdev_bound_beside_U_A": U_abs},
        "unexpected_observations": unexpected,
        "cc6_excluded": sets["cc6_excluded"], "height_screen_exclusions": sets["height_screened"],
        "view_map_files": len(vm.files),
    }
    ana["declared_metrics"] = {
        "outcome_id": outcome_id, "C_A": A["C_X"], "C_R": A["C_R"], "V": A["V"], "SD_null": A["SD_null"],
        "kappa_rel": kh, "z_A": zA, "calibrated_p": A["calibrated_p"], "t_A": cal["t_A"],
        "t_perm": cal["t_perm"], "t_dec": t_dec, "U_A_governing": U_gov, "U_A_signed": U_signed,
        "U_A_absdev": U_abs, "X_rel": Xr, "kappa_M": M["kappa_rel"], "z_M": M["z"], "z_Delta": zD,
        "t_Delta": t_Delta, "PC-NULL-R": pcnull, "PC-R-T": pcrt_i and pcrt_ii, "PC-R-D": pcrd,
        "unexpected": unexpected}
    os.makedirs(out, exist_ok=True)
    write_json(os.path.join(out, "analysis.json"), ana)
    cl = []
    for arm, cc in cells.items():
        cl.append({"arm": arm, "class": "TT", "m": 4, "scope": "band",
                   **{k: v for k, v in cc.items() if k != "per_rung"}})
        for b, r in cc["per_rung"].items():
            cl.append({"arm": arm, "class": "TT", "m": 4, "scope": f"rung{b}", **r})
    for nm, v in cal["PC-NULL-R"]["observed_cells"].items():
        cl.append({"arm": f"null:{nm}", "class": "TT", "m": 4, "scope": "band", **v["band"]})
    write_jsonl(os.path.join(out, "cells.jsonl"), cl)
    write_json(os.path.join(out, "view-map.json"), {"step": "RA-06 unmask", "files": vm.as_list()})
    print(json.dumps({"outcome_id": outcome_id, "seconds": round(time.time() - t0, 1)}))
    return 0


# ------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("p0")
    p.add_argument("--curves", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--rungs", type=int, nargs="+", default=list(RUNGS))
    p.add_argument("--c0", type=int, default=C0)
    p.add_argument("--declared-n", type=int, default=DECLARED_N)
    p.add_argument("--arch-jobs", default=ARCH_JOBS)
    p.add_argument("--arch-calibration", default=ARCH_CAL)
    p.add_argument("--arch-analysis", default=ARCH_ANA)
    p.add_argument("--arch-design", default=ARCH_DESIGN)
    p.add_argument("--localise", default=LOCALISE)
    p.add_argument("--sizing", default=SIZING)
    p.add_argument("--redteam", default=REDTEAM)
    p.add_argument("--reps", type=int, default=PROD_REPS)
    p.add_argument("--designs", type=int, default=PROD_DESIGNS)
    p.add_argument("--fixture", action="store_true")
    c = sub.add_parser("checks")
    c.add_argument("--run-dir", required=True)
    c.add_argument("--design", required=True)
    k = sub.add_parser("calibrate")
    k.add_argument("--table-dir", required=True)
    k.add_argument("--design", required=True)
    k.add_argument("--design-sha256", default=None)
    k.add_argument("--out-dir", required=True)
    k.add_argument("--reps", type=int, default=PROD_REPS)
    k.add_argument("--designs", type=int, default=PROD_DESIGNS)
    k.add_argument("--fixture", action="store_true")
    u = sub.add_parser("unmask")
    u.add_argument("--table-dir", required=True)
    u.add_argument("--design", required=True)
    u.add_argument("--calibration", required=True)
    u.add_argument("--calibration-sha256", required=True)
    u.add_argument("--gate-report", action="append", default=None)
    u.add_argument("--junit", default=None)
    u.add_argument("--out-dir", required=True)
    u.add_argument("--reps", type=int, default=PROD_REPS)
    u.add_argument("--fixture", action="store_true")
    a = ap.parse_args(argv)
    return {"p0": cmd_p0, "checks": cmd_checks, "calibrate": cmd_calibrate, "unmask": cmd_unmask}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

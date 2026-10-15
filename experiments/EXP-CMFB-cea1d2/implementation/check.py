#!/usr/bin/env python3
"""Checker for one trial of EXP-CMFB-cea1d2:  check.py RUN_DIR   (exit 0 only if everything holds).

It validates mathematical invariants, controls and manifest semantics, not merely the presence of
files: M0, curve order / trace / j, labelling, control gates and the invalidation rules I1..I9 (I10 is
a flag, I11 is the source-hash binding to the frozen trial plan).  It imports curves.py only for the
pure instance-list function (the instance-list sha256 of seeds); the arithmetic, the coverage
recomputation (pure-Python set at small N, sort-based unique at C24), the labelling checks and every
statistic of t8 are written again here and never call driver.py, analyze.py or count.py.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import yaml  # noqa: E402

import curves  # noqa: E402  (instance-list function and protocol constants only)

PLAN = REPO / "experiments" / "EXP-CMFB-cea1d2" / "trial-plan.json"
CELLS = {"C16": (2 ** 14, 2 ** 18), "C20": (2 ** 18, 2 ** 22), "C24": (2 ** 22, 2 ** 25), "C18": (2 ** 14, 2 ** 22)}
CODE_CELL = {"C16": 16, "C18": 18, "C20": 20, "C24": 24}
CODE_ARM = {"FAM": 1, "N-A": 2, "N-B": 3, "N-B-ctrl": 4}
FROZEN = list(range(7001, 7011))
RUN_ID = {"t1-inventory": "RUN-CMFB-2373be", "t2-gate-instrument": "RUN-CMFB-5905c0",
          "t3-gate-sensitivity": "RUN-CMFB-66b0fe", "t4-measure-c16-c20": "RUN-CMFB-3dc120",
          "t5-measure-c24-fam": "RUN-CMFB-42a578", "t6-measure-c24-na": "RUN-CMFB-e13f0e",
          "t7-measure-c24-nb": "RUN-CMFB-c71d35", "t8-analysis": "RUN-CMFB-2010d3"}
MEASURE = ("t4-measure-c16-c20", "t5-measure-c24-fam", "t6-measure-c24-na", "t7-measure-c24-nb")
SRC = ["experiments/EXP-CMFB-cea1d2/implementation/" + n for n in ("driver.py", "count.py", "curves.py", "analyze.py", "check.py")] \
    + ["src/crypto_autoresearcher/__init__.py", "src/crypto_autoresearcher/parallel.py"]
DELTA, ALPHA, DRAWS, RESAMPLES, MATERIAL = 0.005, 0.05, 20000, 5000, 0.02


class Errors(list):
    def __call__(self, rule: str, msg: str) -> None:
        self.append(f"{rule}: {msg}")


# ------------------------------------------------------------------ own arithmetic
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        if not any(pow(x, 2 ** r, n) == n - 1 for r in range(1, s)):
            return False
    return True


def add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    lam = ((3 * x1 * x1 + A) * pow(2 * y1, -1, p) if (x1, y1) == (x2, y2) else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return x3, (lam * (x1 - x3) - y1) % p


def mul(k: int, P, A, p):
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R, A, p)
        if bit == "1":
            R = add(R, P, A, p)
    return R


def base_points(A, B, p, count):
    pts, x = [], 0
    while len(pts) < count:
        f = (x ** 3 + A * x + B) % p
        if f and pow(f, (p - 1) // 2, p) == 1:
            y = _sqrt(f, p)
            pts.append((x, min(y, p - y)))
        x += 1
    return pts, x


def _sqrt(f, p):
    if p % 4 == 3:
        return pow(f, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q, s = q // 2, s + 1
    z = next(z for z in range(2, p) if pow(z, (p - 1) // 2, p) == p - 1)
    c, t, r, m = pow(z, q, p), pow(f, q, p), pow(f, (q + 1) // 2, p), s
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt, i = tt * tt % p, i + 1
        b = pow(c, 2 ** (m - i - 1), p)
        r, c = r * b % p, b * b % p
        t, m = t * c % p, i
    return r


def cube_base(N: int) -> int:
    B = 1
    while B ** 3 < 6 * N:
        B += 1
    return B


def own_rng(seed, cell, arm, member, stream):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [seed + curves.SEED_OFFSET, CODE_CELL[cell], CODE_ARM[arm], member, stream])))


def rand_labels(N, B, g):
    half, chosen, seen = (N - 1) // 2, [], set()
    while len(chosen) < B:
        for c in g.integers(1, half + 1, size=B - len(chosen)):
            if int(c) not in seen:
                seen.add(int(c))
                chosen.append(int(c))
    return [c if int(s) == 0 else N - c for c, s in zip(chosen, g.integers(0, 2, size=B))]


def cov_set(labels, N):
    return len({(a + b + c) % N for a, b, c in itertools.combinations_with_replacement(labels, 3)})


def cov_sort(labels, N):
    l = np.array(labels, dtype=np.int64)
    parts = [((l[a] + l[b] + l[b:]) % N).astype(np.int32) for a in range(len(l)) for b in range(a, len(l))]
    return int(len(np.unique(np.concatenate(parts))))


def cov_independent(labels, N, cell):
    return cov_set(labels, N) if cell in ("C16", "C18", "C20") else cov_sort(labels, N)


# ------------------------------------------------------------------------- checks
def valid_instance(i: dict, e: Errors) -> None:
    p, N, A, B = i["p"], i["N"], i["A"], i["B"]
    tag = f"{i['arm']}/{i['cell']}/{i['index']}"
    lo, hi = CELLS[i["cell"]]
    if i["arm"] == "N-B-ctrl":
        hi = 2 * lo
    if not (is_prime(p) and is_prime(N)):
        e("I4", f"{tag}: p or N composite")
    if (N - p - 1) ** 2 > 4 * p:
        e("I4", f"{tag}: Hasse violated")
    if not lo < p <= hi:
        e("I4", f"{tag}: p outside the cell band")
    if not (is_prime(p) and is_prime(N)) or N % 2 == 0:
        return  # nothing below is meaningful for a composite p or an even order
    if (4 * A ** 3 + 27 * B * B) % p == 0:
        e("I4", f"{tag}: singular")
    if N % 2 == 0:
        e("I4", f"{tag}: even order, f has a root")
    r = random.Random(p * 1000003 + N)
    for _ in range(3):
        while True:
            x = r.randrange(p)
            f = (x ** 3 + A * x + B) % p
            if f and pow(f, (p - 1) // 2, p) == 1:
                break
        P = (x, _sqrt(f, p))
        if mul(N, P, A, p) is not None:
            e("I4", f"{tag}: [N]P != O (wrong twist or order)")
            break
    j_target = (1728 * 4 * A ** 3 - (-96 ** 3) * (4 * A ** 3 + 27 * B * B)) % p == 0
    if i["arm"] in ("FAM", "N-A"):
        a, b, d = i["a"], i["b"], i["d"]
        if not j_target:
            e("I4", f"{tag}: j != -96^3")
        if 4 * p != a * a + 19 * b * b or N != p + 1 - a:
            e("I4", f"{tag}: trace identity 4p = a^2 + 19b^2 / N = p+1-a fails")
        if (A, B) != (-152 * d * d, 722 * d ** 3):
            e("I4", f"{tag}: chart is not the d-twist of E_0")
        if i["arm"] == "FAM":
            t = i["t"]
            if not (t % 2 == 1 and p == 5 * t * t + 19 * t + 19 and N == 5 * t * t + 18 * t + 20 and a == t and b == t + 2):
                e("I4", f"{tag}: family formulas violated")
        elif b == a + 2 or a % 2 == 0 or b % 2 == 0 or b < 1:
            e("I4", f"{tag}: N-A parity / b != a + 2 violated")
    else:
        if j_target:
            e("I4", f"{tag}: N-B curve has j = -96^3")
        if N == p:
            e("I4", f"{tag}: anomalous N-B curve")


def manifest_checks(run_dir: Path, trial: str, e: Errors, allow_dev: bool):
    mp, rp = run_dir / "manifest.yaml", run_dir / "raw-result.json"
    if not mp.is_file() or not rp.is_file() or mp.stat().st_size == 0 or rp.stat().st_size == 0:
        e("I1", "manifest.yaml or raw-result.json missing or empty")
        return None, None
    try:
        m = yaml.safe_load(mp.read_text())["run"]
        raw = json.loads(rp.read_text())
    except (ValueError, KeyError, TypeError, yaml.YAMLError) as err:
        e("I1", f"unparseable outputs: {err}")
        return None, None
    try:
        needed = (m["code"]["command"], m["code"]["commit"], m["environment"], m["seeds"], m["timing"]["wall_seconds"],
                  m["resources"]["peak_rss_bytes"])
        if not all(needed[:4]) or needed[4] is None or not isinstance(needed[5], int) or needed[5] <= 0:
            raise KeyError("empty")
        if not isinstance(m["code"]["dirty"], bool):
            raise KeyError("dirty")
    except (KeyError, TypeError):
        e("I1", "manifest lacks command, git commit/dirty, environment, seeds, timings or peak_rss_bytes")
    if m.get("experiment_id") != curves.EXPERIMENT_ID or m.get("trial_id") != trial or m.get("id") != RUN_ID[trial]:
        e("I1", "manifest identity (experiment, trial, run id) differs from the plan")
    if run_dir.name != RUN_ID[trial] and not allow_dev:
        e("I1", f"run directory {run_dir.name} is not {RUN_ID[trial]}")
    if m.get("seeds") != FROZEN or raw.get("seeds") != FROZEN:
        e("I8", "seeds differ from the frozen list 7001..7010")
    if curves.SEED_OFFSET != 0 and not allow_dev:
        e("I8", "seed offset is active")
    if not allow_dev and (raw.get("official") is not True or raw.get("K") not in (200, None)):
        e("I11", "non-official (development) output")
    # I11: the sources that ran are the sources bound in the frozen plan
    if PLAN.is_file() and not allow_dev:
        plan = json.loads(PLAN.read_text())
        for f, h in plan.get("source_sha256", {}).items():
            if (REPO / f).is_file() and hashlib.sha256((REPO / f).read_bytes()).hexdigest() != h:
                e("I11", f"{f} differs from the sha256 bound in trial-plan.json")
            if m.get("code", {}).get("source_sha256", {}).get(f) not in (None, h):
                e("I11", f"{f}: the run executed a different source than the plan binds")
    return m, raw


def sibling(run_dir: Path, trial: str):
    f = run_dir.parent / RUN_ID[trial] / "raw-result.json"
    return json.loads(f.read_text()) if f.is_file() else None


def instances_ok(raw: dict, trial: str, run_dir: Path, e: Errors, allow_dev: bool):
    inv = curves.build_instances()
    if raw.get("instance_list_sha256") != inv["sha256"]:
        e("I8", "instance-list sha256 differs from the recomputation from the seeds")
    if trial != "t1-inventory":
        t1 = sibling(run_dir, "t1-inventory")
        if t1 is None:
            if not allow_dev:
                e("I8", "t1-inventory raw-result.json not found beside this run")
        elif t1.get("instance_list_sha256") != raw.get("instance_list_sha256"):
            e("I8", "instance-list sha256 differs from the one recorded by t1-inventory")
    return inv


def check_t1(raw, inv, e):
    fam = [t for t in range(3, 2601, 2) if is_prime(5 * t * t + 19 * t + 19) and is_prime(5 * t * t + 18 * t + 20)]
    rec = [m["t"] for m in raw["inventory"]["fam_members"]]
    if rec != fam:
        e("I8", "FAM sieve differs from the independent sieve")
    counts = {c: sum(1 for t in fam if CELLS[c][0] < 5 * t * t + 19 * t + 19 <= CELLS[c][1]) for c in ("C16", "C20", "C24")}
    if raw["inventory"]["counts"] != counts:
        e("I8", "member counts differ from the sieve")
    pooled = counts["C16"] < 8 and counts["C20"] < 8 and counts["C16"] + counts["C20"] >= 8
    if (raw["inventory"]["pooling"]["branch"] == "P1_pooled_C18") != pooled:
        e("I8", "pooling rule P1 evaluated wrongly")
    if len(raw["instances"]) != len(inv["instances"]):
        e("I8", "instance count differs from the quotas")
    seen = {}
    for i in raw["instances"]:
        valid_instance(i, e)
        if not i["validity"]["ok"]:
            e("I4", "driver-recorded validity is false")
        if i["arm"] in ("N-A", "N-B"):
            if i["p"] in seen.setdefault((i["arm"], i["cell"]), set()):
                e("I4", f"repeated prime in {i['arm']}/{i['cell']}")
            seen[(i["arm"], i["cell"])].add(i["p"])


def pooled(scans):
    S, L = sum(s["S"] for s in scans), sum(s["L"] for s in scans)
    V, Vl = sum(s["V"] for s in scans), sum(s["Vlift"] for s in scans)
    return S / L, (Vl / V) / (L / S)


def py_scan(A, B, p, S):
    L = V = Vl = 0
    for x in range(S):
        sq = pow((x ** 3 + A * x + B) % p, (p - 1) // 2, p) == 1
        inv = pow(x, (p - 1) // 2, p) != p - 1
        L += sq
        V += inv
        Vl += sq and inv
    return L, V, Vl


def check_t2(raw, inv, e):
    c = raw["controls"]
    bf = c["brute_force"]
    if bf["cases"] != 60 or len(bf["detail"]) != 60 or bf["failures"] != 0:
        e("I3", "brute-force counter check is not 60 clean cases")
    for case in bf["detail"]:
        N, lab = case["N"], case["labels"]
        cnt: dict = {}
        for t in itertools.combinations_with_replacement(lab, 3):
            r = sum(t) % N
            cnt[r] = cnt.get(r, 0) + 1
        if len(cnt) != case["coverage"] or sum(cnt.values()) != comb(len(lab) + 2, 3) or not case["ok"]:
            e("I3", f"brute-force case N={N} B={len(lab)} {case['kind']} disagrees")
        if case["kind"] == "arithmetic_progression" and lab != list(range(1, len(lab) + 1)):
            e("I3", "AP case is not {1..B}")
    if c["instances"]["failures"] or c["instances"]["checked"] != len(inv["instances"]):
        e("I4", "instrument instance validity failed or is incomplete")
    for x in c["labelling"]:
        if not x["check"]["ok"]:
            e("I5", f"labelling check failed {x['arm']}/{x['cell']}/{x['index']}")
    if not c["labelling"]:
        e("I5", "no labelling check recorded")
    byk = {(i["arm"], i["cell"], i["index"]): i for i in inv["instances"]}
    for r in c["m0_recount"]:
        i = byk[(r["arm"], r["cell"], r["index"])]
        B = cube_base(i["N"])
        T = comb(B + 2, 3)
        if r["m0"]["loop_failures"] or r["m0"]["hist_failures"]:
            e("I2", f"M0 failure in the recount of {r['arm']}/{r['cell']}/{r['index']}")
        for h in r["hist"]:
            if h["total"] != T or h["nonzero"] != h["seen"] or h["collisions"] < T - h["nonzero"] or not h["ok"]:
                e("I2", f"histogram identity fails for {r['arm']}/{r['cell']}/{r['index']} {h['base']}")
        if len(r["hist"]) != 3:
            e("I2", "histogram recount must cover three designated bases")
    scans = c["qr_scans"]
    ins = [i for i in inv["instances"] if i["arm"] != "N-B-ctrl"]
    if sorted((s["arm"], s["cell"], s["index"]) for s in scans) != sorted((i["arm"], i["cell"], i["index"]) for i in ins):
        e("I8", "qr scans do not cover the instance list")
    for arm in ("FAM", "N-A", "N-B"):
        for cell in inv["plan"]["cells"]:
            sel = [s["scan"] for s in scans if s["arm"] == arm and s["cell"] == cell]
            if not sel:
                continue
            R, Rw = pooled(sel)
            if arm == "N-B" and not (1.98 <= R <= 2.02 and 0.96 <= Rw <= 1.04):
                e("I6", f"N-B pool {cell}: R_pool={R:.4f}, R_wrong={Rw:.4f} outside the bands")
            # independent pure-Python recomputation of one curve of the pool
            s = next(s for s in scans if s["arm"] == arm and s["cell"] == cell)
            i = byk[(arm, cell, s["index"])]
            Lr, Vr, Vlr = py_scan(i["A"], i["B"], i["p"], min(131072, i["p"] // 2))
            if (Lr, Vr, Vlr) != (s["scan"]["L"], s["scan"]["V"], s["scan"]["Vlift"]):
                e("I9", f"qr scan of {arm}/{cell}/{s['index']} disagrees with the independent recomputation")
    if not all(s["scan"]["lifts_ok"] and s["scan"]["zero"] == 0 for s in scans):
        e("I6", "a lifted y has y^2 != f(x)")
    fp = c["full_period"]
    if not fp or not all(x["ok"] for x in fp):
        e("I6", "full-period point-count identity failed")
    for x in fp:
        if x["L"] != (x["N"] - 1) // 2 or x["chi_sum"] != x["N"] - x["p"] - 1 or x["zero"] != 0:
            e("I6", f"full-period identity wrong for {x['arm']}/{x['cell']}/{x['index']}")
    small = [x for x in fp if x["p"] <= 2 ** 14 * 4]
    for x in small[:1]:
        i = byk[(x["arm"], x["cell"], x["index"])]
        tot = sum(1 if pow((t ** 3 + i["A"] * t + i["B"]) % i["p"], (i["p"] - 1) // 2, i["p"]) == 1 else 0 for t in range(i["p"]))
        if tot != x["L"]:
            e("I6", "full-period count disagrees with the independent recomputation")
    if not c["determinism"]["passed"]:
        e("I8", "parallel.verify_determinism failed")
    if not raw.get("gate_passed"):
        e("R1", "t2 gate failed: " + ", ".join(k for k, v in raw["gates"].items() if not v))


def planted_stats(recs, cells, e):
    """Independent recomputation of the sensitivity table (own randomization test)."""
    out = {}
    for cell in cells:
        rs = sorted((r for r in recs if r["cell"] == cell), key=lambda r: r["index"])
        V, ratios, known, det = [], [], [], 0
        for r in rs:
            rnd = np.array(r["random_seen"], float)
            N, B = r["N"], cube_base(r["N"])
            mu = comb(B + 2, 3) / N
            kn = (1 - math.exp(-mu * (B + 3) / B)) / (1 - math.exp(-mu))
            k_ge = int((rnd >= r["member_seen"]).sum())
            det += (1 + k_ge) / (len(rnd) + 1) <= 0.01
            V.append([r["member_seen"]] + list(rnd))
            ratios.append(r["member_seen"] / rnd.mean())
            known.append(kn)
        V, ratios, known = np.array(V, float), np.array(ratios), np.array(known)
        se = ratios.std(ddof=1) / math.sqrt(len(ratios))
        g = own_rng(7007, cell, "N-B-ctrl", 0, 0)
        n = len(V)
        t_obs = float(np.mean(V[:, 0] / V[:, 1:].mean(axis=1) - 1))
        u = g.integers(0, V.shape[1], size=(DRAWS, n))
        pick = V[np.arange(n)[None, :], u]
        ts = (pick / ((V.sum(axis=1)[None, :] - pick) / (V.shape[1] - 1)) - 1).mean(axis=1)
        p = (1 + int((np.abs(ts) >= abs(t_obs)).sum())) / (DRAWS + 1)
        ok = (n == 8 and det >= 7 and abs(ratios.mean() - known.mean()) <= max(0.001, 3 * se) and p <= 0.001)
        out[cell] = {"detected": int(det), "ratio": float(ratios.mean()), "known": float(known.mean()), "p": p, "ok": bool(ok)}
        if not ok:
            e("I7", f"sensitivity control fails in {cell}: detected {det}/8, pooled {ratios.mean():.5f} vs {known.mean():.5f}, p={p:.2g}")
    return out


def member_checks(members, inv, e, trial_scope, allow_dev):
    byk = {(i["arm"], i["cell"], i["index"]): i for i in inv["instances"]}
    got = sorted((m["arm"], m["cell"], m["index"], m["p"], m["N"], m["A"], m["B"], m["d"]) for m in members)
    want = sorted((i["arm"], i["cell"], i["index"], i["p"], i["N"], i["A"], i["B"], i["d"]) for i in trial_scope)
    if got != want:
        e("I8", "member set differs from the frozen instance list / quotas")
    done: dict = {}
    for m in members:
        tag = f"{m['arm']}/{m['cell']}/{m['index']}"
        N, p, A, Bc = m["N"], m["p"], m["A"], m["B"]
        valid_instance(m, e)
        B = cube_base(N)
        planted = m["arm"] == "N-B-ctrl"
        size = B + 1 if planted else B
        T = comb(B + 2, 3)
        if m["base_size"] != B or m["T"] != T or m["member_base_size"] != size or m["member_T"] != comb(size + 2, 3):
            e("I2", f"{tag}: base size B / T wrong")
        if len(m["random_seen"]) != 200 and not allow_dev:
            e("I8", f"{tag}: number of random bases")
        if m["m0"]["loop_failures"] or m["m0"]["hist_failures"] or m["m0"]["bases"] != len(m["random_seen"]) + 1:
            e("I2", f"{tag}: M0 loop counter or histogram identity failed")
        if m["hist"]:
            names = sorted(h["base"] for h in m["hist"])
            if names != ["member", "rand1", "rand2"]:
                e("I2", f"{tag}: designated histogram bases")
            for h in m["hist"]:
                tt = m["member_T"] if h["base"] == "member" else T
                ss = m["member_seen"] if h["base"] == "member" else m["random_seen"][int(h["base"][-1]) - 1]
                if h["total"] != tt or h["nonzero"] != ss or h["seen"] != ss or h["collisions"] < tt - ss:
                    e("I2", f"{tag}: histogram recount {h['base']} differs from the seen[] count")
        if m["random_distinct_failures"]:
            e("I8", f"{tag}: random base with repeated classes")
        # labelling, independent: rebuild the base, check [l]g = Q for ALL points and 64 triples
        pts, W = base_points(A, Bc, p, size)
        lab = m["labels"]
        if len(lab) != size or lab[0] != 1 or len({min(x, N - x) for x in lab}) != size or W != m["window_W"]:
            e("I5", f"{tag}: labels / window do not match the recomputed base")
            continue
        g = pts[0]
        if any(mul(l, g, A, p) != Q for l, Q in zip(lab, pts)):
            e("I5", f"{tag}: [l(Q)]g != Q for some point")
        rr = random.Random(N * 31 + p)
        for _ in range(64):
            i, j, k = (rr.randrange(size) for _ in range(3))
            S = add(add(pts[i], pts[j], A, p), pts[k], A, p)
            if S != mul((lab[i] + lab[j] + lab[k]) % N, g, A, p):
                e("I5", f"{tag}: sampled triple differs from [l_i+l_j+l_k]g")
                break
        if not (m["label_check"]["ok"] and m["validity"]["ok"] and m["distinct_classes"]):
            e("I5", f"{tag}: driver-recorded label/validity flag false")
        done[(m["arm"], m["cell"])] = done.get((m["arm"], m["cell"]), []) + [m]
    # I9: second code path for 3 members per arm and cell
    for (arm, cell), ms in done.items():
        ms = sorted(ms, key=lambda m: m["index"])
        for m in [ms[j] for j in curves.spread(len(ms), 3)]:
            if cov_independent(m["labels"], m["N"], cell) != m["member_seen"]:
                e("I9", f"{arm}/{cell}/{m['index']}: member coverage differs from the second code path")
            B = cube_base(m["N"])
            lb = rand_labels(m["N"], B, own_rng(7005, cell, arm, m["index"], 2))
            if cov_independent(lb, m["N"], cell) != m["random_seen"][0]:
                e("I9", f"{arm}/{cell}/{m['index']}: random base 1 differs from the second code path")
            S = min(131072, m["p"] // 2)
            if S <= 40000 and py_scan(m["A"], m["B"], m["p"], S)[0] != m["scan"]["L"]:
                e("I9", f"{arm}/{cell}/{m['index']}: scan disagrees with the second code path")


def check_timing(raw, e):
    t = raw.get("timings", {})
    if "stages" not in t:
        e("I1", "no stage timings")
    if "per_member" in t and t["per_member"] and not (t.get("tau_seconds_per_triple") or 0) > 0:
        e("I1", "measured seconds per triple missing")


# --------------------------------------------------------------------- t8 recompute
def holm_adj(ps: dict) -> dict:
    out, run = {}, 0.0
    items = sorted(ps.items(), key=lambda kv: (kv[1], kv[0]))
    for r, (k, p) in enumerate(items):
        run = max(run, min(1.0, (len(items) - r) * p))
        out[k] = run
    return out


def blocks(n, L, g, R):
    L = min(L, n)
    if L == 1:
        return g.integers(0, n, size=(R, n))
    nb = -(-n // L)
    s = g.integers(0, n - L + 1, size=(R, nb))
    return (s[:, :, None] + np.arange(L)).reshape(R, nb * L)[:, :n]


def pct(d, level):
    a = 50 * (1 - level)
    lo, hi = np.percentile(d, [a, 100 - a])
    return float(lo), float(hi)


def close(a, b, tol=1e-9):
    return a == b or (a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b)))


def check_t8(raw, run_dir, inv, e, allow_dev):
    runs = {}
    for t in RUN_ID:
        if t == "t8-analysis":
            continue
        f = run_dir.parent / RUN_ID[t] / "raw-result.json"
        if not f.is_file():
            e("R0", f"{t} raw-result.json missing")
            return
        runs[t] = json.loads(f.read_text())
        if not (run_dir.parent / RUN_ID[t] / "manifest.yaml").is_file():
            e("I1", f"{t} manifest.yaml missing")
    if raw.get("classification") == "INCOMPLETE":
        e("R0", "analysis reports an incomplete run set")
        return
    if not allow_dev and raw.get("all_inputs_official") is not True:
        e("I11", "t8 was computed from non-official inputs")
    members = [m for t in MEASURE for m in runs[t]["members"]]
    tables = raw["tables"]
    cells = inv["plan"]["cells"]
    M = inv["counts"]
    Mc = {c: (M[c] if c in M else M["C16"] + M["C20"]) for c in cells}
    rec_T, rec_ci, rec_p = {}, {}, {}
    cell_pow = {}
    for cell in cells:
        arms = {}
        for arm in ("FAM", "N-A", "N-B"):
            mem = sorted((m for m in members if m["arm"] == arm and m["cell"] == cell), key=lambda m: m["index"])
            if not mem:
                continue
            V = np.array([[m["member_seen"]] + m["random_seen"] for m in mem], float)
            ratio = V[:, 0] / V[:, 1:].mean(axis=1)
            x = ratio - 1
            L = 3 if arm == "FAM" else 1
            ci = pct(x[blocks(len(x), L, own_rng(7006, cell, arm, 0, 0), RESAMPLES)].mean(axis=1), 0.95)
            n = len(mem)
            u = own_rng(7007, cell, arm, 0, 0).integers(0, V.shape[1], size=(DRAWS, n))
            pick = V[np.arange(n)[None, :], u]
            ts = (pick / ((V.sum(axis=1)[None, :] - pick) / (V.shape[1] - 1)) - 1).mean(axis=1)
            p = (1 + int((np.abs(ts) >= abs(x.mean())).sum())) / (DRAWS + 1)
            sig = np.sqrt(np.mean([(np.std(V[j, 1:], ddof=1) / V[j, 1:].mean()) ** 2 for j in range(n)]))
            arms[arm] = (n, x, ci, p, sig, [math.log2(m["p"]) for m in mem])
        cell_pow[cell] = (Mc[cell] >= 8 and len(arms) == 3 and all(a[0] >= 8 for a in arms.values())
                          and all(1.0025 * math.sqrt(3) * 3.61 * a[4] / math.sqrt(a[0]) <= DELTA / 2 for a in arms.values()))
        for arm, (n, x, ci, p, sig, lg) in arms.items():
            rec_T[(arm, cell)], rec_ci[(arm, cell)], rec_p[(arm, cell)] = x, ci, p
            row = tables.get(f"{arm}|{cell}")
            if row is None or not (close(row["T"], float(x.mean())) and close(row["ci95"][0], ci[0]) and close(row["ci95"][1], ci[1])
                                   and close(row["randomization_p"], p) and row["n"] == n):
                e("I9", f"t8 table {arm}|{cell} differs from its recomputation")
    powered = [c for c in cells if cell_pow[c]]
    if sorted(raw["powered_cells"]) != sorted(powered):
        e("I9", "powered cells differ from the recomputation")
    adj = holm_adj({k: rec_p[k] for k in rec_p if k[1] in powered})
    exc, dfc, inside, rej = [], [], True, []
    for k, a in adj.items():
        T = float(rec_T[k].mean())
        row = tables[f"{k[0]}|{k[1]}"]
        if not close(row["holm_p"], a):
            e("I9", f"Holm-adjusted p of {k} differs from the recomputation")
        if a <= ALPHA:
            rej.append(k)
            if T > DELTA:
                exc.append(k)
            if T < -DELTA:
                dfc.append(k)
        inside = inside and rec_ci[k][0] >= -DELTA and rec_ci[k][1] <= DELTA
    # gates re-derived from the raw trials
    ps = planted_stats(runs["t3-gate-sensitivity"]["members"], cells, e)
    for cell, v in ps.items():
        if raw["sensitivity"][cell]["detected"] != v["detected"] or not close(raw["sensitivity"][cell]["randomization_p"], v["p"]):
            e("I9", f"t8 sensitivity table for {cell} differs from its recomputation")
    scans = runs["t2-gate-instrument"]["controls"]["qr_scans"]
    for k, v in raw["scan_efficiency"]["pools"].items():
        arm, cell = k.split("|")
        R, Rw = pooled([s["scan"] for s in scans if s["arm"] == arm and s["cell"] == cell])
        if not (close(v["R_pool"], R) and close(v["R_wrong"], Rw)):
            e("I9", f"t8 scan pool {k} differs from its recomputation")
    by_scan = {(s["arm"], s["cell"], s["index"]): s["scan"] for s in scans}
    for m in members:
        if by_scan.get((m["arm"], m["cell"], m["index"])) != m["scan"]:
            e("I9", "member scan differs between t2 and the measurement trial")
            break
    # contrasts (99 percent) recomputed for every powered cell
    def xs(arm, cell, stratum=None):
        mem = sorted((m for m in members if m["arm"] == arm and m["cell"] == cell and (stratum is None or m["stratum"] == stratum)),
                     key=lambda m: m["index"])
        V = np.array([[m["member_seen"]] + m["random_seen"] for m in mem], float)
        return V[:, 0] / V[:, 1:].mean(axis=1) - 1

    spec = {"fam_na": ("FAM", None, "N-A", None), "fam_natheta": ("FAM", None, "N-A", "theta"), "na_nb": ("N-A", None, "N-B", None)}
    con = {}
    for cell in powered:
        for name, (a1, s1, a2, s2) in spec.items():
            x1, x2 = xs(a1, cell, s1), xs(a2, cell, s2)
            g = own_rng(7006, cell, a1, 0, {"fam_na": 1, "fam_natheta": 2, "na_nb": 3}[name])
            d1 = x1[blocks(len(x1), 3 if a1 == "FAM" else 1, g, RESAMPLES)].mean(axis=1)
            d2 = x2[blocks(len(x2), 3 if a2 == "FAM" else 1, g, RESAMPLES)].mean(axis=1)
            lo, hi = pct(d1 - d2, 0.99)
            con[f"{name}|{cell}"] = (float(x1.mean() - x2.mean()), lo, hi)
            c = raw["contrasts"].get(f"{name}|{cell}")
            if c is None or not (close(c["ci99"][0], lo) and close(c["ci99"][1], hi) and close(c["estimate"], con[f"{name}|{cell}"][0])):
                e("I9", f"contrast {name}|{cell} differs from its recomputation")
    # size slope of the FAM arm (needs three powered cells)
    slope_pos = False
    if len(powered) >= 3:
        parts = [(np.array([math.log2(m["p"]) for m in sorted((m for m in members if m["arm"] == "FAM" and m["cell"] == c),
                                                               key=lambda m: m["index"])]), xs("FAM", c)) for c in powered]
        g = own_rng(7006, "C24", "FAM", 0, 4)
        ix = [blocks(len(a), 3, g, RESAMPLES) for a, _ in parts]
        def ols(a, b):
            ac = a - a.mean()
            return float((ac * (b - b.mean())).sum() / (ac * ac).sum())
        sl = [ols(np.concatenate([a[i[r]] for (a, _), i in zip(parts, ix)]), np.concatenate([b[i[r]] for (_, b), i in zip(parts, ix)]))
              for r in range(RESAMPLES)]
        slope_pos = pct(np.array(sl), 0.95)[0] > 0
        if raw["slopes"]["FAM"].get("positive") != slope_pos:
            e("I9", "FAM slope sign of the lower bound differs from the recomputation")
    # the mechanical classification, recomputed
    cl = raw["classification"]
    rules_ok = all(raw["rules"].values())
    if not allow_dev and not rules_ok and cl != "INSTRUMENT_VOID":
        e("R1", "a rule or gate fails but the classification is not INSTRUMENT_VOID")
    if rules_ok:
        def lead_ok(name, cell):
            c = con.get(f"{name}|{cell}")
            return c is not None and (c[1] > 0 or c[2] < 0) and c[1] > DELTA
        if not powered:
            want = "INCONCLUSIVE_UNDERPOWERED"
        elif not exc and not dfc and inside:
            want = "NULL_AT_RESOLUTION"
        elif not exc and not dfc and not rej:
            want = "INCONCLUSIVE_UNRESOLVED"
        elif exc:
            if any(k[0] == "N-B" for k in exc):
                want = "E1_LEAD"
            elif any(k[0] == "N-A" and lead_ok("na_nb", k[1]) for k in exc):
                want = "E2_LEAD"
            elif all(k[0] == "FAM" for k in exc) and any(lead_ok("fam_na", k[1]) for k in exc):
                want = "E3_LEAD"
            else:
                want = "INCONCLUSIVE_UNATTRIBUTED"
            if want != "INCONCLUSIVE_UNATTRIBUTED":
                big = any(k[0] == "FAM" and float(rec_T[k].mean()) >= MATERIAL for k in rec_T if k[1] in powered)
                tier = "MATERIAL" if big and slope_pos else "SUB-THRESHOLD"
                if raw.get("lead_tier") != tier:
                    e("I9", f"lead tier {raw.get('lead_tier')} differs from the recomputed {tier}")
        elif dfc:
            want = "DEFICIT_RECORDED"
        else:
            want = "INCONCLUSIVE_UNRESOLVED"
        if cl != want:
            e("I9", f"classification {cl} differs from the recomputed {want}")


def check_run(run_dir: Path, allow_dev: bool = False) -> list[str]:
    e = Errors()
    run_dir = Path(run_dir)
    trial = next((t for t, r in RUN_ID.items() if r == run_dir.name), None)
    mp = run_dir / "manifest.yaml"
    if trial is None and mp.is_file():
        try:
            trial = yaml.safe_load(mp.read_text())["run"]["trial_id"]
        except (KeyError, TypeError, yaml.YAMLError):
            trial = None
    if trial not in RUN_ID:
        return ["I1: cannot identify the trial of this run directory"]
    m, raw = manifest_checks(run_dir, trial, e, allow_dev)
    if raw is None:
        return list(e)
    check_timing(raw, e)
    inv = instances_ok(raw, trial, run_dir, e, allow_dev)
    if trial == "t1-inventory":
        check_t1(raw, inv, e)
    elif trial == "t2-gate-instrument":
        check_t2(raw, inv, e)
    elif trial == "t3-gate-sensitivity":
        ctrl = [i for i in inv["instances"] if i["arm"] == "N-B-ctrl"]
        member_checks(raw["members"], inv, e, ctrl, allow_dev)
        planted_stats(raw["members"], inv["plan"]["cells"], e)
        if not raw.get("gate_passed"):
            e("R1", "t3 gate failed: " + ", ".join(k for k, v in raw["gates"].items() if not v))
    elif trial in MEASURE:
        member_checks(raw["members"], inv, e, curves.select_for_trial(trial, inv["instances"]), allow_dev)
    else:
        check_t8(raw, run_dir, inv, e, allow_dev)
    return list(e)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 2
    errors = check_run(Path(sys.argv[1]))
    for line in errors:
        print(line, file=sys.stderr)
    print("check: " + ("FAILED (%d)" % len(errors) if errors else "ok"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EXP-CERTBIN-66e167 Stages 0-2: HEUR-1 n=19 replication.

Successor to EXP-CERTBIN-9ea3d0 after EV-CERTBIN-db7f15 weaken.
New seeds; Stage-0 freeze locked (Stages 1-2 do not rewrite Stage 0).
n=17 unpooled. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve, find_prime_order_generator, is_prime
from gf2n import Field, TableField, is_irreducible
import hashlib

PRED_NAME = "preregistered-predictions.json"
PRED_SHA_NAME = "preregistered-predictions.sha256"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_freeze_sha(root: Path) -> str:
    pred = root / "stage0" / PRED_NAME
    digest = sha256_file(pred)
    (root / "stage0" / PRED_SHA_NAME).write_text(digest + "\n")
    return digest


def assert_freeze_locked(root: Path) -> str:
    """Refuse if Stage-0 predictions were rewritten after freeze."""
    pred = root / "stage0" / PRED_NAME
    sha_path = root / "stage0" / PRED_SHA_NAME
    if not pred.exists() or not sha_path.exists():
        raise RuntimeError("Stage-0 freeze missing; run Stage 0 first")
    expected = sha_path.read_text().strip()
    observed = sha256_file(pred)
    if observed != expected:
        raise RuntimeError(
            f"Stage-0 freeze rewritten: expected {expected}, got {observed}"
        )
    return observed


def load_frozen_cell(root: Path) -> dict:
    """Reconstruct Stage-0 cell without rewriting Stage-0 artifacts."""
    assert_freeze_locked(root)
    pred = json.loads((root / "stage0" / PRED_NAME).read_text())
    cell_path = root / "stage0" / "cell-n19.json"
    if not cell_path.exists():
        raise RuntimeError("stage0/cell-n19.json missing")
    art = json.loads(cell_path.read_text())
    cell19 = setup_cell(N19, MOD19, SEEDS["primary"], require_prime_r=True)
    if cell19["r_work"] != pred["r19"] or art.get("C_eff_n19") != pred["C_eff_n19"]:
        raise RuntimeError("live cell disagrees with frozen Stage-0 prediction")
    return {
        "pred": pred,
        "art": art,
        "cell19": cell19,
        "C19": pred["C_eff_n19"],
        "freeze_sha256": assert_freeze_locked(root),
    }


EXP_ID = "EXP-CERTBIN-66e167"
H_ID = "H-CERTBIN-c50454"
DEC_ID = "DEC-20261003-fa8703"
TASK_ID = "TASK-20261003-69a04e"
AMAZON_BEDROCK = "NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED."

N19, MOD19 = 19, (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1
N17, MOD17 = 17, (1 << 17) | (1 << 3) | 1
ORDER19_EXPECTED = 523492
R19_EXPECTED = 130873
SEEDS = {"primary": 2026100311, "holdout": 2026100312, "zr_control": 2026100313}
EXCLUDED_PREDECESSOR_SEEDS = (2026100301, 2026100302, 2026100303)
assert set(SEEDS.values()).isdisjoint(EXCLUDED_PREDECESSOR_SEEDS)
M = 3
K_LIST = (2, 3)


def comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


def stars_and_bars(B: int, m: int = M) -> int:
    return comb(B + m - 1, m)


def birthday_expectation(C: int, r: int) -> float:
    return C * (C - 1) / (2.0 * r)


def smallest_C_eff(r: int, lo: float = 5.0, hi: float = 50.0) -> tuple[int, float]:
    C = 2
    while birthday_expectation(C, r) < lo:
        C += 1
        if C > 10**7:
            raise RuntimeError("C_eff search diverged")
    exp = birthday_expectation(C, r)
    if exp > hi:
        raise RuntimeError(f"smallest C with exp>={lo} already exceeds {hi}: C={C} exp={exp}")
    return C, exp


def unrank_multiset(rank: int, B: int, m: int = M) -> tuple[int, ...]:
    n = B + m - 1
    combo = []
    rem = rank
    for i in range(m, 0, -1):
        c = i - 1
        while comb(c + 1, i) <= rem:
            c += 1
        combo.append(c)
        rem -= comb(c, i)
    combo.reverse()
    return tuple(combo[i] - i for i in range(m))


def sample_multiset_ranks(rng: random.Random, Mtot: int, C_eff: int) -> list[int]:
    if C_eff > Mtot:
        raise RuntimeError(f"C_eff={C_eff} exceeds multiset budget {Mtot}")
    return rng.sample(range(Mtot), C_eff)


def frob_point(F, P):
    if P is None:
        return None
    return (F.sqr(P[0]), F.sqr(P[1]))


def kernel_sum(curve: Curve, P):
    tauP = frob_point(curve.F, P)
    tau2P = frob_point(curve.F, tauP)
    return curve.add(curve.mul(2, P), curve.add(tauP, tau2P))


def point_key(P) -> str:
    if P is None:
        return "O"
    return f"{P[0]},{P[1]}"


def build_dl_table(curve: Curve, G, r: int) -> dict[str, int]:
    table = {point_key(None): 0}
    P = G
    for i in range(1, r):
        table[point_key(P)] = i
        P = curve.add(P, G)
    if P is not None:
        raise RuntimeError("generator order is not r")
    return table


def lambda_of(curve: Curve, G, table: dict[str, int], r: int) -> int:
    FG = frob_point(curve.F, G)
    k = point_key(FG)
    if k not in table:
        raise RuntimeError("Frobenius(G) not in prime-order subgroup table")
    lam = table[k]
    if (lam * lam + lam + 2) % r != 0:
        raise RuntimeError(f"lambda={lam} does not satisfy lambda^2+lambda+2=0 mod r={r}")
    return lam


def orbit_union(curve: Curve, gens: list, n: int) -> list:
    seen = set()
    pts = []
    for G in gens:
        P = G
        for _ in range(n):
            for Q in (P, curve.neg(P)):
                k = point_key(Q)
                if k not in seen and Q is not None:
                    seen.add(k)
                    pts.append(Q)
            P = frob_point(curve.F, P)
    return pts


def kernel_vectors(curve: Curve, gens: list, index: dict[str, int], B: int, r: int, lam: int) -> list[list[int]]:
    vecs = []
    for G in gens:
        v = [0] * B
        pts = [G, frob_point(curve.F, G), frob_point(curve.F, frob_point(curve.F, G))]
        coeffs = [2 % r, 1, 1]
        ok = True
        for P, c in zip(pts, coeffs):
            k = point_key(P)
            if k not in index:
                ok = False
                break
            v[index[k]] = (v[index[k]] + c) % r
        if ok:
            vecs.append(v)
    return vecs


def mat_rank(rows: list[list[int]], r: int) -> int:
    if not rows:
        return 0
    A = [row[:] for row in rows]
    m, n = len(A), len(A[0])
    rank = 0
    col = 0
    while rank < m and col < n:
        piv = None
        for i in range(rank, m):
            if A[i][col] % r:
                piv = i
                break
        if piv is None:
            col += 1
            continue
        A[rank], A[piv] = A[piv], A[rank]
        inv = pow(A[rank][col], -1, r)
        A[rank] = [(A[rank][j] * inv) % r for j in range(n)]
        for i in range(m):
            if i == rank:
                continue
            f = A[i][col] % r
            if f:
                A[i] = [(A[i][j] - f * A[rank][j]) % r for j in range(n)]
        rank += 1
        col += 1
    return rank


def multiplicity(ms: tuple[int, ...], B: int) -> list[int]:
    v = [0] * B
    for i in ms:
        v[i] += 1
    return v


def setup_cell(n: int, mod: int, seed: int, require_prime_r: bool):
    irr_ok, irr = is_irreducible(mod)
    if not irr_ok:
        raise RuntimeError(f"n={n} modulus not irreducible: {irr}")
    try:
        F = TableField(n, mod)
    except ValueError:
        F = Field(n, mod)
    curve = Curve(F, 0, 1)
    order = curve.count_by_trace()
    if n == 19 and order != ORDER19_EXPECTED:
        raise RuntimeError(f"n=19 order {order} != {ORDER19_EXPECTED}")
    if order % 4 != 0:
        raise RuntimeError(f"n={n} order {order} not divisible by 4")
    odd = order // 4
    G, ell = find_prime_order_generator(curve, order, 4, seed=seed)
    if require_prime_r:
        if not is_prime(odd):
            raise RuntimeError(f"n={n} odd order {odd} is not prime")
        if ell != odd:
            raise RuntimeError(f"n={n} generator order {ell} != {odd}")
        if n == 19 and ell != R19_EXPECTED:
            raise RuntimeError(f"n=19 r {ell} != {R19_EXPECTED}")
    r_work = ell
    return {
        "n": n,
        "mod": mod,
        "order": order,
        "odd_part": odd,
        "r_work": r_work,
        "r_is_prime": bool(is_prime(r_work)),
        "curve": curve,
        "F": F,
        "G": G,
        "irreducibility": irr,
        "seed": seed,
    }


def census_one(cell: dict, k: int, seed: int, C_eff: int, need_logs: bool) -> dict:
    rng = random.Random(seed + 17 * k)
    curve = cell["curve"]
    n = cell["n"]
    r = cell["r_work"]
    gens = []
    used = set()
    while len(gens) < k:
        x = rng.randrange(1, cell["F"].q)
        P = curve.lift_x(x)
        if P is None:
            continue
        Q = curve.mul(cell["order"] // r, P) if cell["order"] % r == 0 else curve.mul(4, P)
        if Q is None:
            continue
        if curve.mul(r, Q) is not None:
            continue
        key = point_key(Q)
        if key in used:
            continue
        used.add(key)
        gens.append(Q)
    for P in gens[:2]:
        if kernel_sum(curve, P) is not None:
            raise RuntimeError("kernel check failed: 2P+tau(P)+tau^2(P) != O")
    pts = orbit_union(curve, gens, n)
    B_phys = len(pts)
    Mtot = stars_and_bars(B_phys, M)
    ranks = sample_multiset_ranks(rng, Mtot, C_eff)
    multisets = [unrank_multiset(rk, B_phys, M) for rk in ranks]
    additions = 0
    fibers: dict[str, list[int]] = defaultdict(list)
    sums = []
    for ti, ms in enumerate(multisets):
        S = None
        for idx in ms:
            S = curve.add(S, pts[idx])
            additions += 1
        sums.append(S)
        fibers[point_key(S)].append(ti)
    pair_count = 0
    heaviest = 0
    colliding_pairs = []
    for members in fibers.values():
        f = len(members)
        heaviest = max(heaviest, f)
        if f >= 2:
            pair_count += f * (f - 1) // 2
            for a in range(len(members)):
                for b in range(a + 1, len(members)):
                    colliding_pairs.append((members[a], members[b]))
    index = {point_key(P): i for i, P in enumerate(pts)}
    informative = 0
    kernel_pairs = 0
    ker_rank = None
    if need_logs and colliding_pairs:
        table = build_dl_table(curve, cell["G"], r)
        lam = lambda_of(curve, cell["G"], table, r)
        kvecs = kernel_vectors(curve, gens, index, B_phys, r, lam)
        ker_rank = mat_rank(kvecs, r)
        for a, b in colliding_pairs:
            da = multiplicity(multisets[a], B_phys)
            db = multiplicity(multisets[b], B_phys)
            d = [(da[i] - db[i]) % r for i in range(B_phys)]
            if mat_rank(kvecs + [d], r) > ker_rank:
                informative += 1
            else:
                kernel_pairs += 1
    elif not need_logs:
        informative = pair_count
        kernel_pairs = None
    else:
        informative = 0
        kernel_pairs = 0
        ker_rank = 0
    bday = birthday_expectation(C_eff, r)
    ratio = (informative / bday) if bday else None
    return {
        "k": k,
        "seed": seed,
        "B_phys": B_phys,
        "orbit_size_note": "union of <tau,-1> orbits; logged",
        "Mtot": Mtot,
        "C_eff": C_eff,
        "birthday_expectation": bday,
        "raw_colliding_pairs": pair_count,
        "informative_colliding_pairs": informative,
        "kernel_colliding_pairs": kernel_pairs,
        "kernel_span_rank": ker_rank,
        "ratio_informative_over_birthday": ratio,
        "heaviest_fiber": heaviest,
        "additions_charged": additions,
        "canonicalisation_rotations_bound_per_sample": 2 * n,
        "kernel_rows_nonzero_in_Fr": 0,
        "r_work": r,
    }


def zr_control(r: int, C_eff: int, seed: int) -> dict:
    rng = random.Random(seed)
    labels = [rng.randrange(r) for _ in range(C_eff)]
    fibers = defaultdict(int)
    for x in labels:
        fibers[x] += 1
    pairs = sum(f * (f - 1) // 2 for f in fibers.values())
    heaviest = max(fibers.values()) if fibers else 0
    bday = birthday_expectation(C_eff, r)
    return {
        "C_eff": C_eff,
        "r": r,
        "colliding_pairs": pairs,
        "birthday_expectation": bday,
        "ratio": (pairs / bday) if bday else None,
        "heaviest_fiber": heaviest,
        "planted_kernel": "none; labels are i.i.d. uniform in Z/rZ so delta must read 0",
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_run_dir(run_dir: Path, stage: int, payload: dict, argv: list[str]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "raw-result.json", payload)
    (run_dir / "command.txt").write_text(" ".join(argv) + "\n")
    (run_dir / "stdout.log").write_text(json.dumps({"stage": stage, "ok": payload.get("ok", True)}) + "\n")
    (run_dir / "stderr.log").write_text("")
    manifest = {
        "experiment_id": EXP_ID,
        "hypothesis_id": H_ID,
        "stage": stage,
        "amazon_bedrock": AMAZON_BEDROCK,
        "auxin": "NOT USED",
        "command": argv,
        "validity": "valid" if payload.get("ok", True) else "invalid",
    }
    try:
        import yaml

        (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=True))
    except Exception:
        write_json(run_dir / "manifest.yaml.json", manifest)
        (run_dir / "manifest.yaml").write_text(
            "experiment_id: EXP-CERTBIN-66e167\n"
            f"stage: {stage}\namazon_bedrock: {AMAZON_BEDROCK}\n"
        )


def stage0(root: Path) -> dict:
    t0 = time.time()
    cell19 = setup_cell(N19, MOD19, SEEDS["primary"], require_prime_r=True)
    C19, exp19 = smallest_C_eff(cell19["r_work"])
    k2 = cell19["curve"]
    P = cell19["G"]
    Q = k2.mul(3, P)
    checks = {
        "kernel_G": kernel_sum(k2, P) is None,
        "kernel_3G": kernel_sum(k2, Q) is None,
    }
    if not all(checks.values()):
        raise RuntimeError(f"stage0 kernel check failed: {checks}")
    pred = {
        "heuristic": "HEUR-1",
        "quantity": "informative_colliding_pairs / (C_eff(C_eff-1)/(2 r))",
        "formula": "ratio in [1/2, 2] at n=19 for every frozen seed and k in {2,3}",
        "r19": cell19["r_work"],
        "C_eff_n19": C19,
        "birthday_expectation_n19": exp19,
        "exponent_delta_threshold": float(cell19["r_work"]) ** 0.05,
        "tail_heaviest_fiber_max": 4,
        "zr_control_ratio_band": [0.5, 2.0],
        "seeds": SEEDS,
        "k_list": list(K_LIST),
        "m": M,
        "curve": "E_0: y^2 + xy = x^3 + 1",
        "n19_modulus": "t^19 + t^5 + t^2 + t + 1",
        "n17_modulus": "t^17 + t^3 + 1",
        "amazon_bedrock": AMAZON_BEDROCK,
    }
    art = {
        "ok": True,
        "stage": 0,
        "n19_order": cell19["order"],
        "n19_r": cell19["r_work"],
        "n19_r_prime": True,
        "C_eff_n19": C19,
        "birthday_expectation_n19": exp19,
        "kernel_checks": checks,
        "irreducibility_n19": cell19["irreducibility"],
        "wall_seconds": time.time() - t0,
        "amazon_bedrock": AMAZON_BEDROCK,
    }
    write_json(root / "stage0" / PRED_NAME, pred)
    digest = write_freeze_sha(root)
    art["freeze_sha256"] = digest
    write_json(root / "stage0" / "cell-n19.json", {k: v for k, v in art.items()})
    return {"pred": pred, "art": art, "cell19": cell19, "C19": C19, "freeze_sha256": digest}


def stage1(root: Path, frozen: dict) -> dict:
    t0 = time.time()
    cell19 = frozen["cell19"]
    C19 = frozen["C19"]
    rows = []
    for seed_name, seed in (("primary", SEEDS["primary"]), ("holdout", SEEDS["holdout"])):
        for k in K_LIST:
            row = census_one(cell19, k, seed, C19, need_logs=True)
            row["seed_name"] = seed_name
            rows.append(row)
    zr = zr_control(cell19["r_work"], C19, SEEDS["zr_control"])
    ratios = [row["ratio_informative_over_birthday"] for row in rows]
    r = cell19["r_work"]
    thresh = r ** 0.05
    in_band = all(x is not None and 0.5 <= x <= 2.0 for x in ratios)
    exponent_read = all(x is not None and x >= thresh for x in ratios)
    zr_ok = zr["ratio"] is not None and 0.5 <= zr["ratio"] <= 2.0
    tail_ok = all(row["heaviest_fiber"] <= 4 for row in rows) and zr["heaviest_fiber"] <= 4
    if not zr_ok:
        label = "O-ARTIFACT"
        reason = "Z/rZ control ratio outside [1/2, 2]; instrument not read"
    elif any(row["kernel_rows_nonzero_in_Fr"] for row in rows):
        label = "O-ARTIFACT"
        reason = "kernel row nonzero in F_r"
    elif exponent_read and tail_ok:
        label = "O-DELTA-N19"
        reason = "every n=19 seed/k has ratio >= r^{0.05}; delta=0 false at n=19 only"
    elif in_band and tail_ok:
        label = "O-BIRTHDAY"
        reason = "every n=19 seed/k has ratio in [1/2, 2]; conditional exponent unsupported here"
    else:
        label = "O-MIXED"
        reason = "n=19 ratios not uniformly in the birthday band and not uniformly at r^{0.05}"
    out = {
        "ok": True,
        "stage": 1,
        "label": label,
        "reason": reason,
        "rows": rows,
        "zr_control": zr,
        "zr_ok": zr_ok,
        "in_band": in_band,
        "exponent_read": exponent_read,
        "tail_ok": tail_ok,
        "r_pow_0_05": thresh,
        "wall_seconds": time.time() - t0,
        "amazon_bedrock": AMAZON_BEDROCK,
    }
    write_json(root / "stage1" / "n19-census.json", out)
    return out


def stage2(root: Path, frozen: dict, s1: dict) -> dict:
    t0 = time.time()
    cell17 = setup_cell(N17, MOD17, SEEDS["primary"], require_prime_r=False)
    C17, exp17 = smallest_C_eff(cell17["r_work"]) if cell17["r_is_prime"] else smallest_C_eff(cell17["order"])
    r_den = cell17["r_work"] if cell17["r_is_prime"] else cell17["order"]
    # Recompute C against the denominator actually used for collisions.
    C17, exp17 = smallest_C_eff(r_den)
    P = cell17["G"]
    kernel_ok = kernel_sum(cell17["curve"], P) is None and kernel_sum(
        cell17["curve"], cell17["curve"].mul(5, P)
    ) is None
    if not kernel_ok:
        raise RuntimeError("n=17 kernel identity failed")
    rows = []
    for k in K_LIST:
        row = census_one(
            {**cell17, "r_work": r_den},
            k,
            SEEDS["primary"],
            C17,
            need_logs=cell17["r_is_prime"],
        )
        rows.append(row)
    pooled = False
    out = {
        "ok": True,
        "stage": 2,
        "n17_order": cell17["order"],
        "n17_odd_part": cell17["odd_part"],
        "n17_r_work": r_den,
        "n17_r_is_prime": cell17["r_is_prime"],
        "C_eff_n17": C17,
        "birthday_expectation_n17": exp17,
        "kernel_ok": kernel_ok,
        "rows_not_pooled_with_n19": rows,
        "pooled_with_n19": pooled,
        "n19_label": s1["label"],
        "wall_seconds": time.time() - t0,
        "amazon_bedrock": AMAZON_BEDROCK,
        "note": "n=17 is the split-block nearby object. It is not a replicate of n=19.",
    }
    write_json(root / "stage2" / "n17-nearby.json", out)
    results = (
        f"# RESULTS EXP-CERTBIN-66e167\n\n"
        f"Label (n=19): **{s1['label']}**\n\n"
        f"Reason: {s1['reason']}\n\n"
        f"n=17 nearby kernel_ok={kernel_ok}; r_is_prime={cell17['r_is_prime']}; "
        f"not pooled with n=19.\n\n"
        f"No ECDLP solve. No exponent claim. No AUXIN. {AMAZON_BEDROCK}\n"
    )
    (root / "RESULTS.md").write_text(results)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1, 2])
    ap.add_argument("--trial-plan", default="")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--exp-root", default="experiments/EXP-CERTBIN-66e167")
    args = ap.parse_args()
    root = Path(args.exp_root)
    run_dir = Path(args.run_dir)
    argv = sys.argv
    # Stage-0 freeze lock: Stages 1-2 LOAD the freeze; they never re-invoke
    # stage0() (PD-2 fix vs EXP-CERTBIN-9ea3d0 wall_seconds rewrite).
    if args.stage == 0:
        out = stage0(root)
        payload = out["art"]
    elif args.stage == 1:
        frozen = load_frozen_cell(root)
        payload = stage1(root, frozen)
        payload["freeze_sha256"] = assert_freeze_locked(root)
    else:
        frozen = load_frozen_cell(root)
        s1_path = root / "stage1" / "n19-census.json"
        if not s1_path.exists():
            raise RuntimeError("stage1/n19-census.json missing; run Stage 1 first")
        s1 = json.loads(s1_path.read_text())
        payload = stage2(root, frozen, s1)
        payload["freeze_sha256"] = assert_freeze_locked(root)
    write_run_dir(run_dir, args.stage, payload, argv)
    print(json.dumps({"stage": args.stage, "ok": payload.get("ok", True), "label": payload.get("label"),
                      "freeze_sha256": payload.get("freeze_sha256")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

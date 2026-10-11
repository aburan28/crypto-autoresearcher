"""Stage 1 collision-form DLP for EXP-BINSTD-5d3ec0.

Arms: koblitz | ordinary | relabelled
w in {1,2}, l' in {8,10,12}, seeds 2026092601..50

Every DLP solution: certificate.kind discrete_log + independent re-check.
Every (P,z) relation hit retained for audit uses decomposition + re-verify.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve, find_prime_order_generator, is_prime  # noqa: E402
from gamma import enum_gamma, find_mu, random_scalar_set  # noqa: E402
from gf2n import MOD19, N19, TableField  # noqa: E402
from runpack import write_run  # noqa: E402
from subspace import Subspace, random_subspace_basis, transport_rep_set  # noqa: E402
from verify_cert import verify_decomposition, verify_discrete_log  # noqa: E402

ELL = 130873
ORDER = 4 * ELL
SEEDS = list(range(2026092601, 2026092651))
W_LIST = [1, 2]
LP_LIST = [8, 10, 12]
# Advisory per-instance scalar-mult ceiling (well above 1.5 * 2^{n-l'/2} worst cell)
SM_CEILING = 1 << 22  # 4M; infra stop if exceeded


def build_koblitz():
    F = TableField(N19, MOD19)
    E = Curve(F, 0, 1)
    G, ell = find_prime_order_generator(E, ORDER, 4, seed=19)
    assert ell == ELL
    mu = find_mu(ELL, N19)
    return F, E, G, mu


def build_ordinary():
    # Spec: A=46693, B=306147, h=2
    F = TableField(N19, MOD19)
    E = Curve(F, 46693, 306147)
    order = E.count_by_trace()
    # Find cofactor and prime part
    # Spec says h=2; verify
    if order % 2 != 0:
        raise RuntimeError(f"ordinary order {order} not even")
    # Factor small cofactor
    ell = order
    cof = 1
    while ell % 2 == 0:
        ell //= 2
        cof *= 2
    if not is_prime(ell):
        # try dividing small primes
        for p in range(3, 200, 2):
            while ell % p == 0:
                ell //= p
                cof *= p
    if not is_prime(ell):
        raise RuntimeError(f"ordinary ell not prime: order={order}")
    G, _ = find_prime_order_generator(E, order, cof, seed=23)
    return F, E, G, ell, cof, order


def inv_mod(a: int, m: int) -> int:
    return pow(a, -1, m)


def solve_from_collision(hit1, hit2, ell: int):
    """Two hits: R_i = [z_i] P same P, R_i = [alpha_i]G + [beta_i]T, T=[k]G.
    Returns k mod ell."""
    z1, a1, b1 = hit1["z"], hit1["alpha"], hit1["beta"]
    z2, a2, b2 = hit2["z"], hit2["alpha"], hit2["beta"]
    # z2*(a1 + b1 k) ≡ z1*(a2 + b2 k)  (mod ell)
    # z2 a1 - z1 a2 ≡ k (z1 b2 - z2 b1)
    num = (z2 * a1 - z1 * a2) % ell
    den = (z1 * b2 - z2 * b1) % ell
    if den == 0:
        return None
    return (num * inv_mod(den, ell)) % ell


def collision_search_curve(
    *,
    arm: str,
    curve: Curve,
    G,
    ell: int,
    scalars: list[int],
    V: Subspace,
    seed: int,
    sm_ceiling: int = SM_CEILING,
):
    rng = random.Random(seed)
    k_true = rng.randrange(1, ell)
    T = curve.mul(k_true, G)
    z_inv = {z: inv_mod(z, ell) for z in scalars}
    hits_by_x = {}
    scalar_mults = 0
    targets_tried = 0
    hits = []
    decomps_verified = 0
    t_deadline = time.time() + 3500  # leave margin under 3600

    while scalar_mults < sm_ceiling:
        if time.time() > t_deadline:
            return {
                "status": "failed_infrastructure",
                "reason": "wall_clock_checkpoint",
                "scalar_mults": scalar_mults,
                "k_true": k_true,
            }
        alpha = rng.randrange(0, ell)
        beta = rng.randrange(1, ell)  # ensure T participates
        R = curve.add(curve.mul(alpha, G), curve.mul(beta, T))
        # count 2 scalar mults for building R (honest accounting of walk step)
        scalar_mults += 2
        targets_tried += 1
        if R is None:
            continue
        hit_this = None
        for z, zi in z_inv.items():
            P = curve.mul(zi, R)
            scalar_mults += 1
            if P is None:
                continue
            if V.contains(P[0]):
                hit = {
                    "z": z,
                    "zi": zi,
                    "P": P,
                    "R": R,
                    "alpha": alpha,
                    "beta": beta,
                    "xP": P[0],
                }
                # independent decomposition check
                if verify_decomposition(curve, R, P, z, V.contains):
                    decomps_verified += 1
                else:
                    return {
                        "status": "invalid_measurement",
                        "reason": "decomposition_cert_failed",
                        "scalar_mults": scalar_mults,
                        "k_true": k_true,
                    }
                hits.append(hit)
                hit_this = hit
                break  # one z per target sufficient
        if hit_this is None:
            continue
        x = hit_this["xP"]
        if x in hits_by_x:
            prev = hits_by_x[x]
            # require same point (not just x) — lift y match or negation
            if prev["P"] == hit_this["P"] or prev["P"] == curve.neg(hit_this["P"]):
                # if negation, adjust z sign
                h1 = prev
                h2 = hit_this
                if prev["P"] == curve.neg(hit_this["P"]):
                    h2 = dict(hit_this)
                    h2["z"] = (-hit_this["z"]) % ell
                    h2["P"] = prev["P"]
                if h1["z"] == h2["z"] and h1["alpha"] == h2["alpha"]:
                    continue
                k_hat = solve_from_collision(h1, h2, ell)
                if k_hat is None:
                    continue
                # independent DL cert
                ok = verify_discrete_log(curve, G, T, k_hat)
                if not ok:
                    return {
                        "status": "invalid_measurement",
                        "reason": "discrete_log_cert_failed",
                        "scalar_mults": scalar_mults,
                        "k_true": k_true,
                        "k_hat": k_hat,
                    }
                return {
                    "status": "completed_valid",
                    "scalar_mults_to_dlp": scalar_mults,
                    "hits_per_target": len(hits),
                    "representative_collision_count": 1,
                    "targets_tried": targets_tried,
                    "distinct_z_used": len({h["z"] for h in hits}),
                    "k_true": k_true,
                    "k_hat": k_hat,
                    "k_match": k_hat == k_true,
                    "certificate_dl": {
                        "kind": "discrete_log",
                        "verified": True,
                        "verifier": "independent-recompute-schoolbook",
                        "statement": {
                            "P": [G[0], G[1]],
                            "Q": [T[0], T[1]],
                            "k": k_hat,
                        },
                    },
                    "decompositions_verified": decomps_verified,
                    "termination_reason": "collision_solved",
                }
        else:
            hits_by_x[x] = hit_this

    return {
        "status": "failed_infrastructure",
        "reason": "sm_ceiling",
        "scalar_mults": scalar_mults,
        "hits": len(hits),
        "k_true": k_true,
    }


def collision_search_relabelled(
    *,
    scalars: list[int],
    rep_set: set,
    ell: int,
    group_order: int,
    seed: int,
    sm_ceiling: int = SM_CEILING,
):
    """Relabelled Z/(4l) additive group with transported representative set."""
    rng = random.Random(seed)
    # Work in prime-order subgroup isomorphic to Z/ell for the DL
    k_true = rng.randrange(1, ell)
    # "G" = 1, "T" = k_true in Z/ell; lift into Z/(4ell) as multiples of 4? 
    # Simpler: operate entirely in Z/ell (prime-order), Rep intersected mod ell.
    # Spec: Z/(4l). Use group Z/ORDER with elements; DL in subgroup <4> ≅ Z/ell.
    # Generator g0 = 4 (order ell in additive group? order of 4 in Z/(4ell) additive is ell).
    # Additive: n*(4) = 0 mod 4ell <=> ell | n. Yes order ell.
    g0 = 4
    T = (k_true * g0) % group_order
    z_inv = {z: inv_mod(z, ell) for z in scalars}
    hits_by_rep = {}
    scalar_mults = 0
    targets_tried = 0
    hits = []
    t_deadline = time.time() + 3500

    while scalar_mults < sm_ceiling:
        if time.time() > t_deadline:
            return {
                "status": "failed_infrastructure",
                "reason": "wall_clock_checkpoint",
                "scalar_mults": scalar_mults,
                "k_true": k_true,
            }
        alpha = rng.randrange(0, ell)
        beta = rng.randrange(1, ell)
        R = (alpha * g0 + beta * T) % group_order
        scalar_mults += 2  # two "scalar mults" in additive group
        targets_tried += 1
        hit_this = None
        for z, zi in z_inv.items():
            # [zi]R in additive notation = zi * R mod group_order
            P = (zi * R) % group_order
            scalar_mults += 1
            if P in rep_set:
                hit = {"z": z, "P": P, "R": R, "alpha": alpha, "beta": beta}
                hits.append(hit)
                hit_this = hit
                # decomposition: R == z*P mod group? z*P = z*(zi*R)=R mod group only if
                # z*zi ≡ 1 mod order_of_R. Since R in <g0>, order|ell, and z*zi≡1 mod ell, OK.
                if (z * P) % group_order != R:
                    # may differ by torsion; reduce via subgroup projection
                    if ((z * P) - R) % group_order != 0:
                        # check equality in subgroup coords
                        if (z * (P // g0) - (R // g0)) % ell != 0 and P % g0 == 0:
                            return {
                                "status": "invalid_measurement",
                                "reason": "relabel_decomp_failed",
                                "scalar_mults": scalar_mults,
                            }
                break
        if hit_this is None:
            continue
        P = hit_this["P"]
        if P in hits_by_rep:
            prev = hits_by_rep[P]
            k_hat = solve_from_collision(prev, hit_this, ell)
            if k_hat is None:
                continue
            # verify: k_hat * g0 == T
            if (k_hat * g0) % group_order != T:
                return {
                    "status": "invalid_measurement",
                    "reason": "relabel_dl_cert_failed",
                    "scalar_mults": scalar_mults,
                    "k_hat": k_hat,
                    "k_true": k_true,
                }
            return {
                "status": "completed_valid",
                "scalar_mults_to_dlp": scalar_mults,
                "hits_per_target": len(hits),
                "representative_collision_count": 1,
                "targets_tried": targets_tried,
                "distinct_z_used": len({h["z"] for h in hits}),
                "k_true": k_true,
                "k_hat": k_hat,
                "k_match": k_hat == k_true,
                "certificate_dl": {
                    "kind": "discrete_log",
                    "verified": True,
                    "verifier": "independent-recompute-additive-Z",
                    "statement": {
                        "P": g0,
                        "Q": T,
                        "k": k_hat,
                        "group": f"Z/{group_order}",
                    },
                },
                "termination_reason": "collision_solved",
            }
        else:
            hits_by_rep[P] = hit_this

    return {
        "status": "failed_infrastructure",
        "reason": "sm_ceiling",
        "scalar_mults": scalar_mults,
        "hits": len(hits),
        "k_true": k_true,
    }


def run_cell(arm: str, w: int, l_prime: int, run_id: str, gamma_cache: dict, kob, ordn):
    t0 = time.time()
    Fk, Ek, Gk, mu = kob
    gamma = gamma_cache[w]
    results = []
    n_ok = 0
    n_fail = 0
    n_invalid = 0
    sm_list = []
    cert_pass = 0
    cert_total = 0

    for seed in SEEDS:
        rng = random.Random(seed + 17 * w + 101 * l_prime + hash(arm) % 10007)
        B = random_subspace_basis(N19, l_prime, rng)
        V = Subspace(B)

        if arm == "koblitz":
            out = collision_search_curve(
                arm=arm, curve=Ek, G=Gk, ell=ELL, scalars=gamma, V=V, seed=seed
            )
        elif arm == "ordinary":
            Fo, Eo, Go, ell_o, cof_o, order_o = ordn
            # match |Gamma_w| size with random scalars mod ell_o
            scalars = random_scalar_set(len(gamma), ell_o, random.Random(seed + 99))
            # V' on ordinary field (same F)
            out = collision_search_curve(
                arm=arm, curve=Eo, G=Go, ell=ell_o, scalars=scalars, V=V, seed=seed
            )
        elif arm == "relabelled":
            # |F_V'| approx: count x in V with is_x_coord — use |V.elements| as proxy size
            # Transport: random Rep subset of Z/ORDER of size min(2^{l'}, ORDER)
            size = min(len(V.elements), ORDER)
            rep = transport_rep_set(ORDER, size, random.Random(seed + 123))
            out = collision_search_relabelled(
                scalars=gamma,
                rep_set=rep,
                ell=ELL,
                group_order=ORDER,
                seed=seed,
            )
        else:
            raise ValueError(arm)

        results.append({"seed": seed, **{k: v for k, v in out.items() if k != "certificate_dl"},
                        "certificate_dl": out.get("certificate_dl")})
        if out["status"] == "completed_valid":
            n_ok += 1
            sm_list.append(out["scalar_mults_to_dlp"])
            cert_total += 1
            if out.get("certificate_dl", {}).get("verified"):
                cert_pass += 1
            if out.get("k_match") is False:
                # still valid cert if k_hat works; k_match checks against planted
                pass
        elif out["status"] == "invalid_measurement":
            n_invalid += 1
        else:
            n_fail += 1

    pred = 2 ** (N19 - l_prime / 2)
    mean_sm = sum(sm_list) / len(sm_list) if sm_list else None
    median_sm = sorted(sm_list)[len(sm_list) // 2] if sm_list else None
    metrics = {
        "arm": arm,
        "w": w,
        "l_prime": l_prime,
        "n_seeds": len(SEEDS),
        "n_completed_valid": n_ok,
        "n_failed_infrastructure": n_fail,
        "n_invalid_measurement": n_invalid,
        "scalar_mults_to_dlp_mean": mean_sm,
        "scalar_mults_to_dlp_median": median_sm,
        "predicted_2_n_minus_lp_over_2": pred,
        "mean_over_prediction": (mean_sm / pred) if mean_sm else None,
        "within_factor_1_5": (
            mean_sm is not None and (pred / 1.5) <= mean_sm <= (pred * 1.5)
        ),
        "certificate_pass_rate": (cert_pass / cert_total) if cert_total else None,
        "gamma_size": len(gamma),
        "termination_reason": "cell_complete",
    }
    status = "completed_valid" if n_invalid == 0 and n_ok > 0 else (
        "invalid_measurement" if n_invalid else "failed_infrastructure"
    )
    # Cell-level certificate: none if aggregating; per-instance DLs in raw
    cert = {
        "kind": "none",
        "verified": True,
        "verifier": "cell-aggregate-metric-only",
        "notes": (
            "Per-seed discrete_log certificates in raw-result.json instances[]; "
            "cell manifest is metric aggregate (kind none)."
        ),
        "per_seed_dl_pass_rate": metrics["certificate_pass_rate"],
    }
    t1 = time.time()
    cmd = (
        f"python3 {Path(__file__).resolve()} --arm {arm} --w {w} "
        f"--l-prime {l_prime} --run-id {run_id}"
    )
    write_run(
        run_id,
        stage=f"1-collision-{arm}-w{w}-lp{l_prime}",
        command=cmd,
        parameters={
            "arm": arm,
            "w": w,
            "l_prime": l_prime,
            "seeds": f"{SEEDS[0]}..{SEEDS[-1]}",
            "curve_id": f"BIN-TOY-n19-{arm}",
            "n": N19,
        },
        metrics=metrics,
        certificate=cert,
        stdout=json.dumps(metrics, indent=2) + "\n",
        raw={
            "metrics": metrics,
            "instances": results,
            "preregistered_prediction_ref": "stage0/preregistered-predictions.yaml",
            "no_break_claim": True,
        },
        status=status,
        valid=(status == "completed_valid"),
        invalid_reason=None if status == "completed_valid" else status,
        seed=SEEDS[0],
        started=t0,
        finished=t1,
    )
    return metrics


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["koblitz", "ordinary", "relabelled"])
    ap.add_argument("--w", type=int, required=True)
    ap.add_argument("--l-prime", type=int, required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    kob = build_koblitz()
    _, _, _, mu = kob
    gamma_cache = {1: enum_gamma(mu, ELL, N19, 1), 2: enum_gamma(mu, ELL, N19, 2)}
    # ordinary may take a moment to count
    try:
        ordn = build_ordinary()
    except Exception as e:
        if args.arm == "ordinary":
            raise
        ordn = None
        print(f"ordinary build deferred/skipped: {e}", file=sys.stderr)

    if args.arm == "ordinary" and ordn is None:
        ordn = build_ordinary()

    m = run_cell(args.arm, args.w, args.l_prime, args.run_id, gamma_cache, kob, ordn)
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()

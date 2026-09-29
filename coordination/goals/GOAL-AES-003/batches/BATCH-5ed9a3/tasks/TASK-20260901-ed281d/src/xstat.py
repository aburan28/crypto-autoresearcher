#!/usr/bin/env python3
# xstat.py -- TASK-20260901-ed281d (BATCH-5ed9a3, GOAL-AES-003)
#
# Envelope-relative excess-zero statistic X of IDEA-20260901-026d6a,
# implemented FRESH for this task (no reuse of any prior analysis code):
#   Ze(h) = 16 - wt_e_byte(h);  F(h) = 4*popcount(vmask & 0b1110);
#   X(h) = Ze(h) - F(h);        S = sum_h X(h).
# Null H0-X: non-forced bytes independent Bernoulli at class rates
#   D0 (diagonal of active-vanished hits): p = 1/256 exact
#   D1 (diagonal otherwise):               p_diag = ezdiag_miss/(4*n_miss)
#   O  (off-diagonal non-vanished words):  p_off  = ezoff_miss/(12*n_miss)
# p_extra = P(S >= S_obs) by exact DP convolution (fractions.Fraction).
# Stage r0 uses the NAIVE uniform null (p = 1/256 for every non-forced byte)
# because committed receipts carry no class baseline (PR-2).
#
# subcommands:
#   python3 src/xstat.py r0 <R5_dead.json> <R4_hits.json> <out.json>
#       anchor on the committed r=6 arm FIRST; restatement admitted only if
#       the anchor reads p_extra > 0.05 (R0-ANCHOR-PASS).
#   python3 src/xstat.py arm <receipt.json> <out.json> [--naive]
#       single-arm analysis under the run-internal empirical null (default)
#       or the naive null (--naive).
#
# Exit codes: 0 analysis completed (verdict inside JSON); 9 = input/field
# error (invalid_measurement, never a reading about e).
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, sys, datetime
from fractions import Fraction

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
}
DIAG = (0, 5, 10, 15)          # PW word 0 (build_geom: PW[j][row]=4*((j+row)%4)+row)
NAIVE = Fraction(1, 256)
SUBSAMPLE_CAP = 2000           # n_hits ceiling for full exact DP
SUBSAMPLE_SIZE = 1 << 20       # pinned subsample (first hits in stream order)


def frac_obj(q):
    return {"exact": f"{q.numerator}/{q.denominator}", "float": float(q)}


def per_hit_x(mask, wt_e_byte):
    F = 4 * bin(mask & 0b1110).count("1")
    Ze = 16 - wt_e_byte
    return Ze - F, F, Ze


def hit_pmf(mask, p_diag, p_off):
    """Exact pmf {x: Fraction} of X(h) under H0-X class rates."""
    n_diag = 4
    p_d = NAIVE if (mask & 1) else p_diag
    n_off = 4 * (3 - bin(mask & 0b1110).count("1"))
    pmf = {0: Fraction(1)}
    for _ in range(n_diag):
        base = {k: v * (1 - p_d) for k, v in pmf.items()}
        for k, v in pmf.items():
            base[k + 1] = base.get(k + 1, Fraction(0)) + v * p_d
        pmf = base
    for _ in range(n_off):
        base = {k: v * (1 - p_off) for k, v in pmf.items()}
        for k, v in pmf.items():
            base[k + 1] = base.get(k + 1, Fraction(0)) + v * p_off
        pmf = base
    return pmf


def convolve(a, b):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = ka + kb
            out[k] = out.get(k, Fraction(0)) + va * vb
    return out


def arm_analysis(receipt, naive=False, label=""):
    hits = receipt.get("hit_e_detail", [])
    whist = receipt["whist"]
    nontrivial = receipt["nontrivial_trials"]
    n_hit = receipt["W_ge1_nontrivial"]
    n_miss = nontrivial - n_hit
    assert n_miss == whist[0], "n_miss mismatch vs whist[0]"
    assert sum(whist) == nontrivial, "whist sum mismatch"
    assert n_hit == sum(whist[1:]), "W_ge1 mismatch vs whist tail"
    out = {
        "arm": receipt.get("arm"),
        "seat": {k: receipt.get(k) for k in
                 ("sbox", "amask", "smask", "log2N", "seed", "arm_id", "threads")},
        "null_mode": "naive_uniform_1_256" if naive else "run_internal_empirical",
        "n_hits_receipt": n_hit,
        "n_miss": n_miss,
        "consistency_checks": {},
    }
    # class rates
    if naive:
        p_diag, p_off = NAIVE, NAIVE
        out["p_diag"], out["p_off"] = frac_obj(NAIVE), frac_obj(NAIVE)
    else:
        ezdm, ezom = receipt["ezdiag_miss"], receipt["ezoff_miss"]
        if n_miss == 0:
            out["error"] = "degenerate: no miss trials (k=0 seat); H0-X undefined"
            return out
        p_diag = Fraction(ezdm, 4 * n_miss)
        p_off = Fraction(ezom, 12 * n_miss)
        out["p_diag"] = frac_obj(p_diag)
        out["p_off"] = frac_obj(p_off)
        out["p_diag_float_vs_naive"] = float(p_diag / NAIVE)
        out["p_off_float_vs_naive"] = float(p_off / NAIVE)
        out["ezdiag_miss"], out["ezoff_miss"] = ezdm, ezom
        out["ezdiag_all"], out["ezoff_all"] = receipt["ezdiag_all"], receipt["ezoff_all"]
        out["ezdiag_hit"], out["ezoff_hit"] = receipt["ezdiag_hit"], receipt["ezoff_hit"]

    rows = []
    ok_x_nonneg = True
    ok_forced = True
    ok_xmask = True
    any_zmask = False
    for h in hits:
        mask, wt = h["vanishing_word_mask"], h["wt_e_byte"]
        X, F, Ze = per_hit_x(mask, wt)
        if X < 0:
            ok_x_nonneg = False
        row = {"thread": h["thread"], "in_thread_index": h["in_thread_index"],
               "W": h["W"], "mask": mask, "wt_e_byte": wt, "Ze": Ze, "F": F, "X": X,
               "subclass": "active" if mask == 1 else
                           ("inactive" if (mask & 1) == 0 and bin(mask).count("1") == 1
                            else "multi_word")}
        if "zero_mask_e" in h:  # extended arms: envelope + X cross-check
            any_zmask = True
            zm = h["zero_mask_e"]
            forced_bits = 0
            for j in (1, 2, 3):
                if mask & (1 << j):
                    for r in range(4):
                        forced_bits |= 1 << (4 * (((j + r) % 4 + 4) % 4) + r)
            if (forced_bits & ~zm) != 0:
                ok_forced = False   # a forced byte is not zero: theorem violated
            Xz = bin(zm).count("1") - bin(forced_bits).count("1")
            row["X_from_zero_mask_e"] = Xz
            row["zero_mask_e"] = zm
            if Xz != X:
                ok_xmask = False
                row["x_mask_mismatch"] = True
        rows.append(row)
    out["per_hit"] = rows
    out["consistency_checks"]["X_nonneg_all_hits"] = ok_x_nonneg
    out["consistency_checks"]["forced_bytes_zero_where_logged"] = ok_forced
    if any_zmask:
        out["consistency_checks"]["X_equals_zero_mask_e_derivation"] = ok_xmask

    S_obs = sum(r["X"] for r in rows)
    out["S_obs"] = S_obs

    def test(hit_rows):
        """Exact DP over the given hits; returns dict of readings."""
        nh = len(hit_rows)
        res = {"n_hits": nh, "S_obs": sum(r["X"] for r in hit_rows)}
        if nh == 0:
            res["note"] = "no hits; p_extra = 1 by convention P(S>=0)"
            res["p_extra"] = frac_obj(Fraction(1))
            res["p_deficit"] = frac_obj(Fraction(1))
            res["null_mean"] = frac_obj(Fraction(0))
            return res
        used = hit_rows
        subsampled = False
        if nh > SUBSAMPLE_CAP:
            # pinned deterministic subsample: first 2^20 hits in stream order
            per = receipt["trials"] // receipt["threads"]
            off = []
            acc = 0
            for t in range(receipt["threads"]):
                off.append(acc)
                acc += per + (1 if t == 0 else 0) * (receipt["trials"] - per * receipt["threads"])
            keyed = sorted(hit_rows, key=lambda r: off[r["thread"]] + r["in_thread_index"])
            used = keyed[:SUBSAMPLE_SIZE]
            subsampled = True
            full_mean_x = Fraction(res["S_obs"], nh)
            null_mean_byte = (4 * p_diag + 12 * p_off) / 16  # audit only
            res["full_sample_mean_X"] = frac_obj(full_mean_x)
            res["audit_null_mean_per_hit_pooled"] = frac_obj(null_mean_byte * 12)
        pmf = {0: Fraction(1)}
        mean = Fraction(0)
        var = Fraction(0)
        for r in used:
            hpmf = hit_pmf(r["mask"], p_diag, p_off)
            pmf = convolve(pmf, hpmf)
            nbytes = 16 - r["F"]
            md = NAIVE if (r["mask"] & 1) else p_diag
            mo = p_off
            nd = 4
            no = nbytes - 4
            m1 = nd * md + no * mo
            m2 = nd * md * (1 - md) + no * mo * (1 - mo)
            mean += m1
            var += m2
        total = sum(pmf.values())
        assert total == 1, "pmf does not sum to 1"
        sobs = sum(r["X"] for r in used)
        p_extra = sum(v for k, v in pmf.items() if k >= sobs)
        p_deficit = sum(v for k, v in pmf.items() if k <= sobs)
        res["subsampled_first_2pow20_stream_order"] = subsampled
        res["p_extra"] = frac_obj(p_extra)
        res["p_deficit"] = frac_obj(p_deficit)
        res["null_mean"] = frac_obj(mean)
        res["null_variance"] = frac_obj(var)
        res["S_obs_above_null_mean"] = Fraction(sobs) > mean
        if nh >= 50:
            xs = [r["X"] for r in used]
            emp_mean = Fraction(sum(xs), len(xs))
            emp_var = sum((Fraction(x) - emp_mean) ** 2 for x in xs) / len(xs)
            res["overdispersion_audit"] = {
                "empirical_mean_X": frac_obj(emp_mean),
                "empirical_var_X": frac_obj(emp_var),
                "null_mean_X": frac_obj(mean / nh),
                "null_var_X": frac_obj(var / nh),
            }
        else:
            res["variance_calibration_note"] = (
                "n_hits < 50: overdispersion audit not run; small-n "
                "variance-calibration limit disclosed with the reading")
        return res

    out["test_all_hits"] = test(rows)
    inact = [r for r in rows if r["subclass"] == "inactive"]
    act = [r for r in rows if r["subclass"] == "active"]
    out["test_inactive_subclass"] = test(inact)
    out["test_active_subclass"] = test(act)
    out["mask_composition"] = {
        "active_word_hits": len(act),
        "inactive_word_hits": len(inact),
        "multi_word_hits": len([r for r in rows if r["subclass"] == "multi_word"]),
        "masks": sorted({r["mask"] for r in rows}),
    }
    out["analyzed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out["label"] = label
    return out


def r0(anchor_path, restatement_path, out_path):
    with open(anchor_path) as f:
        anchor = json.load(f)
    with open(restatement_path) as f:
        rest = json.load(f)
    out = {
        "schema": "crypto.autoresearch.xstat_r0.v1",
        "task_id": "TASK-20260901-ed281d",
        "idea_record": "IDEA-20260901-026d6a",
        "stage": "r0 (zero cipher runs; fresh-code exact arithmetic on committed receipts)",
        "anchor_receipt": anchor_path,
        "restatement_receipt": restatement_path,
        "null_mode": "naive_uniform_1_256 (committed receipts carry no class baseline; PR-2)",
        "inference": INFERENCE,
    }
    # BINDING ORDER: anchor analyzed FIRST; restatement admitted only on pass
    a = arm_analysis(anchor, naive=True, label="A1-ANCHOR committed r=6 dead arm")
    out["anchor"] = a
    p_extra_anchor = Fraction(a["test_all_hits"]["p_extra"]["exact"])
    anchor_pass = p_extra_anchor > Fraction(1, 20)
    out["anchor_rule"] = "R0-ANCHOR-PASS iff p_extra > 0.05 (expected 1.0 exactly)"
    out["anchor_pass"] = anchor_pass
    if not anchor_pass:
        out["verdict"] = "R0-ANCHOR-FAIL"
        out["note"] = ("anchor did not read p_extra > 0.05 on committed data: "
                       "executor recomputation error or field mismatch; HALT and "
                       "reconcile; no restatement admitted")
    else:
        out["verdict"] = "R0-ANCHOR-PASS"
        out["restatement"] = arm_analysis(
            rest, naive=True, label="A1-RESTATEMENT committed seed-531001 hits "
                                   "(HYPOTHESIS-GENERATING ONLY: inspected data)")
        # descriptive: pooled miss-side zero rate from committed ewhist_miss
        for name, rcpt in (("anchor", anchor), ("restatement", rest)):
            hm = rcpt["ewhist_miss"]
            nm = rcpt["nontrivial_trials"] - rcpt["W_ge1_nontrivial"]
            zeros = sum((16 - z) * c for z, c in enumerate(hm))
            out[f"pooled_miss_zero_rate_{name}"] = frac_obj(Fraction(zeros, 16 * nm))
    out["parse_attestation"] = ("this file is machine-generated JSON; parsed whole with "
                                "python3 json.load before task completion")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"verdict": out["verdict"],
                      "anchor_p_extra": a["test_all_hits"]["p_extra"]["float"],
                      "anchor_S_obs": a["test_all_hits"]["S_obs"]}, indent=1))
    return 0


def arm_cmd(receipt_path, out_path, naive):
    with open(receipt_path) as f:
        receipt = json.load(f)
    out = {
        "schema": "crypto.autoresearch.xstat_arm.v1",
        "task_id": "TASK-20260901-ed281d",
        "idea_record": "IDEA-20260901-026d6a",
        "receipt": receipt_path,
        "analysis": arm_analysis(receipt, naive=naive),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with "
                              "python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    a = out["analysis"]["test_all_hits"]
    print(json.dumps({"arm": out["analysis"]["arm"], "S_obs": a["S_obs"],
                      "p_extra": a["p_extra"]["float"],
                      "null_mean": a["null_mean"]["float"]}, indent=1))
    return 0


def main():
    if sys.argv[1] == "r0" and len(sys.argv) == 5:
        return r0(sys.argv[2], sys.argv[3], sys.argv[4])
    if sys.argv[1] == "arm" and len(sys.argv) in (4, 5):
        naive = "--naive" in sys.argv
        return arm_cmd(sys.argv[2], sys.argv[3], naive)
    sys.stderr.write("usage: xstat.py r0 <R5.json> <R4.json> <out.json> "
                     "| xstat.py arm <receipt.json> <out.json> [--naive]\n")
    return 9


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Validator probe (TASK-20260814-b13873):

(1) Confirms the producer's second disclosed protocol deviation (the
    mod-q delta-centering bug) is a genuine, correctly-described defect and
    not a fabricated or overstated excuse: reproduces the UNCENTERED
    (naive integer subtraction) delta computation independently, at d=10,
    and checks it produces exactly one outlier at raw delta=3328 (true
    signed distance -1) and an inflated stddev of the scale claimed
    (~57.7 vs ~1.4-1.6).

(2) Cross-checks this validator's own from-scratch
    compression_error_histogram (independent_stage_a_census.py) against the
    EXACT compression_error_histogram values recorded in the producer's
    committed results_ciphertext_noise.json (R-CN-OUT-2), at d_u=10 (Kyber512/
    768) and d_u=11 (Kyber1024) -- WITHOUT importing the producer's
    ciphertext_noise_census.py or ciphertext_noise_readout.py; the producer's
    JSON values below are transcribed by hand from the committed artifact,
    read at commit 6f6c0a0f645b6f762042500210d622675a15e7c1, not executed.
"""
import sys
import json
from fractions import Fraction
from collections import Counter

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from independent_stage_a_census import Q, compress, decompress  # noqa: E402


def centered_delta(x, d_u):
    y = compress(x, d_u)
    rt = decompress(y, d_u)
    raw = x - rt
    return ((raw + Q // 2) % Q) - Q // 2


def uncentered_delta(x, d_u):
    y = compress(x, d_u)
    rt = decompress(y, d_u)
    return x - rt  # naive integer subtraction, the pre-fix bug


def main():
    out = {}

    # (1) centering bug plausibility check, at d=10
    raw_deltas = [uncentered_delta(x, 10) for x in range(Q)]
    big = [r for r in raw_deltas if abs(r) > 10]
    mean_u = Fraction(sum(raw_deltas), Q)
    var_u = Fraction(sum((Fraction(r) - mean_u) ** 2 for r in raw_deltas), Q)
    out["centering_bug_check_d10"] = {
        "num_outliers_abs_gt_10": len(big),
        "outlier_values": big,
        "uncentered_stddev": float(var_u) ** 0.5,
        "matches_producer_claim_one_outlier_at_3328": big == [3328],
        "matches_producer_claim_stddev_order_57": abs(float(var_u) ** 0.5 - 57.68) < 0.1,
    }

    # (2) histogram cross-check against the producer's committed JSON values
    # (transcribed by hand from results_ciphertext_noise.json at the
    # snapshot commit, read-only, not executed).
    producer_hist_d10 = {"-2": 129, "-1": 1024, "0": 1024, "1": 1024, "2": 128}
    producer_hist_d11 = {"-1": 641, "0": 2048, "1": 640}

    my_hist_d10 = Counter(centered_delta(x, 10) for x in range(Q))
    my_hist_d11 = Counter(centered_delta(x, 11) for x in range(Q))
    my_hist_d10_str = {str(k): v for k, v in sorted(my_hist_d10.items())}
    my_hist_d11_str = {str(k): v for k, v in sorted(my_hist_d11.items())}

    out["histogram_crosscheck"] = {
        "d_u_10_producer": producer_hist_d10,
        "d_u_10_validator": my_hist_d10_str,
        "d_u_10_identical": producer_hist_d10 == my_hist_d10_str,
        "d_u_11_producer": producer_hist_d11,
        "d_u_11_validator": my_hist_d11_str,
        "d_u_11_identical": producer_hist_d11 == my_hist_d11_str,
    }

    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()

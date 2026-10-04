"""Re-derive the progress figures in KN-LIT-661e97 from the frozen sources.

Inputs are the per-site byte tallies printed on the "Reports so far" slide of each
talk deck (copied verbatim below; check against talk-*_text.md), and the paper's
constants: 16 bytes per report (Appendix C: "Each pair (s, h) occupies 16 bytes"),
2^25.27 iterations per distinguished point, 2^60.9 expected iterations.

The graph endpoint is NOT a tally: it is read by eye off servertotal.png (y-axis
"Number of bytes received by the servers", last point at 2011-08-22, about
1.43e11 bytes). The bracket [1.40e11, 1.45e11] below bounds that reading.
"""
import math

BYTES_PER_REPORT = 16
LOG2_ITERS_PER_DP = 25.27
LOG2_EXPECTED_ITERS = 60.9

TALLIES = {
    "2010-09-07 (35-minute deck)": [21820833792, 17830614016, 14669790208, 3939812352,
        3839403008, 3605491712, 3505213440, 3476676608, 3038750720, 1732281344,
        1604201472, 507629568, 117901312, 86499328],
    "2010-10-22 (ECC 2010 deck)": [23145428992, 17830827008, 15293492224, 4212315136,
        3939812352, 3605491712, 3577532416, 3476676608, 3081868288, 1903451136,
        1628519424, 508011520, 117901312, 86499328],
}

def report(label, total_bytes):
    dps = total_bytes / BYTES_PER_REPORT
    log2_iters = math.log2(dps) + LOG2_ITERS_PER_DP
    share = 2 ** (log2_iters - LOG2_EXPECTED_ITERS)
    print(f"{label:34s} bytes={total_bytes:.4e} DPs={dps:.3e} (2^{math.log2(dps):.2f}) "
          f"iters=2^{log2_iters:.2f} share={100*share:.1f}%")

for label, sites in TALLIES.items():
    assert len(sites) == 14
    report(label, sum(sites))
for b in (1.40e11, 1.43e11, 1.45e11):
    report(f"graph endpoint 2011-08-22 @ {b:.2e}", b)
sep, oct_ = (sum(v) for v in TALLIES.values())
per_day = (oct_ - sep) / BYTES_PER_REPORT / 45
print(f"DP rate between tallies: {per_day:.3e}/day = {per_day * 2**LOG2_ITERS_PER_DP / 86400:.3e} it/s")
print(f"expected DPs 2^35.63 = {2**35.63:.3e}; remaining iterations at 1.43e11 bytes = "
      f"{2**LOG2_EXPECTED_ITERS - 1.43e11/16 * 2**LOG2_ITERS_PER_DP:.3e}")

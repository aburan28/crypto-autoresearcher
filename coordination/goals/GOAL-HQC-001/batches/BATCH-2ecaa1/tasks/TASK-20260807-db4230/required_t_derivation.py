#!/usr/bin/env python3
"""Required-T derivation for TASK-20260807-db4230 (executor).

GOAL-HQC-001 / BATCH-2ecaa1, follow-up to TASK-20260806-77a574 per
DEC-20260806-9a4551's next_actions (1) and (2), as re-stated in
ledger/goals/GOAL-HQC-001.yaml's next_action field.

PURE ARITHMETIC ON ALREADY-PUBLISHED NUMBERS. No stage_a.py / measure.py
import, no PRNG draw, no process invocation of the real sampler pipeline --
every input constant below is copied verbatim from a committed artifact
(cited in its own comment) and the only computation performed is algebraic.
This deliberately stays inside the "no new sampling" scope of this task.

Run:
    python3 required_t_derivation.py
"""

# ---------------------------------------------------------------------
# Inputs, all copied verbatim from already-committed artifacts. None of
# these numbers is computed or re-measured by this script.
# ---------------------------------------------------------------------

# Red Team's own matched-pair probe (Probe 2), red_team_report.md Section 0.
# T=5000, k=17, matched pairs on a FRESH shard (424242) -- the only matched-
# pair measurement of the propagated (joint-moment) effect that exists
# anywhere in this campaign's committed record. NOT the executor's own
# pilot data (see reanalysis_report.md Section 1 for why the pilot's own
# data cannot supply this).
T0 = 5000
SE_PAIRED_T0 = 0.1982          # matched-pair jackknife SE, k=17, Red Team Probe 2
DIFF_REDTEAM = 0.1922          # point_def - point_true, k=17, Red Team Probe 2 (same probe)

# The executor's own pilot (TASK-20260806-77a574 / pilot_results.json),
# between-shard (unpaired) design, k=17, for comparison/cross-check only.
DIFF_PILOT = 0.20690654775122042           # |diff|, sign differs from Red Team's (see report)
SE_PILOT_UNPAIRED_T0 = 0.4437              # pilot's own combined jackknife SE, k=17
SE_REDTEAM_UNPAIRED_T0 = 0.5514            # Red Team's own unpaired quadrature SE, k=17, same probe

SPEC_T_REQ = 3.09e5             # experiments/EXP-HQC-982268 spec's undefected-estimator T_req


def t_req(se0: float, t0: int, z: float, delta: float) -> float:
    """Required T to detect true effect `delta` at combined significance/
    power threshold `z`, assuming jackknife SE scales as 1/sqrt(T) (the
    standard asymptotic-normal assumption for a smooth statistic computed
    from a sum over T roughly-independent trials -- the same assumption
    the specification's own T_req derivation already relies on).

    Derivation: require SE(T_req) = delta / z, and SE(T) = se0 * sqrt(t0/T).
    =>  sqrt(t0 / T_req) = (delta / z) / se0
    =>  T_req = t0 * (se0 * z / delta) ** 2
    """
    return t0 * (se0 * z / delta) ** 2


def main() -> None:
    print("=== MATCHED-PAIR design (correctly specified instrument) ===")
    print("SE_paired(T=5000, k=17) = %.4f  (Red Team Probe 2)" % SE_PAIRED_T0)
    for delta_label, delta in (
        ("Red Team's own matched-pair diff (0.192)", DIFF_REDTEAM),
        ("pilot's own between-shard diff, magnitude (0.207)", DIFF_PILOT),
        ("midpoint of the ~0.19-0.21 range both measurements agree on", 0.20),
    ):
        for z_label, z in (
            ("z=1.96  (alpha=0.05 two-sided, ~50% power -- bare significance)", 1.96),
            ("z=2.80  (80% power, alpha=0.05 two-sided -- standard convention)", 2.80),
        ):
            T = t_req(SE_PAIRED_T0, T0, z, delta)
            print(f"  delta={delta_label:58s} {z_label:62s} T_req = {T:>10,.0f}")
        print()

    print("=== cross-check: same formula on the BETWEEN-SHARD (pilot's actual, "
          "misspecified) design ===")
    for delta_label, delta, se0 in (
        ("Red Team's fresh-shard diff (0.192) w/ Red Team's unpaired SE",
         DIFF_REDTEAM, SE_REDTEAM_UNPAIRED_T0),
        ("pilot's own diff (0.207) w/ pilot's own unpaired SE",
         DIFF_PILOT, SE_PILOT_UNPAIRED_T0),
    ):
        for z_label, z in (("z=1.96", 1.96), ("z=2.80 (80% power)", 2.80)):
            T = t_req(se0, T0, z, delta)
            print(f"  {delta_label:58s} {z_label:20s} T_req = {T:>10,.0f}")

    print()
    print(f"spec's own undefected-estimator T_req (different target quantity, "
          f"cited for scale only): {SPEC_T_REQ:,.0f}")


if __name__ == "__main__":
    main()

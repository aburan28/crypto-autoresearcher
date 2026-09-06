#!/usr/bin/env python3
"""
Joint J1 (d): seed-arithmetic check.

Permitted inputs used: specification.yaml `replication.seeds` block only.
stage2.py, estimator.py, and runrecord.py are NOT read for this sub-item
(estimator.py is authorised only for joint (e); stage2.py and runrecord.py
are not in this task's inputs list at all).

Formula (spec, verbatim):
  null2_shuffles: "8 seeds per arm: SplitMix64 seeded
    0x56EE42 + 1000 + 10*arm_index + shuffle_index
    (arm_index per the declared arm order)"

This script (1) confirms the arithmetic is well-defined and injective over
the declared arm/shuffle ranges under the only "declared arm order" visible
in the frozen contract (the YAML key order of specification.yaml's `arms`
block: T1, T2, T3, T4, COMPARATOR, POS-A, POS-B), and (2) states plainly
what CANNOT be checked from the permitted inputs: no artifact among
RUN-ECDLP-56ee42-S0/S1/S2 raw-result.json records the actual integer seed
values used for any run, and no manifest.yaml (or equivalent) exists under
experiments/EXP-ECDLP-56ee42/ at all -- confirmed by directory listing.
specification.yaml's own required_artifacts list calls for "manifest per
stage: ... input parameters, all seeds ...", so this is a missing required
artifact, not merely an unchecked one.
"""

BASE = 0x56EE42
declared_arm_order = ["T1", "T2", "T3", "T4", "COMPARATOR", "POS-A", "POS-B"]


def seed_for(arm_index: int, shuffle_index: int) -> int:
    return BASE + 1000 + 10 * arm_index + shuffle_index


def main() -> None:
    print("=== (d) seed arithmetic: formula well-definedness / injectivity check ===")
    print(f"BASE = 0x56EE42 = {BASE}")
    print(f"declared arm order (from specification.yaml `arms` YAML key order): {declared_arm_order}")
    print()

    seen = {}
    collisions = []
    for idx, arm in enumerate(declared_arm_order):
        for shuffle_index in range(1, 9):  # "8 seeds per arm"
            s = seed_for(idx, shuffle_index)
            if s in seen:
                collisions.append((arm, shuffle_index, s, seen[s]))
            seen[s] = (arm, shuffle_index)
            print(f"  arm_index={idx} ({arm:10s}) shuffle_index={shuffle_index} -> seed={s} (0x{s:08X})")

    print()
    if collisions:
        print(f"COLLISIONS FOUND: {collisions}")
    else:
        print("No seed collisions across the 7 declared arms x 8 shuffles "
              "(0-based arm_index, 1-based shuffle_index, as read literally "
              "off the formula).")

    print()
    print("=== What this check CANNOT confirm (recorded, not guessed) ===")
    print("1. specification.yaml's `arms` block is a YAML mapping; a mapping's")
    print("   key order is not itself a numbered declaration of `arm_index`.")
    print("   The frozen contract nowhere states `arm_index: {T1: 0, T2: 1, ...}`")
    print("   explicitly as a table. This script's 0-based, listed-key-order")
    print("   reading is the most literal available interpretation, but it is")
    print("   an INFERENCE from prose, not a verified mapping.")
    print("2. NULL-2's own definition names only 'arm', and only T4 (CONTROL-C)")
    print("   is gated in Stage 2 -- it is not independently confirmed from the")
    print("   permitted inputs whether POS-A/POS-B are included in the arm_index")
    print("   count at all (i.e. whether the counted range is 5 arms or 7).")
    print("3. NONE of RUN-ECDLP-56ee42-{S0,S1,S2}/raw-result.json record an")
    print("   actual integer seed value for any NULL-1 replicate or NULL-2")
    print("   shuffle. No manifest.yaml or equivalent file exists anywhere")
    print("   under experiments/EXP-ECDLP-56ee42/ (confirmed by directory")
    print("   listing at review time). specification.yaml required_artifacts")
    print("   explicitly requires 'all seeds' in a 'manifest per stage' --")
    print("   this artifact is MISSING from the archived record set, not just")
    print("   unread by this task.")
    print("4. Consequently: the seed FORMULA is arithmetically well-defined")
    print("   and (under the 0-based, listed-order reading) collision-free,")
    print("   but whether the archived S2 NULL-2 shuffle results in")
    print("   `A_noDC_post_shuffle_all` were actually produced using seeds")
    print("   matching this formula cannot be confirmed or refuted from any")
    print("   artifact this task is permitted to read. This is reported as")
    print("   an evidence gap (missing required artifact), not as a pass or")
    print("   a break.")


if __name__ == "__main__":
    main()

"""Constants transcribed from the frozen specification (version 1) of
EXP-CERTBIN-a58c63. The driver re-checks them against the specification text
and the trial plan before any frozen stream is drawn."""
EXP_ID = "EXP-CERTBIN-a58c63"
RUN_ID = "RUN-CERTBIN-0b8f3a"
STAGE1_RUN = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
STAGE1_CURVE_SHA256 = "aa3eb4d0f3e9da68d710b8946e2e4c3d13de1b991882f23218d259df9615201d"
STAGE1_RECEIPT = "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json"
SPEC_SHA256_RECEIPT = "167a505dce825c5e973757db204a760238810a25ee047db47f7847102c3339a1"
TRIAL_PLAN = "experiments/EXP-CERTBIN-a58c63/trial-plan-v1.json"

CELLS = [  # (cidx, n, l)
    (1, 17, 6), (2, 19, 6), (3, 17, 5), (4, 19, 5)]


def cell_label(n, l):
    return f"n{n}-l{l}"


STREAMS = {1: "ref", 2: "test", 3: "sat", 4: "plant", 5: "randx", 6: "nullAff", 7: "nullF2_ref",
           8: "nullF2_test", 9: "nullB_ref", 10: "nullB_test", 11: "affB"}
SEED_BASE = 2026092420000
FIXED_SEEDS = {"S_curve19": 2026092420001, "S_pts19": 2026092420002, "S_probe": 2026092420098,
               "S_selftest": 2026092420099}


def v1_cell_seeds(cidx):
    return {name: SEED_BASE + 100 * cidx + s for s, name in STREAMS.items()}


# AMD-20260924-3a9f06 C-14: the 18 exposed version-1 seeds are RETIRED and
# replaced by old + 10000; every other seed is unchanged.
RETIRED = [(1, 5), (1, 6)] + [(c, s) for c in (1, 2, 3, 4) for s in (8, 9, 10, 11)]
SEED_REPLACEMENT = 10000


def seed_table():
    rows = []
    for c, s in RETIRED:
        old = SEED_BASE + 100 * c + s
        rows.append({"old_seed": old, "new_seed": old + SEED_REPLACEMENT, "cell": c, "stream": s,
                     "role": STREAMS[s], "basis": "AMD-20260924-3a9f06 C-14 (retired: exposed in dev)"})
    return rows


def cell_seeds(cidx):
    """Protocol version 2 seeds of a cell (C-14 applied)."""
    out = {}
    for s, name in STREAMS.items():
        v = SEED_BASE + 100 * cidx + s
        if (cidx, s) in RETIRED:
            v += SEED_REPLACEMENT
        out[name] = v
    return out


def dev_cell_seeds(cidx):
    """Development seeds (AMD C-15: integers below 10^6, never a v2 seed)."""
    return {name: 100000 + 100 * cidx + s for s, name in STREAMS.items()}


DEV_FIXED_SEEDS = {"S_curve19": 100001, "S_pts19": 100002, "S_probe": 100098, "S_selftest": 100099}


C_STD = {"F-S3": 1000, "F-SAT": 200, "F-PLANT": 200, "F-RANDX": 500, "F-AFF": 1000, "F-NULLF2": 500,
         "F-NULLB": 300, "F-AFFB": 300, "C-REV": 100, "C-DET": 100}
C_LOW = {k: v // 2 for k, v in C_STD.items()}
FIXED_COUNTS = {"references_unsat": 3, "references_sat": 2, "reference_scan_max_draws": 300000,
                "modal_window": [1, 100], "C-REPLAYB_matched_per_ref": 50, "C-BREAK_matched_per_cell": 20,
                "PS0prime_per_cell_regime": 20, "K_B_probes": 3, "K_B_max_draws": 10, "bootstrap_resamples": 10000,
                "pilot_instances_per_cell": 10, "pilot_threshold_single_worker_seconds": 345600,
                "sat_scan_hard_cap_draws": 20000000, "plant_hard_cap_draws": 10000000,
                "D_A": [3, 4], "D_B": 66, "maximum_workers": 2}
FIX_A = {(17, 6): {3: (221, 299), 4: (1343, 794)}, (19, 6): {3: (247, 299), 4: (1501, 794)},
         (17, 5): {3: (187, 176), 4: (952, 386)}, (19, 5): {3: (209, 176), 4: (1064, 386)}}
FIX_B = {6: (2028, 2278), 5: (3276, 2278)}


def b_elimination_count(counts):
    """Planned regime-B eliminations per cell (pilot projection): references
    (F-S3, F-RANDX, F-NULLB, F-AFFB: 5 + modal each), targets of the six
    regime-B families, C-REV (targets + F-S3 references + modal), C-DET (same),
    C-REPLAYB replays (50 x 3) and the minimum K_B probes (3 x 3). ROW-ORDER
    replays and rejected probes are unknown before data and not projected."""
    refs = 4 * 6
    targets = counts["F-S3"] + counts["F-SAT"] + counts["F-PLANT"] + counts["F-RANDX"] + counts["F-NULLB"] + counts["F-AFFB"]
    rev = counts["C-REV"] + 6
    det = counts["C-DET"] + 6
    replays = 50 * 3 + 3 * 3
    return {"references": refs, "targets": targets, "C-REV": rev, "C-DET": det, "replays_and_probes": replays,
            "total": refs + targets + rev + det + replays}

AMENDMENT_ID = "AMD-20260924-3a9f06"
AMENDMENT_PATH = "experiments/EXP-CERTBIN-a58c63/amendments/AMD-20260924-3a9f06.yaml"
DEV_OFFSET = None   # superseded by dev_cell_seeds / DEV_FIXED_SEEDS (AMD C-15)

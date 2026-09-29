"""M-A draw-support audit of EXP-ECRANK-76a70d R3-armB.

Reads committed bytes only. Reconstructs the seeded stream from the
predecessor source (imported read-only from its committed path) plus the
snapshot-bound raw-result.json. Never re-simulates from memory.
"""

import json
import os
import random
import sys
from fractions import Fraction as Fr
from math import gcd

REPO_ROOT = os.environ.get("ECRANK_REPO_ROOT", ".")
PRED_SRC = os.path.join(REPO_ROOT, "experiments/EXP-ECRANK-76a70d/source")
PRED_RAW = os.path.join(
    REPO_ROOT,
    "experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json",
)
ARM_SEED = 760708
H_SCHEDULE = [100, 100, 100, 1000, 1000, 1000, 10000, 10000]
S_IDX = [0, 1, 2, 3, 4]
B_INTS = sorted(set(range(-20, 21)) - {0, 1})
N = 8


def _load_pred_engine():
    import importlib.util
    path = os.path.join(PRED_SRC, "ecrank_engine.py")
    spec = importlib.util.spec_from_file_location("ecrank_engine_pred_76a70d", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_recorded():
    with open(PRED_RAW) as f:
        raw = json.load(f)
    tuples = raw["blind_rederivation_inputs_C3"]
    # AT-0/1/2 = first three of the record stream (stream 0, b_index 0,1,2)
    at = tuples[:3]
    return raw, at


def reconstruct_stream0_prefix(PE, n_b=3):
    """Replay stream 0 of arm B exactly as run_arm.py IC-15/IC-16/IC-3."""
    cosets = PE.eligible_cosets()
    rng_arm = random.Random(ARM_SEED)
    coset_ids = rng_arm.sample(range(len(cosets)), 3)
    coset = cosets[coset_ids[0]]
    values = [PE.class_value(m) for m in coset["members"]]
    rng_j = random.Random(ARM_SEED * 100 + 0)
    rows = []
    for bi in range(n_b):
        b_rest = rng_j.sample(B_INTS, N - 2)
        b = [Fr(0), Fr(1)] + [Fr(x) for x in b_rest]
        k = N // 2
        chosen = None
        attempts = 0
        while attempts < 1000:
            attempts += 1
            cand = rng_j.sample(values, k)
            if any(v < 0 for v in cand) and any(v > 0 for v in cand):
                chosen = cand
                break
        if chosen is None:
            raise RuntimeError("class_mix_failure at b_index %d" % bi)
        dpat = []
        for v in chosen:
            dpat += [v, v]
        rng_j.shuffle(dpat)
        draws = []
        for jd, H in enumerate(H_SCHEDULE):
            rS = {i: PE.draw_rational(rng_j, H) for i in S_IDX}
            in_box = all(PE.rational_height(rS[i]) <= H for i in S_IDX)
            draws.append({
                "draw_index": jd,
                "H": H,
                "rS": {str(i): str(rS[i]) for i in S_IDX},
                "in_box": in_box,
                "heights": {str(i): PE.rational_height(rS[i]) for i in S_IDX},
            })
        rows.append({
            "b_index": bi,
            "b": [str(x) for x in b],
            "d_pattern": dpat,
            "draws": draws,
        })
    return {
        "coset_index": coset_ids[0],
        "coset_V": list(coset["V"]),
        "rows": rows,
    }


def compare_recorded(reconstructed, recorded_at):
    mismatches = []
    for i, rec in enumerate(recorded_at):
        got = reconstructed["rows"][i]
        if [str(x) for x in rec["b"]] != got["b"]:
            mismatches.append({"at": i, "field": "b",
                               "recorded": rec["b"], "got": got["b"]})
        if list(rec["d_pattern"]) != list(got["d_pattern"]):
            mismatches.append({"at": i, "field": "d_pattern",
                               "recorded": rec["d_pattern"],
                               "got": got["d_pattern"]})
    return mismatches


def inbox_fraction(reconstructed):
    total = 0
    inbox = 0
    out = []
    for row in reconstructed["rows"]:
        for d in row["draws"]:
            total += 1
            if d["in_box"]:
                inbox += 1
            else:
                out.append({
                    "b": row["b"],
                    "draw_index": d["draw_index"],
                    "H": d["H"],
                    "heights": d["heights"],
                })
    return {
        "n_draws": total,
        "n_in_box": inbox,
        "in_box_fraction": (inbox / total) if total else None,
        "out_of_box": out,
    }


def synthetic_2d_planted_meet(H=20, seed=760808, plant=(1, 2)):
    """R1 / R2 planted-meet arithmetic on a synthetic 2-D integer box.

    |S| = (2H)^2 integer lattice of nonzero coords in [-H,H]\\{0}.
    N_a = 5 |S|. Plant one named point; draw N_a uniform points from S
    using Random(seed); expected meets = 5. Returns the known-answer
    packet and the observed meet count.
    """
    coords = [i for i in range(-H, H + 1) if i != 0]
    S = [(x, y) for x in coords for y in coords]
    absS = len(S)
    N_a = 5 * absS
    plant = (int(plant[0]), int(plant[1]))
    assert plant in S
    rng = random.Random(seed)
    meets = 0
    per_draw = []
    # Do not store all N_a draws (memory); count + log the first 8 and all hits
    for k in range(N_a):
        pt = S[rng.randrange(absS)]
        hit = pt == plant
        if hit:
            meets += 1
            per_draw.append({
                "k": k, "pt": list(pt), "squareness": [True, True],
                "meet": True,
            })
        elif k < 8:
            per_draw.append({
                "k": k, "pt": list(pt),
                "squareness": [False, False],
                "meet": False,
            })
    return {
        "H": H,
        "S_abs": absS,
        "N_a": N_a,
        "expected_meets": 5.0,
        "plant": list(plant),
        "meets_observed": meets,
        "per_draw_log_prefix_and_hits": per_draw,
        "known_answer_note": (
            "Uniform draws on a finite set S containing the plant; "
            "E[meets] = N_a / |S| = 5 by construction of N_a."
        ),
    }


def run_audit(smoke_only=False):
    PE = _load_pred_engine()
    raw, recorded_at = load_recorded()
    recon = reconstruct_stream0_prefix(PE, n_b=1 if smoke_only else 3)
    mismatches = compare_recorded(recon, recorded_at[: (1 if smoke_only else 3)])
    # determinism replay
    recon2 = reconstruct_stream0_prefix(PE, n_b=1 if smoke_only else 3)
    bit_identical = json.dumps(recon, sort_keys=True) == json.dumps(
        recon2, sort_keys=True)
    inbox = inbox_fraction(recon)
    plant = synthetic_2d_planted_meet(H=20, seed=760808)
    plants = []
    if not smoke_only:
        # one planted meet per AT, distinct plants (IV-9)
        for i, h0 in enumerate((7, 11, 13)):
            pkt = synthetic_2d_planted_meet(
                H=20, seed=760808 + 17 * (i + 1), plant=(h0, h0 + 1))
            pkt["at"] = i
            pkt["h0"] = h0
            plants.append(pkt)
    return {
        "audit_source_commit_bound": "a20a49b6adbcce51893c1221dbd69cdcd486ad9d",
        "recorded_AT": recorded_at[: (1 if smoke_only else 3)],
        "reconstructed": recon,
        "b_tuple_mismatches": mismatches,
        "reconstruction_bit_identical_replay": bit_identical,
        "inbox": inbox,
        "r1_planted_2d": plant,
        "r2_plants": plants,
        "pred_raw_parameters": raw.get("parameters"),
    }

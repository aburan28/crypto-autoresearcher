#!/usr/bin/env python3
# =============================================================================
# GATE 1 / CAND-FR-1 -- recomputation set of the AES-128 key-search computation
# graph, measured exhaustively over key-difference SUPPORTS and splice points.
#
# WHAT THIS IS: a combinatorial activity-pattern instrument. It is NOT an
# attack, NOT a distinguisher, NOT a key recovery, and asserts NOTHING about
# AES security at any round count.
#
# Reference: exhaustive key search only (2^128 AES-128 evaluations). No
# literature comparison of any kind is computed, printed, or implied.
#
# Model (frozen by the ideation, restated, not modified):
#   A1  conservative activity propagation: an S-box whose input byte difference
#       support is nonzero is counted as RECOMPUTED. Supports are OR-composed at
#       XOR (differences may cancel; conservative = upper bound on the count).
#   A2  unit of charge = one S-box evaluation; one full AES-128 = 200 of them
#       (160 data path + 40 key schedule).
#   A3  key schedule CHARGED (primary) and FREE (optimistic) both reported.
#   A4  one-dimensional enumeration; strictly weaker than a d-dim biclique.
#
# inference stanza (artifact-provenance gate):
#   requested_policy: executor-implementation
#   resolved_model:   claude-opus-5 (Claude Code subagent, model: inherit)
#   fallback_used:    true  (orchestration/model-policies.yaml names GPT-5.6
#                            family aliases which this harness cannot resolve)
#   model_verified:   false (no `orchestration.adapter doctor --probe` run)
# =============================================================================
import json, sys, time, itertools
from multiprocessing import Pool

SEED_NOTE = "NO RANDOMNESS. This instrument is a deterministic exhaustive " \
            "enumeration over all 65535 nonzero 16-bit key-difference supports " \
            "and all splice points. There is no PRNG and no sampling."

# ---------- byte-index conventions -------------------------------------------
# state byte index i encodes (row = i % 4, col = i // 4)   [column-major, FIPS-197]
IDENT = list(range(16))
TRANSPOSE = [0] * 16
for _c in range(4):
    for _r in range(4):
        TRANSPOSE[4 * _c + _r] = 4 * _r + _c      # (r,c) -> (c,r): semantics-preserving relabel


def build_tables(P):
    """Build 16-bit-mask propagation tables under byte-index relabelling P."""
    # ShiftRows in canonical coords: (r,c) -> (r, c-r mod 4)
    sr_bit = [0] * 16
    for c in range(4):
        for r in range(4):
            src = 4 * c + r
            dst = 4 * ((c - r) % 4) + r
            sr_bit[P[src]] = P[dst]
    isr_bit = [0] * 16
    for i in range(16):
        isr_bit[sr_bit[i]] = i
    # MixColumns column groups in relabelled coords
    cols = [[P[4 * c + r] for r in range(4)] for c in range(4)]
    colmask = [sum(1 << b for b in g) for g in cols]
    # round-key word w, byte j -> state bit P[4w+j]
    wordbit = [[P[4 * w + j] for j in range(4)] for w in range(4)]

    SR = bytearray()  # built as list of ints
    SRt = [0] * 65536
    ISRt = [0] * 65536
    MCt = [0] * 65536
    MCcols = [0] * 65536      # number of active MixColumns columns
    PC = [0] * 65536
    for m in range(65536):
        s = 0
        t = 0
        for i in range(16):
            if (m >> i) & 1:
                s |= 1 << sr_bit[i]
                t |= 1 << isr_bit[i]
        SRt[m] = s
        ISRt[m] = t
        o = 0
        nc = 0
        for k in range(4):
            if m & colmask[k]:
                o |= colmask[k]
                nc += 1
        MCt[m] = o
        MCcols[m] = nc
        PC[m] = bin(m).count("1")
    return SRt, ISRt, MCt, MCcols, PC, wordbit


TAB = {}
for name, P in (("ident", IDENT), ("transpose", TRANSPOSE)):
    TAB[name] = build_tables(P)


def keysched_activity(delta16, wordbit, matrix, Nr):
    """Return (rk_masks[0..Nr], key_schedule_sbox_count) for AES-128 schedule.

    delta16 : 16-bit support of the master-key difference, in state-bit coords.
    matrix  : 'AES' | 'NULL1' | 'NULL2' | 'NULL3'
    """
    if matrix == "NULL1":
        # independent uniformly random round keys: ANY nonzero master-key
        # difference changes every round key in every byte.  Key-schedule S-box
        # charge: the schedule is a black box that is wholly recomputed -> 40.
        return [0xFFFF] * (Nr + 1), 4 * Nr
    if matrix == "NULL2":
        # identity schedule: RK[r] = K for all r.  No key-schedule S-boxes.
        return [delta16] * (Nr + 1), 0
    # real AES-128 schedule (also used by NULL3, which only alters MixColumns)
    dW = [0] * (4 * (Nr + 1))
    for w in range(4):
        dW[w] = sum(1 << j for j in range(4) if (delta16 >> wordbit[w][j]) & 1)
    ks = 0
    for i in range(4, 4 * (Nr + 1)):
        if i % 4 == 0:
            prev = dW[i - 1]
            ks += bin(prev).count("1")          # SubWord: 1 S-box per active byte
            t = 0
            for j in range(4):
                if (prev >> ((j + 1) % 4)) & 1:  # RotWord
                    t |= 1 << j
        else:
            t = dW[i - 1]
        dW[i] = dW[i - 4] | t
    rk = []
    for r in range(Nr + 1):
        m = 0
        for c in range(4):
            w = dW[4 * r + c]
            for j in range(4):
                if (w >> j) & 1:
                    m |= 1 << wordbit[c][j]
        rk.append(m)
    return rk, ks


def datapath(rk, s, Nr, SRt, ISRt, MCt, MCcols, PC, no_mc):
    """Conservative recomputation count on the data path for splice point s."""
    sb = 0        # S-box instances recomputed
    ark = 0       # active bytes entering AddRoundKey  (XOR charge)
    mcc = 0       # active MixColumns columns          (GF mult charge)
    d = 0
    for r in range(s + 1, Nr + 1):
        sb += PC[d]
        d = SRt[d]
        if r < Nr and not no_mc:
            mcc += MCcols[d]
            d = MCt[d]
        ark += PC[d | rk[r]]
        d |= rk[r]
    d = 0
    for r in range(s, 0, -1):
        ark += PC[d | rk[r]]
        d |= rk[r]
        if r < Nr and not no_mc:
            mcc += MCcols[d]
            d = MCt[d]
        d = ISRt[d]
        sb += PC[d]
    return sb, ark, mcc


def run_matrix(args):
    matrix, perm, Nr, lo, hi = args
    SRt, ISRt, MCt, MCcols, PC, wordbit = TAB[perm]
    no_mc = (matrix == "NULL3")
    best = None
    hist = {}
    hist_dp = {}
    for delta in range(lo, hi):
        rk, ks = keysched_activity(delta, wordbit, matrix, Nr)
        for s in range(Nr + 1):
            sb, ark, mcc = datapath(rk, s, Nr, SRt, ISRt, MCt, MCcols, PC, no_mc)
            tot = sb + ks
            hist[tot] = hist.get(tot, 0) + 1
            hist_dp[sb] = hist_dp.get(sb, 0) + 1
            if best is None or tot < best[0]:
                best = (tot, sb, ks, ark, mcc, delta, s)
    return best, hist, hist_dp


def sweep(matrix, perm, Nr, nproc=4):
    bounds = [1 + (65535 * k) // nproc for k in range(nproc + 1)]
    jobs = [(matrix, perm, Nr, bounds[k], bounds[k + 1]) for k in range(nproc)]
    with Pool(nproc) as pool:
        res = pool.map(run_matrix, jobs)
    best = min((r[0] for r in res), key=lambda b: b[0])
    hist, hist_dp = {}, {}
    for _, h, hd in res:
        for k, v in h.items():
            hist[k] = hist.get(k, 0) + v
        for k, v in hd.items():
            hist_dp[k] = hist_dp.get(k, 0) + v
    return best, hist, hist_dp


def summarize(matrix, best, hist, hist_dp, Nr):
    tot, sb, ks, ark, mcc, delta, s = best
    NS_data = 16 * Nr
    NS_ks = {"AES": 4 * Nr, "NULL1": 4 * Nr, "NULL2": 0, "NULL3": 4 * Nr}[matrix]
    NS_tot = NS_data + NS_ks
    import math
    rho_tot = tot / NS_tot if NS_tot else float("nan")
    rho_dp = sb / NS_data
    out = {
        "matrix": matrix,
        "rounds": Nr,
        "N_S_datapath": NS_data,
        "N_S_keyschedule": NS_ks,
        "N_S_total": NS_tot,
        "argmin": {"delta_support_hex": "0x%04x" % delta,
                   "delta_hamming_weight": bin(delta).count("1"),
                   "splice_point": s},
        "min_recomputed_sboxes_total": tot,
        "min_recomputed_sboxes_datapath": sb,
        "keyschedule_sboxes_at_argmin": ks,
        "rho_min_total_charged": rho_tot,
        "rho_min_datapath_only_keyschedule_free": rho_dp,
        "implied_time_log2_keyschedule_charged": 128 + math.log2(rho_tot) if rho_tot > 0 else None,
        "implied_time_log2_keyschedule_free": 128 + math.log2(rho_dp) if rho_dp > 0 else None,
        "linear_work_at_argmin": {"active_ark_bytes_xor": ark,
                                  "active_mixcolumns_columns": mcc,
                                  "gf_mults": 16 * mcc, "mc_xors": 12 * mcc,
                                  "total_linear_ops": ark + 28 * mcc,
                                  "ratio_linear_ops_to_sboxes": (ark + 28 * mcc) / tot if tot else None},
        "histogram_total_count_to_frequency": {str(k): v for k, v in sorted(hist.items())},
        "histogram_datapath_count_to_frequency": {str(k): v for k, v in sorted(hist_dp.items())},
        "histogram_support": {"n_delta_supports": 65535, "n_splice_points": Nr + 1,
                              "n_cells": 65535 * (Nr + 1)},
    }
    return out


if __name__ == "__main__":
    import math
    t0 = time.time()
    result = {
        "gate": "GATE-1 / CAND-FR-1",
        "seed_note": SEED_NOTE,
        "model": {"A1": "conservative OR-propagation of difference SUPPORTS",
                  "A2": "1 S-box = unit; full AES-128 = 200 S-boxes",
                  "A3": "key schedule charged AND free both reported",
                  "A4": "1-D enumeration, weaker than a d-dimensional biclique"},
        "reference": "exhaustive key search, 2^128 AES-128 evaluations (definitional)",
        "class_ceiling_derived": {"aes128_log2": 128 - math.log2(200),
                                  "aes192_log2": 192 - math.log2(224),
                                  "aes256_log2": 256 - math.log2(276),
                                  "max_gain_bits_128": math.log2(200)},
        "matrices": {},
        "round_sweep_void_check": {},
        "control_of_control": {},
    }
    for matrix in ("AES", "NULL1", "NULL2", "NULL3"):
        b, h, hd = sweep(matrix, "ident", 10)
        result["matrices"][matrix] = summarize(matrix, b, h, hd, 10)
        print(matrix, "min_total=%d rho_tot=%.6f rho_dp=%.6f  t=%.1fs"
              % (b[0], result["matrices"][matrix]["rho_min_total_charged"],
                 result["matrices"][matrix]["rho_min_datapath_only_keyschedule_free"],
                 time.time() - t0), flush=True)

    # VOID condition (pre-registered): recomputation count must INCREASE with
    # round count for the real cipher.  Rationale in the frozen spec is that
    # adding rounds can only ADD recomputable S-boxes under A1, so the frozen
    # rationale is about the COUNT.  Both the count and the fraction are
    # reported; the void verdict is evaluated on the count, per the rationale.
    for Nr in range(4, 11):
        b, h, hd = sweep("AES", "ident", Nr)
        result["round_sweep_void_check"][str(Nr)] = summarize("AES", b, h, hd, Nr)
        print("round sweep Nr=%d min_total=%d  t=%.1fs" % (Nr, b[0], time.time() - t0), flush=True)

    # CONTROL-OF-CONTROL: a semantics-preserving relabelling of byte indices
    # (state transpose (r,c)->(c,r), applied consistently to ShiftRows, the
    # MixColumns column grouping and the key-schedule word->byte map) must leave
    # the measured quantity unchanged.  If it does not, the instrument is wrong.
    for matrix in ("AES", "NULL1", "NULL2", "NULL3"):
        b, h, hd = sweep(matrix, "transpose", 10)
        ref = result["matrices"][matrix]
        same_min = (b[0] == ref["min_recomputed_sboxes_total"])
        same_hist = ({str(k): v for k, v in sorted(h.items())}
                     == ref["histogram_total_count_to_frequency"])
        result["control_of_control"][matrix] = {
            "relabelling": "state transpose (row,col)->(col,row), applied to ShiftRows, "
                           "MixColumns column grouping and key-schedule word->byte map",
            "rho_min_unchanged": bool(same_min),
            "full_histogram_unchanged": bool(same_hist),
            "min_recomputed_sboxes_total_relabelled": b[0],
            "min_recomputed_sboxes_total_reference": ref["min_recomputed_sboxes_total"],
        }
        print("control-of-control", matrix, "min_same=%s hist_same=%s t=%.1fs"
              % (same_min, same_hist, time.time() - t0), flush=True)

    result["elapsed_seconds"] = time.time() - t0
    outp = sys.argv[1] if len(sys.argv) > 1 else "gate1_raw_result.json"
    with open(outp, "w") as f:
        json.dump(result, f, indent=1, sort_keys=False)
    print("WROTE", outp, "elapsed %.1f s" % result["elapsed_seconds"], flush=True)

#!/usr/bin/env python3
# Summarizer for GATE 2 / CAND-FR-2.  Merges shard counters and evaluates the
# PRE-REGISTERED conditions exactly as the ideation froze them.  Records
# observations only; asserts nothing about AES.
#
# inference stanza: requested_policy executor-implementation; resolved_model
# claude-opus-5; fallback_used true; model_verified false.
import json, sys, math, glob

def merge(paths):
    tot = None
    N = 0
    for p in paths:
        d = json.load(open(p))
        N += d["N_this_shard"]
        if tot is None:
            tot = {}
            meta = {k: d[k] for k in ("N_total", "seed", "keygen", "nshards")}
        for rec in d["records"]:
            k = (rec["matrix"], rec["delta"], rec["conv"], rec["r"])
            if k not in tot:
                tot[k] = [list(rec["bit0"]), list(rec["byte0"])]
            else:
                a = tot[k]
                for i in range(128): a[0][i] += rec["bit0"][i]
                for i in range(16):  a[1][i] += rec["byte0"][i]
    return meta, N, tot

def stats(tot, N):
    out = {}
    s1 = math.sqrt(0.25 / N)                     # sigma for b=1, null q=1/2
    p8 = 1.0 / 256.0
    s8 = math.sqrt(p8 * (1 - p8) / N)            # sigma for b=8, null q=2^-8
    for (m, d, c, r), (b0, y0) in tot.items():
        ex1 = [(x / N - 0.5) / s1 for x in b0]
        ex8 = [(x / N - p8) / s8 for x in y0]
        out[(m, d, c, r)] = {
            "N": N,
            "b1_q_min": min(x / N for x in b0), "b1_q_max": max(x / N for x in b0),
            "b1_max_abs_excess_sigma": max(abs(e) for e in ex1),
            "b1_n_positions_over_5sigma": sum(1 for e in ex1 if abs(e) > 5),
            "b1_argmax_bit": max(range(128), key=lambda i: abs(ex1[i])),
            "b8_q_max": max(x / N for x in y0),
            "b8_max_abs_excess_sigma": max(abs(e) for e in ex8),
            "b8_n_positions_over_5sigma": sum(1 for e in ex8 if abs(e) > 5),
            "b1_all_q_exactly_one": all(x == N for x in b0),
        }
    return out, s1, s8

def main():
    meta, N, tot = merge(sorted(glob.glob(sys.argv[1])))
    st, s1, s8 = stats(tot, N)
    mats = sorted({k[0] for k in st})
    deltas = sorted({k[1] for k in st})
    convs = sorted({k[2] for k in st})
    res = {
        "gate": "GATE-2 / CAND-FR-2",
        "reference": "exhaustive key search (definitional). NO literature comparison anywhere.",
        "oracle_use": "NONE. Both branches computed offline by the instrument; "
                      "no related-key query is made, so the mechanism stays single-key-legitimate.",
        "N_keys_per_configuration": N,
        "seed": meta["seed"], "keygen": meta["keygen"],
        "resolution": {
            "sigma_b1": s1, "five_sigma_floor_b1_absolute": 5 * s1,
            "five_sigma_floor_b1_relative_to_null": 5 * s1 / 0.5,
            "five_sigma_floor_b1_relative_log2": math.log2(5 * s1 / 0.5),
            "sigma_b8": s8, "five_sigma_floor_b8_absolute": 5 * s8,
            "PRE_REGISTERED_N_WAS": 2**22,
            "note": "N below the pre-registered 2^22/2^30 because of the 1800 s task "
                    "budget. The achieved floor is reported beside every reading, as "
                    "the ideation requires. A null reading at this floor establishes "
                    "the death round AT THIS FLOOR and nothing finer.",
        },
        "per_configuration": {},
        "death_round": {},
        "vacuity_check": {},
        "sensitivity_anchor": {},
        "void_condition": {},
    }
    for m in mats:
        for c in convs:
            for d in deltas:
                ks = [k for k in st if k[0] == m and k[1] == d and k[2] == c]
                if not ks: continue
                rs = sorted(k[3] for k in ks)
                prof = {str(r): st[(m, d, c, r)] for r in rs}
                res["per_configuration"]["%s|%s|%s" % (m, d, c)] = prof
                if d == "zero_vacuity":
                    res["vacuity_check"]["%s|%s" % (m, c)] = {
                        "all_q_exactly_one_at_every_r":
                            all(st[(m, d, c, r)]["b1_all_q_exactly_one"] for r in rs)}
                    continue
                # death round: least r such that for all r' >= r, both b=1 and b=8
                # max excess < 5 sigma
                death = None
                for r in rs:
                    if all(st[(m, d, c, rr)]["b1_max_abs_excess_sigma"] < 5 and
                           st[(m, d, c, rr)]["b8_max_abs_excess_sigma"] < 5
                           for rr in rs if rr >= r):
                        death = r; break
                res["death_round"]["%s|%s|%s" % (m, d, c)] = death
                # sensitivity anchor: r=1 and r=2 must show a large excess
                res["sensitivity_anchor"]["%s|%s|%s" % (m, d, c)] = {
                    "r1_b1_excess_sigma": st[(m, d, c, 1)]["b1_max_abs_excess_sigma"],
                    "r2_b1_excess_sigma": st[(m, d, c, 2)]["b1_max_abs_excess_sigma"] if 2 in rs else None,
                    "r1_over_5sigma": st[(m, d, c, 1)]["b1_max_abs_excess_sigma"] > 5,
                }
                # VOID: the excess must DECAY as r increases
                seq = [st[(m, d, c, r)]["b1_max_abs_excess_sigma"] for r in rs]
                res["void_condition"]["%s|%s|%s" % (m, d, c)] = {
                    "excess_sigma_profile": seq,
                    "decays_from_r1_to_last": seq[0] > seq[-1],
                    "flat_r3_r5_r7": (max(seq[2], seq[4], seq[6]) - min(seq[2], seq[4], seq[6]))
                                     if len(seq) >= 7 else None,
                }
    json.dump(res, open(sys.argv[2], "w"), indent=1)
    # console digest
    for key in sorted(res["death_round"]):
        m, d, c = key.split("|")
        if c != "no_final_mixcolumns": continue
        seq = res["void_condition"][key]["excess_sigma_profile"]
        print("%-16s %-16s death_r=%s  excess_sigma r=1..: %s"
              % (m, d, res["death_round"][key],
                 " ".join("%.1f" % x for x in seq)))
    print("VACUITY:", res["vacuity_check"])
    print("5sigma floor b=1 relative to null: %.3e  (2^%.2f)"
          % (res["resolution"]["five_sigma_floor_b1_relative_to_null"],
             res["resolution"]["five_sigma_floor_b1_relative_log2"]))

main()

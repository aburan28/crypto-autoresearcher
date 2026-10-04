"""J3 (Red Team, TASK-20260906-a6b415): direct inspection of every v2
STAGE 1v2/2v2 run's own summary.json for the CAP(2T,T_sel) arms, checking
S_peak_bits == 2T*bits_per_pool_entry exactly, that max_pool_entries equals
max_pool_entries_within_round (the coarse round-end tracker used for the
headline vs. the fine within-round-peak tracker used for the validity gate),
and that cap_truncations_total is >> 1 per round (evidence that truncation
fires repeatedly WITHIN rounds, not once at round end as in v1)."""
import json

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/runs"
for stage, nbits in [("1v2", 24), ("2v2", 30)]:
    for s in range(1, 6):
        d = f"{RUNS}/RUN-ECDLP-612fb1-v2-{stage}-s{s}"
        summ = json.load(open(f"{d}/summary.json"))
        T = summ["params"]["T"]
        bpp = summ["params"]["bits_per_pool_entry"]
        expected_cap_bits = 2 * T * bpp
        for lab in ("0.65T", "0.75T"):
            name = f"CAP(2T,{lab})"
            a = summ["arms"][name]
            ok = (a["S_peak_bits"] == expected_cap_bits == a["max_pool_entries"] * bpp)
            within_ok = (a["max_pool_entries"] == a["max_pool_entries_within_round"])
            n_rounds = len(summ["arms"][name]["rounds"]) if "rounds" in summ["arms"][name] else None
            print(f"{d} {name}: S_peak_bits={a['S_peak_bits']} expected={expected_cap_bits} "
                  f"max_pool_entries={a['max_pool_entries']} 2T={2*T} "
                  f"matches_within_round={within_ok} cap_honest_every_round={a['cap_S_peak_honest_every_round']} "
                  f"cap_truncations_total={a['cap_truncations_total']} "
                  f"-> {'OK' if ok and within_ok and a['cap_S_peak_honest_every_round'] else 'MISMATCH'}")

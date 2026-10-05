#!/usr/bin/env python3
"""w5_verdict_rule_poison.py -- joint W5 (1): the card's statement says the verdict is 'impossible' iff N_std < |V|. closure_cert.closure_certificate takes a separate branch when 1 enters W:
it sets verdict=sufficient and s=0 without comparing with the caller-supplied |V| (s_known). Demonstrate with the producer's own function (prodcopy: closure_cert.py copied byte-for-byte, my build of closure.c)
by handing it a deliberately WRONG |V| on a solution-free instance and on a solution-bearing one with a spurious... (only the first is needed). Scratch."""
import sys, os, json
SP = os.environ["SP"]; sys.path.insert(0, f"{SP}/work/prodcopy"); sys.path.insert(0, "/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures")
import closure_cert
for stem, V_true, V_poison in (("chained_n18_m2_t2_k9_d0", 0, 5), ("chained_n18_m2_t2_k9_d0", 0, 0)):
    s = json.load(open(f"{SP}/work/inst/{stem}.json"))
    c = closure_cert.closure_certificate(s["N"], s["equations"], 4, 1.0, s_known=V_poison)
    print(f"{stem}: true |V|={V_true}; |V| handed to the verdict rule = {V_poison} -> verdict={c['verdict']!r} basis={c['verdict_basis']!r} solutions={c['solutions']} solutions_source={c['solutions_source']!r} contains_one={c['contains_one']}")
# the same function on a solution-bearing instance with a wrong count: the non-contains_one branch does compare
s = json.load(open(f"{SP}/work/inst/chained_n16_m2_t2_k8_d0.json"))
for V in (2, 1, 3):
    c = closure_cert.closure_certificate(s["N"], s["equations"], 4, 1.0, s_known=V)
    print(f"chained_n16_m2_t2_k8_d0 (true |V|=2): |V| handed in = {V} -> verdict={c['verdict']!r} basis={c['verdict_basis']!r}")

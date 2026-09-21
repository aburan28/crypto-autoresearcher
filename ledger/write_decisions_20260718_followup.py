#!/usr/bin/env python3
"""Coordinator decisions for the 2026-07-18 follow-up evidence (EV-SIG-002, EV-DREG-002)."""
import json, re, sys
from pathlib import Path

LEDGER = Path("/Volumes/Volume/crypto-autoresearcher/ledger")

def q(s): return json.dumps(s, ensure_ascii=False)

def dec_yaml(d):
    L = ["coordinator_decision:", f"  id: {d['id']}", f"  context: {q(d['context'])}",
         f"  decision: {d['decision']}", "  target_ids: [" + ", ".join(d["targets"]) + "]",
         "  rationale:"]
    L += [f"    - {q(r)}" for r in d["rationale"]]
    L.append("  evidence_refs: [" + ", ".join(d["ev"]) + "]")
    L.append("  limitations:")
    L += [f"    - {q(x)}" for x in d["limitations"]]
    L.append("  next_actions:")
    L += [f"    - {q(x)}" for x in d["next"]]
    L += ["  decided_by: coordinator", '  decided_at: "2026-07-18"']
    return "\n".join(L) + "\n"

DECS = [
 dict(id="DEC-20260718-017",
  context="EXP-SIG-002 growth resolution for H-SIG-001 (non-rewritable syzygy component)",
  decision="supported_scoped", targets=["H-SIG-001"],
  ev=["EV-SIG-002", "RUN-EXP-SIG-002-a", "RUN-EXP-SIG-002-b", "RUN-EXP-SIG-002-c", "RUN-EXP-SIG-002-d",
      "RUN-EXP-SIG-002-e", "RUN-EXP-SIG-002-f", "RUN-EXP-SIG-002-g", "RUN-EXP-SIG-002-h", "RUN-EXP-SIG-002-i"],
  rationale=[
   "Growth question RESOLVED at replicated, multi-seed scope: residual non-rewritable D4 syzygy count = 9, 10, 13, 14 at n = 12, 15, 18, 21 — monotone increasing over the anchored range, +55.6%, zero within-size seed variance (16 standard instances).",
   "Separation from the null is exact: support-matched nulls show residual = 0 and rank = sr_pred on all 22 boolean + 4 D5 cells — the component is a genuine structural deviation, not a generic effect.",
   "Falsification clause (a) fails on every standard seed at every size (residual > 0; non-Koszul D3 syzygy present at every n = 9..21); the falsification disjunct 'deviations constant-sized in n' is numerically false over n = 12..21.",
   "Controls all PASS (null extra = 0; injected-syzygy detection; T2 anchor reproduced bit-exactly; determinism; cross-instrument D5 anchor 69,073 = EXP-DREG-001).",
   "n = 12 degeneracy resolved: seed-1 R_x = 0 instance reproduced bit-exactly and quarantined; 5 non-degenerate seeds are uniform (deficit 32 = 8n/3, residual 9).",
   "SCOPE OF SUPPORT: existence + monotone growth of a non-rewritable low-degree syzygy component over n = 12..21 at D <= 4. Whether a solver can exploit it is NOT measured — no d_reg/d_ff impact is claimed."],
  limitations=["D <= 4 (D5 cells counted but not signature-classified); growth resolved only over n = 12..21; n = 9 is uniformly exceptional (residual 23, deficit 41 != 24) — mechanism unexplained; new anomaly class 'linear-equation instances' (2/22 cells) excluded via input-side filter."],
  next=["H-SIG-001 = supported_scoped. Dispatch EXP-SIG-003 (link test): determine whether the non-rewritable syzygy family generates the EXP-DREG rank deficit (1,322/1,862 series) at n = 12/15 — if the residual syzygies span the deficit kernel, the two programs merge into one structural object; if not, they are independent anomalies. Theory note: n = 9 exception."]),
 dict(id="DEC-20260718-018",
  context="EXP-DREG-002 first past-wall cell (n = 17) for H-DREG-001",
  decision="inconclusive", targets=["H-DREG-001"],
  ev=["EV-DREG-002", "RUN-DREG-002-CONTROL-N17-SEM-PARTCONSIST-b", "RUN-DREG-002-CONTROL-N17-NULL-A-VERIFY"],
  rationale=[
   "First past-wall measurement, two-partition certified: n = 17 sem rank 125,099, deficit 1,823 vs sr_pred 126,922 (chunk 24000 vs 20000 partitions identical: system_hash, rank, deficit; all carries sha256-verified).",
   "Deficit series now 1,322 / 1,862 / 1,823 / 1,999 at n = 12 / 15 / 17 / 18 — NON-MONOTONE at the n = 17 insert; relative deficit declining 4.71% -> 2.70% -> 1.46% -> 1.39%. The within-wall deceleration continues past the wall; no acceleration observed.",
   "Review correction C1 discharged (partition A): n = 17 null rank = 126,922 == sr_pred_D exactly — the null is semi-regular at n = 17; null-arm two-partition gate remains OPEN (partition B in progress under the concurrent coordinator session).",
   "Hypothesis clauses still not evaluable: d_reg > 5 both arms (no d_reg separation), d_ff distribution unmeasured past n = 12, and one past-wall point cannot distinguish growth regimes.",
   "Rule-8 continuation: sem Macaulay column support 81.9% at n = 17, continuing the 84.2/82.2/80.8% decline while the null stays at 100% — the support-signature and the deficit now track together."],
  limitations=["One past-wall point (n = 17); n = 21/24 unmeasured; null partition B pending; timings contention-affected (ranks exact); measurement cells executed by the concurrent coordinator session, independently certified by EXP-DREG-002 from sha256-pinned copies."],
  next=["H-DREG-001 remains inconclusive, leaning bounded/stalling. The concurrent session owns the null-B gate and the n = 21 sem cell (costed 7–9 h, checkpointed); no duplicate dispatch from this thread. Watch for the support-coverage vs deficit link in EXP-SIG-003."]),
]

for d in DECS:
    p = LEDGER / f"{d['id']}.yaml"
    body = dec_yaml(d)
    if p.exists() and p.read_text() != body:
        print("REFUSE overwrite", p.name); sys.exit(1)
    p.write_text(body)
    print("wrote", p.name)

# H-SIG-001 -> supported_scoped
p = LEDGER / "H-SIG-001.yaml"
txt = p.read_text()
new, cnt = re.subn(r"(?m)^(\s*status:\s*)[a-z_]+", r"\g<1>supported_scoped", txt, count=1)
assert cnt == 1, "no status line in H-SIG-001.yaml"
p.write_text(new)
print("H-SIG-001.yaml: status -> supported_scoped")

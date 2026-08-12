# Red-team falsification review — GOAL-SSI-001 BATCH-001

Task `TASK-20260725-503` · Snapshot `1d907a5cefe5895af02b9a5acf58e8c78a50e5f4`  
Verdict: **REVISE**

## What survives

The baseline map is the right shape for a launch batch: SIDH/SIKE are treated as
a closed torsion-image regime; CGL, endomorphism-ring/SQIsign foundations, and
CSIDH are the survivors; `KN-OPEN-013`…`015` are named residuals. IDEA-20260725-001
is not a rediscovery of Castryck–Decru / Robert / Petit / GPST.

## What fails as stated

1. **Category error relative to completion criteria.** A Wiener-style cost-model
   correction can change which algorithm is the honest baseline. It does not, by
   the candidate's own limits, improve the attack cost of a surviving hardness
   assumption. Admitting it as an "algorithmic cryptanalytic candidate" invites
   BATCH-002 to spend a mechanism slot on documentation.

2. **Regime collapse.** On \(\mathbb{F}_p\)-rational instances, Delfs–Galbraith
   \(\tilde{O}(p^{1/4})\) already beats MITM \(\tilde{O}(p^{1/2})\) in step count.
   Full-cost makes MITM worse. Unless the gate separates \(\mathbb{F}_{p^2}\) MITM
   from \(\mathbb{F}_p\) DG, the "matched baseline changes" prediction is likely
   decision-irrelevant.

3. **Underspecified low-memory analogue.** Distinguished-point collision search
   on groups does not automatically transfer to expander isogeny graphs. The
   candidate lists this as a falsification condition; that condition is the real
   technical content of the next gate.

## Independence limit

Producer and this review share a conversation lineage after an API-limit
fallback away from `research-sol-max` / `review-xhigh`. Independence is
weakened. Do not treat BATCH-001 as sufficient for any completion-level claim.

## Required revision

Admit a **scoped baseline derivation** for BATCH-002, not a breakthrough-track
mechanism:

- Split \(\mathbb{F}_{p^2}\) vs \(\mathbb{F}_p\) regimes.
- Define or falsify the low-memory graph collision-search analogue.
- Cap promotion at a matched-baseline recommendation / `KN-TECH` note unless a
  material ranking change is proved.
- Keep orientation, CSIDH-quantum, and SQIsign-transcript lanes available as
  separate later candidates.

## Missed-candidate check

No cheaper typed cryptanalytic mechanism was sitting in the snapshot and wrongly
excluded. Deferred orientation / SQIsign-transcript routes remain higher setup
cost than the revised derivation gate.

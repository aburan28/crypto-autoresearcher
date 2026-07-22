# Prime-field ECDLP — candidate avenues & runnable-instrument handoff

Portable export of this session's idea generation + feasibility research.
Purpose: let a Sage-equipped environment pick up the highest-value next tests
directly. Nothing here is a breakthrough; every avenue carries an
expected-negative prior. Scope: generic prime-field ECDLP, toy scale.

## Honest status (what is already established)
The structural-exploitation space is largely closed by the campaign's ~20
hypotheses (most `rejected_scoped`) and confirmed on multiple independent axes:
- **Relation-yield axis**: decomposition yield saturates the birthday bound
  `~ k*B^m/#E` with bounded `k` (m=2 ~1.85, m=3 ~1.30), flat across ~100x in
  `#E`; m=2 is combinatorially capped at `~B^2/#E`. No sub-rho signal.
- **Solver axis**: a working index-calculus solver costs 10-27x MORE group
  operations than Pollard rho at toy scale.
- **Additive-structure axis**: degree-4 additive energy of the natural factor
  base is indistinguishable from random (ratio ~1.0).
- **Degree-of-regularity axis (DREG)**: `H-DREG-001` inconclusive; the decisive
  D6/n=12 datum is unmeasured (instrument is Sage/m4ri-gated).

Four hypotheses are `supported_scoped` — a real, measured non-generic
*structure* exists but does NOT convert to a sub-rho algorithm:
`H-INCB-001` (chord-richness excess), `H-BKKMV-001` (mixed-volume sparsity),
`H-JETB-001` (jet-augmented GGM), `H-SIG-001` (cascade laws).

## Environment tooling provisioned this session
- **m4ri** (exact bit-sliced GF(2) rank): `tools/provision_m4ri.sh` builds it
  from source (git clone works where conda/tarballs are proxy-blocked);
  `tools/m4ri_rank.py` binds it and reads the LinBox **SMS** format that
  `src/macaulay_export.py` emits. Verified: 31512x46717 GF(2) rank in ~19s.
- `galois` (numpy GF(2)/GF(p), small-scale) installed via pip.

## Candidate avenues (ranked; full records in `ledger/proposals/`)
| ID | Avenue | Why it survives | Priority | Runnable |
|---|---|---|---|---|
| IDEA-20260721-002 | p-exponent audit of the 4 `supported_scoped` signals | Only place a real lead can hide: does any confirmed structural advantage GROW with p? | high | Sage |
| IDEA-20260721-001 | Do INCB richness x BKKMV mixed-volume COMPOUND? | Two confirmed signals, only ever tested in isolation | high | Sage |
| IDEA-20260721-003 | Batch IC vs BATCH rho | Amortized setting not in ledger; baseline must be batch rho | medium | needs EC harness |
| IDEA-20260721-004 | BKKMV MV/Bezout ratio to the S_6..S_8 frontier | Extends a supported result; higher m usually costs more | medium | Sage |
| IDEA-20260721-005 | Quantum-annealing/QUBO relation search | Real 2024 direction; hardware-gated, no asymptotic change | low | hardware |

## How to run the top tests in a Sage environment
**IDEA-002 (recommended first).** For each confirmed signal, re-measure its
advantage magnitude across >=4 field sizes and fit the exponent vs p (log-log,
with 95% CI). Instruments already exist:
```
sage experiments/EXP-BKKMV-001/bkkmv1_cert.sage --stage counts3 --out mv_p<P>.json   # sweep P
sage experiments/EXP-INCB-001/incbarrier1_richness.sage ...                          # sweep P
```
Decision rule: any signal whose advantage-exponent 95% CI lower bound > 0 is a
genuine lead — escalate to independent verification. All exponents flat =>
the structural-signal space is rigorously closed (a strong negative result).

**DREG D6/n=12 (the coordinator's committed #1 next measurement).** Split the
pipeline: construct in Sage, rank here with m4ri.
```
# in the Sage env:
sage -python src/macaulay_export.py  ... --n 12 --d 6 --out d6n12_sem.sms   # + support-matched null
# here (m4ri, no Sage):
tools/provision_m4ri.sh
python3 tools/m4ri_rank.py d6n12_sem.sms  --deficit <SR_PRED>
python3 tools/m4ri_rank.py d6n12_null.sms --deficit <SR_PRED>
```
Report the D6 rank deficit vs the null — the first admissible degree-axis datum
for `H-DREG-001` (`DEC-20260720-002`).

## Bottom line
No medium-or-greater cryptographic breakthrough was discovered; the evidence is
uniformly barrier-confirming. These are falsifiable next-tests, not results.
The binding constraint on executing them here is Sage availability; m4ri (the
hard rank back-end) is already solved.

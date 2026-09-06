---
id: KN-FIND-1ba0fe
type: internal_finding
title: "ECDLP-IDEA-436's D1 coordinate-valuation profile collapses exactly to the +/-fibre indicator on a toy instance, confirming Proposition E and its canonical-lift mechanism"
tags: [lifting, local-torsion, p-adic, valuation, ecdlp, prime-field, toy-verified, ecdlp-idea-436, rc-1, negation-map]
confidence: toy_scale_two_instances_reproduced_by_three_independent_implementations
internal_refs: [H-ECDLP-a40416, EXP-ECDLP-c373eb, RUN-ECDLP-c373eb-1, EV-ECDLP-f5c698, DEC-20260901-34e038]
knowledge_refs: [KN-TECH-73630e, KN-OPEN-3417fc, KN-TECH-005, KN-TECH-006]
proof_status: empirical_only
proof_refs: [experiments/EXP-ECDLP-c373eb/runs/RUN-ECDLP-c373eb-1/raw-result.json]
added: 2026-09-01
superseded_by: null
---

## Finding

`ECDLP-IDEA-436`'s coordinate/valuation functional D1 (disjunct D1 of its
disjunctive hypothesis H), predicted by `Proposition E`
(`ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate_erratum_20260831.md`
section C.2) to collapse to the `<S>/{+/-1}` fibre indicator with zero
information and zero computational leverage beyond what Pollard rho's
negation map already exploits, is **confirmed by a toy-scale measurement**
(`RC-1`, `RUN-ECDLP-c373eb-1`), exhaustively on the tested instance:

- **Instance:** `E/F_p`, `p = 1009`, `y^2 = x^3 + x + 1` (ordinary, good
  reduction, `#E(F_p) = 1034 = 2 * 11 * 47`), `S = (286, 680)` of prime
  order `n = 47`, canonical order-`n` prime-to-`p` torsion lift `S-hat` at
  `p`-adic precision `r = 8`.
- **Order-`n` certificate:** `n * S-hat` equals the exact projective
  identity mod `p^8` (the full precision cap) — independently re-verified
  by the Coordinator via a separate, from-scratch Jacobian-coordinate
  implementation.
- **Primary tabulation (exhaustive, all 1035 pairs `1 <= j < k < 47`):**
  `D1(j,k) = v_p(x([k]S-hat) - x([j]S-hat))` truncated at `r=8` takes
  **exactly** the two values `{0, >=8}` — `0` on all 1012 off-fibre pairs,
  `>=8` on all 23 on-fibre pairs (`k = n-j`) — with **zero exceptions**.
  Independently re-verified by the Coordinator for five pairs (both
  on- and off-fibre) via a second, independent implementation; all matched.
- **Discriminating null-lift control:** the identical tabulation on a
  different, non-order-`n` Hensel lift of `S` shows image `{0, 1}` —
  genuinely different from `{0, 8}` — ruling out the alternative explanation
  that the observed flatness is a `p`-adic-library precision artifact rather
  than a consequence of the canonical lift's order-`n` (group-isomorphism)
  property.
- **`RTF-1` rigidity probe:** the Vandermonde (rigid, three-pairwise-
  difference) functional matches D1's own two-valued pattern exactly on the
  tested triples, consistent with the rigidity reading. The non-rigid
  three-point functional's image was `{0}` on the six tested triples — this
  is **statistically underpowered**, not a confirming or refuting result,
  since a generic non-rigid functional's mod-`p` coincidence is expected
  only with probability roughly `1/p` per triple.

## What this establishes

For this tested instance, `ECDLP-IDEA-436` disjunct D1 offers **zero
information and no computational leverage** beyond the `<S>/{+/-1}` quotient
already available for free in `E(F_p)` via a single `x`-coordinate
comparison, and already exploited by Pollard rho's negation map
(`KN-TECH-006`). This is a **negative result for this specific candidate**,
consistent with — and a fresh, independently confirmed instance of — this
program's existing structured-hardness baseline (`KN-TECH-005`).

## What this does NOT establish

- **Not replicated.** This is a single toy instance (one curve, one `n`);
  it has not been repeated on a second curve or a different `n`. Confidence
  is recorded as `preliminary`, not `strong` or `replicated`.
- **Not a closure of `KN-OPEN-3417fc`.** That open problem quantifies over
  *any* computable non-group-theoretic coordinate or valuation invariant;
  this finding concerns exactly one named functional family (D1), the one
  `KN-OPEN-3417fc` itself names as its headline worked example, not the
  question in general.
- **Not a disposition of `ECDLP-IDEA-436` disjunct D2** (a single-point
  coordinate-digit statistic, a different mathematical object from D1's
  two-point difference), which remains open.
- **Not a retiering of `KN-FIND-002` or `KN-FIND-b7e091`.** Objections
  against their recorded tier/justification remain routed to their own,
  still-unopened `review-breakthrough` round.
- **No cryptographic-scale claim.** Toy tier only
  (`docs/claims-and-verification.md`); no transfer argument to
  cryptographic-scale curves is made.
- **No information-theoretic novelty.** This is fully consistent with, and
  in fact a direct consequence of, `KN-TECH-73630e`'s prior result that the
  canonical torsion lift is information-theoretically empty.

## Forward guidance

A second toy instance (different curve, different `n`) would move this
finding from `preliminary` toward `replicated`. The `RTF-1` non-rigid probe
needs either a larger sample or a deliberately constructed triple exhibiting
a mod-`p` coincidence to be genuinely informative. `RC-3` (a held-out oracle
class outside `KN-FIND-002`/`KN-FIND-b7e091`) and `RC-4` (a frozen
regression fixture against `experiments/EXP-GGM-001/simulability_test.py`)
remain queued and undischarged, per `DEC-20260831-a9716f`.

## Provenance

- `ledger/hypotheses/H-ECDLP-a40416.yaml` (internal — the tested hypothesis)
- `experiments/EXP-ECDLP-c373eb/specification.yaml`,
  `experiments/EXP-ECDLP-c373eb/runs/RUN-ECDLP-c373eb-1/` (internal — the
  frozen specification and the run's manifest, raw results, and script)
- `ledger/evidence/EV-ECDLP-f5c698.yaml` (internal — the composed evidence
  record, including the Coordinator's independent re-verification)
- `ledger/decisions/DEC-20260901-34e038.yaml` (internal — this finding's
  promoting decision)
- `ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate_erratum_20260831.md`
  (internal — Proposition E, the mechanism this finding measures)
- `knowledge/techniques/KN-TECH-73630e.md` (internal — the isomorphism fact
  underlying the canonical lift)
- `knowledge/open-problems/KN-OPEN-3417fc.md` (internal — the broader open
  question this finding narrows one instance of, without closing)

## Confidence held at `preliminary` — upgrade to `replicated` refused 2026-09-03

A replication run (`RUN-ECDLP-c373eb-2`: p=1013, y²=x³+2x+2, S=(393,263),
n=41) was executed specifically to move this entry from `preliminary` toward
`replicated`, and an independent two-reviewer round (`BATCH-e8a3a7`, plan
committed before either reviewer launched) **refused the upgrade** on a
conjunctive split verdict. See `DEC-20260903-9f1190` and `EV-ECDLP-921b5d`.

**The run is sound.** A fresh blinded validator re-derived the instance and
the full 780-pair tabulation using methods sharing nothing with the
producer's — exhaustive digit search rather than Newton/Hensel, affine
sequential chain rather than Jacobian double-and-add, division polynomials
`ψ₄₁` as an independent order-`n` criterion — reproducing ~1560 per-pair
values and both 23-digit coordinates with zero mismatches. It additionally
ran a `t = 1..9` dose-response sweep yielding image exactly `{0, min(t,8)}`,
which **independently rules out the precision-artifact explanation** that the
null-lift control alone could not reach.

**Why the upgrade was still refused.** `RUN-2`'s script shares **266 of ~270
executable lines** with `RUN-1`'s, every function byte-identical, the entire
executable difference being five lines (`p`, `A,B`, `n`, the triples literal,
one added assert). The two runs are therefore one implementation on two
instances: `P(agree | shared systematic error) = 1`, so their agreement has
likelihood ratio 1 on the question at issue. The order-`n` block that
`RUN-2`'s manifest calls `independent_certificate` is likewise not
independent — it uses the same `jac_add`/`jac_dbl` as everything else.
The upgrade argument was shown to **prove too much**: run unchanged against
two runs of the same systematically wrong script, it still licenses
`replicated`.

**Two defects in the target label**, recorded for the corpus rather than
settled here: `docs/evidence-and-reproducibility.md` defines `replicated`
only as "reproduced from a clean run, *preferably* independently", which does
not decide this case; and `replicated` is absent from the KN-FIND
`confidence` vocabulary entirely (0 of 81 findings use it).

**What would discharge this (FG-1).** An independent cross-implementation
reproduction, ~40 lines and under five seconds: build the order-`n` lift
group-theoretically with no Hensel iteration —
`Ŝ' = [p^(r−1)·((p^(r−1))⁻¹ mod n)]L` for any lift `L` — using affine `Z/p^r`
arithmetic instead of Jacobian coordinates. It shares no line with either
existing script and exercises a different lift construction *and* a different
group law; since the order-`n` lift is unique, `x̂' == x̂` on all 8 digits is a
hard binary check on the load-bearing object. Do not re-attempt the upgrade
before it returns.

## J2 objection DISCHARGED 2026-09-03 — confidence raised

The refusal recorded in the section above is **superseded** (additively; that
section stands as the record of why the upgrade was refused at the time).
`FG-1` (`EXP-ECDLP-809375` / `RUN-ECDLP-809375-1`) discharged the objection.
See `DEC-20260903-256c7c` and `EV-ECDLP-feb897`.

**What FG-1 did.** Re-measured the D1 image on *both* already-measured
instances with an implementation independent on all three required axes: a
group-theoretic order-`n` lift
`Ŝ = [p^(r−1)·((p^(r−1))⁻¹ mod n)]L` with **no Hensel/Newton iteration**,
**affine `Z/p^r`** arithmetic rather than Jacobian coordinates, and no reuse
of either prior script. Image `{0,8}` on both: instance A 1035 pairs
(1012 zeros / 23 caps), instance B 780 pairs (760 / 20), every capped pair
satisfying `j+k=n` and every such pair capped.

**Control C-1 is decisive in kind, not degree.** The order-`n` prime-to-`p`
torsion lift is **unique**, so a differently-constructed lift either equals
the recorded one exactly or one construction is wrong. It matched **8/8
base-`p` digits of `x` and 8/8 of `y`, on both instances**. The Coordinator
independently reproduced this with a **third** implementation before
accepting it — three implementations now agree on the load-bearing object.

**Control C-3 strengthened the precision-artifact refutation** from the
indirect form ("the null lift differs") to the direct form: the on-fibre
value **tracks `r`** — 4→4, 8→8, 12→12.

**A correction this round produced.** The null-lift family used by RUN-1 and
RUN-2 (`x0 = S.x + p^e`) does **not** track `e`; it reads `{0,1}` at every
depth, because the naive integer-representative lift is already off-fibre at
depth 1. It was a **valid `e=1` refutation** — that conclusion stands — but it
was never a tunable dose-response instrument and must not be cited as one.

**What this still does not establish.** Implementation independence, *not*
answer-blindness: the contract stated the expected image and permitted
reading the prior manifests for the C-1 targets. Still toy tier — two ~10-bit
instances from one configuration family, held fixed *by design* so the
implementation was the only variable. FG-1 itself was **not** independently
reviewed; its force comes substantially from the discharging criterion having
been pre-specified *adversarially* by the reviewer whose objection it
discharges. If this finding is to move beyond toy tier, the ranked next step
is **scale and family diversity**, not more implementations.

> ## ⚠ SUPERSEDED IN PART — READ `CORR-20260807-3ee25d` FIRST
>
> This document was written **before** independent review. The Red Team found ten
> material defects and **five of the findings below are withdrawn or refuted**.
> The text is left unedited (AGENTS.md rule 4: corrections supersede, never
> overwrite); this header is its correct reading, and the adjudicated position is
> `EV-ENDO-e8d3e5` + `DEC-20260807-c8aa8b` (disposition: **revise**).
>
> | Section | Status |
> |---|---|
> | §3 "the isogeny-class grouping carries no detectable information" | **WITHDRAWN.** The permutation null is a between-class *mean* detector (power 1.00 at a 0.9% shift) and is blind to within-class structure. |
> | §3 relation yield reduces to invariants | **REFUTED.** Under the corrected sampler, yield is over-dispersed within class at both m and both primes — §5 prediction 1 fails. |
> | §3 walk speedup "94.7% of the ceiling, never above" | **WITHDRAWN.** One draw; the 8-seed mean 1.7344±0.2046 sits *on* the ceiling, 3/8 seeds exceed it, and the fruitless-cycle attribution is contradicted by the run's own zero counter. |
> | §3 "transport at ~1/6 the cost of rebuilding" | **REFUTED.** The rebuild baseline was inflated ~12× (double-and-add per entry for consecutive multiples). Transport loses at every odd ℓ tested. |
> | §3 j-invariant Gröbner cost "~3%" | **WRONG NUMBER.** Measured movement is under 1%; the only ~3% quantity is basis *size* for j=1728, at +3.41% (larger). |
> | §3 volcano level | **Survives on the correct variable**, but the batch's "level" was the 2-torsion count resolving 2 of 5 levels; the Red Team re-ran it properly (p=0.3115) with n=3 at the crater. |
>
> **Still standing:** the S₃ monomial-support counts (9/10/13, exact and
> hand-re-derived), the liftable-count identity and its Var(z)/4 consequence
> (2.9×10⁻¹⁴), the Hurwitz-Kronecker-certified enumerator, and transport
> *correctness* at odd ℓ. Also note §8's review-status paragraph is stale: the
> Validator produced **nothing**, so this batch has no independent run-integrity
> validation at all.

# BATCH-cb71b5 synthesis — GOAL-ENDO-001

Coordinator synthesis of the opening batch of the endomorphism / isogenous-curve /
j-invariant decomposition of prime-field ECDLP. **This document is a synthesis,
not an evidence record.** Every claim below cites the run, correction, or
proposal it rests on, and nothing here changes a hypothesis status.

Snapshot commits: `22eb74ba`, `96f0b5ca`, `b808751b` on
`claude/ecdlp-endomorphism-analysis-4m2w3z`, base `origin/main` at `e34afdd0`.

## 1. What was produced

| Artifact | Count | Where |
|---|---|---|
| Subproblem lanes, each with a research question | 14 | `ledger/questions/RQ-{ICINV,VOLC,JINV,EQIC,EQLA,EWALK,TORS,PAIR,CANL,CLGP,MODEL,GGMB,MTGT,INSTR}-*.yaml` |
| Falsifiable proposals | 121 | `ledger/proposals/IDEA-20260807-*.yaml` |
| Draft experiment contracts | 121 | `experiments/EXP-*/specification.yaml`, indexed in `experiment_index.json` |
| Executed experiments with immutable run records | 8 | `experiments/EXP-{INSTR-2d32ba,ICINV-180a0d,ICINV-9b1f7c,JINV-6c5b8e,JINV-dd60d3,EWALK-cc0353,EWALK-4fc679,VOLC-9fec05,MTGT-321a54}/runs/` |
| Corrections | 3 | `ledger/corrections/CORR-20260807-{df0585,a05e1e,2c9ae4}.yaml` |

Every draft contract is at `status: draft` and **none is approved**. Approval is
Coordinator-only and the proof-search-map gate (`KN-TECH-080`) applies before any
expensive run.

## 2. The organising fact

**Transport theorem T1.** An `F_p`-isogeny `phi: E -> E'` of degree coprime to
`N` restricts to an injective homomorphism on `G = <P>`, and `phi(Q) = [k]phi(P)`.
The scalar `k` is unchanged. Verified per-entry, independently of the code that
computed the isogeny, in `RUN-MTGT-p2003e3` (400/400 table entries) and by the
Vélu transport certificate in `harness/isogeny_class.py:verify_transport`; every
target curve lands at the same trace, as Tate requires.

So ECDLP difficulty is an isogeny-class invariant up to transport cost, and the
whole class falls if any curve in it does. That makes the campaign's gating
question well-posed: **is any attack-cost functional non-constant across a
class?**

## 3. What the eight executed experiments found

All at toy scale, `p <= 100003`, `claim_tier: toy`.

**The instrument passes its two-directional control first, and it is blocking**
(`EXP-INSTR-2d32ba`). It detects a planted spread and rejects a matched null, and
it records a sensitivity floor so that every negative below reads as a **bound**
rather than as "no effect".

**Enumeration completeness is certified, not assumed.** Curves are enumerated by
j-invariant and twist, and the weighted class sizes are checked against the
Hurwitz–Kronecker class number `H(4p - t^2)`. The census **rejected the first
implementation on 60 of 127 traces at p = 1009** (imprimitive forms counted) and
passes on every ordinary trace at p = 1009, 2003, 4001, 6007 after the fix. A
variance measured over an incomplete class would be meaningless, which is why
this gate exists.

**The gating result (`EXP-ICINV-9b1f7c`, p = 4001 and p = 6007).** Under the
corrected uniform sampler, the label-permutation null shows the isogeny-class
grouping carries **no detectable information** about decomposition efficiency:
`p = 0.131` (m=2) and `0.295` (m=3) at p = 4001; `p = 0.196` and `0.691` at
p = 6007. Every functional measured reduces to one of three things:

1. **An exact class invariant** — `#E` and the `S_3` monomial support have
   literally zero within-class variance.
2. **The 2-torsion structure** — the full-field liftable density obeys the exact
   identity `#liftable_x = (#E - 1 + z)/2`, verified on every curve of every class
   at three primes. `#E` is the class; `z` is not; and the observed within-class
   variance of the count matches the predicted `Var(z)/4` to `2.9e-14`.
   The window decay test confirms the mechanism: within-class count variance rises
   with window size (52 → 96 → 151 → 250 → 347 from `p/32` to `p/2` at p = 6007)
   and collapses to `0.252` at the full field.
3. **Sum-set size** — the m=3 over-dispersion is entirely `|3V|`; the residual
   after removing it is 0.73× the binomial sampling variance, i.e. below noise.

None of the three gives a class-level attack handle.

**Special j-invariants (`EXP-JINV-dd60d3`).** The `S_3` monomial support is
exactly **9** for `j = 0`, **10** for `j = 1728`, **13** for generic — a real,
exactly symbolic structural simplification. It does not move solver cost:
Gröbner-time ratios are 0.988, 1.011, 1.000 against generic. The factor-base
polynomials dominate.

**The automorphism-quotient walk (`EXP-EWALK-4fc679`, p = 100003, 100% solve
rate).** Observed quotient-over-plain speedup **1.641** against the incremental
ceiling `sqrt(|Aut|/2) = sqrt(3) = 1.732`, i.e. 94.7% of it, never above. The
shortfall is fruitless-cycle cost. The generic arm returns exactly 1.000, which is
a definitional self-check (both modes already quotient by negation), not a
measurement.

**Volcano level (`EXP-VOLC-9fec05`, p = 4001, ell = 2, genuine level diversity:
72 curves at degree 1 and 66 at degree 3).** Level carries no detectable
information about decomposition rate, `p = 0.391`.

**Preprocessing transport (`EXP-MTGT-321a54`).** A table of (point, scalar) pairs
transports with every entry independently certified, at ~1/6 the cost of
rebuilding. This moves a point on the `S*T^2 = N` frontier; it does not move the
frontier.

## 4. Three defects found, and how

This is the part of the batch most worth reading, because in every case the
defect was found by a control or by an independent reader, not by the author.

| Correction | Defect | Found by |
|---|---|---|
| `CORR-20260807-df0585` | The quotient walk canonicalised orbit representatives **without carrying the automorphism eigenvalue through the exponents**, so every orbit collision produced a relation that does not hold. On j=1728 it turned a 9-step solve into a 1676-step one and reported the 260× slowdown as a measurement. | The arm's own internal consistency: a quotient walk cannot be slower than what it quotients, and the generic arm returned 0.991 where 1.000 is forced. |
| `CORR-20260807-a05e1e` | The target sampler hashed to an `x` and kept it if it lifted. Liftability is a function of `(#E, z)`, and `#E` **is** the class — so the sampler encoded the grouping variable into the data and every between-class comparison partly measured the sampler. | **Replication.** p = 4001 alone showed nothing; p = 6007 produced a signal (`p = 0.0035`) that did not replicate. Conditioning on `z` did not remove it; a uniform sampler did (`0.0035 -> 0.1910`). |
| `CORR-20260807-2c9ae4` | (A) the decay verdict tested for *zero* variance where the identity predicts `Var(z)/4`; (B) T4 omitted the group structure of `E(F_p)` from what varies within a class; (C) T5's cost conclusion was wrong. | Independent lane sessions reading the committed artifacts. |

**(C) deserves emphasis because it strengthens the negative.** T5 originally
concluded that a good curve identifiable only by a global address "is unreachable,
and the lane dies on cost". Identification is claw-finding on `Cl(O)` at
`p^{1/4+o(1)}`, and `1/4 < 1/2` — that is **cheaper** than the rho baseline it was
charged against. The reachability gate closes no lane asymptotically. What closes
this one is the measurement: there is nothing to find. A negative resting on
"nothing varies" is a result; one resting on "you could not reach it anyway" would
have been an excuse. (Concretely the verdict flips: `2^96`–`2^112` against `~2^89`
at 2^256 under a conservative `O(ell^3)` per-step model. Both statements travel
together.)

## 5. The obstruction, named

Combining the measurements with the lanes' derivations, the campaign's negative
has a mechanism rather than a fatigue count:

> **On a prime-order subgroup, every endomorphism acts as a scalar** (`H-ENDO-001`),
> so nothing routed through the group action can distinguish curves in a class.
> **Isogeny transport is exact and information-free**: `Tate` fixes `N`, so
> transport multiplies representations without adding a congruence. The
> quantities that DO vary within a class — `j`, the coefficients, the group
> structure, the volcano level — enter the measured attack costs only through
> `(#E, z)` and sum-set combinatorics, both of which are computable in negligible
> time from the curve and neither of which is a discrete-log handle.

Independent convergence worth recording: the `RQ-JINV` lane derived from
`KN-TECH-018` alone that the naive `sqrt(6)` reading double-counts negation and
overstates the special-j discount by `sqrt(2)`. That is exactly the
incremental-ceiling correction the `EWALK` measurement forced empirically the same
day, from the opposite direction.

## 6. What stays open — this is not a closed lane

- **`RQ-CANL-63098f` is under-populated** (3 proposals against 8–9 elsewhere) and
  has no executed experiment. It is not adjudicated.
- **Arity `m >= 3`**: the `RQ-ICINV` lane's genus-1 argument for exact yield
  invariance gives out entirely at `m >= 3` and every closure must be redone there.
- **The one exponent-shaped open rung** (`RQ-EWALK` lane): an efficiently
  computable, non-constant `<lambda>`-invariant on the *encoding* would be worth
  `N^{1/3}` at `O(1)` memory, and Shoup does not forbid it because such an
  invariant is non-generic by construction. Honest prior recorded as 0.02.
- **Complete enumeration is `O(p^2)`**, so complete classes and cryptographically
  meaningful `N` are mutually exclusive in this harness. Nothing here says what
  replaces enumeration above ~2^14.
- **T5's rapid mixing is GRH-conditional and cited, not measured.** No experiment
  in this batch measured an isogeny-walk mixing time.
- **A corpus over-read flagged by the `RQ-MTGT` lane**:
  `experiments/EXP-ISADV-001/advice_transfer.py`, whose result is recorded
  downstream as a scoped negative on isogeny advice transfer, **applies no isogeny
  anywhere in its computation**. It measured the null object with no treatment
  arm. The number was right; the reading was not. That prior negative must not be
  cited against transport. This is flagged for the owning campaign, not corrected
  here.

## 7. Scope and honesty

Everything is toy scale and capped at `claim_tier: toy`. **No lane produced a
speedup and none is claimed.** `dominated_by`: every proposal and every measured
arm is dominated by parallel Pollard rho with distinguished points at
`0.886 sqrt(N)` group operations and `O(1)` memory (`KN-TECH-001`,
`KN-TECH-006`), by the automorphism-discounted variant on CM curves
(`KN-TECH-018`), and by BSGS at `sqrt(N)` time and memory. `sota_delta`: **zero**.
No standardized or deployed curve is affected by anything in this batch.

## 8. Review status

Independent validation (`review-adversarial`) and red-team review were dispatched
against snapshot `22eb74ba` and their reports land under `reviews/`. **No evidence
record and no hypothesis-status transition may be written before those reports are
read**; this synthesis is a producer artifact and carries no official standing
until then.

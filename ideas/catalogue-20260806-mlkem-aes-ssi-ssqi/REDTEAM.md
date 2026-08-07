# REDTEAM — adversarial review of catalogue-20260806-mlkem-aes-ssi-ssqi

Reviewer role: red team. Twelve slice files read (M1, M2, M3, A1, A2, A3, S1, S2, S3, Q1, Q2, Q3),
~120 entries. Every entry was checked in the order (a) lossy-projection failure, (b) uncharged
resource, (c) ceiling violation, (d) non-discriminating test, (e) scope leak.

**Independent recomputation performed during this review** (standalone Python, stdlib only, no
catalogue code reused):

- **A1's four algebraic facts all reproduce exactly.** AES S-box DDT is a function of
  `m = δ·A⁻¹(γ)` alone: 255 classes, 0 violations; the 4-entries are exactly the class `m = 1`;
  row profile of every nonzero δ is `{0:129, 2:126, 4:1}`. BCT is a function of the same label:
  255 classes, 0 violations, histogram `{0:128, 2:124, 4:1, 6:2}`, boomerang uniformity 6 attained
  exactly at `m ∈ {0xbc, 0xbd}`. Trace-form LAT of `Inv` is a function of `a·b` alone: 255 classes,
  0 violations, 16 distinct values in `[−28, 32]`, `max|W| = 32`. MixColumns: weight-1 → weight-4
  1020/1020; weight-2 → weight-3 6120 of 390150.
- **A1-9's fibre histogram reproduces exactly**: maxima over the 255 nonzero slopes
  `{4:84, 5:136, 6:31, 7:3, 8:1}`; `a = 01,02,03 → 4,5,5`; `a = 09,0b,0d,0e → 5,5,5,6`;
  and `max_b #{x : Inv(x)+ax = b} = 2` for every `a ≠ 0` (the conic gate).
- **A2's KS-1 and KS-2 reproduce exactly.** FIPS 197 A.1 gives `W[4] = a0fafe17`,
  `W[43] = b6630ca6`. Word counts: AES-128 40 words / 10 SubWord / 30 linear → 960; AES-192
  46 / 8 / 38 → 1216; AES-256 52 / 13 / 39 → 1248. Cross-key shift defect: defect-set size
  **exactly 1** at every `s ∈ {1..9}` over 300 random keys, values `03,05,09,11,21,41,81,1a,37`,
  replicated identically in all four words.
- **M1-8's Compress fibre census reproduces**: `d_u = 11` gives 767 singleton fibres and 1281
  doubles (767 + 2·1281 = 3329); `d_u = 10` gives 767 fibres of size 3 and 257 of size 4.
- **M2-2's variance table, M2-5's `2^12 − q = 767` binomial, M2-10's wire-length census
  (`384k+32` = 800/1184/1568 vs `32(d_u k + d_v)` = 768/1088/1568), M3-1's cost table,
  M3-3's `11/6` vs `4/3`, M3-10's binomial tail, S2-1's `#Cl = 3h(−p)` with `h(−p)` odd,
  S2-2's crossover table, S2-6's `L_p[1/2,√2]`, S2-10's two gates, S3-9's `2^{e_rsp−1}`
  consistent pairs, S3-10's `6X²/(p ln X)` and `12/ln p = 0.069`, Q2-6's `W* = p^{1/6}`,
  Q2-9's `126.21 − 108.73 = 17.48` all reproduce.**

The arithmetic backbone of this catalogue is, with the exceptions named below, correct. The
failures are almost entirely **inferential**: correct numbers attached to the wrong quantity, to a
strawman adversary, to an event the proposed data complexity cannot reach, or to a prediction that
is a theorem.

---

## 1. KILLS

### K-1. M2-6 — "Best-of-`2^t` seeds: moving the selector to the victim's key generator"
**Defect: the threat model is empty.** The only actor holding `M = 2^t` at the key generator is the
key generator itself, and it already knows `(s, e)`. Exfiltrating the key strictly dominates
grinding `2^{40}` seeds for a norm ratio of 0.836 and a bounded `Δβ`. There is no adversary for whom
this is the best available move, and the entry never names one. The `t`-to-halve column
(111 / 185 / 246) confirms the lever is inert even in the fictional model. Its `sqrt(log M)` law is
correct and belongs in M2's CEIL-2 as a one-line note, not as an entry.

### K-2. M2-9 — "The combiner binding bit-vector"
**Defect: the prediction is a tautology.** "A combiner inherits a planted defect `X_A` iff its
bit-vector omits `X_A`" is, given a collision-resistant KDF, the statement that a hash output
depends on its inputs. The proposed 6×3 = 18-cell cross-product confirms elementary function
composition. The only non-trivial residue — a combiner that omits `X_A` but resists the defect
because `X_A` is derivable from another included input — is arranged away by the planting
construction itself. F9-a is therefore unreachable by design.

### K-3. A1-8 — "The mixture agreement-pattern word"
**Two defects, either fatal.** (i) The stated mechanism is vacuous: `T` ranges over the 14 proper
nonempty subsets of a **4-byte** diagonal, so "`A_2` is a function of a 4-bit reduction of `T`,
i.e. of which post-ShiftRows column `T` touches" is a bijective relabelling of `T`. The prediction
`|supp(A_2)| ≤ 16` is then the (different, unstated) claim that `A_2` is essentially constant.
(ii) The entry's own risk band concedes the expected deliverable is a **two-round** depth
statement, i.e. dominated by the committed REF-C death rounds (r = 4 for the 1-byte integral,
r = 5 for the full-diagonal one). An entry whose expected value is "dominated by an already
committed measurement" is not a candidate.

### K-4. A2-4 — "Mode-transfer identity: a GF(2)-affine combiner preserves set-aggregate death rounds"
**Defect: the entire entry is one line of linear algebra.** `⊕_x C(E(x)) = C'(⊕_x E(x))` for affine
`C` and even `|X|` is the definition of affine. All four predictions — (i) XOR-of-two-keyed-
permutations reproduces REF-C, (ii) CTR keystream reproduces REF-C, (iii) the GF(2^128) product
destroys balance, (iv) truncation preserves it — are forced by that line. The six-arm,
`2^{35.6}`-encryption sweep has no reachable outcome other than instrument failure. The falsifier
F4-b ("the non-affine arm also balances") would be a bug report about the field arithmetic, not a
finding about combiners.

### K-5. A3-7 — "Hull minus characteristic, measured, at `r = 2, 3, 4`"
**Defect: out of envelope by roughly 90 bits, and the repair silently changes the object.** With
`Δ_in` supported in one byte, a 3-round AES characteristic activates `1 + 4 + 16 = 21` S-boxes, so
the exact differential probability `Pr_x[E^3(x) ⊕ E^3(x⊕Δ_in) = Δ_out]` is on the order of
`2^{-126}`. The proposed exact `2^{32}` sweep at `r = 3` and sampled `2^{34}` at `r = 4` cannot
produce a single hit, so `κ(3)` and `κ(4)` — the entry's whole deliverable and the only place the
"only named crack in O-1" would be touched — are unmeasurable. The "32-bit projected difference
counter" that makes the `r = 4` arm affordable replaces the exact differential by a **truncated**
one, which is a different object and is no longer comparable to "the best single characteristic"
computed by the per-column DP. The `r = 1` gate (`κ = 1.000` exactly) is sound and is the only part
that survives.

### K-6. M1-6 — "Pool survival across a sliding BKZ window"
**Defect: the charge being audited is not in the model the slice's bits are denominated in.** The
entry states "Every core-SVP number charges a BKZ tour as `d` independent SVP calls at
`2^{0.292β}`." Core-SVP is precisely the convention that charges **one** SVP oracle call and
deliberately discards the tour count and the factor `d`; that is what makes it a lower bound. So
`log2(1/ρ)` measures the removal of an overcharge that core-SVP has already given away for free,
and CEILING-M1's Budget C ("tour count, warm starts") is charging a term core-SVP does not carry.
The `ρ = 0` zero-slide gate and the `ρ ≈ 1` β-slide gate are good instrument design and should be
salvaged into M1-5, but the entry's headline cannot move any number in this slice's own units.

### K-7. S1-2 — "The terminal-filter exponent identity `1/(2(2−c))`"
**Defect: the identity does not follow from the cost expression it is derived from, and the
three-row table is a fit through two committed numbers.** The entry writes
`T(M) = p·C_test(M)/M^{3/2} + C_find(M) + poly`, sets `C_test = M^c`, `C_find = M^{c'}` with
`c' ≥ c`, and asserts the optimum at `M = p^{1/(2−c)}`. Balancing the two terms actually gives
`M = p^{1/(c'−c+3/2)}`, which equals `p^{1/(2−c)}` only when `c' = 1/2` — violating `c' ≥ c` for the
`c = 1` row. Reverse-engineering the published table shows the identity is really `T = M^{1/2}`
with `M = p^{1/(2−c)}`: the entry silently uses the **ball cost `M^{1/2}`** for the test while
simultaneously calling the test cost `M^c`. Two further breakages: at `c = 1` it places
`M = p`, far beyond the saturation point `M = p^{2/3}` at which `A_M` is already the whole vertex
set (the entry's own §0.3(2)); and a one-parameter family passed through the two anchors
(`1/2` at `c = 1`, `1/3` at `c = 1/2`) is an interpolation, not a retrodiction, so the
`c = 0 → 1/4` row — advertised as "the entry's sharpest content" and as a defect report about
charging — is pure extrapolation of that fit. The `c ≥ 1/2` ball-geometry argument is worth
keeping; the identity is not.

### K-8. S2-10 — "The key box is not uniform on the class group: an entropy-deficit ceiling"
**Defect: the tracked object provably does not bound the family it claims to cap, and the entry's
own cited neighbour is the counterexample.** `Δ = log2 #Cl − H(π_*Unif(box))` bounds
distinguishing/guessing advantage arising from **non-uniformity** of the shift on `Cl`. A
"short-key" lever exploits the box's **additive decomposability** in `Z^{n_primes}` (`e = e1 + e2`),
which is untouched by `Δ` and survives even at `Δ = 0` exactly. The entry's nearest-prior-art
neighbour `B2-10` records precisely such a lever — the full-cost `|Cl|^{2/3}` MITM on exponent
vectors. So the claim "no such lever can gain more than `Δ` bits, because `Δ` is exactly the
information the non-uniformity carries" is refuted by the record the entry cites. Its two
known-answer gates are exact and correct (orthogonal `Λ` ⇒ `Δ = 0.000`;
`Λ = diag(2(2m+1),…)` ⇒ `Δ = n_primes` exactly) — they simply gate the wrong invariant.

### K-9. A3-10 — "The anytime-progress axis"
**Two defects.** (i) Both curves are forced by the source code's return structure, not measured: a
filter attack that returns only on completion has `E(t) = 0` before completion by construction, and
a trial loop eliminates keys at its trial rate by construction. (ii) The dominance is over nothing:
`E_REF-A(t) = log2(7.555e7·t)` reaches ≈ 42 bits over a whole campaign, i.e. it excludes `2^{42}`
of `2^{128}` keys — a partially-run exhaustive search has an anytime value of `2^{-86}` of the key
space. "Strictly dominant on the anytime axis" is dominance over a quantity that is itself
negligible. The genuinely useful residue — "do not pro-rate a structured attack across producer
tasks" — is a paragraph obtainable by inspection, not a ten-minute measurement with a
Pareto-axis claim attached.

---

## 2. DEMOTIONS

Each survives only at the stated reduced ceiling.

**ML-KEM (M1/M2/M3).**

- **M1-1** → toy instrument only. "The estimator's optimisation over `m` is a function of `(n_q, n_1)`
  alone" is false; `lwe_primal`'s `m`-optimisation consumes the full simulated profile including the
  middle-segment slope. The tracked object is coarser than the consequent requires.
- **M1-2** → already `control`; note that best-of-`R` over reductions is capped by the *same* generic
  `gain ≤ log2 R` accounting as `GOAL-MLKEM-005`'s `G ≤ log2 M`, so the claim that "that convexity
  argument does not apply at all" understates how closely this rediscovers a committed ceiling.
- **M1-3** → arithmetic note only. Arikan's `E[G]` is not the metric published hybrid costings use;
  they charge the size of the enumerated set for a target success probability, a Rényi order
  depending on that probability, not `H_{1/2}`. The table (`H`, `H_{1/2}`, `log2|supp|`) is right;
  the claim that the literature is charging "the wrong exponent" is aimed at a charge nobody makes.
- **M1-4** → requires re-derivation before use. The headline table compares a **discrete** entropy
  `H(CBD_η)` against a **differential** entropy `(1/2)log2(2πeσ²)`; and §0.3's screening constant
  `K` is defined on a gain `v` in **log2-variance**, while M1-4 substitutes an **entropy** gap.
  Under the entropy-power relation an entropy deficit of `v` bits corresponds to `dL = v`, not
  `v/2`. The `0.179–0.249 core-SVP bits` headline is not derived from the stated conversion. The
  `min_Q D_KL` computation the test proposes is the right object and should replace the table.
- **M1-5** → instrument calibration only. `γ(d) = log2 P / log2 N` is a ratio of logs; with
  `P = 2^{ad+c1}` and `N = 2^{bd+c2}` it rises to `a/b` from below for purely arithmetic reasons.
  The declared load-bearing prediction ("the sign and monotonicity, not the value") is therefore
  forced by additive constants rather than by the sieve — non-discriminating. The all-pairs gate
  returns `2 − 1/log2 N`, not `2.000`.
- **M1-7** → sign is instrument-forced. The observable is "the greedy lift contains the **true
  shortest vector**", strictly stronger than what d4f operationally requires (a vector short enough
  for BKZ progress), so `f_{1/2} < f_closed` is forced by the definition of the observable. The
  closed form moves only 13.4 → 14.0 dimensions across `β ∈ [45, 65]`, so "differs by > 1 dimension
  with a consistent sign" carries no extrapolation content.
- **M1-9** → `t*` only. `A_n`, the lag-`n` autocorrelation of the GS profile, is a **presentation**
  statistic: the profile is basis-ordering dependent, which is the exact failure mode of the refused
  P3 adjudicator (`EV-MLKEM-94c773`). The entry pre-registers the AM-4 check, which it should fail.
- **M1-10** → design defect. An `r = 4` by `c = 4` layout with **one observation per cell** has zero
  residual degrees of freedom; the interaction is completely confounded with error and cannot be
  F-tested at all. Replication within cells is not optional here.
- **M2-1** → per-key DFR dispersion arithmetic only. The selection the headline proposes is
  unimplementable: `δ(sk)` depends on `||s||²` and `||e||²`, which are secret, and the entry
  explicitly distinguishes itself from the prior art that selects on the **public** norm shortfall.
  "Best-of-`2^{40}` keys buys 17.6 / 15.2 / 25.2 bits" is a maximum no attacker can locate.
- **M2-2** → not a ceiling on failure boosting. `c_u` is also encapsulator-known
  (`u = A^T r + e_1`, both computable), so real boosting maximises the whole known coefficient
  vector `(r, e_1, c_u)`, not only `D = e_2 + c_v`. Bounding `α(t)` for the `D`-only adversary
  prices a strawman. The variance table is correct.
- **M2-3** → the `H` arm is decorative. With `Q = 1` hints do not compose across keys whatever
  `H(Δβ)` is; the conclusion follows from the rectangle alone, so the hint-planting measurement
  cannot change the verdict in either direction.
- **M2-5** → conformance note. The encoding fibre is collapsed to exactly 1 by the standard's own
  **mandatory** encapsulator check, which the entry states. What remains describes a non-conformant
  party — i.e. OL-2 territory the slice declared off-limits.
- **M2-7** → instrument only. A multi-target loss factor is a **worst-case** quantity; a slope
  measured against a synthetic adversary the analyst plants measures that adversary's interaction
  with one implemented simulator. Both `σ_N = 0` and `σ_N = −1` are consistent with the published
  bound being loose or tight.
- **M2-8** → `control` and forced. The one prediction labelled "the falsifiable one" — explicit
  rejection flips exactly the reject-branch rows — is true by construction, since the reject-branch
  output is the only thing the variant changes.
- **M3-1** → ceiling argument only, with an internal inconsistency to fix. `α = 1/D` with `D ≤ 3`
  makes `1/3` a **floor** for a random-access workload, not the "cap" of the title; `D = 2` (the
  entry's own thermally-limited layout) gives `α = 1/2`, i.e. a *larger* charge. Separately, the
  whole "required α" column is driven by `c_E`, which the repo records as calibrated so the
  crossover reproduces **by construction**; a sensitivity table is supplied for `c_M` and not for
  `c_E`, the one constant that is admittedly fitted.
- **M3-2** → instrument artifact risk. `ρ = mean_hop / N^{1/3}` measures the **analyst's chosen**
  bucket-major embedding into a cubic grid, not the sieve; a different embedding gives a different
  `ρ`. And by the entry's own formula `α_eff = 1/3 + log2 ρ/(c_M β)`, a constant `ρ` gives
  `α_eff → 1/3`: a constant locality factor is a constant-factor saving, never an exponent.
- **M3-3** → exponent arithmetic only; the MAXDEPTH half is a scope leak. `M^{11/6}` vs `M^{4/3}`
  and the `M^{5/6}` break-even are correct and survive. But the depth claim maps the explicitly
  **illustrative** `β ∈ {400, 600, 875}` onto NIST categories 1/3/5 and then concludes "the depth
  convention binds at exactly one of the three". That conclusion is an artifact of arbitrary `β`
  values the slice itself says are not ML-KEM's block sizes.
- **M3-4** → conditional on a reading that must be verified first. The claim that the dual attack's
  FFT accumulator is `q^{k_fft}` should be read off the estimator, not asserted: MATZOV
  modulus-switches before the FFT, and a table of `p^{k_fft}` with `p < q` collapses the 117.01-bit
  headline. Everything downstream depends on it.
- **M3-5** → floor on oracle-only recovery, not on key recovery. `queries ≥ H(s)/C(p)` assumes the
  entire secret is transmitted through the oracle. Real chosen-ciphertext attacks recover a partial
  secret and finish with lattice reduction, transmitting far less than `H(s)`. So "ORS-004's 2950
  queries sit at 1.350× the floor, hence no room for a further factor-2 reduction" does not follow.
  The floor table itself is correct.
- **M3-6** → the NTT half only. The `d_v = 4` row ranks a representation in which the message-bit
  decision is never taken (decapsulation decodes the 12-bit `w = v − s^T u`), and "compression
  amplifies identifiability" is largely forced by word length — the Hamming weight of a 4-bit word
  nearly *is* the word. The layer-1 NTT aggregation is legitimate (the coefficient pairs are
  disjoint, so summing per-butterfly mutual informations is valid) and is the salvageable part.
- **M3-7** → the countermeasure conclusion does not follow. `A \ B = ∅` does not imply "no useful
  fault site": the select/`cmov` instruction lies in `A ∩ B` and remains faultable, as does any
  instruction the attacker can reach that forces the accept branch without disturbing the KDF input
  through a path the taint engine models as shared.
- **M3-9** → the `G4` transposition probe only. The stated theorem — "by pigeonhole every `m`-bit
  surrogate over `8L` input bits with `m < 8L` has `d_φ ≤ 2`" — is false (pigeonhole yields a
  nonzero kernel element, not one of byte-weight 2) and is contradicted by the entry's own CRC-32
  row (`d_φ ≤ 4`). The value-preserving transposition generator and its `1.0039` expected probe
  count survive.

**AES (A1/A2/A3).**

- **A1-1** → the class-collapse derivation only. Prediction (ii) quantifies over `β ∈ 255^4 ≈ 4.2e9`
  weight-4 outputs; the charged test enumerates `4·255` "one-active outputs" plus the 127 listed
  `β*`, so it never searches the space the prediction is about. And "β over one-active outputs" is
  incoherent: a one-active super-box input forces a weight-4 output.
- **A1-2** → confounded. The two arms are matched on "activity pattern and Hamming weight" only;
  changing the middle difference also changes the DDT probabilities of the upper and lower trails,
  so the measured on/off ratio confounds switch multiplicity with trail probability. The
  random-S-box arm does not repair this — a random S-box has its own BCT.
- **A1-3** → per-key computation only. The linear hull of a **keyed** super-box carries a
  key-dependent sign `(−1)^{⟨γ,k⟩}` on each intermediate mask. The entry computes "the exact
  255-term hull" with no key anywhere, so `F(α,β)` is not the key-free quantity the frozen histogram
  claims, and the `r = 2,3,4` measurement arms will not produce it.
- **A1-5** → certificate, not experiment; and the quantifier is overstated. The prediction reads
  "`d(V,a) = 4` for every one-dimensional `V` and **every offset**", while the sweep covers 8
  offsets of `2^{32}` and 8 subkeys of `2^{32}`. The verdict is also forced a priori: 255 difference
  vectors failing to span a 4-dimensional `GF(2^8)` space has probability on the order of
  `256^{-252}`, so 3 core-hours confirm a foregone conclusion.
- **A1-6** → `r ≤ 3` only. At `r = 4, 5` a weight-5 branch-equality event at the MixColumns interface
  requires a 1- or 2-active column difference entering it, which after three or more rounds occurs
  at roughly `2^{-90}`; with `2^{30}` pairs those arms are empty, so the deliverable ("the deviation
  grows monotonically with `r`") is unmeasurable beyond `r = 3`.
- **A1-10** → operator construction only; its ceiling limb is a non-sequitur. Prediction (iii) —
  "no statistic that is a function of the activity pattern alone can separate AES from a random
  permutation beyond `r*+1`, because by construction it sees only `π_r`" — confuses what the
  **value-averaged operator** predicts with what a pattern-only statistic can **detect**;
  prediction (iv) (the measured pattern law deviates from `π_r`) directly contradicts it. The same
  non-sequitur is written into CEILING-A1's second limb, so it propagates to every TO-PATTERN entry.
- **A2-1** → `control`, not `medium`. `dim Ann = 960` is a **theorem**, not a prediction: `(K, σ) ↦ RK`
  is injective, so `rank = 448` exactly. And prediction (iii) — "a chosen-key strategy respecting
  only the linear relations over-counts its freedom by exactly 320 bits" — is a strawman; the
  schedule is a bijection from 128 bits and no analysis assumes 448.
- **A2-3** → effect size undeclared. The direction and the 5-sd threshold at `2^{24}` keys are
  asserted with no computed effect size, and the risk band concedes the likely outcome is
  "invisible". The marginal-invariance derivation also requires the SubWord input to be uniform
  given `δ_i`, which is asserted rather than shown.
- **A2-6** → not a MILP substitute. A pure byte-**activity** automaton with nondeterministic XOR
  cancellation is the truncated relaxation known to be far too weak for AES key schedules;
  `A_min` will be a small, uninformative integer. The out-of-envelope declaration for the joint
  `2^{32}` automaton (64 GB, with the byte count printed) is the honest and valuable part.
- **A2-7** → `θ*` for the yoyo and influence-bias instruments only. The declared "main content",
  prediction (ii) that the integral instruments are blind to `θ`, is a **theorem** — the integral
  balance holds for every key and every schedule — so six `2^{32}` sweeps (`2^{34.6}` encryptions)
  confirm something derivable.
- **A2-8** → algebraic note. Exact and independently verified here, but self-declared CLOSED, and
  the relation `K' = KS_s(K)` is not instantiable by any adversary. It is not a slide result.
- **A2-10** → bound validity unestablished. The lower bound imports the wide-trail
  "≥ 25 active S-boxes per 4 rounds" credit, which is a **single-key** theorem; in the
  related-key/open-key model the entry itself works in, that credit does not hold. "Every relaxation
  enlarges the feasible set" is therefore not established, and the bound may be invalid in the
  unsafe direction — exactly what F10-d is for, but the entry proceeds as if the direction were
  settled.
- **A3-2** → keep, with a sign error to fix. The text states "sampling gives a lower bound on the
  realizable set, so `φ_measured ≥ φ_true`". Sampling can only miss realizations, so
  `φ_measured ≤ φ_true` and the reported gap is an upper bound; the two clauses contradict.
- **A3-5** → forced arithmetic. Both predictions are computable in advance from the committed
  receipts alone: `Λ` for a deterministic 16/16 integral is essentially the null exponent (order
  100+ bits inside 53 s), while a 59-vs-4.0 Poisson excess concentrates a few tens of bits into a
  much longer run. "The rankings differ" and "by at least `2^5`" follow from that, so the 10-minute
  re-timing is not the discriminator.
- **A3-6** → an overdispersion number, not an ROC. The titular object needs the matched
  random-permutation arm, which the entry itself declares **OUT OF ENVELOPE** (8.590 GB at `2^{26}`,
  against a required `2^{30}`). What remains is `Var/Mean` on the AES arm alone.
- **A3-9** → the `g3` figure only. The "structural zero" (`g1` has no power over readout faults) is
  true by definition: known-answer vectors test the cipher, and a readout fault leaves the cipher
  correct. Only `E[readout][g3] ≥ 80%` is a measurement.

**SSI / SSQI (S1/S2/S3/Q1/Q2/Q3).**

- **S1-1** → parameters not jointly identifiable. Fitting `N_sep = c·p^α(log p)^β` over **three**
  toy primes with `⌊p/12⌋ ∈ {10², 10³, 10⁴}` means `log p` varies by a factor ≈ 1.7; `α` and `β`
  cannot be separated, so the clause "`β` consistent with 2/3 and in any case `β < 2`" is not
  decidable by the proposed measurement. Same defect recurs in S1-3 and Q1-1.
- **S1-3** → the forced-symmetry half only. `End(E^{(p)}) ≅ End(E)^{op}` has the same optimal
  embeddings, so 1-WL can never separate a Galois pair — a real, cheap ceiling. The `α = 2/3 ± 0.05`
  rigidity exponent is the same unidentifiable three-point fit, and the "free side" rests on
  Gross–Zagier / Gross–Keating recollections the entry flags as unverified.
- **S1-6** → a note, not an experiment. The distance-concentration argument alone closes the
  ALT/landmark family: in an `(ℓ+1)`-regular Ramanujan graph the radius-`r` sphere is `≈ ℓ^r`, so
  `d(E,L) = log_ℓ n ± O(1)` for a `1 − O(1/ℓ)` fraction and the ALT lower bound is identically 0.
  The `ρ` measurement confirms a derivation, on a family nobody proposed.
- **S1-7** → the null is mis-specified. Eichler's mass formula fixes `Σ_E m_D(E)/w_E` **exactly**
  (the entry's own gate (a)), so the field carries a hard sum constraint and is multinomial-like
  with negative correlation, not Poisson. The fitted excess-variance exponent `b` is measured
  against a null the entry proves wrong. The synthetic-Poisson arm calibrates the pipeline, not the
  null.
- **S1-9** → the derivation only. The decomposition (coset identification + word problem; step 2
  linear; `length = log_ℓ Nrd` exactly, hence no metric distortion) is sound and is the value. The
  measurement is not: the toy implementation realises coset identification as a `Θ(p)` precomputed
  vertex table, after which lookup is `O(1)` and word reduction is `O(log n)` — so the measured
  split will show step (2) **dominating**, the opposite of the `< 1%` prediction, for reasons that
  have nothing to do with the mathematics. The entry's own self-indicting note says as much.
- **S2-3** → the table contradicts the entry's own formula. `k_i = log2(Q·n_primes/ε)/log2 ℓ_i`, but
  the quoted budgets (25.2 / 17.2 / 14.2 / 4.3 at `ε = 2^{-40}`) use `log2(1/ε) = 40` alone. At
  `Q = 2^{40}` and 74 primes the correct `k(ℓ=3)` is 54.4, not 25.2 — and the dropped factor is
  exactly the `Q`-dependence on which the headline ("the surcharge grows as the attack gets
  bigger") rests.
- **S2-5** → prediction is against the pinned text's own structure. The collimation sieve is a
  **list** algorithm and the source's `L̃_max = 8L` cap is a cap on live phase vectors, which are
  the quantum states; predicting peak liveness `Θ(d)` rather than `Θ(L̃)`, and concluding "the sieve
  is depth-bound, not width-bound", is predicting against that. Compounding: the repo holds
  committed locators for five claims on three of twenty-five pages, from which a dependency DAG
  cannot be reconstructed — the entry's own F-c ("under-determined") is the likely outcome.
- **S2-7** → contradicts S2-1 in the same slice. It assumes the shift can be split as "resolve `k`
  bits by search, run the sieve on a residual instance of size `2^{n−k}`", i.e. that the group
  splits along a digit chain. S2-1 argues precisely that `#Cl = 3h(−p)` is odd with large prime
  factors, so no such chain exists. The two entries cannot both be right about the same group.
- **S3-2** → measures the analyst's toy signer. The `n_bt` law obtained is a property of "Arm A
  (translation-shaped)", which is the analyst's own guess at the construction; a two-sample test
  across two toy keys measures that construction. The derived geometric nulls (`2^{-k}` or `3^{-k}`)
  and the planted-`δ` gate are good.
- **S3-3** → blocked. The deliverable is a set difference on a document the environment cannot read
  (CEILING-S3(iii): the SQIsign PDF is not in the tree). The predicted `W \ S = {n_bt, r_rsp,
  hint_aux, hint_chl}` is a guess about unread text. The two Schnorr poles are a good rubric gate
  and can be run now.
- **S3-4** → charged into irrelevance by its own F4b. Detecting a bias `ε` needs `Θ(ε^{-2})`
  **independently generated public keys**; no deployment publishes `2^{20}` of them, so the honest
  resolution is `ε ≳ 2^{-5}` at any realistic key count. The exactly enumerated toy reference law is
  the salvageable product.
- **S3-6** → over-claimed detection. "One supersingularity test at the end of a chain detects a
  fault anywhere in it" is false as stated: it detects only **locus-exiting** faults, and the fault
  model is adversarial — faulting an index, a loop counter, a scalar, or a kernel point leaves the
  state supersingular and passes the test. The entry's own F6a (the projective `(A : C)`
  representation) is correctly made mandatory and is the likelier killer.
- **S3-8** → statement about the model. The "discharged obligation" is discharged against a toy
  signer the analyst writes, so it is about the model, not about Algorithm 2.1. The resolution is
  honestly pre-stated (`N ≈ 10^4` resolves `ε ≈ 2^{-4}` at `k = 2` and no better).
- **S3-9** → conditional, not exact. The arithmetic is right (`2^{f−1}` units × `2^{-e_chl}` =
  `2^{e_rsp−1}` consistent pairs, exactly the count of odd `d < 2^{e_rsp}`). But "the pairing
  relation constrains `d` by exactly zero bits" holds only if `det(M_sk)` is uniform on
  `(Z/2^f)^×`. `H-SQISIGN-c0488f`'s undischarged obligation — quoted verbatim inside the
  neighbouring S3-8 — is that the normalisation constrains the basis **modulo 2**. So the headline
  is conditional on exactly the obligation the sibling entry exists to test, and S3-9 declares a
  dependency on S3-10 but not on S3-8.
- **Q1-1** → same unidentifiable fit. `ln B_opt/√(L ln L)` moving 0.3420 → 0.3178 toward a predicted
  `1/√12 = 0.2887` is a 10% gap still drifting; the two-parameter `(a, b)` fit over a ladder where
  `ln ln p` varies by well under a factor 2 cannot separate them. The entry's own gate (b) misses
  the committed `log2 B_opt = 14.2` by 0.76 octaves and says so — that gap should be resolved before
  the asymptotic law is quoted.
- **Q1-5** → self-declared toy. `N ∈ [203, 611]` vertices and "toy B is not B" — the entry states
  that the transfer to cryptographic `p` is by argument, not by the experiment. The measured
  correlation length cannot decide the composition identity it is aimed at.
- **Q2-1** → one term omitted. The headline is a large memory saving at "time unchanged at
  `M/P0`". Narrowing the stored side to degrees `≤ τ` requires the **complementary** side to be
  streamed, and at an asymmetric split the streamed side's cardinality exceeds the balanced `M`.
  That term is not in the prediction. Until it is charged, the "time unchanged" column is not
  established, and the entry survives only as the memory-side observation.
- **Q3-6** → retrodiction plus one out-of-sample bet. The mechanism is stated as "the Siegel
  exponent 3/2 and the Lipschitz constant `ℓ²` make the improving-neighbour probability exactly
  `1/9` at `ℓ = 2`", which reproduces the already-measured trapped fraction (`(8/9)^3 = 0.702`).
  But the same constant does not generate the `ℓ = 3` and `ℓ = 5` predictions (0.865 and 0.954 would
  need per-neighbour probabilities of ≈ 1/27 and ≈ 1/128, which the stated derivation does not
  produce). One measured number retrodicted by a constant that fits it is not a derivation; the
  `ℓ = 3` figure is a genuine out-of-sample prediction and is the only falsifiable part.

---

## 3. STRONGEST — entries I could not break

1. **M1-8** (`Compress` partitions coordinates into noise classes). Census re-verified exactly
   (`d_u = 11`: 767 singletons + 1281 doubles = 2048 bins, 3329 residues; `d_u = 10`: 767 fibres of
   3 and 257 of 4). The label is public, computed from what an honest sender transmits, with no
   oracle and no chosen ciphertext; the arithmetic is on actual FIPS 203 parameters; the `v`-side
   rows are a graded internal control; and the expected verdict is stated as CLOSED in advance.
2. **M3-8** (decapsulation-key field-integrity signature). The forced 4-row table re-derived
   independently and correct: flipping `H(ek)` corrupts `r`, so `c' ≠ c`, so decapsulation rejects
   and the output changes on a valid ciphertext only → `(1,0)`; `z` is the unique `(0,1)` region and
   its cardinality is exactly 32 at every parameter set; `dk` is `768k + 96` bytes = 2400 at k=3.
   The positive control (a `z`-constant build) is invisible to the incumbent ciphertext generator
   **by construction**, which is exactly what `KN-TECH-054` demands and what searches usually fail
   to supply.
3. **M3-10** (`SampleNTT` XOF block-budget class). Exact binomial arithmetic re-verified: 168 bytes
   → 56 groups → 112 candidates per block; `p = 3329/4096 = 0.812744`; `P(short | 3 blocks) =
   0.0083277`; `1 − 0.99167^9 = 0.0725`; `n = 62` key generations for 99% power at k = 3. Two
   degenerate gates with analytically known outputs bracket the instrument from both sides
   (acceptance bound 4096 ⇒ detection rate exactly 0; bound 2048 ⇒ exactly 1). Distinct from the
   comparison class the goal already owns.
4. **A1-7** (across-key overdispersion `φ = Var_K(N)/E_K(N)`). A second moment **across keys** is a
   functional no statistic in the repo tracks, and it is identically 1 for any first-moment effect
   however large — the orthogonality claim is exact. The signature is `φ − 1` growing **linearly in
   `M`**, which no constant artifact or key-schedule offset can produce. The `r = 3` saturation gate
   forces `φ = 0.000` and the `r = 4` degenerate `0/0` case emits a flag rather than a number, which
   traps the exact failure that produced the withdrawn influence-density closure.
5. **A1-9** (slope-collision fibre histogram). Every number re-verified here. An honest negative —
   "the MixColumns coefficients are unexceptional" — with an exact receipt, a hard `Inv`-conic gate
   (`max fibre = 2` for every nonzero slope), and a two-arm design whose arms differ at the extremes
   of the measured histogram rather than by hand-waving.
6. **A2-2** (permanent-zero incidence set of the key schedule). Predicts the **set** from
   `S`-box-free `GF(2)` algebra, with the `Z_pred ⊆ Z_true` direction argued rather than assumed,
   plus two substitution arms (random bijective S-box; `Rcon ≡ 0`) that decide whether the measured
   0.78125 support density is about AES or about wiring. The `r = 0` identity gate is exact in every
   arm. This is the correct repair of a record that retracted its own symbolic derivation.
7. **A2-5** (GCM's counter sits on a column). ShiftRows index arithmetic re-derived independently:
   bytes `{12,13,14,15}` map to `{12,9,6,3}` — one per column — against the diagonal
   `{0,5,10,15} → ` column 0, so the one-round diffusion deficit follows. The message-limit charge
   is exact and is stated as part of the result: within counters `1 … 2^{32}−2` the largest aligned
   coset is `2^{30}` (`[2^{30}, 2^{31}−1]`), and the tag-mask block `E_K(J_0)` restores `2^{31}` and
   no more.
8. **A2-9** (GHASH weight-constancy on level sets). The condition is at the right granularity — a
   weighted aggregate vanishes for every value distribution iff the weights are constant on each
   level set of the byte-value map — and `H = 1` gives an exact known-answer gate (the weighted
   digest must equal the unweighted aggregate bit for bit). The 2-valued-weight sibling isolates the
   named mechanism rather than "`H ≠ 1`", and the carry-less-multiplication cost is charged at
   2–5× the AES path instead of being absorbed.
9. **A3-1** (`κ(W) = ρ_time/ρ_ops` sweep). Tests an assumption every cost quote in the repository
   silently makes, with both branches informative. The two degenerate gates are the right ones: an
   L1-resident footprint must give `κ ∈ [0.9, 1.1]`, and `X = Y` (same binary, different argv label)
   must give `κ = 1.00 ± 0.03`, which separates a memory-hierarchy effect from thermal/scheduler
   artifacts. Single-core is charged as a **restriction**, not a saving.
10. **A3-3** (the domination curve `D(h)`). Turns a single committed anecdote into a monotone
    measured curve with a mechanism for its shape, an exact `h = 16` gate (residual of one
    candidate), a falsified-hint control that must return an empty survivor set, and an explicit
    `OUT OF ENVELOPE / DEFERRED_UNBOUNDED` region below `h = 11` instead of an extrapolated
    crossing. It also flags that the committed "~25 s" and its own 57 s brute-force estimate
    disagree, and re-measures both in one binary rather than comparing across records.
11. **S1-8** (planted-orientation instances). The positive control the whole S1 slice is missing,
    built on a constructor that already exists and already verifies supersingularity **independently
    of the construction that produced it**. Gate (c) is a genuine discriminator: at
    `|D| ≥ p^{2/3}·C` the planting must become statistically invisible, which catches a filter that
    "fires" on everything and would otherwise be scored as sensitive. Honest that the ladder is
    sparse at the top because `h(D) ≈ p^{1/3}` class polynomials are infeasible.
12. **S3-1** (verification accept-fibre `|A(pk,m)|`). The known-answer gate is external and exact —
    ECDSA with low-`s` enforced must return `|A| = 1`, without must return `|A| = 2` — so a broken
    counter cannot pass silently. The entry kills its own would-be headline in two lines (the
    `M_chl` malleability orbit collapses to `U = I` because the aux basis is reconstructed
    independently by the verifier), and the surviving claim is priced exactly: strong unforgeability
    costs precisely the hint's speed benefit, one `TorsionBasisToHint` call per hint.
13. **S3-7** (the second published curve, with the theorem-dead arm as negative control). The paired
    design is the right one: one arm is dead **by a proof** (`I·conj(I) = n(I)·O` makes response-
    codomain pair statistics secret-independent), so it is an exact negative control measured by the
    same code on the same batch as the open `E_aux` arm. The null is exactly Poisson because the
    coincidence partition is relabelling-invariant; `C(200,2)/2730 = 7.29` re-checked. It also names
    an algebraic kill-early that would replace a 3-CPU-hour experiment with a one-page proof.
14. **Q2-8** (the coverage ratio `ρ = 12M/p` and the `ρ`-stability test). Asks whether the toy
    instruments everyone else in the slice depends on are even in the regime the attack occupies,
    and delivers a **classification of statistics into `ρ`-stable and `ρ`-unstable with a
    measurement behind each row** rather than an opinion. This is the entry most likely to
    invalidate its own siblings, which is why it should run first.
15. **Q3-7** (the `p^{1/4}` certificate and the 3/8 coincidence). Four independently checkable
    necessary conditions, and the observation that "enlarge the closable family" and "exploit the
    tail of curves that already have small `δ_E`" are the same ball-density computation priced
    twice — `p^{1/4}·p^{1/8} = p^{3/8}`, which is also `E(1/4, 0, 1/4)` in the committed screen
    identity. Three routes converging on one number, with the audit's two outcomes pointing in
    opposite directions and no compute required.

---

## 4. SYSTEMIC DEFECTS

1. **The lossy-projection test is passed on paper while the instrument, not the target, is what gets
   measured.** M3-2's `ρ` is a property of the analyst's chosen cubic-grid embedding; A1-3's "exact
   hull" omits the round key that makes the hull key-dependent; S1-9's cost split is decided by a
   `Θ(p)` precomputed vertex table the real attacker cannot pay for; S3-2/S3-8 measure a toy signer
   the analyst wrote. The catalogue asks "is the map invertible?" and never asks "is the map a
   property of the cipher or of my harness?".
2. **Headline predictions that are theorems or tautologies, presented as falsifiable.** A2-4's
   affine-combiner identity; M2-9's combiner bit-vector; A2-7's prediction (ii) (integral balance is
   key-independent); M2-8's prediction (iii) (explicit rejection flips the reject-branch rows);
   A3-9's structural zero (known-answer vectors cannot see readout faults); A3-10's both curves;
   A1-5's expected CLOSED at a prior of ~`2^{-2000}`; A2-1's `dim Ann = 960`. In each case the
   falsifier can only fire on instrument failure.
3. **Three-point log-log fits with two free parameters.** S1-1 (`N_sep = c·p^α(log p)^β`), S1-3
   (rigidity exponent), Q1-1 (`ln B_opt = κ(ln p)^a(ln ln p)^b`) all fit an exponent **and** a log
   power over three or four toy sizes where `log p` varies by well under a factor 2. The two
   parameters are not jointly identifiable; the reported "±7%" and "±0.05" bands are not evidence
   about the asymptotic law.
4. **Data complexity is not checked against the event rate.** A3-7 proposes `2^{32}`–`2^{34}` samples
   for an event of probability ≈ `2^{-126}`; A1-2 proposes `2^{30}` quartets against a return event
   its own prior art records at 96 bits; A1-6's `r = 4,5` arms need a weight-5 interface event that
   occurs at ≈ `2^{-90}` once the state has saturated. Each entry states a "resolution in bits"
   somewhere and then never compares it to the predicted rate.
5. **Unit slippage between entropy, log-variance, and cost.** M1-4 compares a discrete entropy to a
   differential entropy and then feeds the difference into a constant defined on log-variance;
   M2-1's linearised `sd(log₂ δ)` treats a Gaussian-tail sensitivity coefficient as exact under a
   tail the slice's own CEIL-5 says is thinner; S2-3's published budget table drops the `Q·n_primes`
   factor its own formula carries. Every one of these is a factor-of-two-to-four error in a headline
   bit count.
6. **Ceilings asserted over families strictly larger than the invariant can bound.** S2-10's entropy
   deficit does not bound levers that use the key box's additive structure; M3-5's `H(s)/C(p)` floor
   does not bound attacks that recover a partial secret and finish with lattice reduction;
   CEILING-A1's TO-PATTERN limb conflates what the value-averaged operator predicts with what a
   pattern-only statistic can detect. A ceiling that names the wrong invariant is worse than no
   ceiling, because it retires proposals it does not actually cover.
7. **Cross-entry contradictions inside a single slice, undetected because entries were written
   independently.** S2-1 argues `#Cl` has no usable digit chain while S2-7 assumes the shift splits
   into `k` searched bits plus a residual instance; S3-9's "exactly zero bits" depends on
   `det(M_sk)` being uniform mod `2^f`, which is precisely the obligation S3-8 in the same file
   exists to test. Slice-level consistency was never checked.
8. **Adversary models with no adversary.** M2-6's grinder is the key generator, which already holds
   the secret; M2-1's selector must rank keys by a quantity computable only from the secret key;
   A2-8's relation `K' = KS_s(K)` cannot be requested by anyone. These entries define a *maximum*
   and never ask who is allowed to take it.
9. **Duplicate closures across slices with no cross-reference.** S1-6 and Q2-5 close two different
   families (landmarks/ALT, and LSH proximity sketches) by the *same* Ramanujan distance-
   concentration argument and never cite each other; A1's §0.2 recomputes the MixColumns branch
   number and the S-box DDT/LAT maxima by exhaustive enumeration and A3-4 and A3-7 each separately
   claim to "discharge the twice-named open item" of doing so. Work is being paid for three times.
10. **Charged-cost tables that do not cover the test actually proposed.** A1-1 charges `1.5e8`
    multiplications for a prediction quantified over `255^4 ≈ 4.2e9` outputs; Q2-1 charges memory
    for the stored side and asserts "time unchanged" without charging the complementary streamed
    side; A1-5's cost is charged for 8 offsets while the prediction quantifies over all `2^{32}`.
    The charging discipline is applied to the machine and not to the quantifier.

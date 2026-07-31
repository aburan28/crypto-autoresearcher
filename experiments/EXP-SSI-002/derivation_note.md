# EXP-SSI-002 derivation note

Coordinator, 2026-07-31. Written **before** any measurement exists, and
committed in the BATCH-002 opening control-plane commit. This note derives the
three things the specification asserts without proof: (1) why Algorithm 1 as
published cannot be run and what the minimal completion is; (2) what quantity
the sweep can and cannot identify; (3) why the fitted slope is reported in the
`sqrt(log2 p)` parameterisation and what that choice does and does not mean.

Nothing here is a result. Nothing here is executed. This session has no shell.

---

## 1. GAP-1: Algorithm 1 never seeds the list

Algorithm 1 of the frozen source (`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`,
SHA-256 `ca34a0f7…a9cf`) reads:

```
1. L <- {}
2. for l <= B do
3.   for i = 1, ..., floor(log_l(X)) do
4.     for psi in L such that l*deg(psi) <= X do
...
7.       L <- L union {eta . psi}
```

Line 1 initialises `L` to the empty set. Line 4 ranges over `psi in L`. The
body at lines 5–7 is the only place any element is ever added to `L`. So the
body executes `|L|` times on its first pass, `|L| = 0`, the body never runs, no
element is added, `L` stays empty forever, and the algorithm returns the empty
list for every input. **This is not a subtle quantifier slip; the loop is
unreachable.** It is recorded as GAP-1 at `ledger/evidence/EV-P13-001.yaml`,
confirmed by `coordination/tasks/TASK-20260724-P13-REV/review_report.yaml`
against Panny's proof-of-concept implementation.

Correctness of Algorithm 2 does not depend on the repair: Lemma 3.4's proof
requires only that `psi in L(E, X, B)` and `chi in L(E, X, B)` are *present in
the table*, where `L(E, X, B)` is Definition 3.1's **set**, which includes the
degree-1 isogeny (`1 in S(X, B)` for any `X >= 1`, since 1 is vacuously
`B`-smooth). So the intended reading of line 1 is almost certainly
`L <- {id_E}`, not `L <- {}`.

**SEED-A** takes exactly that reading and nothing more. It is minimal in the
precise sense that it adds one element, the one Definition 3.1 already contains,
and changes no other line. Every other entry — including the whole first layer
of `l`-neighbours of `E` — is then produced by the algorithm's own loop and is
charged to a timed window.

**Why this cannot be left to the executor.** The measured quantity is a *cost
per entry*. Seeding changes both the numerator (is the first layer's modular
polynomial work inside or outside the timed window?) and the denominator (how
many entries exist). At the small `X` this sweep reaches, the first layer is a
large fraction of the whole table: with `X = B^{1/2}(p/2)^{1/6}` and `B` small,
the table is only a few layers deep, so first-layer effects do not wash out.
An unseeded-vs-seeded difference therefore lands **directly in the constant this
experiment exists to measure**. SEED-B is run at the two extreme primes precisely
to size that effect, and SEED-GATE requires the report to say so if the ratio
leaves `[0.90, 1.10]`.

**What this does not do.** Supplying a seed is an implementation decision of
EXP-SSI-002. It does not repair, close, or discharge GAP-1 in the frozen text,
and no artifact of BATCH-002 may say that it does.

---

## 2. What the sweep can identify, and what it cannot

Lemma 3.3's cost statement is
`Psi(X,B) * X^{1+o(1)} * B^{O(1)}`, with the per-neighbour-batch cost given as
`(B + log p)^{O(1)}` — an unresolved exponent that the frozen source explicitly
declines to pin down ("We do not presently investigate the best possible
exponent O(1) … It is of course critical for a practical deployment").

Section 4.1 then replaces that unresolved factor with **one `F_{p^2}`-operation
per entry**, stated as deliberately conservative. **The entire NIST-I question
in `DEC-20260724-016` is the size of the gap between "one operation" and the
truth.** That gap is what this experiment measures.

What a sweep over `p in [2^20, 2^40]` can identify:

- the realised per-entry cost, in seconds and in host-normalised
  `F_{p^2}`-operations, **at those primes, at those `B`, in this
  implementation**;
- the *slope* of that cost against a chosen function of `log p`, with an
  interval.

What it cannot identify:

- **the true functional form.** Over `log2 p in [20, 40]`, `sqrt(log2 p)` runs
  over roughly `[4.47, 6.32]` and `log2(log2 p)` over roughly `[4.32, 5.32]`.
  These two regressors are close to affinely related on this interval, so eight
  noisy points will not separate M-A from M-B. This is pre-registered as the
  *expected* outcome (`fitting_protocol.collinearity_is_pre_registered_as_an_expected_limitation`)
  so that failing to separate them is reported, not silently resolved by
  picking the prettier `R^2`.
- **the behaviour at the operating `B`.** The `B^{O(1)}` factor is real, and this
  sweep never leaves `B <= 32`. EA-3 states this as the single largest
  limitation.
- **anything about the NIST-I margin as a measurement.** Everything past
  `log2 p = 40` is extrapolation and is labelled as such.

The `FIT-ELL` requirement exists for a specific failure mode: because
`X = B^{1/2}(p/2)^{1/6}` grows with `p`, the *mixture* of `l` values
contributing entries changes across the sweep, and under B-ASY the bound `B`
itself changes with `p`. A pooled slope can therefore be produced entirely by a
drifting `l`-mixture with no per-`l` `p`-dependence at all. Fitting `l = 2`
alone and `l = 3` alone holds `l` fixed and separates the two. If the pooled and
fixed-`l` slopes disagree beyond their intervals, the pooled slope is an artifact
of the mixture, and the report must say that in those words.

---

## 3. Why `sqrt(log2 p)`, and what the choice does not mean

The committed cost model `experiments/EXP-P13VOW-001/cost_model.py` already
parameterises the hidden overhead as a multiplier `2^{c*sqrt(log2 p)}`, with
scenario values `c in {0, 0.5, 1, 2}` (`specification.yaml`,
`scenario_definitions.overhead_scenarios`). The red team's calibration `c ~ 1.8`
and the whole `2.3`-bit NIST-I margin at `DEC-20260724-016` live in that
parameterisation.

The shape is not arbitrary: Algorithm 3 sets `B = e^{(1/3)sqrt(log(p/2))}`, so
`log B ~ sqrt(log p)/3`, and any cost of the form `B^{theta}` is
`e^{theta sqrt(log p)/3}` — that is, `2^{c sqrt(log2 p)}` up to constants.
`sqrt(log2 p)` is therefore the natural coordinate in which a `B^{O(1)}` overhead
is linear in the exponent.

Fitting in that coordinate makes the output **directly substitutable into the
committed model without re-deriving it**, which is why the extrapolation
protocol forbids hand arithmetic: the fitted `c` and both interval endpoints go
into the unmodified `cost_model.py`, and `c_star` — the `c` at which the model's
own NIST-I margin equals the recorded 3.51-bit irreproducibility band — is
solved numerically by that same model rather than asserted.

**What the choice does not mean.** A slope fitted in a chosen coordinate is a
slope in that coordinate. It is not evidence that the true overhead is
`2^{c sqrt(log2 p)}`. M-B and the null model M-0 are fitted alongside precisely
so that this is visible, and GOF-3 makes "no detectable `p`-dependence in this
regime" an admissible, reportable outcome rather than something to be avoided.

---

## 4. The asymmetry between the two directions

Both directions must be reported; they do not license the same conclusion, and
saying so *before* the measurement is the point.

- A **small** measured `c` is comparatively robust. This is an interpreted-Sage
  proof of concept with no batching; its per-entry cost is an **upper bound** on
  what an optimised implementation pays. A small measured overhead therefore
  sits near a floor, and a floor is the side that matters for a security claim.
- A **large** measured `c` is comparatively weak. It may be measuring this
  implementation's inefficiency. The frozen source's own footnote to Lemma 3.3
  says the fast route is likely *batched* modular polynomial evaluation, which
  this experiment does not implement. So a large `c` does **not** establish that
  SQIsign NIST-I parameters are safe, and `READING-LARGE-C` requires that
  weakness to travel with the number.

Neither direction is preferred by this contract, and neither may be suppressed.

---

## 5. What stays broken

- **GAP-2** is untouched: Corollary 1.2 cites a nonexistent Proposition 8.5 of
  [35]; Proposition 8.4 is the direction actually needed and is GRH-conditional
  as published.
- **Section 4.1** remains UNVERIFIABLE-AS-WRITTEN, with its stated "lower bound"
  recorded as overestimating the provable bound by ~2.2 bits.
- **Heuristic 1** is not under test here and gains nothing from this batch.
- **Model independence** is unavailable under this harness: producer, validator
  and red team all resolve to `claude-opus-5` with `model_verified: false`.
  Independence is session-level and implementation-level at best.

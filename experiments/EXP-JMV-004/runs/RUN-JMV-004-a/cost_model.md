# cost_model.md — RUN-JMV-004-a

specification.yaml's `proof_refs` target (type: `theoretical`, proof_status:
`derivation`, claim_tier: `not_applicable`). This document states the model
exactly as computed in `compute_grid.py` and reported in `crossover.csv`,
`constants_table.csv`, and `raw.json` in this run directory. It draws only on
the held transcription in `source_statements.md` (UNCHECKED-AGAINST-SOURCE;
C1 STATUS: PENDING throughout — see that file's banner) and on
specification.yaml's own frozen method text.

**GRH-CONDITIONALITY (CTRL-GRH)**: every quantitative statement in this
document is conditional on GRH, because Lemma 4.1's bound (as held) is
GRH-conditional (Bach-Sorenson-type explicit constant). Nothing here
confirms or disconfirms GRH.

**CLAIM BOUNDARY**: this document evaluates a stated model at a stated
parameter. It asserts nothing about real attack cost, improves no attack,
and bears on GRH not at all (per specification.yaml `claim_boundary`).

---

## 1. Degree convention (condition E2)

**ONE degree convention is adopted as PRIMARY throughout this run's
`crossover.csv` sign column (`sign_log_kc_half_PRIMARY`) and
`analysis.md`'s reported cells**:

```
k = k_half = Li(m) / 2
```
i.e. the split-prime count is estimated via the offset logarithmic integral
`Li(m) = li(m) - li(2)` (the standard closed-form estimator for `pi(m)`, the
number of primes `<= m`), divided by 2.

**Written reconciliation to the held Sec 4.3 statement**
(`source_statements.md`): the held transcription states
`k = lambda_triv ~ #{split p <= m} ~ pi(m)/2`. This run reads that `/2`
factor as: *a split prime contributes ONE generator to the set S, so the
count of usable split primes `<= m` is approximately half the count of all
primes `<= m`* (the other half being inert or ramified primes, which do not
split and so do not contribute a generator under this reading). `pi(m)` is
estimated by `Li(m)` rather than the held scouting script's numerical
integration of the same closed form — a precision improvement of the
implementation, not a change to the transcribed formula (see
`compute_grid.py` docstring, and `source_statements.md`'s "pi(m) estimator"
row in `constants_table.csv`).

**Written reconciliation to Proposition 3.1**: `k` (however defined) is the
generator-set size fed directly into `k/c`, the ratio inside Prop 3.1's
`log(k/c)` denominator. The degree convention therefore determines the sign
of `log(k/c)` — Prop 3.1's inequality is only informative (gives a finite
`r`) when `k/c > 1`.

**ALTERNATE convention, computed for E2 sensitivity ONLY, never adopted as a
result**: `k_full = Li(m)` (no `/2`; "each split prime contributes 2
generators"). Both are present side by side in every row of
`crossover.csv` (`k_half_split_primes_over_2`, `k_full_split_primes_no_half`)
and every cell of `raw.json` (`k_half`, `k_full`), with a per-cell
`degree_convention_flip` boolean recording whether the sign of
`log(k/c)` differs between the two conventions at that cell.

**Measured flip rate this run**: 37 of 400 cells flip sign between the
`k_half` (PRIMARY) and `k_full` (ALT) degree conventions (`stderr.txt`:
"degree-convention sign flips (half vs full), count: 37"). Per condition
E2-CONVENTION, every one of those 37 cells is reported in `crossover.csv`
with `degree_convention_flip = True` and is CONVENTION-DEPENDENT, never
reported as a directional result in `analysis.md`.

---

## 2. Logarithm convention (both computed side by side)

`m = (log q)^(2+delta)` is ambiguous in "log q" between base-2 (bits) and
natural log — an ambiguity the held transcription itself flags
(`cost_model.py` CRITICAL HONESTY NOTE 2). **Both are computed for every
grid cell**:

- `bits`: `log q := bits` (i.e. `log2(q)`, the field's bit size directly).
- `natural`: `log q := bits * ln(2)` (natural log of `q = 2^bits`).

This choice affects ONLY the `m`-formula's input; the natural logarithm of
`q` used elsewhere in the model (inside `c`'s `log|mD|` term, and inside
`h ~ sqrt(q)`) is ALWAYS the true natural logarithm of `q`, regardless of
which "log q" convention is being swept for `m` — this is a deliberate
implementation choice to keep `c` and `h` well-defined and comparable across
both `m`-conventions, and is disclosed here rather than silently assumed
(see `compute_grid.py`, `compute_cell()`, `ln_q` variable and its inline
comment).

**Measured flip rate this run**: 16 of 200 `(bits, delta, C)` triples flip
the PRIMARY (`k_half`) sign between the `bits` and `natural` log conventions
for `m` (`raw.json`'s `log_convention_flips`; `stderr.txt`: "log-convention
sign flips (bits vs natural), count: 16"). Each is flagged in
`crossover.csv`'s `log_convention_flip_bits_vs_natural` column and is
CONVENTION-DEPENDENT wherever it occurs, never reported as a directional
result.

---

## 3. Precomputation term (condition E4, binding)

**Phi_l is NOT assumed precomputed and free.** Per specification.yaml's own
method item 5 (frozen contract text): "Phi_l has on the order of l^2
coefficients and is not storable" at the `m` the theorem's generator set
forces at cryptographic `q`. This run states the storage term explicitly,
at the ORDER-OF-MAGNITUDE COEFFICIENT-COUNT level (no bit-size-per-coefficient
conversion is held anywhere in this program's corpus, so none is asserted —
see `constants_table.csv`'s "Phi_l storage" row, `NOT_COMPUTABLE_WITHOUT_CITATION`
for a bit-size figure):

- **Per-step storage**, at the typical `l ~ Theta(m)` used at each grid cell:
  `phi_l_storage_coeffs_order = l^2 ~ m^2` coefficients.
- **Full generating-set storage**, if every distinct split-prime `Phi_l` for
  `l <= m` were cached simultaneously (an upper bound on total precomputation,
  since the theorem's generator set draws a uniformly random split prime
  `l <= m` per step, not a fixed one):
  `phi_l_full_set_storage_coeffs_order = k_half * m^2` coefficients (`k_half`
  distinct split primes, each contributing an order-`m^2`-coefficient
  polynomial).

Both figures are reported per cell in `crossover.csv` and `raw.json`. **Two
precomputation-assumption variants are therefore reportable from this run's
data, and the reader/reviewer chooses which to apply**:

1. **Free-precomputation variant** (Phi_l for every needed `l` is assumed
   already available, storage cost not charged against the walk): this is
   the variant `crossover.csv`'s `cost__*` columns report — `total_cost = r
   * per_step_cost` with `per_step_cost` the ROOT-FINDING cost only (e.g.
   `l^3` for the `phi_l` row), NOT including the one-time cost of computing
   or storing `Phi_l` itself.
2. **With-precomputation variant** (the storage/compute figure above is
   charged in addition): NOT separately summed into a single number in this
   run's `cost__*` columns, because doing so would require converting a
   coefficient COUNT into a field-operation or byte figure, which needs a
   per-coefficient bit-size formula this program's corpus does not hold
   (flagged `NOT_COMPUTABLE_WITHOUT_CITATION` in `constants_table.csv`).
   The order-of-magnitude coefficient count itself (`phi_l_storage_coeffs_order`,
   `phi_l_full_set_storage_coeffs_order`) IS reported per cell so a reader
   can see that it is NOT free: at `q = 2^256`, `delta = 1`, `m = 2^24`
   (`16777216`, see `raw.json` cell `bits=256, delta=1.0, convention=bits,
   C=1.0`), the per-step storage order is `m^2 ~ 2^48` coefficients — plainly
   not free, not silently dropped, and not asserted to equal a specific
   field-operation count without a citation for the conversion.

**A cost that silently assumed free precomputation would not be a cost, per
condition E4; this run does not make that assumption silently.**

---

## 4. Cost unit (named explicitly)

The named cost unit throughout `crossover.csv`'s `cost__*` and `rho_sqrt_n`
columns is **one field operation in the base field `F_q`** (or, for the
Pollard-rho comparator, one group operation in the target group of order
`n ~ q`) — the same unit used by the held scouting script
(`cost_model.py`'s `main()`, "field operations", "group operations"). Per-step
costs (`l^3`, `l`, `sqrt(l)` for the three per-step algorithm variants) are
counted in this same unit as an order-of-magnitude figure, per the held
transcription's own framing (`O(l^3)`, `O(l)`, `O(sqrt l)`); no
lower-order constant is asserted for any per-step cost beyond the stated
`O(-)` order.

---

## 5. Constants — see constants_table.csv

Every constant used (`delta`, the log convention, the degree convention,
the `pi(m)` estimator, `C`, the `|D| <= 4q` bound, `h ~ sqrt(q)`, `eps`, the
per-step cost exponents, and the `Phi_l` storage order) is listed with its
source, statement number, and governing hypotheses in
`constants_table.csv` (condition CTRL-CONSTANT-PROVENANCE). No constant is
invented; `C` and `eps` are the two constants without a held numeric
citation and are explicitly SWEPT (`C`) or DECLARED (`eps`), never silently
fixed to 1 or otherwise assumed, with the effect of each choice on the sign
of `log(k/c)` stated in that table (`C`: increases `C` strictly decreases
the ratio and biases toward `negative`; `eps`: no effect on the sign of
`log(k/c)` at all).

---

## 6. Total cost formula (as computed)

```
Total reduction cost (free-precomputation variant)
  = r_half * per_step_cost(l)

  where r_half = ( ln(2) + ln(h) - 0.5*ln(eps*h) ) / ln(k_half / c)   [Prop 3.1, PRIMARY convention]
        h       = sqrt(q)                                              [class number, order of magnitude]
        k_half  = Li(m) / 2                                            [Sec 4.3, PRIMARY convention]
        c       = C * sqrt(m) * ln(4*q*m)                              [Lemma 4.1, |D|=4q as equality]
        m       = (log q)^(2+delta)                                    [Thm 1.1]
        per_step_cost(l) in { l^3 (phi_l, PRIMARY), l (velu), sqrt(l) (sqrt_velu) }
        l in { m (typical), 2 (best-case) }

compared, in the SAME unit (field operations), against
  rho = 2^(bits/2)                                                     [Pollard rho, sqrt(n)]
```

`r_half` is defined (finite, positive) only where `k_half/c > 1`
(`sign_half = positive`); where `sign_half` is `negative` or `zero`,
`r_half` is `null`/undefined in `raw.json` and `crossover.csv`, and no total
cost is computed for that cell (recorded as `NA_ratio_not_positive`) — this
is a structural consequence of Prop 3.1's inequality requiring `k > c` to be
informative, not a computational failure, and is not itself the vacuity
conclusion (that judgement is reserved for the C1-gated review; see
`analysis.md`'s banner).

---

*Every quantitative statement above is GRH-conditional (CTRL-GRH). C1
STATUS: PENDING — see `source_statements.md`.*

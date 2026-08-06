# A2 — ECDLP algebra: solving degree, degree of regularity, Gröbner/Macaulay structure

Catalogue slice A2, generated 2026-08-05. Anchors: `KN-OPEN-002` (prime-field
solving-degree growth), `KN-OPEN-004` (support-aware elimination / Newton
saturation), `KN-OPEN-006` (structured linear algebra, cited only where the
algebra slice touches it).

**This file is a catalogue of research ideas. It is not a ledger record, not a
proposal, not a hypothesis, and it mints no identifier.** Nothing here has any
official status; nothing here is evidence.

---

## 0. Standing constraints that shaped every entry

**S1 — Sage is absent and uninstallable here** (`CORR-20260805-7f3a08`
`infrastructure_outcome`). `src/semaev_tree.py`, `src/h012c_block_m4ri.py` and
`src/ic_first_fall_fast.py` all import `sage.all` at module level and cannot
run. Every idea below is either Sage-free or names its Sage-free fallback
explicitly. A reimplemented *builder* cannot settle builder identity
(that failure mode cost this campaign three batches); a reimplemented *rank or
combinatorics engine operating on a committed system artifact* is a different
thing and does not inherit that objection, because the system is fixed data.

**S2 — one committed system artifact carries this slice.**
`experiments/EXP-SIG-008/work/n1_ms.json` holds the descended boolean N1 null
system at `n=12, seed 2, nb=24`, 24 equations (12 of degree 2, 12 of degree 3),
each a list of integer bitmasks over 24 variables. Degree = popcount, boolean
monomial product = bitwise OR. This reproduces every committed D6 structural
number exactly (`nrows 183,312`, `ncols 174,033`, `deleted 16,018`, against
`N(24,6)=190,051`). **The sem system, the n=9 systems, and the seed-2026 systems
are NOT committed as data.** Any idea needing them is blocked on Sage and says
so.

**S3 — full D6 rank at n=12 is out of reach without m4ri.** The committed
measurement took 1,183 s under Sage's block-m4ri. A pure-Python/NumPy bitset
elimination at `183,312 × 174,033` is off by orders of magnitude. Reachable
exact ranks in this environment top out around `nb ≈ 18, D = 6` and
`nb ≈ 24, D = 5`, chunked. NumPy/SciPy availability is **unverified** in this
session (`src/h012_peel_rank.py` imports NumPy, which is suggestive, not
evidence); each cost line states the pure-Python fallback.

**S4 — boolean ≠ prime-field.** The SIG/DREG/SDEG lineage is boolean chained
Semaev over GF(2). The ECDLP target of `KN-OPEN-002` is prime-field. Ideas
A2-1..A2-7 are boolean and transfer to no prime-field statement. Ideas
A2-8..A2-12 are prime-field and are toy-tier by field size. No idea here moves
an ECDLP exponent, and `Pollard rho remains the baseline` on every entry.

**S5 — novelty is not adjudicable here.** eprint and arXiv are unreachable from
this session. Every entry carries `novelty: unverified`. Nothing is claimed new;
nothing is dismissed as known. Where a technique is plainly established in the
public literature from memory (symmetrization, first-fall degree, transversal
matroids, block Wiedemann) the entry says so as a *caution*, not as a citation.

**S6 — predictions must be fixable before data** (`EV-IC-002` retraction). Every
entry states its discriminating quantity and its band in a form that can be
frozen before any compute. Where a band would be settleable after seeing the
cell, the entry says which degree of freedom must be fixed by fiat first
(`DEC-20260805-cc2b32` B1).

**S7 — a gate that cannot fail is worthless** (`DEC-20260805-cc2b32` B2, on
G2/G5 as model tautologies). Every `Falsifier` below is checked for
reachability, and every entry names a `Null object / control` of the same shape.

---

## 1. Object-first framing (inventor protocol §1)

The corpus reports this target as heavily worked. Per §1 the established
lenses are named and **declared off-limits as the primary lens** for this
catalogue:

| # | Established family (off-limits as primary lens) | Where it stands |
|---|---|---|
| E1 | Semi-regular / Bardet Hilbert series `sr_pred` and its truncation conventions | `P(pass) = 0` proved for the **entire** partial-sum lattice `{0,1,2,25,289,2013,9117,17513,26037}` against required `Q = 24,623` (`DEC-20260805-cc2b32`; RT OBJ-4) |
| E2 | First-fall degree `d_ff` as a `d_reg` proxy | measured non-operative for the boolean sem (`d_ff = 2–3`); untested over prime fields (`KN-OPEN-002`) |
| E3 | Variety saturation `rank = ncols − |V|` | the n=9 shape; explicitly **not** the n=12 shape (`149,410 ≪ 174,031`) |
| E4 | Koszul / field-equation syzygy family `K_D`, `extra_D` | `rankK6_null = 26,792 = nrows − sr_pred` exactly; the residual `7,110` is unexplained |
| E5 | BKK / Newton polytope mixed volume | scoped negative at `m ≤ 5`, generic geometry (`KN-OPEN-004`) |
| E6 | Subresultant / PRS backward-state size | scoped negative, `β_deg = 0.5985` vs generic `3/5` (`EV-SUBRES-001`) |
| E7 | Column-formation up-closure law | exact, zero deviation, at every degree on both arms (`EV-SIG-006`) — used here as a **tool**, not as a lens |

**Candidate tracked objects enumerated for this session**, scored on
(new-or-repackaged / one-step propagation definable / how far it survives):

| Object | Genuinely new here? | Propagation definable? | Survival horizon | Used in |
|---|---|---|---|---|
| O1 transversal matroid of the Macaulay support pattern | not a repackaging of E1–E7 | yes: `supp(f·m)` is a function of `supp(f)` and `m` | to any `(n,D)`; gap to true rank widens with density | A2-1 |
| O2 collision/fibre pattern of `(i,m) ↦ supp(f_i·m)` | new in this lineage | yes: pointwise `∪` + parity | exact at all `(n,D)` | A2-2 |
| O3 pairwise ideal-intersection excess over variable blocks | new in this lineage | yes: block union is a ring homomorphism target | dies when blocks stop being local | A2-3 |
| O4 the definitional column-set convention itself | instrument object | yes, by enumeration | n/a | A2-4 |
| O5 miss-fraction `u_D / C(nb,D)` as a control parameter | reframing of a committed quantity | yes | to any `nb` | A2-5, A2-6 |
| O6 rank as a random variable at fixed support | new in this lineage | yes | n/a | A2-7 |
| O7 support-matched random Semaev (prime field) | boolean analogue exists (N1); prime-field version not in corpus | yes | to any `m`, `p` | A2-8, A2-9 |
| O8 composition/fibre structure of the factor-base polynomial `V(x)` | not in corpus for solving degree | yes | to any `L` | A2-10 |
| O9 isotypic components under the Semaev symmetry group | symmetrization is established; deficit **localization** is not, in this corpus | yes for symmetric multipliers; states its own restriction | to any `m` | A2-11 |
| O10 weight-graded (non-uniform) degree | order-dependence is textbook; the charged comparison is not in this corpus | yes | to any grading | A2-12 |

Per `KN-OPEN-019`, this program has **no** written object enumeration for the
ECDLP. The table above is a **sketch for this slice, not a taxonomy**, and must
not be cited as one.

---

## 2. The twelve ideas

---

### A2-1. Transversal-matroid ceiling: how much of the 7,110 is forced by the support pattern alone, before any GF(2) algebra

**Claim.** For the committed `n=12, seed 2` N1 D6 Macaulay pattern, the
bipartite maximum matching `ν` between the 183,312 rows and the 174,033 columns
satisfies `ν < sr_pred = 156,520`. Because `rank_{GF(2)} ≤ rank_generic =
ν` (transversal matroid / Frobenius–König), any `ν` below `156,520` means the
semi-regular prediction is **unattainable by any matrix with this support
pattern**, i.e. a quantified share `(156,520 − ν)` of the 7,110 deficit is
combinatorial rather than algebraic. Pre-registered three-way partition of
outcomes, fixed before compute: `ν = 149,410` (deficit **entirely**
combinatorial); `149,410 < ν < 156,520` (split, reported as the exact pair);
`ν ≥ 156,520` (deficit **entirely** algebraic, this object refuted).

**Mechanism.** `sr_pred` is support-independent by construction — it counts
monomials in the full degree-`≤D` space and never consults which columns
actually exist. The real matrix lives on 174,033 columns with 16,018 sextics
deleted, and the deleted set is the complement of the up-closure of the equation
supports (`E7`). Deletion concentrates incidences: surviving sextic columns can
be hit by few rows, and a set `S` of columns with `|N(S)| < |S|` caps the rank by
Hall's theorem at `A − (|S| − |N(S)|)`. Matching numbers are **not** partial sums
of the Hilbert series, so this candidate family lies outside the lattice
`DEC-20260805-cc2b32` proved unpassable.

**Lossy-projection test (algebraic, no compute).** Projection: matrix ↦ its
transversal matroid, i.e. `A ↦ ν(A)`. What is discarded: every GF(2) linear
dependence not forced by incidence — all cancellation. This is genuinely lossy
*as a rank functional*: distinct GF(2) matrices with equal `ν` have distinct
ranks (this is exactly the gap being measured), so the map is many-to-one on the
quantity of interest. Objection anticipated and answered: over GF(2) the entries
are 0/1, so the pattern determines the matrix — but the object is not the
pattern, it is the **generic realization** of the pattern, which is a different
matrix over a different field. Compatibility with the target's operation: the
Macaulay row-generation map sends `(f_i, m)` to a row whose support is a
function of `supp(f_i)` and `m` alone (boolean up-set map), so the pattern
propagates deterministically under exactly the operation that builds the matrix.

**Minimal discriminating test.** Rebuild the bipartite incidence graph from
`experiments/EXP-SIG-008/work/n1_ms.json` (rows = `(i, m)` pairs with
`deg(m) ≤ D − d_i`; edges = `{mask | m}` restricted to popcount `≤ D`;
edge count ≈ 183,312 × mean support ≈ 7×10⁶). Run Hopcroft–Karp
(`scipy.sparse.csgraph.maximum_bipartite_matching` if SciPy resolves, else a
hand-rolled HK). **Emit a certificate either way**: a matching of size `≥
156,520` (verifiable in linear time) for the negative branch, or an explicit
Hall violator `S` with `|N(S)| < |S|` for the positive branch. Both certificates
are independently re-checkable without rerunning the search — this is the
program's certificate discipline applied to a combinatorial claim.

**Null object / control.** (i) **Instrument control with a committed answer**:
run the identical code on the D5 slice, where the null's rank is committed at
`sr_pred(12,5) = 29,418` with `extra = 0`. Since `rank ≤ ν`, the code **must**
return `ν ≥ 29,418`; anything less is a code defect and halts the idea, not the
model. (ii) **Configuration-model null**: a random bipartite graph with the
identical row-degree and column-degree sequences. If the real `ν` equals the
configuration-model `ν` within sampling error, the deficiency is a degree-
sequence artifact and carries no Semaev or deletion content — report a
controlled null, not a finding.

**Falsifier (reachable).** `ν ≥ 156,520`, exhibited by a matching. This is the
*likely* outcome for a graph this dense and it kills the object outright. It is
reachable in the first greedy pass, before Hopcroft–Karp augmentation begins.

**Cost.** Impl: low — one file, ~200 LOC, standard library plus optional SciPy.
Compute: low — graph build seconds; HK worst case `O(E√V) ≈ 7×10⁶ × 598 ≈
4×10⁹` steps, so tens of seconds to minutes in C, and **not** feasible in pure
Python at full size (fallback: column-block-restricted matching, which yields
only the `ν ≥` direction and therefore only the negative branch — state this
degradation in the contract, do not discover it mid-run).

**Ceiling.** `toy`. Boolean chained Semaev, `t=3`, `ti=0`, GF(2), one cell, one
seed. Instrument-level: even `ν = 149,410` exactly would explain a measurement
artifact, not make any system easier to solve. No exponent moves. `sota_delta`
zero on every axis. Does not touch `KN-OPEN-002`.

**Kills-it-early.** Greedy matching on the first pass. If greedy alone already
exceeds 156,520, stop and write the negative — under 60 seconds of compute.

---

### A2-2. Weight-≤2 left-kernel census: zero rows, duplicate rows, and boolean self-cancellation as an exact certified lower bound on the rank defect

**Claim.** A pre-registered, exactly computable share of the D6 left-kernel
dimension `33,902 = 183,312 − 149,410` is carried by relations of Hamming weight
`≤ 2` in the rows: rows that vanish identically (`weight 1`) and pairs of
distinct `(i,m)` producing the identical row (`weight 2`). Pre-registered
thresholds, fixed before compute: `Z + Σ_c (|c| − 1) > 0` at all (the object is
alive); `> 7,110` (weight-≤2 relations alone exceed the unexplained residual);
`> 26,792 = nrows − sr_pred` (the semi-regular prediction is refuted by **row
counting alone**, with no rank computation anywhere).

**Mechanism.** In the boolean Macaulay construction the row indexed by `(i,m)`
has support `{s ∪ m : s ∈ supp(f_i)}` reduced **mod 2**, so two distinct
`s₁, s₂ ∈ supp(f_i)` with `s₁ ∪ m = s₂ ∪ m` cancel. Idempotency (`x·x = x`)
means a multiplier can act trivially: if every monomial of `f_i` already
contains the variables of `m`, then `f_i·m = f_i` and the two rows are literally
equal. Neither event is representable in any Hilbert-series convention, which
counts `nrows` as if every generated row were distinct and nonzero. This is a
rank-defect source that is structurally outside the partial-sum lattice —
it does not perturb `Q`, it invalidates the row count that `Q` is measured
against. Note `EV-SIG-006` establishes zero cancellation deviation in the
**column-formation law**; that is a statement about which columns appear, and it
does not bound within-row cancellation or between-row coincidence.

**Lossy-projection test.** Projection: row space ↦ the fibre partition of the
map `(i,m) ↦ supp(f_i·m)` (as a parity-reduced set). Discarded: all linear
structure of weight `≥ 3`, i.e. essentially all of the syzygy module. Retained:
the exact fibres, which propagate deterministically because the map is defined
pointwise by `∪` and parity. This is maximally lossy and still exact in what it
retains — the certificate `nrows − rank ≥ Z + Σ_c(|c| − 1)` is a theorem, not an
estimate.

**Minimal discriminating test.** Load `n1_ms.json`; for each of the 183,312
pairs `(i,m)` compute the canonical reduced row as a `frozenset` of masks with
popcount `≤ D`; hash; tally zero rows and collision-class sizes at `D = 5` and
`D = 6`. Report `Z`, the collision spectrum, and the certified bound. **Second,
non-optional step**: test whether the weight-≤2 relations lie inside the span of
the pre-declared `K_D` family (`|K6| = 27,156`, `rankK6_null = 26,792`). If
`K_D`'s generator definition cannot be recovered from the committed
`experiments/EXP-SIG-008/SIG8_run.sage`, report the census as an **unattributed**
lower bound and say so — do not attribute it to the 7,110 residual by default.

**Null object / control.** The identical census on a synthetic boolean system
with the same degree histogram (`n` quadratics, `n` cubics on `nb = n + 3⌈n/3⌉`
variables) and matched per-equation support sizes, but supports drawn uniformly
at random with no chained structure. If collision rates match, weight-≤2
relations are a **boolean-ring artifact** with no Semaev content, and the finding
is a controlled null.

**Falsifier (reachable).** `Z = 0` and every collision class is a singleton →
weight-≤2 relations contribute exactly nothing and the object is dead in one
run. Symmetrically, `Z + Σ_c(|c|−1) > 33,902` contradicts the committed rank and
routes to a correction record rather than to a finding.

**Cost.** Impl: low — ~120 LOC, standard library only. Compute: low — 183,312
hashed frozensets, single-digit minutes, well under any per-invocation cap. No
dependency beyond CPython.

**Ceiling.** `toy`, boolean, instrument-level. A complete explanation of 7,110
would repair a measurement baseline and move no exponent. `sota_delta` zero.

**Kills-it-early.** Hash the first 10,000 rows. Zero collisions and zero
vanishing rows → stop, write the negative, ~10 seconds.

---

### A2-3. Pairwise ideal-intersection excess over variable blocks: a candidate family outside the partial-sum lattice with a non-tautological D5 control

**Claim.** The equations of the descended boolean system are **variable-local**
(each `f_i` involves `|V_i| ≪ nb` of the 24 variables), and the D6 deficit is
generated by pairs `(i,j)` whose blocks overlap, for which
`dim (I_i ∩ I_j)_{≤D} > dim (f_i f_j · R)_{≤D}`. Pre-registered candidate:

```
deficit_pairwise(D) = Σ_{i<j} [ dim (I_i ∩ I_j)_{≤D} − dim (f_i f_j R)_{≤D} ]
```

with the frozen band `|deficit_pairwise(12,6) − 7,110| / 7,110 ≤ 0.25` **and**
`deficit_pairwise(12,5) ≤ 50` (the D5 null's committed deficit is exactly 0).
Two-sided, and neither side is an identity.

**Mechanism.** The Bardet/semi-regular series `Π_i (1 + z^{d_i})^{-1}` is
precisely the alternating Koszul inclusion–exclusion count, which assumes
`I_i ∩ I_j = (f_i f_j)` — the generic/coprime case. Block locality breaks that:
when `V_i ∩ V_j ≠ ∅`, the two boolean polynomials share variables, boolean
idempotency collapses `f_i f_j` to lower degree than the generic
`d_i + d_j`, and the intersection acquires elements the model does not count.
Extra intersection ⇒ the subspace sum is smaller than the generic count ⇒ rank
below `sr_pred` ⇒ positive deficit. The mechanism is a **structural ingredient
converting a bottleneck into a tractable one** in the target-profile sense: the
global `183,312 × 174,033` rank question is replaced by `C(24,2) = 276`
computations in rings on `|V_i ∪ V_j| ≲ 15` variables. Supporting evidence that
the locality premise is live: `EV-SIG-008` records cubic supports of size
13–105, and 105 monomials of degree `≤3` require only about 9 variables
(`N(9,3) = 130`), consistent with block-local equations on ~9 of 24 variables.

**Lossy-projection test.** Projection: the ideal `I = Σ_i I_i` ↦ the family of
its 1- and 2-generator sub-ideals restricted to their own variable blocks.
Discarded: all triple-and-higher interaction and all cross-block coupling beyond
pairs. Retained: each pair's exact intersection dimension, which propagates
deterministically because restriction to a variable block `F_2[x] →
F_2[V_i ∪ V_j]` is a ring map compatible with multiplication by block-supported
multipliers. Lossy in the required direction: many global ideals share the same
pairwise data (the projection forgets the triple terms of the Bonferroni
expansion), so this is not a change of coordinates.

**Minimal discriminating test.** (a) From `n1_ms.json`, compute `|V_i|` and the
overlap matrix — **one minute, and it is the kill-switch**. (b) For each of 276
pairs, compute `dim (f_i f_j R)_{≤D}` combinatorially and `dim (I_i ∩ I_j)_{≤D}`
by exact GF(2) elimination inside `F_2[V_i ∪ V_j]` (at `|V_i ∪ V_j| ≤ 15` the
whole ring has `N(15,6) = 9,949` monomials — trivial). (c) Sum, and evaluate the
frozen band at `D = 6` and at `D = 5`.

**Null object / control.** (i) **The D5 cell is the control and it can fail**:
the committed null at `n=12, D=5` has `rank = sr_pred = 29,418`, `extra = 0`,
under a support with `u_5 ∈ {8,738, 8,746, 8,761}` (see A2-4). A model that
predicts a large D5 deficit is refuted by a committed number. This is the exact
opposite of the `G5` defect in `DEC-20260805-cc2b32` B2, where `u_D` cancelled
identically. (ii) **Synthetic block-free null**: the same computation on a
system whose supports are drawn with `V_i = all 24 variables`. Prediction: the
pairwise excess collapses to ~0, because generic pairs are coprime. If it does
not, the excess is an artifact of the counting convention rather than of
locality.

**Falsifier (reachable).** Either `|V_i| = 24` for all `i` (mechanism void, dies
in one minute), or the pairwise excess is `< 500` at D6 (two orders below
7,110 — the mechanism exists but is not the mechanism), or it exceeds 50 at D5
(refuted by a committed zero).

**Cost.** Impl: medium — ~350 LOC, needs a small exact GF(2) elimination over
≤10k columns and an intersection routine (`dim(A ∩ B) = dim A + dim B − dim(A+B)`
on row spaces, so three ranks per pair). Compute: low/medium — 276 pairs × three
small ranks; single-digit minutes to ~1 core-hour.

**Ceiling.** `toy`, boolean, model-repair only. Even an exact hit on 7,110
repairs a null baseline; it makes nothing easier to solve, moves no exponent,
and does not narrow `KN-OPEN-002`. If it succeeds, the natural successor is
whether the same pairwise correction is computable for prime-field Semaev — that
successor is a separate idea and is **not** claimed here.

**Kills-it-early.** Step (a): print `|V_i|` for `i = 1..24`. Under a minute.

---

### A2-4. The D5 column-count trichotomy is definitional or it is a defect: exhaustive enumeration of a pre-declared convention space

**Claim.** The three mutually inconsistent committed D5 readings at `n=12` —
`ncols/u_5` of `46,694 / 8,761` (independent reconstruction, `CORR-20260805-7f3a08`),
`46,709 / 8,746`, and `46,717 / 8,738` (BATCH-003 `RT-CTRLB.md` as `{5: 8,736, 4: 2}`),
all partitioning `N(24,5) = 55,455` and differing only in the degree-5 column
count `33,743 / 33,758 / 33,766` — are generated by **different definitions of
the column set applied to the same committed system**, and the responsible
definitions are identifiable by exhausting a finite, pre-declared convention
space. Frozen before compute: at least two of the three readings are reproduced
by named conventions, or the enumeration returns none and **at least one lineage
carries a defect that is not a convention**, which is then named and routed to a
correction.

**Mechanism.** Every D5 number in the SDEG/DREG/SIG lineage — `sr_pred(12,5)`
comparisons, the `1,321`/`1,322` sem D5 deficit, clause-(6) preconditions, the
`u_5 = 8,746` value that `RT OBJ-5` found nowhere in the repository outside
`H-SDEG-0dd021` itself — is measured against one of these three column sets. A
15-to-23-column disagreement is small, but it is a disagreement about a
*definition* in a lineage whose central claim is a 7,110-unit rank anomaly, and
it is currently unlocalized beyond "the degree-5 column count." The convention
space is small and enumerable: (a) columns = union of parity-reduced row
supports vs. union of raw `{mask | m}` supports; (b) constant monomial included
or excluded; (c) multiplier degree `≤ D − d_i` vs. multiplier degree `≤ D` with
post-truncation to popcount `≤ D`; (d) equations with `d_i > D` dropped or kept;
(e) columns from the `K_D` syzygy-family rows included or excluded; (f) the
up-closure of equation supports taken with slack `≤ D − d_i` vs. slack `≤ D`;
(g) degree measured on the equation's max-degree monomial vs. per-monomial. Full
cross product is 2⁷ = 128 evaluations of a routine that already runs in seconds.

**Lossy-projection test.** The tracked object is the *convention*, not the
matrix: the projection sends (system, convention) ↦ `(ncols, per-degree
histogram)`. Discarded: the entire matrix. Retained: exactly the observable the
three lineages disagree on, which is what makes the collision search of
inventor-protocol §8 audit 2 executable here — this **is** an observation-
collision search, run deliberately.

**Minimal discriminating test.** Enumerate all 128 conventions on the committed
`n1_ms.json` at `D = 5`; record `(ncols, u_5, hist)` for each; match against
`{46,694 / 8,761}`, `{46,709 / 8,746}`, `{46,717 / 8,738}`. Repeat at `D = 6`,
where all committed readings agree at `174,033 / 16,018` — **that agreement is
the control**: a convention set that reproduces the D5 spread must also collapse
to a single value at D6, or it is the wrong convention set.

**Null object / control.** The `D = 6` agreement, as above: any candidate
convention that produces a spread at D6 is rejected regardless of its D5
behaviour. Second control: the `nrows` values, which all three lineages agree on
at `31,512` (D5) and `183,312` (D6) — a convention that changes `nrows` is out
of the space by construction.

**Falsifier (reachable).** No convention in the enumerated 128 reproduces
`46,709` or `46,717`. That outcome is a *named defect*, not a null result: it
says at least one committed D5 reading cannot arise from any plausible reading of
the committed system, and it is routed to a correction record with the
enumeration attached as the evidence.

**Cost.** Impl: low — ~180 LOC, standard library. Compute: minutes. This is the
highest value-per-second entry in the catalogue and it is **not** a research
result; it is instrument integrity that three goals currently depend on.

**Ceiling.** `toy`, boolean, instrument-only. Resolves no mechanism, moves no
exponent, changes no hypothesis status. Its value is that every D5 statement
downstream becomes citable or is correctly withdrawn.

**Kills-it-early.** Not applicable in the usual sense — the run is minutes end to
end. The early exit is that the first convention tried (union of raw supports)
already reproduces one reading, which is known.

---

### A2-5. Is 7,110 generic? A self-built restricted-support n-ladder at reachable size, with the miss fraction as the dialed parameter

**Claim.** In self-built boolean systems of the *same shape* as the SIG lineage
(`n` quadratics and `n` cubics on `nb = n + 3⌈n/3⌉` variables, supports truncated
to force a controlled degree-`D` miss fraction `f = u_D / C(nb,D)`), the D6 rank
deficit against `sr_pred` is a **monotone increasing function of `f`, strictly
positive above a threshold `f*`**, and the normalized committed point
`(f, deficit/sr_pred) = (0.119, 0.0454)` at `nb = 24` lies on the extrapolated
curve within a pre-registered ±40% band. Frozen alternative hypotheses, both
reachable: (H-gen) the deficit is generic in `f` and 7,110 is an ordinary point
on a response curve; (H-art) the deficit is 0 for all `f` at every reachable
size, and the n=12 phenomenon is not a miss-fraction effect at all.

**Mechanism.** `DEC-20260805-cc2b32` B5 records the canonical artifact tell for
this shape: `h_6(12) = 7,494` against `h_6(13) = 106,743`, a 14.2× jump, so the
freeze condition `s_6 = h_6 − u_6 ≤ 0` can hold only for `n ∈ {10,11,12}`, and
every partial-sum candidate predicts deficit exactly 0 at `n = 13`. A mechanism
live at exactly one measured size is the canonical artifact signature
(inventor-protocol §3). The n-axis is blocked on Sage for the *true* system, so
this idea replaces it with an axis that is **not** blocked: build the analogous
family directly, at `n ∈ {6,7,8,9}` where exact GF(2) rank is reachable, and
dial `f` continuously by truncating supports rather than by changing `n`.
Reachable sizes, from the same shape law: `n=6 → nb=12, ncols(D6) = N(12,6) =
2,510, nrows = 6,558`; `n=7 → nb=16, 14,893 × 22,498`; `n=8 → nb=17,
21,778 × 32,384`; `n=9 → nb=18, 31,180 × 45,324` (this last equals the committed
n=9 null column count exactly, which is a free cross-check on the shape law).

**Lossy-projection test.** The tracked object is `(f, D, nb) ↦ deficit/sr_pred`
— the response surface, with the identity of the system projected away entirely.
Discarded: which monomials are missing, the curve, the descent, the seed.
Retained: how many are missing, which propagates deterministically to
`ncols = N(nb,D) − u_D` and hence to every quantity in the comparison. Lossy in
the required sense: uncountably many support families share an `f` and the
question is precisely whether they share a deficit.

**Minimal discriminating test.** For each `n ∈ {6,7,8}` (with `n=9` as a stretch
rung, chunked): draw supports with the SIG per-equation size distribution
(quadratics 13–33 monomials, cubics 13–105), truncate to hit target
`f ∈ {0, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25}`, build the D6 Macaulay matrix
Sage-free from bitmasks, compute exact rank by chunked big-integer bitset
elimination with per-chunk checkpoints, and report `deficit = sr_pred − rank`.
Three seeds per `(n, f)` cell.

**Null object / control.** (i) **`f = 0` control**: at zero miss fraction the
deficit must be 0 (the system is full-support generic and `sr_pred` is the
semi-regular value). A nonzero deficit at `f = 0` means the instrument, not the
mechanism, produces deficits — the run halts. (ii) **`n = 9` shape cross-check**:
the synthetic `n=9` column count must come out `31,180`, matching the committed
n=9 null; a mismatch means the shape law was reimplemented wrongly and the
ladder is void. (iii) The committed `n=12, D=5` cell (`deficit 0` at
`u_5 ≈ 8,750`, `f ≈ 0.206`) is a **committed high-`f` zero** that any monotone
response curve must accommodate at D5 — the response surface is `D`-dependent
and must say so before fitting.

**Falsifier (reachable).** Deficit identically 0 across every `(n, f)` cell with
`f` up to 0.25 → H-art; the miss fraction is not the controlling variable and the
whole `u_D`-driven family (of which the partial-sum lattice was one member) is
refuted at reachable size for a reason independent of the collapse convention.
Equally reachable: deficit positive but non-monotone in `f`, which refutes the
response-surface framing without refuting `u_D` relevance.

**Cost.** Impl: medium — ~500 LOC (support builder, bitmask Macaulay builder,
chunked bitset elimination with checkpoint/resume). Compute: medium — projected
`n=6` seconds, `n=7` ≈ 250 s, `n=8` ≈ 500 s, `n=9` ≈ 1,000–2,000 s **per cell**
in pure Python big-int bitsets, times 7 `f`-values times 3 seeds. Budget the
`n ∈ {6,7}` core at ≈2 core-hours and treat `n ∈ {8,9}` as optional rungs with
graceful degradation. **All projections are an unverified `nrows × rank ×
words` model, not a measurement**, and must be re-costed after the first cell.

**Ceiling.** `toy`, boolean. A clean response curve would make 7,110 ordinary and
retire the anomaly; it would not repair `sr_pred` for use in a cost model, would
not transfer to prime fields, and moves no exponent. `sota_delta` zero.

**Kills-it-early.** The `f = 0`, `n = 6` cell: seconds. If it returns a nonzero
deficit, the instrument is wrong and nothing else runs.

---

### A2-6. Sage-free forward prediction of the miss fraction: does the freeze window actually close at n = 13?

**Claim.** The sextic miss fraction `u_6(n)/C(nb,6)` is a deterministic function
of the equation-support hypergraph alone — computable by up-closure enumeration
with **no rank engine and no Sage** — and under a support model calibrated to
reproduce the committed `u_6(12) = 16,018` (11.90% of `C(24,6) = 134,596`) within
±10%, the predicted `u_6(13)/C(28,6)` is **below** the 28.3% that any partial-sum
candidate needs in order to predict a nonzero deficit at `n = 13, D = 6`. Frozen
before compute: predicted `n=13` miss fraction, with an interval, and the
resulting binary prediction (deficit 0 / deficit nonzero).

**Mechanism.** `E7` (the up-closure law, exact with zero deviation at every
degree) says a monomial `m` survives iff some `s ∈ supp(f_i)` satisfies `s ⊆ m`
and `|m| − |s| ≤ D − d_i`. So the deleted set is exactly the set of `D`-subsets
of the `nb` variables that are **independent** in the hypergraph whose edges are
the equation supports with slack. That is a purely combinatorial object: no
curve, no descent, no field. It follows that `u_D` can be predicted for any
`(nb, support statistics)` without ever constructing the true system — which is
precisely what the Sage blockage otherwise prevents. `DEC-20260805-cc2b32` B5
made the `n=13` prediction the decisive decay control and left it unreachable;
this idea makes it reachable **as a prediction with a stated model**, which is
weaker than a measurement and is labelled as such.

**Lossy-projection test.** Projection: the true descended system ↦ its
support hypergraph ↦ the per-equation support-size distribution and overlap
statistics. Discarded: every coefficient, the identity of the monomials, the
elliptic-curve origin. Retained: the independence structure at the sampled
statistics, which propagates deterministically to `u_D` through the up-closure
law — the one law in this lineage verified exact at every degree on both arms.
Genuinely lossy: many hypergraphs share a size distribution and the question is
how tightly that pins `u_D`.

**Minimal discriminating test.** (a) **Calibration, and it can fail**: sample
synthetic support hypergraphs at `nb = 24` with the committed SIG size
distribution and compute `u_6` by up-closure over all 134,596 sextics. If the
sampled distribution of `u_6` does not contain 16,018 within its 10th–90th
percentile, the support model is refuted at the one cell where the truth is
known, and no `n=13` extrapolation is made. (b) If it calibrates, run the
identical procedure at `nb = 28` (`n = 13`) over `C(28,6) = 376,740` sextics and
report the predicted miss-fraction interval. (c) Also report the `D`-axis at
`nb = 24`: `u_4, u_5, u_6, u_7` (the last over `C(24,7) = 346,104`), which needs
no new system at all and tests whether the miss fraction behaves in `D` the way
the freeze mechanism requires.

**Null object / control.** The `nb = 24` calibration cell **is** the control and
it is a committed number the model must hit without tuning. Second control: the
committed `u_5` reading — but note this control is *currently unusable*
because of the three-way D5 disagreement, so this idea is **gated on A2-4** for
its D5 arm and states that dependency rather than quietly averaging.

**Falsifier (reachable).** Calibration failure at `nb = 24` (model refuted before
any extrapolation), or a predicted `n=13` interval that straddles 28.3% (the
prediction is uninformative and must be reported as such rather than rounded to
a side).

**Cost.** Impl: low — ~200 LOC, standard library, `itertools.combinations` plus
bitmask subset tests. Compute: low/medium — 134,596 sextics × subset tests is
seconds; 376,740 septuple-variable 6-subsets at `nb=28` is still seconds to
minutes; the `D = 7` arm at 346,104 monomials is minutes.

**Ceiling.** `toy`, boolean. **This produces a prediction, not a measurement**,
and the distinction is load-bearing: it cannot confirm the decay control, only
sharpen or refute the support model that the decay control's arithmetic rests
on. It moves no exponent and does not unblock any goal.

**Kills-it-early.** The calibration cell at `nb = 24`, minutes.

---

### A2-7. HEUR-BF-1 as a measurement: is the rank deficit even a function of the support, or is it seed noise?

**Claim.** At **fixed column set** — the antecedent `RT OBJ-10` showed the
committed `138,570 / 138,573` pair fails to satisfy (`174,033` vs `174,035`
columns) — the D-rank of a restricted-support boolean system is
**deterministic**: across `K = 20` systems drawn with distinct seeds and verified
to produce byte-identical column sets, the rank spread `σ = 0`. Frozen
alternative: `σ > 0`, with the pre-registered comparison `σ` against the
deficit magnitude at the same cell. If `σ` is within an order of magnitude of the
deficit, **no closed form in `(n, D, histogram, null family)` can exist**, and
that is a named obstruction meeting the inventor-protocol §4 closure standard
for the entire Φ-repair programme.

**Mechanism.** Every closed-form search in this lineage — `H-SDEG-0dd021`,
`IDEA-20260803-202a15`, and any successor working outside the partial-sum lattice
— presupposes HEUR-BF-1. `IDEA-20260803-202a15` itself records that HEUR-BF-1 is
`NOT ESTABLISHED` and that its own `validation_plan` is "measure it first";
`RT OBJ-10` then established that the one datum offered to test it **cannot**,
because the fixed-support antecedent fails by construction. So the premise of
the whole lane is untested, and it is cheap to test at reachable size where the
antecedent can be *enforced* rather than hoped for.

**Lossy-projection test.** The tracked object is the rank **as a random
variable** conditioned on the support: `rank | column-set`. Discarded: the
particular system. Retained: the conditional distribution, which propagates
deterministically in the trivial sense that the conditioning event is checkable
exactly (column-set equality is a set comparison). The projection is lossy
because many systems share a column set; whether they share a rank is exactly
the question, which is what makes this a measurement rather than a definition.

**Minimal discriminating test.** At `nb = 16` (`n = 7`) and `nb = 17` (`n = 8`),
`D = 6`: fix a template support hypergraph; draw systems by resampling each
equation's monomial set within the template; **retain only draws whose D6 column
set is set-equal to the template's** (rejection sampling, and report the
acceptance rate, which is itself informative); compute exact rank for the first
20 accepted draws; report `min`, `max`, `σ`, and the full spectrum. Repeat at a
support truncated to `f ≈ 0.12` to match the committed n=12 miss fraction.

**Null object / control.** (i) **Full-support control at `f = 0`**: there the
semi-regular model is the accepted baseline and the rank should be `sr_pred`
deterministically. Nonzero `σ` at `f = 0` means the generic baseline is itself
stochastic, which would be a finding about `sr_pred` and not about the deficit,
and must be reported that way. (ii) **Permutation control**: relabel the
variables of one accepted system by a random permutation that preserves the
column set (if any exists); the rank must be invariant, or the rank routine is
order-dependent and broken.

**Falsifier (reachable).** `σ = 0` across all 20 draws at both cells → HEUR-BF-1
survives at reachable size, the closed-form lane is licensed to continue, and
this idea's own claim (that the premise is untested) is discharged positively.
Also reachable: acceptance rate ≈ 0, meaning the fixed-column-set antecedent is
essentially unsatisfiable by resampling — which is itself a reportable
obstruction (the heuristic quantifies over an almost-empty set).

**Cost.** Impl: medium — reuses A2-5's builder and rank engine plus a rejection
sampler, ~250 additional LOC. Compute: medium — 20 accepted draws × (`n=7` ≈
250 s, `n=8` ≈ 500 s) × 2 support settings ≈ 4–8 core-hours, chunked. Shares
`experiments/` write scope with A2-5 and must therefore be sequenced with it,
not run concurrently.

**Ceiling.** `toy`, boolean. A `σ = 0` result licenses a search; it does not
find a closed form. A `σ` large result **closes a lane properly** — named
obstruction (rank is not support-determined), argument (measured spread at
matched supports), forward guidance (what remains: models conditioning on more
than the support, e.g. A2-3's pairwise data). Neither branch moves an exponent.

**Kills-it-early.** The acceptance rate of the rejection sampler on the first 200
draws. If it is 0, the experiment as designed cannot run and must be redesigned
before any rank is computed.

---

### A2-8. Prime-field: does Semaev's arithmetic buy any solving degree over a support-matched random system?

**Claim.** For prime-field point-decomposition systems (`S_3` chained to `m = 4,
5` over `F_p`, factor base `V(x) = 0` of degree `L`), the solving degree of the
**true** Semaev system equals, exactly, that of a random system with identical
monomial supports and identical degree pattern, at every tested cell. Direction
is stated as equality; the informative alternative is strict inequality
(`d_true < d_random`), which would be the first evidence in this corpus that
Semaev arithmetic contributes to solving degree beyond its support.

**Mechanism.** This is `controls before belief` (inventor-protocol §3) applied to
the central object of `KN-OPEN-002`. It matters because of what each branch
licenses. **If equality holds**, solving-degree scaling becomes a purely
combinatorial question about supports — and Semaev supports are computable at any
`m` and any `p` without solving anything — so solving-degree predictions become
extrapolable to cryptographic parameters at negligible cost. That is a genuine
methodological unlock for the `C_decomp(p,m)` numerator that `GOAL-SDEG-001`
exists to produce, and it is the prime-field analogue of a move already made in
the boolean lineage (the N1 column-matched null of `EV-SIG-006`/`EV-SIG-008`).
**If strict inequality holds**, the difference localizes exactly where the
exploitable structure is, and it is measurable rather than conjectural.

**Lossy-projection test.** Projection: system ↦ (monomial supports, degree
pattern), with all coefficients replaced by fresh uniform elements of `F_p^*`.
Discarded: every coefficient, hence the entire elliptic-curve group law.
Retained: the supports, which propagate deterministically under Macaulay row
generation (`supp(f·m) ⊆ supp(f)·m`, with generic coefficients ensuring no
accidental cancellation w.h.p. over large `p`). Genuinely lossy: `p^{|supp|}`
systems share each support, and whether they share a solving degree is the
measurement.

**Minimal discriminating test.** `p ∈ {1009, 65521}` (10 and 16 bits — `toy` by
`docs/claims-and-verification.md`), `m = 3` then `m = 4` if it fits, `L` small,
`D` up to 6. Define solving degree operationally and freeze the definition
before data: the least `D` at which `dim (F_p[x]/I)_{≤D}` — computed as
`ncols(D) − rank(D)` — equals the number of affine solutions counted by brute
force over the factor base. Compute Macaulay ranks over `F_p` by dense
fraction-free/mod-`p` elimination at sizes ≤ a few thousand. Three seeds per
cell. Report `d_true` and `d_random-support-matched` per cell.

**Null object / control.** (i) **Support-matched random** — the object under
test. (ii) **Dense random of the same total degrees, support-unmatched** — the
second null, which separates "the support explains it" from "nothing explains
it." Expected ordering `d_true ≤ d_support-matched ≤ d_dense`; any inversion
means the instrument is wrong. (iii) **Brute-force solution count** is the
ground truth for the stopping condition and is exactly computable at these `L`,
so the solving-degree definition never depends on the model being tested.

**Falsifier (reachable).** `d_true ≠ d_support-matched` at any single cell kills
the equality claim outright. Symmetrically, `d_true = d_support-matched =
d_dense` at every cell means neither the support nor the arithmetic matters at
reachable `m`, and the instrument has no resolving power at this scale — which
must be reported as an instrument limit, not as a mathematical result.

**Cost.** Impl: medium — ~450 LOC: Semaev `S_3` construction over `F_p` (pure
Python, no Sage — `S_3` has a closed form), chaining, Macaulay builder,
mod-`p` elimination. Compute: medium — ≈3–6 core-hours across cells and seeds at
`m = 3`; `m = 4` is a stretch and must degrade gracefully.

**Ceiling.** `toy`. `p ≤ 16 bits`, `m ≤ 4`. **This is the first prime-field entry
in the catalogue and it still says nothing about cryptographic-size curves.** It
does not close or narrow `KN-OPEN-002`; it decides whether the *method* of
extrapolating solving degree from supports is licensed, which is upstream of any
growth law. No exponent moves. `Pollard rho` remains the ECDLP baseline.

**Kills-it-early.** The smallest cell (`p = 1009`, `m = 3`, `L = 4`) with one
seed: if `d_true ≠ d_support-matched` there, the equality claim is dead in
minutes and the interesting branch opens immediately.

---

### A2-9. Prime-field first-fall/solving-degree gap: is `d_ff` a safe proxy, and in which direction does it err?

**Claim.** For prime-field `S_3`-chained decomposition systems, the gap
`g(m) = d_solve(m) − d_ff(m)` is **bounded by 1** across `m ∈ {3,4,5}` at every
tested `p` and seed. Frozen alternative: `g` increases with `m`, in which case
every `d_ff`-based cost estimate for prime-field point decomposition is an
**underestimate**, by a factor that grows with `m` — a statement about the
direction of an error, which is the only kind of statement three data points can
support (`EV-SUBRES-001` `boundaries`: three points cannot establish a power law,
only gross inconsistency with one).

**Mechanism.** `KN-OPEN-002` states the open question precisely: whether
first-fall degree tracks the true degree of regularity, and how both scale, is
not settled **over prime fields** — the `d_ff` proxy is studied mostly over
binary fields. The boolean lineage measured `d_ff = 2–3` and non-operative for
the chained sem, which says nothing about prime fields (S4). This is therefore
the most direct measurement in the catalogue against its anchor open problem,
and its value is asymmetric: `g` bounded makes the existing proxy usable and
cheap; `g` growing invalidates a class of published estimates *in a named
direction*, which is more useful than a mere "unknown."

**Lossy-projection test.** Projection: the full Gröbner computation ↦ the pair
`(d_ff, d_solve)`, two integers. Discarded: the basis, the staircase, the
coefficients, all timing. Retained: the two degrees, which propagate
deterministically in the sense that both are defined as the least `D` satisfying
an exactly checkable rank condition on the degree-`D` Macaulay matrix. Extremely
lossy and exactly computable — the combination that makes the measurement
trustworthy at small scale even though the systems are not.

**Minimal discriminating test.** Freeze both definitions before data.
`d_ff` = least `D` at which the degree-`D` Macaulay matrix has a **degree fall**,
i.e. `rank(D) < ` the no-fall count predicted from the row count minus the
Koszul-trivial relations. `d_solve` = least `D` at which
`ncols(D) − rank(D)` equals the brute-force solution count. Cells:
`p ∈ {1009, 65521, 16769023}` (10/16/24 bits), `m ∈ {3,4}` with `m = 5` optional,
`≥ 3` seeds. Report `g` per cell, plus the pairwise `g`-increments across `m`.

**Null object / control.** (i) The **support-matched random null of A2-8**, which
gives the generic `g` baseline at the same shapes: the claim of interest is the
*difference* `g_true − g_random`, not `g_true` alone. (ii) A **planted control**:
a system with a known small solution set constructed by choosing the solutions
first — its `d_solve` is bounded in advance, so a routine returning a larger
value is broken. (iii) **Solution counts by exhaustion**, so the stopping
condition never consults the model.

**Falsifier (reachable).** `g` constant **and equal to** the random baseline at
every cell → no prime-field-specific proxy effect at reachable `m`; `KN-OPEN-002`'s
proxy sub-question gets a scoped negative in the "proxy is fine" direction, which
is a real answer at toy scale. Also reachable: `d_solve` not attained within the
`D` budget at `m ≥ 4`, which is an **infrastructure/coverage outcome and never
mathematical evidence** (`AGENTS.md` rule 5) and must be recorded as censored.

**Cost.** Impl: medium — reuses A2-8's builder and elimination; adds a
first-fall detector and a brute-force solution counter, ~250 LOC. Compute:
medium — ≈4–8 core-hours; `m = 5` is likely out of reach and is declared optional
and outside the completion gate up front, not discovered as a shortfall.

**Ceiling.** `toy`. Three field sizes and at most three arities. **Cannot
establish a growth law** and must not be written as one. Does not close
`KN-OPEN-002`; narrows it to a measured direction on a stated scope. No exponent
moves.

**Kills-it-early.** `m = 3`, `p = 1009`: if `d_ff = d_solve` there and at
`m = 4`, `g` is bounded on the reachable range and the growing-gap branch cannot
be examined at this scale — report that limit rather than extrapolating.

---

### A2-10. Designed factor-base polynomial: does compositional structure in `V(x)` lower the solving degree, and does it survive the relation-probability charge?

**Claim.** Choosing the factor-base defining polynomial `V(x)` with a
composition structure (`V = W ∘ W'`, e.g. Dickson/Chebyshev `D_k`, or
`x^k − a`) lowers `d_solve` of the resulting decomposition system by `≥ 1`
relative to a random `V` of the same degree `L`, at `m = 3` and at every tested
`p`, **and** the induced drop in decomposition probability is smaller than the
solving-degree saving under a fully-charged cost model. Both halves are frozen
before data, and either half failing kills the lever.

**Mechanism.** A composition `V = W ∘ W'` makes `F_p[x] ⊃ F_p[W'(x)]` a tower, so
the decomposition ideal acquires a fibered structure: solving splits into an
outer system in the `W'`-coordinates and inner fibres, and the solving degree of a
fibered system is governed by the maximum over the two stages rather than by their
product. This is the target-profile move of hunting a **structural ingredient that
converts a bottleneck step into a tractable one**, and it is the only entry in
this catalogue with a plausible route to an exponent lever, because Gröbner cost
is exponential in the solving degree — so an *additive* reduction in `d_solve` is
a *multiplicative-in-the-exponent* change in the point-decomposition cost that no
current model charges as a free variable. The counterweight, which the design must
charge and not assume away: a structured `V` shrinks the factor base's
pseudo-randomness and lowers the probability that a target decomposes, exactly the
double-ledger that `KN-OPEN-006` insists on for the AP-support construction. And
crucially, `KN-OPEN-004`'s Newton-saturation negative was measured for **generic**
geometry at `m ≤ 5`; designed geometry is outside that tested scope by rule 6, so
this is not re-treading a closed lane.

**Lossy-projection test.** Projection: the factor base ↦ the fibration
`x ↦ W'(x)` of the affine line it lies on. Discarded: the individual points of
the factor base and their group-theoretic relationship to the curve. Retained:
the fibre partition, which propagates deterministically because the Semaev
relation is a symmetric function of `x`-coordinates and therefore descends along
`W'` whenever `V` is `W'`-invariant. Lossy: many factor bases share a fibration,
and whether they share a solving degree is the measurement.

**Minimal discriminating test.** At fixed `L`, four families of `V`:
(a) random `V` of degree `L` (the baseline); (b) `V = D_k ∘ (·)`,
Dickson/Chebyshev; (c) `V(x) = x^k − a` with `k | L`; (d) `V` a product of linear
factors whose roots form an arithmetic progression `{x, x+d, …}` — which imports
`KN-OPEN-006`'s designed-support object into the algebra slice and lets one
experiment address both anchors. For each: measure `d_solve` (the A2-9
instrument), the Macaulay matrix size at `d_solve`, and the empirical
decomposition probability over ≥ 500 screened random targets. Report the
**charged** figure `size(d_solve)^2 / Pr[decompose]`, never `d_solve` alone.

**Null object / control.** (i) The random-`V` arm is the null and it is measured
in the same run with the same code. (ii) **A support-matched random system built
on the designed `V`'s supports** (A2-8's null): if it achieves the same
`d_solve`, the drop is a support effect, not a composition effect, and the
mechanism claim is refuted while the practical saving survives — the two must be
reported separately. (iii) Certificates: every claimed decomposition is a signed
sum of factor-base points verified independently by a from-scratch group law,
following `EV-SUBRES-001`'s three-implementation precedent.

**Falsifier (reachable).** `d_solve` identical across all four families → the
composition lever does not touch the solving degree, and that is a clean scoped
negative that additionally narrows the residual of `KN-OPEN-004` (which left
designed geometry open). Second reachable falsifier: `d_solve` drops but
`Pr[decompose]` drops by more, so the charged figure worsens — a **net negative
under the fully-charged model**, which is the outcome `KN-OPEN-006` was written
to force and which must be reported as such rather than as a partial win.

**Cost.** Impl: medium/high — ~600 LOC: four `V`-families, decomposition
screening with certificates, plus the A2-9 solving-degree instrument. Compute:
medium/high — ≈8–15 core-hours; dominated by the decomposition-probability arm,
which needs many targets per cell for the probability to be worth reporting.

**Ceiling.** `toy`. `p ≤ 24 bits`, `m = 3` (`m = 4` optional), small `L`. **A
positive result at toy scale is a lever *candidate*, not a lever**: an additive
`d_solve` drop at `L = 4..28` does not establish that the drop persists as
`L → q^{1/(m-1)}`, and the asymptotic claim is explicitly not made. No exponent
is claimed to move. If the charged figure improves, the honest successor is a
crypto-scale support-only extrapolation licensed by A2-8, not an attack claim.

**Kills-it-early.** One cell at `p = 1009`, `L = 6`, families (a) and (c). If
`d_solve` is equal, the mechanism has no toy-scale signal and the expensive
probability arm is never built.

---

### A2-11. Isotypic localization: does the rank deficit live in the invariant component of the Semaev symmetry?

**Claim.** For the symmetric Semaev system (`S_m` is symmetric in
`x_1, …, x_{m-1}`), decomposing the Macaulay row space under `S_{m-1}` into
isotypic components gives a deficit concentrated in the **trivial (invariant)**
component: `deficit_trivial / deficit_total ≥ 0.8` at every tested cell. Frozen
alternative: the deficit splits in proportion to component dimensions, in which
case symmetry is not the mechanism and symmetrization buys only the known
dimension reduction and nothing about solving degree.

**Mechanism.** Symmetrization of Semaev systems (working in `e_1, …, e_{m-1}`) is
**established public technique** — Gaudry's index calculus for abelian varieties
and the Faugère–Gaudry–Huot–Renault line, from memory and therefore
`unverified` here (S5). What is not in this corpus is the use of the isotypic
decomposition as a **localizer of the rank defect**: the semi-regular model is
computed for the whole system and is blind to the group action, so it can be
right on one component and wrong on another. If the defect is invariant-supported,
then the invariant subsystem is where the real algebraic content sits and the
cost model should be built there — which is also where the dimension is smallest,
so the measurement would be cheap *and* the modelling would improve.

**Lossy-projection test.** Projection: row space `↦` its image under the isotypic
projector `π_λ` for each irreducible `λ` of `S_{m-1}`. Discarded: the
cross-component structure, i.e. how components sit relative to each other inside
the ambient space. Retained: each component, which propagates deterministically
**for symmetric multipliers**, because the multiplier action then commutes with
the group action. Non-symmetric multipliers mix components, and the honest
statement is that the projection is compatible only on the symmetric-multiplier
sub-family — stating that restriction explicitly is what makes the projection
lossy-but-compatible rather than a change of coordinates. Any experiment must
therefore either restrict multipliers to the invariant ring or report the mixing
explicitly; a design that silently uses general multipliers is measuring
something else.

**Minimal discriminating test.** At toy `m = 4` over `F_p` with `p ∤ (m-1)!` (so
the projectors are defined): build the Macaulay matrix with symmetric multipliers
only; apply the isotypic projectors; compute each component's rank; compare
against a component-wise semi-regular prediction derived from the isotypic
Hilbert series of the same degree pattern. Report the per-component deficits and
their shares.

**Null object / control.** (i) **A random system with identical supports and no
symmetry** (A2-8's null, symmetrized artificially by averaging over the group):
its isotypic deficits should be proportional to component dimensions. If the true
system matches that profile, the finding is a controlled null. (ii) **Dimension
check**: the component dimensions must sum to the ambient dimension exactly, or
the projectors are wrong. (iii) **`p` sensitivity**: repeat at a second prime; a
result that changes with `p` at fixed `m` indicates a modular-representation
artifact (`p | (m-1)!`) rather than structure.

**Falsifier (reachable).** Proportional split → symmetry is not the mechanism.
Also reachable: `deficit_total = 0` at every reachable `m` and `D`, in which case
there is no deficit to localize at this scale and the experiment reports that it
had no signal to resolve — an instrument-reach statement, not a mathematical one.

**Cost.** Impl: medium — ~400 LOC on top of A2-8's builder: Young symmetrizers or
character-based projectors for `S_3`, plus component-wise elimination. Compute:
medium — ≈3–5 core-hours at `m = 4`.

**Ceiling.** `toy`. Prime-field but small; the symmetrization technique is
established prior art and only the deficit-localization framing is being
proposed, with novelty recorded `unverified` because it cannot be screened here.
Moves no exponent; at best it tells a future cost model which subsystem to
model.

**Kills-it-early.** Verify `deficit_total > 0` at the smallest cell before
building any projector. No deficit, no localization, no experiment.

---

### A2-12. Weight-order sensitivity: is the solving degree an invariant of the system or an artifact of the grading — and does the charged cost move?

**Claim.** Over a pre-declared finite family of integer weight vectors `w`
respecting the descent/block structure, there exists a `w` for which the
`w`-graded solve reaches the solution at `w`-degree strictly below the
standard-grading solving degree, **and the charged cost** — the size of the
Macaulay matrix at the attaining degree, squared, not the degree itself —
strictly improves against uniform weights by `≥ 20%` at every tested cell.
Frozen alternative: no `w` in the family improves the charged cost, in which case
the standard grading is empirically optimal within that family and every cost
model built on it is at least not erring optimistically.

**Mechanism.** Solving degree is order- and grading-dependent; the standard total
degree is a *choice*, and the systems in this slice have an intrinsic variable
hierarchy that the choice ignores — in the boolean lineage, `nb = n + 3⌈n/3⌉`
splits the variables into `n` original and `3⌈n/3⌉` auxiliary descent variables;
in the prime-field lineage, the chained `S_3` tree distinguishes leaf from
internal coordinates. Because Gröbner cost is exponential in the attained degree,
even a small degree reduction is an exponent-level change in cost — which is why
this is worth testing and also why the **counter-charge must be paid**: a
non-uniform weight enlarges the monomial set at any fixed degree bound, so the
matrix can grow faster than the degree shrinks. Reporting a degree drop without
the size is the classic uncharged-invariant error (`KN-LIT-7593`: an eliminated
search dimension is not a speedup until the invariant's own cost is charged), and
this idea's entire design is built to prevent it.

**Lossy-projection test.** Projection: the ideal `↦` its `w`-graded Hilbert
function. Discarded: the total-degree filtration, i.e. the standard grading is
*replaced*, not refined — different `w` give genuinely different, mutually
incomparable projections and no one of them recovers the others. Retained: the
`w`-graded pieces, which propagate deterministically because `w`-degree is
additive under multiplication. Lossy in the required sense: many ideals share a
`w`-graded Hilbert function, and the standard total degree is itself just the
`w = (1,…,1)` member of the family — which makes the *comparison* well-posed and
the family the object rather than any single grading.

**Minimal discriminating test.** Pre-declared family, fixed before data:
`w₀ = (1,…,1)` (baseline); `w₁ =` 1 on original, 2 on auxiliary; `w₂ =` 2 on
original, 1 on auxiliary; `w₃ =` block index `1,2,3,…` along the descent chain;
`w₄ =` reverse of `w₃`; `w₅ =` a uniformly random weight vector with the same
weight sum (the **null weight**). For each: build the `w`-graded Macaulay matrix
at increasing `w`-degree bounds, find the least bound at which the quotient
dimension equals the brute-force solution count, and record `(degree, ncols,
nrows)` at that bound. Report the charged figure `ncols · min(nrows, ncols)` (an
elimination-cost proxy stated as a proxy), never the degree alone. Run on both
arms: the boolean `n1_ms.json` system at reduced `nb` (A2-5's synthetic family)
and the prime-field `m = 3` system (A2-8's builder).

**Null object / control.** (i) **`w₅`, the random weight**: any structured weight
that fails to beat a random weight of the same weight sum has demonstrated
nothing about structure. (ii) **The uniform baseline `w₀` must reproduce the
committed solving degrees** where they exist — a mismatch halts the run as an
instrument defect. (iii) **Support-matched random system under the same weights**:
if it shows the same weight sensitivity, the effect is a property of the support
geometry, not of Semaev.

**Falsifier (reachable).** No `w` in the family improves the charged cost, or the
best structured `w` fails to beat the random `w₅`. Either is a §4-standard scoped
closure **within the named family** — obstruction (no member of this family beats
uniform on charged cost), argument (the measured size/degree trade at every
cell), forward guidance (what remains: block orders, elimination orders,
non-graded orders, and weights derived from the actual staircase rather than from
the descent structure). It is not, and must not be written as, a claim that no
grading helps.

**Cost.** Impl: medium — ~350 LOC of weighted-Macaulay builder on top of A2-5 and
A2-8; the rank engines are shared. Compute: medium — 6 weights × cells × seeds;
≈5–10 core-hours, with the boolean arm cheaper than the prime-field arm.

**Ceiling.** `toy` on both arms. A positive result is a **cost-model** result at
small parameters — a better grading for a solver — and explicitly **not** an
ECDLP break: nothing here produces a discrete logarithm, and the charged-cost
improvement at `nb ≤ 18` or `L ≤ 28` supports no asymptotic statement. No
exponent is claimed to move. `Pollard rho` remains the baseline.

**Kills-it-early.** `w₀` vs `w₅` at the smallest boolean cell: if the random
weight already beats uniform, the family is mis-specified and must be redesigned
before the structured weights are worth running.

---

## 3. Batches

Four bounded batches. `≤ 3` concurrent non-archive tasks at any time. Write
scopes are disjoint by construction: each task writes only beneath its own task
directory and none writes to `ledger/`, `experiments/EXP-SIG-*`, or any shared
record. All budget figures are **unverified projections from a
`nrows × rank × words` model calibrated on one committed cell**, not
measurements, and must be re-costed after each batch's first completed cell.

---

### BATCH A2-α — "What the committed system already says"

**Objective.** Extract every zero-to-low-compute fact obtainable from the one
committed system artifact (`experiments/EXP-SIG-008/work/n1_ms.json`) before any
new system is built or any large rank is attempted. Decide whether any part of
the 7,110 deficit is forced by the support pattern, by trivial relations, or by
block locality — and settle whether the D5 trichotomy is definitional.

**Ideas.** A2-1, A2-2, A2-3, A2-4.

**Why this grouping.** All four read the same committed artifact, all four are
pure combinatorics or small-ring linear algebra, none needs Sage, none needs a
system that does not exist, and each produces a certificate (a matching, a Hall
violator, a collision census, a pairwise intersection table, a convention table)
that is independently re-checkable without rerunning the search. Grouping them
also amortizes one shared loader/validator for `n1_ms.json` whose correctness is
pinned by the committed D6 numbers `183,312 / 174,033 / 16,018`.

**Concurrency.** Three tasks: α1 = A2-1 + A2-3 (both are structure-of-the-matrix
objects sharing the incidence build); α2 = A2-2; α3 = A2-4.

**Rough budget.** ≈2 core-hours total, dominated by A2-3's 276 small ranks and
A2-1's Hopcroft–Karp. Every idea has a sub-minute kill switch that runs first.

**What it decides.** Whether a candidate family outside the partial-sum lattice
exists at all and has the right order of magnitude (A2-3 is the leading
candidate; A2-1 and A2-2 are the exact-bound flanks); and whether the D5
lineage's numbers are citable (A2-4).

**Test first — A2-2, then A2-3.** A2-2 is the cheapest valid discriminator in
the entire catalogue: it needs one committed file, the standard library, and a
dictionary of hashed frozensets; it terminates in minutes; its output is an
**exact theorem** (`nrows − rank ≥ Z + Σ_c(|c|−1)`), not an estimate; and its
negative branch (`Z = 0`, all classes singleton) is reached in the first 10,000
rows, at which point the idea is dead for ~10 seconds of compute. It also has the
rare property that a *large* result would refute the semi-regular prediction by
row counting alone, with no rank computation anywhere. A2-3 follows immediately
because its own kill switch — printing `|V_i|` for the 24 equations — is one
minute and determines whether the best-motivated non-partial-sum candidate family
is alive.

---

### BATCH A2-β — "Is 7,110 generic, or is it a one-size artifact?"

**Objective.** Run the null-object control that `DEC-20260805-cc2b32` B5 named
and that the Sage blockage made unreachable on the true system: build the
analogous family directly at reachable size, dial the miss fraction, and decide
between a generic response curve, a one-size artifact, and seed noise.

**Ideas.** A2-5, A2-6, A2-7.

**Why this grouping.** All three build synthetic systems of the SIG shape
(`n` quadratics + `n` cubics on `nb = n + 3⌈n/3⌉`) and share one builder, one
chunked GF(2) bitset rank engine with checkpoint/resume, and one shape-law
cross-check (`n = 9 ⇒ ncols(D6) = 31,180`, a committed number). A2-6 is the cheap
combinatorial front end that predicts the miss fractions A2-5 then dials, and
A2-7 tests the premise (HEUR-BF-1) that both of the others presuppose — so
running them apart would mean building the same instrument three times and
discovering the premise failure last.

**Concurrency.** Two tasks, sequenced not parallel on the rank engine:
β1 = A2-6 (combinatorial, independent, runs immediately); β2 = A2-5 then A2-7
(shared builder and rank engine, same write scope, must be sequential).
A2-6's D5 arm is **gated on A2-4** and declares that dependency.

**Rough budget.** ≈2 core-hours for A2-6; ≈2 core-hours for the A2-5
`n ∈ {6,7}` core with `n ∈ {8,9}` as optional rungs outside the completion gate;
≈4–8 core-hours for A2-7. Total ≈8–12 core-hours, chunked under the
per-invocation cap, with graceful degradation reporting what was covered.

**What it decides.** Whether the 7,110 is an ordinary point on a miss-fraction
response curve (retiring the anomaly), an `n ∈ {10,11,12}` artifact (the
canonical shape flagged by the decay control), or noise at fixed support — the
last of which would be a **proper §4 closure of the entire closed-form lane**,
with a named obstruction rather than a fatigue report.

---

### BATCH A2-γ — "Prime-field solving degree: is the method licensed, and is the proxy safe?"

**Objective.** Address `KN-OPEN-002` directly and at its own field: decide
whether solving degree is a function of the supports (licensing cheap
extrapolation to crypto-scale supports) and whether `d_ff` tracks `d_solve` over
prime fields or errs in a named direction.

**Ideas.** A2-8, A2-9.

**Why this grouping.** A2-9's null baseline **is** A2-8's support-matched random
system, and both need the same three artifacts: a Sage-free `S_3` construction
over `F_p`, a mod-`p` Macaulay builder, and a brute-force solution counter that
supplies the stopping condition independently of any model under test. Splitting
them would duplicate all three and, worse, would let A2-9 be run without its
control.

**Concurrency.** One task, two stages (A2-8 gates A2-9: if the support-matched
null is not correctly calibrated, `g_random` is meaningless). Runs concurrently
with α and β, which touch no prime-field code.

**Rough budget.** ≈3–6 core-hours for A2-8 at `m = 3` (`m = 4` a stretch);
≈4–8 core-hours for A2-9. `m = 5` is declared optional and outside the completion
gate up front. Total ≈7–14 core-hours.

**What it decides.** Whether `GOAL-SDEG-001`'s `C_decomp(p,m)` numerator can be
built from support combinatorics at crypto parameters (A2-8) and whether existing
`d_ff`-based prime-field cost estimates under- or over-state the true cost (A2-9)
— both scoped to `p ≤ 24 bits` and `m ≤ 4`, and neither closing `KN-OPEN-002`.

---

### BATCH A2-δ — "Levers" (gated on γ)

**Objective.** Test the three candidate levers on the exponent-determining
quantity — factor-base composition, symmetry-isotypic localization, and grading
choice — each under a fully-charged cost model that can and should return a net
negative.

**Ideas.** A2-10, A2-11, A2-12.

**Why this grouping.** All three consume the solving-degree instrument that γ
builds and validates; running any of them before γ would mean measuring a lever
with an uncalibrated meter, which is the `EV-SUBRES-001` `deg_u` failure
(a demonstrated-blind instrument reporting a confident exponent) repeated. All
three also share the discipline that distinguishes this batch: **report the
charged figure, never the degree alone** — `size²/Pr[decompose]` for A2-10,
per-component shares against dimension for A2-11, `ncols · min(nrows, ncols)` for
A2-12.

**Concurrency.** Two tasks after γ completes: δ1 = A2-10 (own write scope, own
certificate pipeline); δ2 = A2-11 + A2-12 (shared prime-field builder and
weighted/projected Macaulay code).

**Rough budget.** ≈8–15 core-hours for A2-10 (dominated by the
decomposition-probability arm); ≈3–5 for A2-11; ≈5–10 for A2-12. Total
≈16–30 core-hours — the largest batch, and the one most likely to be truncated.
Each idea's kill switch runs first and is designed to close the expensive arm
before it is built.

**What it decides.** Whether any of the three levers moves the charged cost of
prime-field point decomposition at toy scale. A positive is a **lever candidate
at toy parameters**, never an attack; a negative on all three is a scoped closure
naming three obstructions and the classes that remain (elimination orders,
non-graded orders, multi-block-coupled objects, staircase-derived weights).

---

## 4. Honest accounting (inventor protocol §5)

**Objects studied.** O1–O10 of §1, enumerated and scored. No object was carried
to a verified structural depth in this session: **this catalogue reports zero
measurements.** Every number cited is read from a committed record
(`EV-SIG-006`, `EV-SIG-008`, `EV-DREG-008`, `DEC-20260805-cc2b32`,
`CORR-20260805-7f3a08`, the two review reports) or is elementary arithmetic on
those numbers, independently recomputed here where it is load-bearing
(`nrows(12,6) = 12·N(24,4) + 12·N(24,3) = 155,412 + 27,900 = 183,312`;
`N(24,6) = 190,051`; `174,033 + 16,018 = 190,051`;
`Q = 174,033 − 149,410 = 24,623`; `17,513 + 7,110 = 24,623`).

**Depth of verified structure.** None. Twelve proposals, zero experiments, zero
evidence records, zero identifiers minted.

**`dominated_by`.** `n/a (no result claimed)`. No attack, no Pareto point, no
cost claim on any axis — time, memory, or data/queries. This is written
explicitly rather than left `null` (`AGENTS.md` rule 5). For the ECDLP itself,
`Pollard rho` at `O(√N)` time and `O(1)` memory remains the frontier row that
every idea here fails to approach, because none of them attacks the ECDLP.

**`sota_delta`.** Zero on every axis. No exponent moves. `KN-OPEN-002` is neither
closed nor narrowed by this catalogue; `KN-OPEN-004`'s scoped negative is
untouched (A2-10 proposes to test outside it, which is not the same as narrowing
it); `KN-OPEN-006` is referenced only where A2-10's arithmetic-progression arm
overlaps it.

**Enumerated closures (§4 standard).** **None asserted.** This session records no
closure. The one closure-shaped fact in the live state is
`DEC-20260805-cc2b32`'s: `P(pass) = 0` for the **entire** partial-sum lattice
against `Q = 24,623`, with the named obstruction (the required quotient is not
within one window width of any partial sum of the model's own series), the
argument (the reachable lattice is `{0,1,2,25,289,2013,9117,17513,26037}`, nearest
miss `1,058.5 = 1.5` window widths), and forward guidance (a successor needs a
candidate family outside the lattice). That closure belongs to that decision, not
to this file, and this catalogue's job is to supply the forward guidance it asks
for: A2-1 (transversal matroid), A2-2 (weight-≤2 relations), A2-3 (pairwise
intersection excess) are three such families, and A2-5/A2-6/A2-7 are the controls
that decide whether any family can exist. **A count of rejected mechanisms would
be a fatigue report; none is offered here** (`KN-TECH-056`).

**Premature closure check.** This session did not decline to generate on
saturation grounds and asserts no lane is dead. Where a lane is currently
unreachable it is recorded as **blocked on infrastructure** (`S1`: Sage absent;
`S3`: no m4ri, so `n=12 D6` rank is out of reach) — which is never mathematical
evidence (`AGENTS.md` rule 5), and each such lane carries a Sage-free
substitute (A2-5 substitutes for the blocked `n`-axis; A2-6 substitutes a
prediction for the blocked `n=13` measurement and is labelled a prediction).

**Open directions for the next session.**
1. **The 7,110 mechanism remains fully open.** Nothing here explains it.
2. Whether a **valid D≥6 null baseline** exists at any `n ≥ 12` is open;
   `GOAL-SIG-001`'s question is untouched.
3. The **D5 column-count trichotomy** is unresolved and now has three readings
   plus one independent reconstruction agreeing with none (A2-4 targets it).
4. **Builder identity** across the SIG and DREG lineages is unresolved and
   requires a Sage-capable environment (`CORR-20260805-7f3a08`); nothing here
   substitutes for it, and no reimplementation should be claimed to.
5. `KN-OPEN-019` — the ECDLP tracked-object enumeration — is still unwritten, so
   §1's table remains a sketch. Writing it for the *algebra* slice specifically
   would be a bounded and useful successor to this catalogue.
6. **The boolean/prime-field gap is unbridged.** A repaired boolean `d_reg` model
   transfers to no prime-field statement, and no idea in this file claims
   otherwise.

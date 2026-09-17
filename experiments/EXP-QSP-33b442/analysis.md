# EXP-QSP-33b442 — analysis

Lifecycle step 8–10 composition (`.claude/skills/review-evidence/SKILL.md`) for
the claim-changing review round opened by
`ledger/handoffs/TASK-20260917-43701b.yaml`. Written by the Coordinator after
all three reviewers returned and their reports were committed.

Branch `claude/ecc2k-130-quasi-subfield-poly-nhcj1f`, HEAD `9bdcc586c`, PR #1265.

**This document is strictly sectioned.** Observation carries only what was
measured. Comparison carries only pre-registered-vs-measured and
prior-vs-outcome contrasts. Inference carries only what follows. Limitation
carries what does not. A number that appears in Inference without appearing
first in Observation is a defect in this document.

**Companion records.** Evidence `EV-QSP-a6aa4b`; decision `DEC-20260917-793ae2`;
validity gate and amendment rulings `CORR-20260917-8b80cc`; review plan and
recorded prior `TASK-20260917-43701b`.

**Not results.** The JSON files under `analysis/qsp-ecc2k130/explore/` are
CONTEXT and the source of the pre-registered values. They are not artifacts of
this experiment, are not cited as measurements anywhere below, and agreement
between a run value and an explore value is reproduction of a pre-registered
number, never independent corroboration.

---

## 1. Observation

Every figure in this section is read from a committed artifact named at the end
of the paragraph carrying it. Nothing here is interpreted.

### 1.1 Validity of the run set

Run count against contract: six counted stage invocations (`S1`, `S1B`, `S2`,
`S2B`, `S3`, `S4`) against `budget.maximum_runs: 6`, with `S0` (zero compute)
and `S5` (extraction) declaring `counts_against_maximum_runs: false` and
quoting the contract's own `budget.note`. Eight run directories, six counted
invocations. Seed integrity: `base_seed 20260917` with six named Stage-1b
sub-streams `20260917:stage1b:n{11,13}-np{6,7}-d{3,5,7}` and two Stage-4
sub-streams `20260917:stage4:n11-np6`, `20260917:stage4:n23-np12`, matching
`specification.yaml replication.seeds` exactly; Stages 0, 1, 2, 3 and every
control are seed-free exhaustive enumerations. Raw-versus-summary agreement was
recomputed from per-candidate rows rather than read off summaries at eight
points, all agreeing. Fifteen ledger-schema errors exist on the package, none
on a measurement-bearing run directory; the five S0 errors are disclosed
standing debt. [`CORR-20260917-8b80cc`
`independent_checks_performed_beyond_the_validator`, `gate_verdict`]

`AMD-20260917-001` (the I3 feasibility cap, `deg D <= 1000000`) was authored
before the affected runs, is named in `amendments_in_force` on all eight
manifests, and is RATIFIED. Its ratification is explicitly scoped NOT to cover
its own characterisation of its cost. `amendments/v2.yaml` is NOT ratified and
was never in force on any run; its two diagnoses (the F1/F2 stopping-rule
contradiction, which never fired, and the M1 metric-scope gap, which was
covered in practice) are accepted as standing version-1 contract defects.
[`CORR-20260917-8b80cc` `amendment_rulings`]

### 1.2 What the runs measured

| stage | scope | headline measurement |
|---|---|---|
| S0 | zero compute | hand re-derivation note archived before S1; the two (4,3) cells worked by hand (N = 1 slack 0; N = 0 with D having 2 K-roots, both failing the closing test) |
| S1 | 5 cells × 252 λ = 1260 candidates, I1+I2+I3 on every one | M2 = 0 pairwise disagreements; M1 = 0.52 / 0.56 / 1.00 / 0.25 / 0.25 at (11,6)/(13,7)/(7,3)/(11,4)/(13,5); 0 above the bound; 0 degenerate; M6 = (64, 8, 32768, 4); C6 0 disagreements on 30 linearized candidates |
| S1B | 6 cells × 200 = 1200 seeded K-coefficient draws | 0 instrument disagreements; 0 above the bound; per-cell M1 0.6667 / 0.2000 / 0.1224 / 0.5556 / 0.2000 / 0.0816; 0 degenerate |
| S2B | 95 cells, 42 244 candidates; I2 on all, I1 on 10 444, I3 on 342 of 356 near-complete | 356 near-complete rows; 65 complete splitters at exactly (7,3)[36], (7,4)[3], (31,5)[24], (31,6)[2]; min(β − exact) = 0.000000; min(β − conservative) = 0.21875; 0 above the bound; 0 C6 disagreements on 1170 linearized candidates |
| S3 | 3 cells × 244 = 732 candidates at n = 131, I3 only | max N = 132 at n′ = 33, histogram {0:62, 1:118, 2:60, 132:4}; max N = 2 at n′ = 44 and 66, histogram {0:62, 1:122, 2:60} each; M1 = 0.054977 / 0.074074 / 0.222222; 546 certificates written, 546/546 independently re-verified, 0 failures; orbit-tail upper probabilities 0.1190 / 1.0 / 1.0 |
| S4 | 2 cells × 200 = 400 rational draws | max N = 2 in both cells against the conjectured bound 14; 0 of 400 above it |
| S5 | extraction only | metrics.json + report.md; (D)(ii) recorded WITHDRAWN AS STATED |

[`experiments/EXP-QSP-33b442/execution-report.yaml`; run raw results under
`experiments/EXP-QSP-33b442/runs/`]

Wall clock: S1 2.857 s, S1B 24.865 s, S2B 1099.091 s, S3 143.841 s, S4 5.845 s;
peak RSS at most 73 916 416 bytes on any stage, against a 4 GB
machine-protection cap. `RUN-QSP-33b442-S2` aborted on an implementation defect
(constructing D before deciding whether I3 would run on it, needing ~35 TB for a
single (31,2) candidate) and is superseded by `-S2B`; no number from it is
reported anywhere. [execution-report `runs`, `M10`]

Six protocol deviations are declared by the producer: PD-1 (I3 withheld on 14
Stage-2 near-complete candidates and on C3, under the ratified amendment), PD-2
(two stages run concurrently against a literal `maximum_workers: 1`), PD-3
(smoke tests to a scratch directory, no smoke number reported), PD-4 (serving
model differs from the adapter binding and is not probe-verified), PD-5 (the
run wrapper's YAML emitter wrote five manifests unparseable; repaired in-task by
de-indenting continuation lines only, no key, value, count or timestamp
altered), PD-6 (no seventh invocation was spent on an independent replication).
[execution-report `protocol_deviations`]

### 1.3 What the review round measured — J1, J3, J5 (`TASK-20260917-34b637`)

**J1 — HOLDS.** An instrument for `p != 2` was written against the statement,
never adapting the producer's package (`implementation/**` was not opened at any
point): dense `F_p[X]` at arbitrary prime p, with brute enumeration over all
`p^n` elements, `deg gcd(X^{p^n} − X, L)` with `X^{p^n} mod L` by *generic* p-th
powering rather than by the identity under test, and the derivation's own D
object with the injection step checked directly. Roll-up
(`out/j1_grand_total.txt`): 205 rows, 292 105 candidates, **0** violations of
`N <= max(d^{q+1}, p^{n′−r})`, **0** with `deg D >` bound, **0** where the
K-root set of L fails to divide D, **0** brute-vs-gcd disagreements, **0**
injection-vs-gcd disagreements, 46 candidates with `D = 0`, largest `N/bound`
anywhere exactly 1.0. The report's deduplicated totals are 203 rows / 291 997
candidates, of which 290 641 at odd p over 55 odd-p cells, plus 2 400
K-coefficient draws at odd p (all with a coefficient outside `F_p`) and 6 980
re-checked through a third pure-Python route. Odd-p cells reach n = 13 at p = 3
and n = 11 at p = 5 and p = 7, over n′ ≤ 8, at degrees 2..4
(`code/cells_p{3,5,7}.txt`). The bound is ATTAINED at odd p: `(p,n,n′) = (3,8,3)`
with d = 2 gives N = 8 = max(8, 3), and `(5,5,3)` with d = 2 gives
N = 5 = max(4, 5). The two Stage-0 (4,3) hand cells reproduce line for line on
all three of the reviewer's instruments. The reviewer found and fixed two bugs
in its own code before taking any result, both caught by the (4,3) known-answer
fixture.

**J3 — HOLDS, with a required narrowing.** All 65 M3 rows recomputed from
`(n, n′, d)` alone with exact rationals — β and both thresholds do not depend on
N, so the check trusts no instrument: **0** disagreements with the archive on
any of `q, r, β, corollary_exact, corollary_conservative, β−exact,
β−conservative, bound`; `min(β − exact) = 0` exactly; `min(β − conservative) =
7/32 = 0.21875` exactly; complete-splitter cells and counts (7,3): 36, (7,4): 3,
(31,5): 24, (31,6): 2. Both threshold columns are present and non-null on all 65
complete and all 356 near-complete rows. **Exactly three** complete splitters
attain `β = exact`: `X^2+X` and `X^2+X+1` at (7,3,d=2), and `X^4+X^2+X` at
(7,4,d=4). Three of the 356 near-complete rows sit strictly below the exact
corollary — (7,4,d=3,N=8) twice and (7,5,d=4,N=16) — and are not F2 events only
because they are not complete splitters; at (7,4) with d = 3 the bound is
max(9, 2) = 9 < 16 = 2^{n′}, so (A) actively forbids a complete splitter there
and none is observed. On scope: over all 54 356 pairs `(n, n′)` with n′ not
dividing n, `β >= n/((q+1)n′)` is valid for every n′ including q = 0, but the
final step `n/(n + n′ − r) > 1/2` holds for 18 614 pairs and **fails for
35 742**, every failing pair having q = 0 and n′ >= 2n, with equality exactly at
n′ = 2n. A witness object was produced, not described: p = 2, n = 5, n′ = 11,
λ = X^2 gives `V = {x ∈ F_32 : x^{2^11} = λ(x)} = F_32`, N = 32 measured by
brute enumeration over all 32 elements and by `deg gcd(X^{2^5}−X, L)` in
agreement, with β = 5/121 = 0.0413. Further witnesses (2,3,7), (2,2,5), (3,2,7),
(3,3,7).

**J5 — BREAKS, on its scope half only.** Enumeration half, clean: for each of
n′ = 33, 44, 66 the 244 rows are set-equal to the reviewer's independently
derived set, **0** duplicates, **0** missing, **0** extra, **0** linearized
present, per-exact-degree counts {3:8, 4:12, 5:32, 6:64, 7:128}; the three
histograms rebuilt from the rows agree with the archived `N_histogram` and sum
to 244; `q`, `r`, `bound` recomputed on all 732 rows with **0** disagreements
and **0** rows with N > bound; affine marking correct on all 732 with **0**
mismatches (4 per cell: `X^4+1`, `X^4+X+1`, `X^4+X^2+1`, `X^4+X^2+X+1`). Scope
half, broken: of the 732 candidate rows at n = 131, **546 carry a
`certificate_path` and 186 have N = 0 with `certificate_path: null`**; 546
certificate files exist on disk; `raw-result.json` records
`certificates_written: 546`.

### 1.4 What the review round measured — J2, J4, J6, proves-too-much (`TASK-20260917-52b4e6`)

**J2 — HOLDS; the measurement it is credited with does not exist.** Degeneracy
requires `d = p^j` with `j(q+1) = n′ − r`; the identity `n′ − r = (q+1)n′ − n`
(verified mechanically for every `1 <= n, n′ <= 399`) makes that integral **iff
`(q+1)` divides `n`**. Every one of the contract's 111 declared cells (95
Stage-2 + 5 Stage-1 + 6 Stage-1b + 3 Stage-3 + 2 Stage-4, spanning 98 distinct
`(n, n′)` pairs) has n prime with `2 <= n′ < n`, hence `2 <= q+1 < n`, hence
`(q+1) ∤ n`. The degenerate-detection instrument returned `False` on **45 436**
candidates (1260 + 1200 + 42 244 + 732, counted row by row) and could not have
returned `True` on any. The contract contains exactly two `(n, n′)` pairs at
which a degenerate candidate exists and ran neither: (4,3), the Stage-0
hand-gate cell, which uses `X^2+X+1` and `X^3+1`; and (12,6), control C1, the
one cell in the contract with composite n, which uses λ = X at d = 1.

The instrument was then exercised and it fires: 26 degenerate instances were
constructed by solving `(q+1) | n` and pushed through the producer's own
unmodified `qspcore.deg_D_and_degenerate` and `qspcore.i3_injection_f2` at 26
`(n, n′)` pairs spanning `r >= 1` and `r = 0`, `j = 1..5`, `d = 2..32`,
including (12,6) and (4,3). On all 26: `D == 0` symbolically, both routines
report degenerate, `L == M^{2^j}` as an exact integer identity, and the
exhaustive distinct-root count equals I1 equals I2 equals `2^{gcd(n′−j, n)}`.
The full degenerate family over all K-coefficients at (4,3), (6,4), (6,5) gives
20 + 72 + 72 = **164** degenerate λ, every one with `N = 2^{n′−j}` exactly and
none splitting completely. A search for `D = 0` outside the claimed shape
`cX^{2^j}+b` over **331 664** λ found **0**. A search for a char-p counterexample
to `f ∘ g = Y^m ⇒ g = cY^e + b` over **1 324 468** compositions over
`F_2, F_3, F_4, F_5, F_7, F_8, F_9` found **0**; `g = Y^p + Y` and
`g = Y^{p^2} + Y^p` admit none for `deg f <= 3`; inseparable `f = h(Y^p)`
produced none at p = 2 or 3.

**J4 — HOLDS; the description of the redundancy does not.** Static call-graph
analysis of the committed `qspcore.py`: I1, I2, I3 and `verify_roots_f2` all
bottom out on `clmul`, `deg`, `polymod`, `square`; `gcd` is shared by I2 and I3
and not I1; **I1 has no primitive of its own** — its primitive set is a subset
of both others'. `verify_roots_f2`'s docstring claim to share no code path with
the injection count is true of the algorithm and false of the arithmetic
(`K.pow2k` is iterated `polymod(square(·))`, `K.eval_f2poly` is
`polymod(clmul(·))`). `stage1.py` dispatches the compiled C helper only at
`n′ >= 10` and every Stage-1 cell has `n′ ∈ {3,4,5,6,7}`, so **`gf2rc.c`
produced none of the 1260 Stage-1 agreements**; all 1260 rows carry
`instruments_run = [I1, I2, I3]` with `I2_implementation` absent.

Fault injection on a scratch copy whose sha256 was verified equal to the
committed file (`32a5ad6b68678e71e9be24173040a9cb972a6576d6a2b7385ebcfdffbc2ad495`)
before any edit, 8 faults plus 1 negative control, sample 120 candidates at
(7,3) and (11,4) degrees 2..5 against an unfaulted baseline `M2 = (0,0,0)`:
`F-c` (corrupt `clmul`, reached by all three) changed **87 of 120** counts and
took the matrix to **(75, 73, 43)**; `F-e` (I2-only) gave (92, 0, 92); `F-g`
(I1-only) gave (17, 17, 0); `F-a` and `F-b` were caught by
`KField.__init__`'s own irreducibility assertion as a load failure and a hang;
`G-a`, `G-b`, `G-d`, designed to be invisible to the `n <= 13` field-polynomial
check, were all caught by `ddf_factor`'s `assert deg(rest) <= 0`; `F-d` was not
in fact a fault (a semantically identical rewrite of Euclid) and served as the
negative control at 0 changed.

At n = 131 the reviewer built **two** independent decision procedures the
experiment never used — Proposition 2 of `KN-LIT-4fe9d2` via
`qspcore.c6_linearized_N`, and 131×131 `F_2` linear algebra written from scratch
with its own field arithmetic — and made **36 determinations** (24 on
linearized λ outside the census, 12 on the **affine λ inside the census**,
`lambda_bits` 17, 19, 21, 23). `linalg N == C6 N == I3 N` on every one, **0**
disagreements, and all 12 census values match the archived rows exactly
(N = 0, 1, 1, 0 per cell). 720 of the 732 census rows (98.4 %) remain
single-instrument. The 62 candidates per cell with N = 0 carry
`root_verification: None`.

The amendment's cost verified independently from `S2B/raw-result.json`: of the
65 `M3_complete_splitters` rows, **exactly 10** carry `i3_run: false` with
`i3_skip_reason: deg_D_above_declared_cap`, all at `(n, n′, d) = (31, 5, 8)`
with N = 32 and `deg D = 2 097 152`; on those 10, I1 is null and I3 is null, so
I2 alone — and at Stage 2 I2 is the C helper `gf2rc`, not the Python routine.
They are the only 10 of 65 with a single non-null instrument; 55 have two or
more. The other 4 capped candidates, at (29,2,d=3) and (31,2,d=3) with N = 2,
are not complete splitters.

PD-6's substitute verified: 54 S2 checkpoint cells have an S2B counterpart,
**23 176 of 42 244** candidates (54.9 %) are common to both, **0** have a
differing N; same binary, same host, I2 only. The reviewer additionally ran
`gf2rc.c` on all 1260 Stage-1 candidates: **1260/1260 agree with all three
archived Python instruments, 0 disagreements, 0 rejected inputs.**

**J6 — BREAKS.** From the frozen sources: Euler–Petit Proposition 7 states
κ is "currently majored by 4.876"
(`inputs/EULER-PETIT-2019-QSP/paper_fulltext.md:2597`) — an upper bound; Huang
Lemma 3.1 gives the eliminant cost as `Õ(m^5.188 (3d)^{4.876 m^2})` — an upper
bound; Huang Appendix A.1 states the univariate polynomials are of degree
"bounded by M(E)" and that root-finding "can be neglected in the overall
complexity estimation" (`inputs/HUANG-2020-JMC-QSP/paper_fulltext.md:1116-1118`).
H1's declared *rigorous ingredient* asserts the eliminant "has degree M(E)" and
that root-finding "costs at least M(E)". Exact arithmetic on the threshold: at
n = 131 the smallest β admitted by (B) over n′ = 2..130 is `131/260` at n′ = 130
(q = 1, r = 1) = 0.5038462, and `α_β > 1` at that β requires
`κ < 1/(2β) = 260/262 = 130/131 = 0.9923664`; the general worst case is
n′ = n−1, threshold exactly `(n−1)/n` → 1. H1's own formal statement assumes
`κ >= 1`. `H-QSP-5540d7` `heuristic_assumptions[H1].validation_experiment_ids`
is `[]`; `IDEA-20260916-b84e2d` is a proposal at `status: proposed`, described
in the hypothesis itself as "scheduled, not yet designed", and its engine
impediment is re-confirmed by this run's own `environment.json` (`sage`,
`magma`, `macaulay2`, `singular`, `msolve`, `ntl_or_flint` all absent).

Two of J6's other named breaking artifacts were hunted and **not** found. The M7
fence holds: S5 `report.md` §2 is headed "ARITHMETIC, NOT MEASURED",
`metrics.json -> M7_arithmetic_not_measured` repeats the label, and a
repository-wide search for `2^117.7`, `117.6`, `0.898` finds them only in
M7-labelled contexts. Proposition 7 instantiated in full at integer m (carrying
`m!`, `m^{5.188}` and `3^{κ m^2}`, which the `m >> 1` form drops), minimised
over `n′ ∤ n` and integer `m ∈ 2..59` at β = (B)'s bound and κ = 4.876, gives a
minimum of **2^166.43** at (n′ = 3, m = 2) against M7's idealised 2^117.67 and ρ's
2^60.9; dropping `3^{κ m^2}` entirely still gives 2^126.24.

**proves_too_much — HOLDS; the declared failure signature is ABSENT on both
families.** FAMILY 1 (`n′ | n`): the bound is vacuous on all 3 422 triples
`(n, n′, d)` with `n′ | n`, `n <= 32`, `d <= 29`, and the vacuity is structural —
`r` enters (A) in exactly one place, the exponent of `Y^{p^{n′−r}}`, which at
r = 0 *is* `deg L`. (A) does not assume `r >= 1`; (B) states it and uses it
exactly once, where it is needed. Sharpened: every `(n, n′, d)` with `n′ | n`,
`n < 40` and `d^{q+1} = p^{n′}` exactly was enumerated (30 triples), and at the
5 reachable ones every λ of that degree was run — **65 832** candidates — with
`deg D < 2^{n′}` on most, **0** splitting completely, and `N <= deg D` on every
one. Broadening to every λ of degree 1..8 at every `r = 0` cell with `n <= 14`,
`n′ <= 10` gives **7 244** candidates, **0** violations of `N <= deg D`, **141**
objects at r = 0 that split completely, and the derivation vacuous on **every
one** of the 141; of the 288 candidates where the derivation is non-vacuous at
r = 0, **not one** splits completely. FAMILY 2 (linearized, Theorem 1): **1 032**
`F_2`-linearized complete splitters at `n <= 40` were enumerated by
Proposition 2 alone — **with no instrument of the experiment** — giving **0**
violations of (B), **0** objects with `3/4 <= β < ` (B)'s bound (the object that
would satisfy Theorem 1 and refute (B)), and **0** with `β < 3/4`; (B) is
exactly tight at (35,15) β = 7/9, (35,20) β = 0.875, and (33,22), (36,24),
(39,26) at β = 3/4 where (B) and Theorem 1 coincide. At n = 131, `T^131 − 1`
factors as `(T+1) · Φ_131` with `deg Φ_131 = 130`, so the only `F_2`-linearized
complete splitter at the target field is at n′ = 130 with β = 0.999941.

### 1.5 What the blind re-derivation measured (`TASK-20260917-5fa7d5`)

`blind_from_respected: true`. The re-deriver read exactly two repository files
(`AGENTS.md`, `agents/validator.md`), ran no `git` command of any kind, searched
the repository for nothing, and never listed or read any sibling path under
`coordination/investigations/QSP-ECC2K130/`.

From the statement of the quantity and the parameters alone it derived the
candidate-set size (248 exact-degree polynomials minus 4 linearized = **244**)
and produced: **max N = 132**; attained by exactly **4** candidates, all of
degree 7, bit-packed **{132, 161, 204, 251}** =
`X^7+X^2`, `X^7+X^5+1`, `X^7+X^6+X^3+X^2`, `X^7+X^6+X^5+X^4+X^3+X+1`; histogram
**{0: 62, 1: 118, 2: 60, 132: 4}**; orbit sizes **[1, 131]** for each maximizer;
528 explicit roots as 131-bit coefficient vectors, plus the degree-131 minimal
polynomial of each 131-orbit as a compact re-checkable certificate.

Method, disjoint from the producer's: because λ has `F_2` coefficients,
`x^{2^{33k}} = λ^{(k)}(x)`, and `33 · 4 = 132 = 131 + 1`, so every K-root of L is
a root of `P(X) := λ^{(4)}(X) + X^2` of degree `d^4 <= 2401`; then
`g = gcd(P, X^{2^131} + X)` and `G = gcd(X^{2^33} + λ(X), g)`, with `N = deg G`.
**The degree-2^33 polynomial L is never materialised.** The 244-candidate sweep
runs in ~6 s.

Controls the re-deriver ran: exhaustive brute force at n = 7, 9, 11, 13 with
**two different irreducible field polynomials each**, ~2000 ground-truth
comparisons, 0 mismatches, including a composite-n case (9,7) where orbits of
size 1, 3 and 9 occur; an `F_2`-rank computation at n = 131 on 8 linearized λ,
agreeing; the translation involution `λ(X) ↦ λ(X+1)+1` holding across all 248
exact-degree polynomials; an independent composition depth `k = 8`
(`33·8 = 264 ≡ 2 mod 131`, `P_8 = λ^{(8)} + X^4`) agreeing at n = 131 on all
exact-degree-3 and -4 polynomials and degree-5 spot checks; a **full independent
re-implementation in sympy `GF(2)` arithmetic** over all 244 candidates, 0
mismatches, independently reproducing the maximum, the argmax and the histogram;
and re-verification of all 528 published root vectors by **two disjoint
checkers** (sympy `galoistools`, and from-scratch coefficient-list arithmetic),
528/528 under each. It also caught and fixed a false pass in its own small-case
harness (an inverted parity filter meant the brute force never ran while the
script still printed OK).

**Null-model control, and it is new evidence.** Non-`F_2` roots arrive only in
orbits of size 131, so the expected number of λ carrying an orbit is
`244/131 = 1.86` against **4 observed**, Poisson `P[>=4] = 0.12`; after the
involution pairing ((132,251) and (161,204)) there are 2 independent events
against 0.93 predicted, `P[>=2] = 0.24`. Measured: 242 `F_2` roots over 244 λ
(0.992 per λ, null predicts 1.000) and 524 non-`F_2` roots (2.148 per λ). The
re-deriver's stated conclusion: "the result is consistent with the null model
and I claim no signal."

Sensitivity recorded: had "linearized" been read to include affine, the
candidate set would be 240 with histogram {0:60, 1:116, 2:60, 132:4}, and the
maximum and the attaining set would be unchanged.

### 1.6 Procedure deviations observed in the round itself

- **PROC-1.** The orchestrating session committed the sibling red team's
  **completed** report to the shared branch at `8f15567f6` while this
  mutually-blind round was still running, and committed the other two reviewers'
  in-flight artifacts at `600bc97af` and `c0b3125ec`.
  `review_plan.blindness.mutual` is `true` and `lifted_for` is empty. The
  validator declares it saw the path (via `git ls-tree --name-only`) and the
  commit subject line, and did not open the file; the red team declares
  `read_sibling_reports: false`; the blind re-deriver ran no git command at all.
- **PROC-2.** Commit `c0b3125ec` is labelled a work-in-progress snapshot and in
  fact contains the validator's FINAL 814-line report.
- **PROC-3.** The coordinator subagent that wrote `TASK-20260917-43701b` had no
  Bash tool and produced an unparseable YAML file; the orchestrating session
  quoted one scalar so it would parse, changing no content. Disclosed in
  `TASK-20260917-5b9153` and its receipt.
- **PROC-4.** The blind re-deriver deliberately skipped the agent-bus inbox
  check and ran no git/merge-digest command, because two bus records
  (`MSG-20260917-97a8d4`, `MSG-20260916-945e58`) are named in `blind_from` and an
  inbox render could surface them. It disclosed this in §0 of its report rather
  than doing it quietly.
- **PROC-5.** A post-round fix to the validator's own instrument `j1_kcoef.c`
  (commit `4e74a24af`) after Cursor Bugbot found its irreducibility test was the
  order-of-one-element test rather than the Rabin gcd criterion. As reported by
  the orchestrating session: of ten cells only (5,6) has n with two distinct
  prime factors, its modulus `X^6+X+2` is irreducible, all ten moduli were
  confirmed irreducible independently, and a re-run under the corrected
  criterion reproduces the committed output byte for byte.
- **PROC-6.** The Coordinator subagent composing this document could not write
  it: this runtime refuses a markdown write from a subagent, deterministically,
  on two attempts at this exact path. The file was composed in full and returned
  verbatim, and the orchestrating session wrote those bytes. No content was
  authored or altered in transcription.

### 1.7 Unexpected observations recorded by the producer (AGENTS.md rule 8)

- The (13,5) cell has slack identically 0 across all 252 candidates; no other
  Stage-1 cell behaves this way (maxima 22, 26, 63, 33).
- The four orbit-carrying candidates at n = 131, n′ = 33 all have slack 0, are
  all of degree 7 and all non-linearized.
- The design-time cost estimate is inverted by the measurement: Stage 3 cost
  143.8 s (estimated "of order one hour") and Stage 2 cost 1099.1 s (estimated
  "a few minutes").

---

## 2. Comparison

### 2.1 Pre-registered versus measured

Every pre-registered exact value in `specification.yaml
preregistered_prediction.formula` was reproduced by the run's own computation:
M1 = 0.52 / 0.56 / 1.00 / 0.25 / 0.25; complete splittings only at (7,3), (7,4),
(31,5), (31,6); 356 near-complete and 65 complete; Stage-3 max N = 132 at
n′ = 33 with histogram {0:62, 1:118, 2:60, 132:4} and the same four named
candidates; max N = 2 with histogram {0:62, 1:122, 2:60} at n′ = 44 and 66;
M2 = 0; M6 = (64, 8, 32768, 4). Predictions P-A through P-F all met as written.
Falsification branches F0–F6: none reached.

| success conjunct | pre-registered | measured | met |
|---|---|---|---|
| S1: M1 <= 1 at every cell of Stages 1, 1b, 2, 3 | yes | 0 above the bound in 1260 + 1200 + 42 244 + 732 = 45 436 candidates | **yes** |
| S1, second conjunct: degenerate candidates listed separately, each satisfying `N <= 2^{n′−j}` | yes | 0 degenerate candidates, and *structurally* 0 — no cell can host one | **vacuously** |
| S2: M2 = 0 over 1260 | yes | 0 | **yes** |
| S3: M6 = (64, 8, 32768, 4) | yes | exactly | **yes** |
| S4: no complete splitter below the exact corollary | yes | 0 of 65; independently recomputed 0 of 65 | **yes** |
| S5: Stage-0 hand check passes; every Stage-3 root list re-verified | yes | gate PASS; 546/546 re-verified | **yes**, on 546 lists |

**The one pre-registered sentence that is not met is the success criterion's own
headline.** It reads "**732 certificate-bearing exact counts at n = 131**". The
archive carries 732 exact counts of which **546** bear a certificate; 186 rows
have N = 0 and `certificate_path: null`. The contract contradicts itself here:
its own `required_artifacts` defines the Stage-3 certificates as "one file per
n = 131 candidate **with N > 0**". The overstatement is **186 rows — 732 claimed
against 546 that exist, i.e. 34 % more than exist (732/546 = 1.3407) — in the
direction that flatters the claim**. Stated precisely, because this is the one
sentence whose whole purpose is to correct an overstated count: the 186 surplus
rows are **25 %** of the 732 claimed and **34 %** of the 546 actual, and an
earlier draft of this passage read "186 rows, 34 % of the claimed set", which
glued a correct count to a percentage of the other denominator.
`RUN-QSP-33b442-S5/report.md`
§7 restates it more sharply still as "732 exact, independently re-verified
counts", which contradicts the execution report, its own M4 section and
`raw-result.json`, all three of which say 546. "Independently re-verified" is a
defined operation in this contract and cannot be performed on an empty root
list.

Two further pre-registration-versus-measurement mismatches, both non-numeric:
the contract's attainment tail check says "the d = 4 complete splitters" at
(7,4) in the plural where there is exactly one (the producer records this), and
the execution report's "minimum β − exact = 0.000000 (equality at two
splitters)" undercounts by one — the independently recomputed answer is
**three**, which also overturns `CORR-20260917-8b80cc`'s inference of "at least
four".

### 2.2 Recorded prior versus outcome

The prior in `TASK-20260917-43701b review_plan.coordinator_prior` was written
before any reviewer ran, and declares its own contamination: the Coordinator had
already read the headline numbers and had itself recomputed several of them.

| prior item | stated probability | outcome |
|---|---|---|
| J2 degeneracy defect confirmed | 0.70 | **confirmed and strengthened** |
| J2 escalates into an error in the characterisation | 0.05 | **did not** (0 of 331 664; 0 of 1 324 468) |
| J4 "the joint where I most expect the round to cost the claim something" | 0.65 | **HOLDS; the named mechanism was disproved by experiment** |
| J4 an actual I3 undercount at n = 131 | 0.08 | **not realised** (36 determinations, 0 disagreements) |
| J6 (E) not promotable | 0.60 | **confirmed, and exceeded** |
| J3 quantifier scope is not what the argument supports | 0.40 | **confirmed, with a produced witness** |
| J1 certified counterexample to (A) | 0.02 | **not produced** (0 in 291 997 + 2 400) |
| J5 enumeration error | 0.20 | **not found** (clean on all six checks) |
| J5 a downstream sentence over-reading the census | 0.45 | **found — but not downstream** |
| a genuine F1 at n = 131 | 0.01 | **did not occur** |
| modal expectation | 0.70 | **essentially exactly what came back** |

**Was the prior well calibrated? On WHAT the round would find, yes. On WHICH
joint would cost the claim and BY WHAT MECHANISM, no.** Four departures, stated
plainly because a prior the review overturns is the most informative thing this
round produces:

1. **The two joints the prior priced highest as breaks — J4 at 0.65 and J2 at
   0.70 — both returned `holds`.** The two joints that actually broke are J6
   (priced 0.60, and the prior was right) and J5 (priced 0.20 / 0.45, and framed
   as a wording risk downstream of the claim). The prior conflated "the
   description is overstated", which is what it correctly foresaw at J4 and J2,
   with "the joint breaks", which is not what happened at either.

2. **The prior's J4 hypothesis was falsifiable and was falsified in the record's
   favour.** It stated: "if a single injected fault leaves the agreement matrix
   clean, the matrix is measuring shared code, not agreement." The antecedent
   does not hold — a single fault in the most-shared primitive changed 87 of 120
   counts and took `M2` from (0,0,0) to (75,73,43), and three faults designed to
   evade the field-polynomial self-check were caught by an internal algebraic
   assertion instead. `M2 = 0` moves from *suspected artifact* to *measured
   property*. This is the single most valuable overturn in the round and the
   Coordinator was wrong about it.

3. **The prior's J2 reasoning reached the right conclusion by a wrong
   criterion.** It argued from `n′ − r` being small against `q+1 >= 2`. The
   correct criterion is `(q+1) | n`, and the prior's stated reason is false on
   **56 of the 95 Stage-2 cells** — (13,12) has `n′ − r = 11`, (31,15) has 14.
   The conclusion never changed, the count of affected candidates grew from 3192
   to 45 436, and the superseded reason must not be repeated.

4. **The prior under-priced J5 and mislocated it.** It expected an over-reading
   in a downstream sentence at 0.45. What was found is an arithmetic
   overstatement of 186 rows — 732 claimed against 546 actual, 34 % more than
   exist — **in the frozen contract's own success-criterion
   headline**, the exact sentence the round was convened to evaluate, and a
   sharper restatement of it in the Stage 5 report that contradicts three of the
   run's own records.

A fifth observation about the prior's *structure* rather than its numbers: on
every quantity the Coordinator had already recomputed for itself, the round
agreed and bought nothing. On the three quantities it had **not** recomputed —
the direction of the cited κ constant, the certificate accounting, and the
fault-injection behaviour of the agreement matrix — the round corrected the
Coordinator each time, twice against the record and once in its favour. A
contaminated prior does not merely weaken agreement as evidence; it also
predicts, in advance, exactly where the round will be informative.

### 2.3 Producer's claim versus reviewers' scope

The producer stated **no verdict** (`observations.interpretation: "NONE
OFFERED"`), which is correct and is honoured. What was put to the reviewers is
the contract's own pre-registered success headline. Each reviewer reported on
its own joints and explicitly declined a whole-claim verdict; the composition is
this document's.

---

## 3. Inference

Nothing in this section introduces a number that does not appear in §1.

### 3.1 The run set is valid evidence

Expected run count, schema completeness of measurement-bearing manifests, seed
integrity against the pre-registration, raw-versus-summary agreement at eight
independently recomputed points, and control comparability all check out. The
fifteen schema errors are record-level and fall on S0 (zero compute), S5
(extraction) and S2 (aborted, no number reported); both reviewers who were asked
to opine on that classification independently declined to overturn it. **This
run set is not returned to the Executor.** The five residual S0 errors are
disclosed debt and must be named in the archive receipt.

### 3.2 (A) and (B) survived every attack named in advance, and two that were not

Across the producer's 45 436 candidates and the review's further ~294 400 at
`p ∈ {2,3,5,7}` with disjoint implementations, no λ was found with
`N_K(L) > max(d^{q+1}, p^{n′−r})`, no candidate with `deg D >` the bound, no
K-root of L failing to divide D, and no complete splitter with
`β < n/(n + n′ − r)`. The bound is attained at p = 2 and now also at p = 3 and
p = 5. The derivation's exclusion clause is exhaustive (`D != 0` bounded by (A);
`D = 0` bounded by `p^{n′−j}`, with no third case), its degenerate branch is
exactly tight (`N = p^{n′−j}` attained on all 190 instances tested), and the
composition-equals-monomial step survives 1 324 468 characteristic-p tests
including the additive and inseparable maps where characteristic-0 intuition is
least reliable. The proves-too-much control's declared failure signature is
absent on both known-false families, and the vacuity at `r = 0` is traceable to
the single occurrence of `r` in the derivation rather than to a choice of
parameters.

Two attacks the plan did not name also failed: the fault injection (§1.4) and
the two independent decision procedures at n = 131 (§1.4).

**Therefore (A), (B) and the tightness claim (C) are supported at DERIVATION
TIER on the tested scope.** "Derivation tier" means a checkable argument plus
certificate-bearing numerical checks, not a machine-verified proof
(`docs/claims-and-verification.md`). The general statement over all p, n, n′ and
λ rests on the derivation, which three independent sessions checked and did not
break; it does not rest on the enumeration.

### 3.3 The load-bearing quantity at the target field is independently established

The n = 131 census was produced by a single instrument with a re-verifier that
can falsify a listed root and cannot detect a missing one — a verification
asymmetry that runs in the direction favouring the hypothesis. That exposure is
now materially reduced, by two disjoint routes that did not exist before this
round:

- A **blind** re-derivation, from the statement and parameters alone, by a
  method that never materialises L, returned max N = 132, the same four
  attaining λ, the same candidate-set size 244, the same histogram
  {0:62, 1:118, 2:60, 132:4} and the same orbit shape [1, 131] — **exactly**
  equal to the archive on every one of those, and re-implemented a second time
  inside its own task in foreign (sympy) arithmetic with 0 mismatches.
- Twelve **census rows** (the affine λ) now carry an independent linear-algebra
  determination that agrees exactly, and 24 further determinations on the
  excluded linearized slice agree with Proposition 2 of `KN-LIT-4fe9d2`.

Under `review_plan.blind_rederivation.interpretation_rule`, fixed in advance,
agreement is evidence about the **quantity** and is the only evidence at n = 131
that does not pass through the producer's instrument. It is therefore now
established, on two lineages with no shared code, that at n = 131, n′ = 33 the
largest number of K-rational roots over the 244 non-linearized `F_2`-coefficient
λ of exact degree 3..7 is 132.

### 3.4 The null model removes an anomaly rather than explaining it

The execution report flagged as an unexpected observation that the four
orbit-carrying candidates at n′ = 33 are all of degree 7, all non-linearized and
all of slack 0. The blind re-derivation's null model — new information, not
available when that anomaly was recorded — gives an expectation of
`244/131 = 1.86` λ carrying an orbit against 4 observed, Poisson `P[>=4] = 0.12`,
and 2 independent events after the involution pairing against 0.93 expected,
`P[>=2] = 0.24`. **The four maximizers are the generic outcome, not a signal.**
The anomaly needs no explanation, and any later claim treating those four λ as
algebraically distinguished would require evidence this round did not seek and
did not produce. This is "controls before belief" discharging in the direction
of *less* structure, which is the direction that is easy to skip.

### 3.5 The closure reading (E) is not promotable, and its stated reason is refuted

Two independent grounds, and the second is the stronger:

1. **Promotion gate (2) is unsatisfied.** `agents/coordinator.md` requires every
   conditional dependence to be an explicit numbered heuristic backed by
   archived validation evidence or a scheduled validation experiment, and states
   that an unvalidated heuristic caps the claim below `supported`. H1 is
   explicit, numbered and formally stated; its `validation_experiment_ids` is
   empty; its route is a proposal, not an experiment; and the gate's own last
   sentence is unconditional, so the blockage of that route is a scheduling fact
   and not the reason. (E) cannot move toward `supported` on this evidence, and
   the contract's own `heuristic_under_test_note` already said so.

2. **(E)'s stated reason invokes a ceiling as a floor.** (E) argues that "the
   required β < 1/(2κ) is unreachable because β > 1/2 forces κ < 1, five times
   below Rojas' 4.876". A quasi-subfield factor base beats generic iff the
   **solver is cheap**, i.e. iff κ is small; excluding that requires a **lower**
   bound on κ. Both frozen sources give 4.876 as an **upper** bound. The
   exclusion at n = 131 needs `κ >= 130/131 = 0.9924`, against H1's own
   assumption `κ >= 1` — a margin of **0.76 %, tending to zero as n grows** —
   not a factor of five. Separately, H1's declared "rigorous ingredient" asserts
   degree exactly `M(E)` and cost at least `M(E)` where its own cited appendix
   says degree "bounded by `M(E)`" and root-finding cost "can be neglected"; the
   step that would convert the upper bound into an equality is the
   BKK/generic-attainment statement H1 itself marks `RECALLED`, which AGENTS.md
   rule 9 bars from discharging `supporting_results`. **After honouring that
   label, H1 has no retrieved support in the direction (E) uses it.**

This is a defect in the RECORD's argument, not in H1's truth: H1 may well be
true, its `formal_statement` and `falsification_condition` are correctly written
as a heuristic, and `(A)` and `(B)` are unconditional and untouched. The
refutation artifact reaches **derivation** tier: a self-contained checkable
argument over verbatim quotations from two frozen source texts plus exact
rational arithmetic. It does not reach counterexample tier, because no instance
of a solver with `κ < 130/131` is exhibited — the break is that nothing in the
record excludes one.

Note in the record's favour, because a red team's failed attacks are evidence
too: the M7 arithmetic fence holds in both the prose and the machine-readable
record, and the `m >> 1` idealisation errs toward the attacker by ~49 bits,
which for a non-existence claim is the conservative direction.

### 3.6 The empirical headline overstates what was measured, in two independent ways

- **"732 certificate-bearing exact counts at n = 131" is wrong by 186 rows —
  732 claimed against 546 actual, 34 % more than exist.**
  732 exact counts exist; 546 bear a certificate; the 186 with N = 0 are
  precisely the subset the certificate architecture cannot check at all. The
  correct sentence is "732 exact counts at n = 131, 546 of them
  certificate-bearing".
- **"1260 exhaustive toy candidates under three agreeing instruments" overstates
  the redundancy.** At Stage 1 the three routines share `square`, `polymod` and
  `clmul`, I1 has no primitive of its own, the certificate re-verifier shares the
  same three, and the one implementation-independent instrument in the package
  contributed none of the 1260 agreements. The honest count of independent
  determinations is **two** at Stage 1 over a shared primitive base, and **one**
  at n = 131. The fault injection shows those two are doing real work; it does
  not make them three.

Neither is a defect in a measured value. Both are defects in the one sentence
the round was convened to evaluate, and both run in the direction that flatters
the claim.

### 3.7 The degeneracy branch has a structural reason, not a measurement

`degenerate_candidates: 0` at every cell is a consequence of the cell design:
degeneracy requires `(q+1) | n`, and every one of the 111 declared cells has n
prime with `2 <= n′ < n`. The instrument could not have returned `True` on any of
45 436 candidates. This does not weaken (B), whose first step is a theorem and
was independently confirmed — the constructed degenerate instances all attain
`N = p^{n′−j}` exactly and none splits completely. It weakens what the
**experiment** established: a declared blocking control was never exercised, and
success conjunct S1's second clause is vacuously satisfied. The 26 + 164
constructed instances in `TASK-20260917-52b4e6` §2.2–2.3 supply the missing
measurement, produced outside the frozen protocol and therefore evidence about
the mathematics rather than a result of this contract.

### 3.8 (B) and (E) need `n′ < n` stated

`β > 1/2` is derivable exactly when `q >= 1`, i.e. exactly when `n′ < n`; the
final step fails on 35 742 of 54 356 admissible pairs, all with q = 0. The
corollary itself cannot be witnessed false, because its own antecedent
`N_K(L) = p^{n′}` forces `p^{n′} <= |K| = p^n` and hence `n′ <= n` — a one-line
step written nowhere in the record — and the QSP setting supplies the same
constraint from outside via Definition 3.1 of `KN-LIT-0a321c`. But **(E)'s
written quantifier "at any p, n, n′" is over-broad and a witness against it was
produced**: `V = {x ∈ F_32 : x^{2^11} = X^2(x)} = F_32` has β = 0.0413, is a
factor base of exactly the form (E) quantifies over, and satisfies (A). The fix
is one clause; shipping without it would be an unforced error.

### 3.9 Rulings on the procedure deviations

- **PROC-1 — real, and the orchestrating session's fault, not any reviewer's.**
  The round's independence survives **on this evidence**: all three reviewers
  declared their exposure, the validator disclosed what it saw of the sibling
  (a path and a commit subject line, carrying no verdict, number or finding) and
  states every verdict was fixed by its own computation before the commit
  landed, and the blind re-deriver ran no git command at all. But
  `blindness.mutual: true` with `lifted_for: []` now describes a property of
  three reviewers' **restraint** rather than of the round's **setup**, and that
  is the weaker guarantee. It is undetectable downstream unless written down,
  which is why it is written down here. `TASK-20260917-43701b` is **not edited**;
  the plan's own rule requires a superseding record.
- **PROC-2 — recorded, not repairable.** A commit subject that calls a final
  deliverable a work-in-progress snapshot misstates the state of the record at
  that commit. It changes no artifact content. History is pushed and is not
  rewritten; a superseding note carries the correction.
- **PROC-3 — accepted.** A serialisation repair that altered no key, value or
  meaning and was disclosed before any reviewer read the card. It is the same
  class as the producer's PD-5. The systemic finding is worth routing: **two
  independent YAML-emission defects in one round, both from agents with no
  shell** — three, counting PROC-6. That is a tooling item, not a campaign item.
- **PROC-4 — the right call, and it should be precedent.** The inbox check is a
  standing convention; blindness is a property of one round's setup and cannot
  be restored once destroyed. Two `blind_from` paths are bus records and an
  inbox render addressed to a review role could surface exactly those. The agent
  disclosed the suspension in its report rather than performing it quietly or
  omitting it silently, which is the required behaviour. The cost is stated and
  accepted: if a peer sent it something it needed, it did not see it, and
  nothing in its output depends on repository state. The same reasoning covers
  its refusal to run `git log`/`show` or a merge digest.
- **PROC-5 — J1's verdict is not disturbed.** The defect is in a *precondition
  check* (is the declared modulus irreducible), not in a counting routine; the
  precondition was independently confirmed true for all ten moduli; only (5,6)
  has an n with two distinct prime factors, the configuration where the
  order-of-one-element test and the Rabin criterion can diverge, and its modulus
  `X^6+X+2` is irreducible; and a re-run under the corrected criterion
  reproduces the committed output byte for byte. Two conditions attach. First,
  the byte-for-byte reproduction receipt must be archived with the report — the
  artifact a later reader finds at HEAD is not the artifact that produced the
  committed output, and only that receipt closes the gap; asserting it in prose
  does not. Second, the lesson is the reviewer's own and generalises: its
  known-answer fixture caught two of its bugs and did not cover its own
  precondition test, which an external linter caught instead.
- **PROC-6 — accepted, same test as PROC-3.** The composing agent could not
  write this file and the orchestrating session transcribed it verbatim. No
  content was authored or altered in transcription. Recorded because git
  attributes the file to the session that typed it.

### 3.10 What this round does NOT license

No attack, no exponent, no statement about any deployed curve. No curve, group
or point was constructed anywhere in this contract. ρ on ECC2K-130 stands at
2^60.9 (`KN-LIT-096`) and nothing here touches it. `RQ-QSP-f9bbdb` decision
target (a) — an existence result at n′ = 33 — is answered **negatively on the
732 enumerated candidates and on nothing else**: a complete splitter there would
need N = 2^33 and the largest observed is 132.

---

## 4. Limitation

What follows does **not** follow, stated as flatly as the findings.

1. **Ten of the 65 complete splitters rest on one instrument.** All at
   `(31, 5, d = 8)` with N = 32 and `deg D = 2 097 152`, excluded from I3 by the
   ratified `AMD-20260917-001` and unaffordable for I1. They are the only 10 of
   65 with a single non-null instrument. Mitigations, which reduce but do not
   remove the exposure: at Stage 2 the surviving instrument is the C helper
   `gf2rc`, the one implementation in the package sharing nothing with
   `qspcore`; β depends on `(n, n′, d)` alone and their margin over the exact
   corollary is 2.834, the largest in the table; and I2 ran on all 42 244
   candidates, so the cap cannot have *hidden* a splitter. This figure must be
   reported as "10 of 65 complete splitters" and never again as "14 of the 356
   near-complete candidates" without it.

2. **720 of the 732 census rows at n = 131 are single-instrument.** The 12
   affine rows now carry an independent determination; for non-linearized,
   non-affine λ no independent decision procedure was available to any session
   in this round. The blind re-derivation covers the *maximum, the argmax, the
   histogram and the orbit structure* of the whole cell at n′ = 33 by a disjoint
   method, which is a strong check on the cell's aggregate quantities; it is not
   a per-row second instrument at n′ = 44 and n′ = 66, which it did not compute.

3. **The degeneracy control is vacuous by construction.** No cell of this
   contract can host a degenerate candidate, because degeneracy requires
   `(q+1) | n` and every cell has n prime with `2 <= n′ < n`. The instrument
   returned `False` on 45 436 candidates and could not have returned anything
   else. An earlier statement of this reason — that every cell has `n′ − r` in
   {1, 2} — is **wrong on 56 of the 95 Stage-2 cells** and is superseded by the
   `(q+1) | n` criterion; the conclusion never changed.

4. **`p != 2` evidence now exists, and only barely.** It exists at `p ∈ {3,5,7}`
   at n ≤ 13 (p = 3) and n ≤ 11 (p = 5, 7), over n′ ≤ 8, at degrees 2..4, plus
   2 400 K-coefficient draws at odd p. It is an artifact of the **review**
   (`TASK-20260917-34b637`), not of `EXP-QSP-33b442`, whose every numerical cell
   is p = 2. The transfer from p = 2 to general p is by the derivation and never
   by measurement.

5. **`β > 1/2` requires `n′ < n`.** The corollary cannot be witnessed false
   because complete splitting forces `n′ <= n`, but that step is written nowhere
   in the record, and (E)'s written quantifier admits objects where `β <= 1/2`.

6. **The census certifies 244 distinct λ examined at three n′, not "732 named
   polynomials".** 732 rows, 732 distinct `L = X^{2^{n′}} − λ(X)`, 244 distinct
   λ. Every occurrence found also writes `3 × 244` alongside, so a reader of the
   full clause is not misled; the short form standing alone is wrong.

7. **The census is a measure-zero slice.** 732 `F_2`-coefficient λ of degree at
   most 7 out of `F_{2^131}[X]`; K-coefficient λ at n = 131 are untouched
   (Stage 1b reaches K-coefficients only at n = 11 and 13). Every other λ at
   those n′ is covered by the derivation, not by a list.

8. **PD-6 stands: no independent replication run was spent.** The substitute is
   a determinism cross-check — same binary, same host, I2 only, 23 176 of 42 244
   candidates (54.9 %), 0 mismatches. It tests determinism, not correctness, and
   the producer says so. What partly compensates is structural rather than
   procedural: Stages 0, 1, 2, 3 and every control are exhaustive and seed-free,
   so they are deterministic by construction, and the load-bearing n = 131
   quantity was independently re-derived blind.

9. **H1 is untested and untestable here**, by the contract's own design. (E)
   stays conditional whatever this experiment returns. Nothing in this analysis
   asserts H1 is false; what is established is that the record's *support* for
   H1's direction is absent once `recalled` citations are honoured.

10. **(D)(ii), the rational-λ extension, is WITHDRAWN AS STATED** by the Stage 5
    report — the pole bookkeeping was not written out — so rational λ are **not**
    closed and belong in (E)'s survivor list, which currently omits them.

11. **Two citation defects in the hypothesis record, neither touching a bound.**
    The degenerate case is described as "an affine binomial of subfield or
    multiplicative type" citing Appendix C.2 of `KN-LIT-0a321c` and Proposition 6
    of `KN-LIT-4fe9d2`; both cited results are the multiplicative family
    `X^{q^{n′}} − X^a`, which fits the `b = 0` subcase, while for `b != 0`
    `M = X^{p^{n′−j}} − c′X − b′` is an affine **trinomial** covered by neither.
    And `baseline_embedding.parameter_slice` (iii) states the `r = 0` vacuity for
    the `max` form only, where (A) also asserts `N <= deg D`, which at `r = 0`
    with `d^{q+1} = p^{n′}` can be strictly below `deg L`.

12. **An unreconciled discrepancy inside the J1 artifacts, disclosed rather than
    resolved.** `out/j1_grand_total.txt` records 205 rows / 292 105 candidates /
    `degenerate (D == 0): 46` / 12 boundary rows covering 53 993 candidates
    (29 526 survive + 24 421 cancel); the report's prose gives deduplicated
    totals of 203 rows / 291 997, and 10 boundary rows covering 53 885 with
    29 526 / 24 321 / 38. The verdict does not depend on which is used — every
    violation count is 0 in both — but the numbers do not reconcile and this
    analysis quotes the machine roll-up where it quotes a total. Assigned back
    rather than adjudicated here, for the same reason `CORR-20260917-8b80cc`
    declined to repair the producer's "equality at two splitters": this session
    may not edit a producer's record.

13. **One unfinished computation in the review, reported as unfinished.** An
    exhaustive `p = 7`, `(4,3)`, `d = 7` boundary run over all 5 764 801
    candidates was launched and did not complete in the review window. Nothing
    in any verdict rests on it; the question it would have settled is settled
    exhaustively by a different route.

14. **Infrastructure is not evidence.** `RUN-QSP-33b442-S2`'s abort, the absent
    Gröbner/resultant/sub-quadratic-`GF(2)[X]` engines, and the two hung fault
    injections are infrastructure outcomes under AGENTS.md rule 3. None of them
    is negative mathematical evidence and none is counted as one anywhere above.

15. **This analysis promotes nothing.** A joint that held means the receipt is
    admissible on that joint and nothing more. The official transition is
    `DEC-20260917-793ae2` and rests on a committed ledger archive.

---

## 5. Refutation artifacts backing the adverse findings

Per `docs/claims-and-verification.md`, "Refutation artifacts", the strongest
checkable artifact each adverse finding admits, produced and archived **before**
the decision that relies on it:

| finding | tier reached | artifact |
|---|---|---|
| J6 / O1: (E)'s stated reason invokes an upper bound as a lower bound; H1's "rigorous ingredient" is contradicted by its own cited appendix | **derivation** | `coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/report.md` §4.2–4.3, §8 O1, with verbatim quotations from `inputs/EULER-PETIT-2019-QSP/paper_fulltext.md:2597` and `inputs/HUANG-2020-JMC-QSP/paper_fulltext.md:1116-1118`, and exact arithmetic in `scratch/j6_kappa.py` → `scratch/j6_kappa_out.txt` |
| J5-1 / J5-2: the headline's certificate count overstates by 186 | **counterexample certificate** (against the claim sentence, not against a theory): 186 named rows with `N = 0` and `certificate_path: null`, re-countable from the committed cell JSONs | `coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/report.md` §3.3, `out/j5_census_enum.txt`; `experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/n131_np{33,44,66}.json` |
| J3 / scope: (E)'s written quantifier admits objects with `β <= 1/2` | **counterexample certificate** (against the quantifier as written): `(p, n, n′, λ) = (2, 5, 11, X^2)`, `N = 32` by two agreeing instruments, `β = 5/121` | `TASK-20260917-34b637/out/j3_scope_witness.txt`, `out/j3_scope.txt` |
| O2 / degeneracy control vacuous | **derivation** | `TASK-20260917-52b4e6` §2.1, `scratch/j2_structural.py`, `scratch/j2_cells.py` |

No refutation artifact of any tier was produced against (A) or (B). The record's
overall `proof_status` is `derivation`, the tier of the artifact the adverse
direction on `H-QSP-5540d7` itself rests on.

---

*Composed by the Coordinator, 2026-09-17, and transcribed to this path by the
orchestrating session (PROC-6). No run manifest, measured value or certificate
payload was read for modification or altered by this document. The composing
session had no shell: every number above is quoted from a committed artifact
named beside it, and no command was run to produce any of them.*

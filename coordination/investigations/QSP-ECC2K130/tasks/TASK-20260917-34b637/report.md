# TASK-20260917-34b637 — validator-breakthrough review report

Round: the claim-changing review of **EXP-QSP-33b442** opened by the
`review_plan` on `ledger/handoffs/TASK-20260917-43701b.yaml`.
Repo `/home/user/crypto-autoresearcher`, branch
`claude/ecc2k-130-quasi-subfield-poly-nhcj1f`, HEAD `2c1c4a34a` (pushed, PR #1265).
Policy `review-breakthrough`, reasoning effort `max`, independent session.

**Joints owned: J1, J3, J5 — and nothing else.** No verdict is offered here on
J2, J4, J6, the proves-too-much control, or on the claim as a whole.

---

## 1. `review_attestation`

```yaml
review_attestation:
  task_id: TASK-20260917-34b637
  joints_owned: [J1, J3, J5]
  sources_read:
    # the round's own contract
    - ledger/handoffs/TASK-20260917-43701b.yaml            # full
    - AGENTS.md                                            # "Review architecture", "Inter-agent messaging"
    - agents/validator.md                                  # full
    - CLAUDE.md                                            # as supplied in session context
    - templates/research-records.md                        # review_attestation + archive receipt blocks
    # the frozen contract and the run package
    - experiments/EXP-QSP-33b442/specification.yaml        # full
    - experiments/EXP-QSP-33b442/execution-report.yaml     # full
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/derivation-note.md   # full
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S2B/raw-result.json     # read programmatically (M3, near-complete, agreement, I3 cap, tail_checks)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/raw-result.json      # read programmatically
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/n131_np33.json # read programmatically (all 244 rows)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/n131_np44.json # read programmatically (all 244 rows)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/n131_np66.json # read programmatically (all 244 rows)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/certificates/        # DIRECTORY LISTING AND COUNT ONLY; no certificate file was opened
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S5/report.md            # partial: lines 128-160, 408-461, 515-532, plus targeted greps
    # ledger and knowledge
    - ledger/hypotheses/H-QSP-5540d7.yaml                  # partial: lines 1-200, 715-752, plus targeted greps
    - ledger/corrections/CORR-20260917-8b80cc.yaml         # partial: lines 1-200, 590-625, 718-740, plus targeted greps
    - ledger/questions/RQ-QSP-f9bbdb.yaml                  # grep only
    - knowledge/literature/KN-LIT-0a321c.md                # partial: the QSP definition / existence section
    - inputs/HUANG-2020-JMC-QSP/paper_fulltext.md          # partial: Definition 3.1 region, plus targeted greps
    # my own outputs, under my own write scope
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/**
  sources_deliberately_NOT_read:
    - experiments/EXP-QSP-33b442/implementation/**         # the plan's J1(c) requires the p != 2 instrument to be written against the STATEMENT, not adapted from the producer's code. No file here was opened at any point.
    - analysis/qsp-ecc2k130/explore/**                     # declared CONTEXT ONLY and forbidden as results. Not opened.
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/**
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/**
  read_sibling_reports: false
  sibling_disclosure: >-
    `ls` of coordination/investigations/QSP-ECC2K130/tasks/ showed the directory
    NAME TASK-20260917-52b4e6 (TASK-20260917-5fa7d5 appeared later in a
    `git status --porcelain`). No file inside either was opened, listed, or
    read. Disclosed rather than omitted.
  blind_from_respected: null       # not a blind re-derivation task
  verdict:
    J1: holds
    J3: holds            # with a REQUIRED NARROWING; see 3.2, and read the caveat there
    J5: breaks           # the enumeration half holds EXACTLY; the scope half breaks
  verdict_scope: >-
    These are verdicts on J1, J3 and J5 only. This reviewer cannot see J2, J4,
    J6 or the proves-too-much control and offers no opinion on the claim.
```

---

## 2. What I built, and its lineage

The plan's J1 attacks are computational and require an instrument that does not
exist in this repository: **every numerical cell of EXP-QSP-33b442 is `p = 2`,
and the producer's package is bit-packed `GF(2)[X]`.** So I wrote one.

- `code/j1_fp_sweep.c` — dense `F_p[X]` for arbitrary prime `p`, with **three
  mutually independent counting routes**:
  - **A, brute enumeration.** All `p^n` elements of `K = F_p[z]/(f)`; count
    `x` with `sigma^{n'}(x) = lambda(x)`. Assumption-free, no algebra.
  - **B, direct gcd.** `N = deg gcd(X^{p^n} - X, L)`, with `X^{p^n} mod L`
    computed by **generic repeated `p`-th powering**, deliberately *not* via
    the twisted-iterate identity that J1 is testing (using it would be circular).
  - **C, the derivation's own object.** Build `Lambda_{q+1}`, form
    `D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}}`, test `D != 0`, test
    `deg D <= max(d^{q+1}, p^{n'-r})`, test that the K-root set of `L`
    **divides** `D` (the injection step of (A), checked directly and not
    inferred from the inequality), then take `D`'s K-roots and apply the
    closing test `L(x) = 0`.
- `code/j1_kcoef.c` — the same at **K-coefficients**, where the coefficient
  twist `Lambda_k^{(n')}` is non-trivial. Nothing in this program has ever
  exercised that twist at odd characteristic.
- `code/j1_closure_check.py` — a pure-Python re-check of the injection by a
  third, separate route.
- `code/j3_recompute_m3.py`, `code/j3_scope.py`, `code/j5_census_enum.py`.

**Lineage, stated because the tier requires it:** none of this is copied or
adapted from `experiments/EXP-QSP-33b442/implementation/` or from
`analysis/qsp-ecc2k130/explore/`. Those files were never opened. The producer
uses bit-packed `GF(2)` words and a compiled `gf2rc.c` helper; mine uses dense
`int` arrays mod `p` and works at any `p`. The field polynomials my brute
instrument chose are its own (printed in every `#CELL` line) and differ from the
producer's — the count is model-independent, so agreement across two different
models of the same field is itself a check.

**I found and fixed two bugs in my own code before taking any result**: a wrong
reduction index in K-multiplication, and a stale-buffer read in the `p`-th-power
routine. Both were caught by the `p = 2`, `(n,n') = (4,3)` known-answer fixture
disagreeing with the archived hand counts. Every number below was produced after
both fixes, with that fixture passing. This is recorded because it is exactly
what a known-answer control is for.

Environment note (not an impediment to any result): `numpy` is absent and `pip
install` fails against the proxy, so the sweeps are C rather than Python.
Measured peak RSS of the largest cell **120.4 MiB** against the 4 GB
machine-protection cap; `p=3` sweep 20 s, `p=5` 78 s, `p=7` 569 s wall.
Randomness used anywhere in my work: the seeded `xorshift64` draws of the
K-coefficient arm (seed `20260917`, printed on every output line) and two
deterministic sampling strides (331, 4001) at the two `p=7` boundary cells that
are too large to enumerate. Everything else is exhaustive and seed-free.

---

## 3. Per-joint verdicts

### 3.1 J1 — the derivation of (A), and the `p != 2` sweep → **HOLDS**

**Coverage produced (`out/j1_grand_total.txt`, `out/j1_p{3,5,7}_sweep.txt`,
`out/j1_boundary.txt`, `out/j1_kcoef_oddp.txt`):**

| | value |
|---|---|
| distinct `(p, n, n', d)` rows | **203** over **64 cells** |
| distinct `F_p`-coefficient candidates, each through all available instruments | **291,997** |
| of which at **odd `p`** (`p = 3, 5, 7`), over **55** odd-`p` cells | **290,641** |
| K-coefficient draws at odd `p`, all with a coefficient outside `F_p` | **2,400** |
| candidates re-checked by the separate pure-Python injection route (overlapping the sweeps by design) | **6,980** |
| **violations of `N <= max(d^{q+1}, p^{n'-r})`** | **0** |
| **candidates with `deg D > max(d^{q+1}, p^{n'-r})`** | **0** |
| **candidates where the K-root set of `L` fails to divide `D`** | **0** |
| **brute-vs-gcd disagreements** | **0** |
| **injection-vs-gcd disagreements** | **0** |
| K-coefficient **injection failures** (a K-root of `L` with `D(x) != 0`) | **0** |

The plan's named cells — `(n,n') = (5,3), (7,3), (7,4), (11,4)` at `p = 3` and
`p = 5`, every `lambda` of degree 2..4 — are all covered, plus 20 further cells
at `p=3`, 11 further at `p=5`, and 11 cells at `p=7`. The assumption-free brute
instrument ran on **52 of 64 cells**; the 12 cells where `p^n` is too large
(listed in the outputs) carry the two algebraic instruments only, which is
stated rather than smoothed over.

**(a) The identity, and whether `D` is ever applied outside `K`.**
`(q+1)n' = qn' + n' = n + (n' - r)` verified as an identity on all **54,356**
pairs `(n, n')` with `2 <= n <= 139`, `2 <= n' <= 399`, `n'` not dividing `n`
(`out/j3_scope.txt`). The collapse
`x^{p^{n'(q+1)}} = (x^{p^n})^{p^{n'-r}} = x^{p^{n'-r}}` uses `x^{p^n} = x` and
therefore needs `x in K`; the Stage 0 note isolates this correctly and says so
("The step `x^{p^n} = x` is the **only** place `x in K` … is used"). Tracing
(A) and (B): `D` is applied only to K-roots; step (iv)'s "a nonzero polynomial
has at most `deg D` roots" counts roots in the closure, which over-counts in the
**safe** direction; (B) invokes (A) on a K-root set. **No step applies `D` to an
element outside `K`.**

That the injection is into the *right* set was also checked from the other side
(`out/j1_closure_check.txt`): on every candidate examined, `deg gcd(D, L) <
deg L` strictly — so `D` does **not** vanish on all closure-roots of `L`, i.e.
the restriction to `K` is load-bearing and the bound is not vacuous by
construction.

**(b) The equal-degree boundary (`out/j1_boundary.txt`).** Two things, and they
are different.

1. *The `max` form can never quietly become the `sum` form.*
   `deg(f - g) <= max(deg f, deg g)` is unconditional; cancellation can only make
   `deg D` **smaller**, which tightens (A). Nothing to measure, and I say so
   rather than dressing a triviality as a finding.
2. *What the boundary actually is.* `d^{q+1} = p^{n'-r}` forces `d = p^j` with
   `j(q+1) = n' - r` — **exactly the numerical precondition for degeneracy**.
   The equal-degree boundary and the degenerate branch are the same locus.
   Over **53,885** boundary candidates in **10** rows at `p = 2, 3, 5, 7`:
   - `deg D = max` (leading terms survive): **29,526**
   - `deg D < max` (leading terms cancel): **24,321**
   - `D = 0` (degenerate): **38**

   At `p = 3` the leading term *always* cancels: writing
   `a_{q+1} = c^{(d^{q+1}-1)/(d-1)}` for `lambda` over `F_p` with leading
   coefficient `c`, at `d = 3, q = 1` this is `c^4 = 1` for every `c in F_3^*`.
   At `p = 5` and `p = 7` it frequently survives. And at
   `(p, n, n', d) = (5, 4, 3, 5)` the bound is **attained at the boundary**
   (`N = 25 = max(25, 25)`), so the `max` form is exactly right there and cannot
   be sharpened.
   `D != 0` off the degenerate case held on **every** candidate: every `D = 0`
   case sits at the boundary and has the form `lambda = cX^{p^j} + b` with
   `c^{p^j+1} = 1` and `b(c+1) = 0`. Exhaustively measured per boundary cell:
   **2** at `p=2`, **4** at `p=3`, **6** at `p=5` — matching that closed form
   exactly. The two `p=7` boundary cells were enumerated with a deterministic
   stride (331, 4001) because exhaustive enumeration there is `6 * 7^7` and
   `6 * 7^7` candidates respectively; their 1-per-cell degenerate count is a
   SAMPLE, and the closed form predicts 8. SEE `out/j1_boundary_p7_exhaustive.txt`
   FOR THE EXHAUSTIVE `p=7`, `(4,3)`, `d=7` run settling it.

**(c) The `p != 2` sweep — the datum the program did not have.** 290,641
candidates at `p in {3, 5, 7}`, zero violations, three instruments agreeing
everywhere. The bound is **attained at odd `p`** — `(p,n,n') = (3,8,3)` with
`d = 2` gives `N = 8 = max(8, 3)`, and `(5,5,3)` with `d = 2` gives
`N = 5 = max(4, 5)` — which is a tightness datum for (C) at odd characteristic
that did not previously exist anywhere in the program.

Separately, the **coefficient twist at odd `p`** (`out/j1_kcoef_oddp.txt`): 24
cell-degree rows, 2,400 seeded draws, **all 2,400** with a coefficient outside
`F_p`, across `p = 3, 5, 7` and 10 cells. Zero violations, zero `deg D > bound`,
**zero injection failures** — i.e. every K-root of `L` found by brute
enumeration was verified directly to satisfy `D(x) = 0` with the non-trivial
twist taken. The bound is attained here too (`(3,5,3)` and `(3,7,4)` at `d = 2`).
Nothing in EXP-QSP-33b442 exercises a non-trivial twist at odd `p`; per
Stage 0 (i) that twist is "the only place the coefficient twist does any work",
so this closes a real hole.

**(d) The two Stage 0 hand cells at `(4,3)`, `p = 2` (`out/j1_stage0_43_gate.txt`).**
Both reproduce **exactly** on all three of my instruments:

```
lam = X^2+X+1   N = 1  Nbrute = 1  Ninj = 1  bound = 4  degD = 1  slack = 0
lam = X^3+1     N = 0  Nbrute = 0  Ninj = 0  bound = 9  degD = 9  slack = 2
```

matching `specification.yaml stage_0.numeric_gate` and the derivation note
(`N = 1` slack 0; `N = 0` with `D` having 2 K-roots, both failing the closing
test) line for line.

**Named breaking artifact NOT produced.** No tuple `(p, n, n', lambda)` with
`D != 0` and an independently re-verified K-root set larger than
`max(d^{q+1}, p^{n'-r})`; and no step of (A) applied to an element outside `K`.

---

### 3.2 J3 — the beta corollary → **HOLDS**, with a required narrowing

> **Read this caveat first.** One of J3's three named breaking artifacts **is**
> produced below (3.2a) — but against the **written quantifier of (E)**, not
> against the corollary. I return `holds` because the corollary's own antecedent
> (`N_K(L) = p^{n'}`) forces `n' < n`, so **no object can witness a false
> instance of the corollary itself**. The Coordinator should compose this as
> "true as stated, derivation gap in the record, one clause to fix", not as
> "clean".

**(b) All 65 M3 rows recomputed from `(n, n', d)` alone (`out/j3_m3_recompute.txt`).**
`beta`, `corollary_exact`, `corollary_conservative` and both differences depend
on `(n, n', d)` and **not on `N`**, so this check trusts no instrument. Exact
rational arithmetic (`fractions.Fraction`), not floats:

- rows recomputed: **65**; rows disagreeing with the archive on any of
  `q, r, beta, corollary_exact, corollary_conservative, beta_minus_exact,
  beta_minus_conservative, bound`: **0**
- `min(beta - exact) = 0` **exactly**; `min(beta - conservative) = 7/32 =
  0.21875` **exactly**. Both match the archived values.
- Complete-splitter cells and counts: `(7,3): 36, (7,4): 3, (31,5): 24,
  (31,6): 2` — 65 total, at exactly the four pre-registered cells.
- rows with `beta < exact` or `beta < conservative`: **0**. No F2 event.

**(c) The equality count — resolved, and both existing records are wrong.**

- **EXACTLY THREE** complete splitters attain `beta = exact`:
  `(7, 3, d=2)` `X^2 + X` and `X^2 + X + 1`, and `(7, 4, d=4)` `X^4 + X^2 + X`.
- `experiments/EXP-QSP-33b442/execution-report.yaml` says
  *"minimum beta - exact = 0.000000 (equality at two splitters)"* — **undercount
  by one; it is three.**
- `CORR-20260917-8b80cc` infers *"at least four distinct splitters at equality,
  not two"* — **overcount; it is three.** Its inference came from 8 literal
  `"beta_minus_exact": 0.0` occurrences in the file; those are **3** on
  complete splitters plus **5** on near-complete rows (the near-complete list
  contains the 3 complete ones plus two genuinely near-complete `(7,4,d=4,N=8)`
  rows). Its underlying reasoning — equality holds for *every* `d=2` splitter at
  `(7,3)` and *every* `d=4` splitter at `(7,4)` — is **correct**; what is wrong
  is attaching the per-**cell** counts 36 and 3 to those degrees. Per degree the
  counts are 2 and 1, giving 3.
- **Its classification is CONFIRMED**: a prose imprecision in a summary
  sentence, not a defect in a measured value. The metric (the minimum), all 65
  rows and both threshold columns reproduce exactly from `(n, n', d)`.

**(d) The weaken/reject split is decidable from the archive.** Both
`corollary_exact` and `corollary_conservative` are present and non-null on
**all 65** complete splitters **and all 356** near-complete rows; 0 missing.
A future F2 event would be decidable from the archived rows alone.

Worth recording because it shows the margin is *not* automatic: **3 of the 356
near-complete rows sit strictly below the exact corollary** —
`(7,4,d=3,N=8)` twice and `(7,5,d=4,N=16)` — and are not F2 events only because
they are not complete splitters. At `(7,4)` with `d=3` the bound is
`max(9, 2) = 9 < 16 = 2^{n'}`, so **(A) actively forbids a complete splitter
there**, and none is observed. That is (A) doing visible exclusion work rather
than being passively satisfied.

**(a) THE SCOPE — the required narrowing (`out/j3_scope.txt`, `out/j3_scope_witness.txt`).**

Decided over all 54,356 pairs `(n, n')` with `n'` not dividing `n`:

- `beta >= n/((q+1)n') = n/(n + n' - r)` is valid for **every** `n'`, including
  `q = 0`. The identity does not need `q >= 1`.
- The final step `n/(n + n' - r) > 1/2` is equivalent to `n + r > n'`. It holds
  for **18,614** pairs and **fails for 35,742**. Every failing pair has `q = 0`;
  every failing pair has `n' >= 2n`; equality (`= 1/2`) occurs exactly at
  `n' = 2n`. So: **`beta > 1/2` is derivable exactly when `q >= 1`, i.e. exactly
  when `n' < n`.**
- **Neither (B) nor (E) states `n' < n`.** (B) ends "*> 1/2, for every `n'` not
  dividing `n`*"; (E) says "*at any `p`, `n`, `n'`*". The Stage 0 note states the
  needed proviso and then drops it **in the same sentence**:

  > "And `n + n' - r < 2n` whenever `n' - r <= n' <= n`, so `beta > 1/2` for
  > every `n'` not dividing `n`. **Re-derives.**"
  > — `RUN-QSP-33b442-S0/derivation-note.md` (vi)

  The `whenever n' <= n` is asserted, not derived, and is then generalised past.
- **Why the conclusion survives anyway, by a step written nowhere in the record:**
  `N_K(L)` counts distinct roots **in `K`**, so `N_K(L) <= |K| = p^n`. (B)'s own
  hypothesis `N_K(L) = p^{n'}` therefore forces `p^{n'} <= p^n`, i.e. `n' <= n`;
  with `n'` not dividing `n`, `n' < n`, hence `q >= 1`. **Complete splitting at
  `n' > n` is impossible.** Independently, the QSP setting supplies the same
  thing from outside: Definition 3.1 of `KN-LIT-0a321c` requires
  `L | X^{q^n} - X`, so `deg L = q^{n'} <= q^n`.
- **The named breaking artifact, produced not described — against (E)'s wording.**
  `p = 2`, `n = 5`, `n' = 11` (`n'` does not divide `n`; `n' >= 2n = 10`),
  `lambda = X^2`. Then `V = {x in F_32 : x^{2^11} = lambda(x)}` is a factor base
  **of exactly the form (E) quantifies over**, and because `11 = 1 mod 5` we have
  `x^{2^11} = x^2` for every `x in F_32`, so `V = F_32` and `N = 32` — measured
  by brute enumeration over all 32 elements and by `deg gcd(X^{2^5}-X, L)`, in
  agreement, with the injection `G | D` verified. Its quality parameter is
  `beta = log_2(2) * 5 / 11^2 = 5/121 = 0.0413`, far **below** 1/2.
  Further witnesses in the same file: `(2, 3, 7)` `lambda = X^2`, `V = F_8`,
  `N = 8`, `beta = 3/49 = 0.061`; plus `(2,2,5)`, `(3,2,7)`, `(3,3,7)`.
  These objects satisfy (A) (e.g. `N = 32 <= max(2, 2^6) = 64`) and are **not**
  quasi-subfield polynomials (`|V| = 32 << 2^11`), so they do not touch (B).
  They touch only **(E)'s stated reason**: (E) asserts "no factor base of the
  form … at any `p`, `n`, `n'`" *because* "`beta > 1/2`", and `beta > 1/2` is
  false for these. (E)'s *conclusion* may well survive by a different route —
  such a `V` has `|V| <= p^n` and cannot deliver the QSP speedup — but that
  route is a cost-model question and belongs to **J6, not to me**.

**Required narrowing, stated so the Coordinator can act on it:** (B) and (E)
should carry `n' < n` explicitly, with the one-line reason
`N_K(L) <= |K| = p^n`, or (E) should be restricted from "factor base of the
form …" to "quasi-subfield polynomial in the sense of Definition 3.1".

---

### 3.3 J5 — the `n = 131` census's coverage claim → **BREAKS**

**Read the split before the verdict word: the ENUMERATION half holds exactly.
What breaks is the SCOPE half — the certificate count in the sentence this round
exists to evaluate.**

**(a) Re-enumerated from the definition (`out/j5_census_enum.txt`).** Built
independently from `specification.yaml stage_3.candidates`, never from the file:

```
sum_{d=3..7} 2^d = 248 = 8 + 16 + 32 + 64 + 128
linearized of exact degree 3..7 = 4   -> X^4, X^4+X, X^4+X^2, X^4+X^2+X
                                         (bits 16, 18, 20, 22; exponents all powers of two)
248 - 4 = 244 per cell, 732 rows in total
```

For **each** of `n' = 33, 44, 66`: 244 rows; set **equal** to my independently
derived set; **0** duplicates; **0** missing; **0** extra; **0** linearized
present; every `lambda_bits` in `[2^3, 2^8)`; per-exact-degree counts
`{3:8, 4:12, 5:32, 6:64, 7:128}` (the 12 at degree 4 being 16 − 4 linearized);
the row `d` field agrees with the bit degree on all 244.

**(b) Histograms rebuilt from the rows, not from the summary.** `n' = 33`:
`{0: 62, 1: 118, 2: 60, 132: 4}`. `n' = 44` and `n' = 66`:
`{0: 62, 1: 122, 2: 60}`. All three **agree with the archived `N_histogram`**
and sum to 244. `max N` from the rows agrees with the archived `max_N`
(132 / 2 / 2). Also recomputed from `(n, n', d)` on all 732 rows: `q`, `r`, and
`bound = max(d^{q+1}, 2^{n'-r})` — **0** disagreements; **0** rows with
`N > bound`; **0** rows flagged degenerate.

**(d) Affine marking.** 4 rows marked affine per cell — `X^4+1`, `X^4+X+1`,
`X^4+X^2+1`, `X^4+X^2+X+1` — and **0** mismatches against the definition on all
732 rows. The nearest-neighbour family is marked correctly.

**(c) THE SCOPE AUDIT — where it breaks.**

**Finding J5-1 (the breaking artifact).** The claim under review, quoted
verbatim from `specification.yaml success_criterion` and from
`review_plan.claim_under_review`, says:

> "… and **732 certificate-bearing exact counts at `n = 131`** …"

Measured from the archive:

| quantity | value |
|---|---|
| candidate rows `(lambda, n')` at `n = 131` | 732 |
| rows with `N > 0`, carrying `certificate_path` | **546** |
| rows with `N = 0`, `certificate_path: null` | **186** |
| certificate files on disk under `RUN-QSP-33b442-S3/certificates/` | **546** |
| `raw-result.json` `certificates_written` | **546** |

**732 exact counts were produced; 546 of them bear a certificate.** The headline
overstates its certificate-bearing counts by **186 (34%)**. The contract
contradicts itself here: its own `required_artifacts` defines the Stage 3
certificates as "one file per `n = 131` candidate **with `N > 0`**".

**Finding J5-2 (sharper, and it contradicts the run's own records).**
`RUN-QSP-33b442-S5/report.md` §7 restates it as:

> "… and **732 exact, independently re-verified counts** at `n = 131`, the
> largest of which is 132 against a ceiling of 2401."

"Independently re-verified" is a *defined operation* in this contract — the
wrapper evaluating `x^{2^{n'}} - lambda(x)` in `K` and asserting zero, plus
pairwise distinctness — and it was performed **546 times, on 546 root lists**.
It cannot be performed on an empty root list. This sentence contradicts
`execution-report.yaml` ("546/546 independently re-verified"), the Stage 5
report's own M4 section ("**546 certificates written (182 per cell), and all 546
independently re-verified**"), and `raw-result.json`. The 186 zero counts are
precisely the subset the certificate architecture cannot check at all.

**Finding J5-3 (softer; disclosed in situ, but wrong standing alone).**
`specification.yaml scale_relevance` — "certificates about exactly
`3 x 244 = 732` **named polynomials**"; `report.md` — "certify exactly the **732
enumerated lambda**"; `H-QSP-5540d7` — "certifies exactly `3 x 244`
polynomials". I verified that the three cells enumerate the **identical**
244-element set: there are **244 distinct `lambda`**, examined at three values of
`n'`, giving 732 rows (and 732 distinct `L = X^{2^{n'}} - lambda(X)`). Every
instance I found writes the `3 x 244` alongside, so a reader of the full clause
is not misled; "732 named polynomials" / "732 enumerated lambda" standing alone
is wrong.

**What is CLEAN, and should be said as plainly as the defects:**
- `execution-report.yaml` is **exact everywhere** on this: "732 of 732
  candidates, 546 certificates, 546 re-verified"; "546 certificates written and
  546/546 independently re-verified".
- The Stage 5 report's M4 section is exact (182 per cell, 546 total, per-cell
  table with an explicit `certificates` column, "Instrument I3 only").
- Both the report's scope paragraph and `H-QSP-5540d7`'s scope bullet correctly
  state that the census covers only non-linearized **`F_2`-coefficient** lambda
  of **exact degree 3..7**, and that *every other lambda in `F_{2^131}[X]` at
  those `n'` is covered by the derivation, not by a list*. The K-coefficient
  case at `n = 131` is correctly recorded as untouched.
- **No sentence anywhere lets "no violation at `n = 131`" do work the derivation
  should be doing.** The closure block says "numerically checked here, **not
  proved here**", and §7 says "What this run adds to the argument is
  certification and refutation-seeking, **not proof**". Searched specifically
  and found nothing; this was one of the two things J5(c) named and it is clean.

**The fix is small, and the defect is not:** the claim that would be promoted is
wrong by 186 in the direction that flatters it, and the wrongness is in the one
sentence the round exists to evaluate. Either the headline becomes "732 exact
counts at `n = 131`, 546 of them certificate-bearing", or the contract's
definition of "certificate-bearing" is widened to cover a zero count — and the
second would need an argument about what certifies a negative, which nothing in
this run supplies.

**Scope limit on this verdict, stated because it is easy to over-read:** J5 is
about *coverage, enumeration and scope*. **I did not verify any `n = 131`
count.** Whether `max N = 132` is right, and whether the four attaining
candidates are the right ones, is the blind re-derivation's question
(TASK-20260917-5fa7d5) and I say nothing about it.

---

## 4. `independent_recomputation` (required at this tier)

```yaml
independent_recomputation:
  recomputed_by_me_from_raw_artifacts_or_from_scratch:
    - what: M1 at all five Stage 1 cells
      result: 0.52 / 0.56 / 1.00 / 0.25 / 0.25 at (11,6)/(13,7)/(7,3)/(11,4)/(13,5)
      note: >-
        Regenerated the 1260 candidates and recounted from scratch with three
        instruments of my own; the producer's artifacts were not consulted for
        this at all. All three of my instruments agreed on all 1260.
    - what: the attainment tail at p = 2
      result: >-
        exactly TWO attaining candidates at (7,3) d=2 -- X^2+X and X^2+X+1, both
        N = 8 = bound -- and exactly ONE at (7,4) d=4, X^4+X^2+X, N = 16 = bound.
        This independently confirms the execution report's own note that the
        contract's tail check said "the d = 4 complete splitters" in the plural
        where there is exactly one.
    - what: all 65 M3 rows (beta, exact corollary, conservative corollary, both
            differences, q, r, bound) from (n, n', d) with exact rationals
      result: 0 disagreements; min(beta-exact) = 0 exactly; min(beta-conservative) = 7/32
    - what: the count of complete splitters attaining equality
      result: 3 (not 2 as the execution report says, not ">= 4" as CORR-20260917-8b80cc infers)
    - what: threshold completeness on 65 complete + 356 near-complete rows
      result: 0 missing
    - what: the n = 131 census candidate set, from the definition
      result: 244 per cell, set-equal, 0 duplicates / 0 missing / 0 linearized present
    - what: the three N-histograms, rebuilt from the 732 rows
      result: identical to the archived N_histogram in all three cells
    - what: affine marking, bound, q, r on all 732 rows
      result: 0 mismatches; 0 rows with N > bound
    - what: certificate accounting
      result: 546 rows with N > 0 and a certificate_path; 186 with N = 0 and null; 546 files on disk
    - what: the (4,3) Stage 0 hand counts
      result: N = 1 slack 0, and N = 0 slack 2 -- both exact
    - what: the identity (q+1)n' = n + (n'-r), and where n/(n+n'-r) > 1/2
      result: identity holds on 54,356 pairs; "> 1/2" fails on 35,742, all with q = 0, all with n' >= 2n
  re_verified_with_a_disjoint_checker:
    - what: (A) itself -- N <= max(d^{q+1}, p^{n'-r}), deg D <= max(...), D != 0
            off the degenerate case, and the injection step "every K-root of L is
            a root of D"
      checker: >-
        coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/code/
        {j1_fp_sweep.c, j1_kcoef.c, j1_closure_check.py}
      lineage: >-
        DISJOINT. Written from the statement of H-QSP-5540d7 (A). No file under
        experiments/EXP-QSP-33b442/implementation/ or analysis/qsp-ecc2k130/
        explore/ was read at any point in this task. Dense F_p[X] at arbitrary p
        versus the producer's bit-packed GF(2)[X]; different field polynomials;
        three mutually independent counting routes; X^{p^n} mod L computed by
        generic p-th powering rather than by the identity under test.
      scale: 291,997 distinct F_p-coefficient candidates (290,641 at odd p, over
             55 odd-p cells) + 2,400 K-coefficient draws at odd p + 6,980
             re-checked through a third route.  Totals are DEDUPLICATED: two rows
             were run twice and returned identical results.
      result: 0 violations, 0 deg-D excesses, 0 injection failures, 0 disagreements
  taken_on_the_producers_word_and_NOT_verified_by_me:
    - Every N at n = 131, including max N = 132 and the four attaining candidates.
      I verified the enumeration, the histogram's consistency with the rows, and
      the bound arithmetic -- NOT the counts. They pass through the producer's I3
      and nothing of mine. This is the blind re-derivation's question.
    - The contents of the 546 certificate files. I counted them and checked which
      rows point at one; I opened none.
    - Every Stage 2 N (the 42,244 counts), hence WHICH candidates are the 65
      complete splitters. My M3 recomputation is deliberately N-free -- beta and
      both thresholds depend only on (n, n', d) -- so the columns are verified
      without trusting any instrument, but the membership of the list is not.
    - Stage 1b (1200 K-coefficient draws) and Stage 4 (400 rational draws):
      not touched at all.
    - All manifests, seeds, timings, resource figures and environment records.
    - Whether the producer's I1/I2/I3 are independent of one another (J4).
  baseline_comparison:
    status: not_applicable_and_that_is_a_finding_in_itself
    reason: >-
      The tier requires a claimed speedup to be a measured ratio against a
      baseline reproduced in the same run. THE CLAIM UNDER REVIEW MAKES NO
      SPEEDUP CLAIM: the headline says in terms that it "proves nothing about any
      deployed curve, moves no attack exponent". There is therefore no ratio to
      reproduce and no `failed` on that count. The one place a comparison against
      a baseline appears at all -- M7's "2^117.7 against rho's 2^60.9" -- is
      declared ARITHMETIC ON (B), NOT MEASUREMENT, and belongs to J6. I did not
      evaluate it.
  cost_accounting_of_my_own_work:
    wall_clock: 'p=3 sweep 20 s; p=5 sweep 78 s; p=7 sweep 569 s; boundary, witness, K-coefficient and analysis runs seconds each'
    peak_rss_measured: '120.4 MiB (largest cell), against the 4 GB machine-protection cap'
    randomness: 'seeded xorshift64, seed 20260917, printed on every K-coefficient output line; deterministic strides 331 and 4001 at the two p=7 boundary cells too large to enumerate; everything else exhaustive and seed-free'
    success_probability: 'none: every quantity is an exact integer count of a finite set. No estimator, no oracle, no inverse-success-probability term anywhere in my joints.'
    unfinished: 'none. No run of mine timed out, crashed, or was abandoned.'
  falsifier_named_and_tested:
    - claim: (A)
      what_would_have_to_be_true_for_it_to_be_false: >-
        Since N_K(L) <= #{K-roots of D} <= deg D, (A) can fail only if (i) some
        K-root of L is NOT a root of D, or (ii) deg D > max(d^{q+1}, p^{n'-r}).
      tested: >-
        BOTH, directly and separately, rather than only the inequality:
        (i) by checking that the squarefree product of L's K-roots DIVIDES D on
        all 291,997 candidates, plus D(x) = 0 on every brute-found root in 2,400
        K-coefficient draws; (ii) by comparing deg D to the bound on all 291,997.
        0 failures of either kind.
    - claim: (B)
      what_would_have_to_be_true_for_it_to_be_false: >-
        A complete splitter (N = p^{n'}, r >= 1) with beta < n/(n + n' - r).
      tested: >-
        beta recomputed from (n, n', d) on all 65; and the only route to
        beta <= 1/2 is q = 0, which complete splitting makes impossible because
        N_K(L) <= p^n. No such object can exist.
    - claim: the census coverage
      what_would_have_to_be_true_for_it_to_be_false: >-
        A lambda in the declared set absent from the 244, a duplicate, a
        linearized lambda present, an affine mis-marking, a histogram mismatch,
        or a committed sentence asserting more certified objects than exist.
      tested: 'all six. The first five: clean. The sixth: FOUND (J5-1, J5-2).'
```

---

## 5. What I attacked and could NOT break

Stated because a failed attack named in advance is evidence and an unstated one
is not.

1. **A counterexample to (A) at odd `p`.** 290,641 odd-`p` candidates over 55
   cells at `p = 3, 5, 7`, every `lambda` of exact degree 2..4, three
   instruments. Zero violations. **Falsification branch F1 not reached at odd
   characteristic.**
2. **A failure of the injection step.** 0 in 291,997 (`G | D`), 0 in 6,980 by a
   separate pure-Python route, 0 in 2,400 K-coefficient draws with the
   non-trivial twist.
3. **`deg D > max(d^{q+1}, p^{n'-r})`.** 0 in 291,997, including 53,885 at the
   equal-degree boundary.
4. **Degrading the `max` form to the `sum` form at the boundary.** Impossible:
   `deg(f-g) <= max(deg f, deg g)` unconditionally. I exhibited both boundary
   behaviours and an attained case instead of asserting it.
5. **`D = 0` off the degenerate shape.** All 38 degenerate candidates I produced
   have the form `cX^{p^j} + b`, matching the closed-form count exactly.
6. **A step of (A) or (B) applying `D` outside `K`.** None; and `D` provably
   does *not* vanish on all closure-roots of `L`, so the K-restriction is real.
7. **An instrument disagreement among my own three routes.** Zero, on every
   candidate in every arm. (Two `(p,n,n',d)` rows were run twice by accident of
   my cell lists -- `(3,6,4,d=3)` and `(3,8,5,d=3)` -- and returned byte-identical
   summaries both times; a free determinism check, and the totals above are
   deduplicated so it is not double-counted.)
8. **A complete splitter below either corollary.** 0 of 65, recomputed with
   exact rationals.
9. **A recomputed M3 column disagreeing with the archive.** 0 of 65 rows × 8
   columns.
10. **An actual falsifier of (B) at `n' > n`.** None can exist: `N_K(L) <= p^n`
    makes complete splitting at `n' > n` impossible. My scope finding is about
    what the record *writes*, not about what is true.
11. **An enumeration defect in the `n = 131` census.** None: no missing lambda,
    no duplicate, no linearized present, no affine mis-marking, no histogram
    discrepancy, in any of the three cells.
12. **A sentence letting "no violation at `n = 131`" substitute for the
    derivation.** Searched specifically; none found. The artifacts are careful
    here.

---

## 6. Out-of-scope findings — **FLAGGED, NOT COVERAGE**

These bear on joints I do **not** own. I adjudicate none of them and the
Coordinator must not read them as review of those joints.

**OOS-1 (J2's joint).** My boundary sweeps produced the first `D = 0` candidates
anywhere in this program's evidence: **38** of them, at `p = 2, 3, 5, 7`, in
cells this experiment did not run. On every one, `N` attained **exactly**
`p^{n'-j}` and never `p^{n'}` — e.g. `p=3, (8,5), d=3, lambda = X^3` gives
`N = 81 = 3^4 = p^{n'-j}` with `j = 1`, against `p^{n'} = 243`. So a
degenerate-detection instrument has now returned true, 46 times, on code with no
shared lineage, and the characterisation held each time. Counts per boundary
cell -- 2 at `p=2`, 4 at `p=3`, 6 at `p=5`, 8 at `p=7` -- match the closed form
`#{(c,b) : c^{p^j+1} = 1, b(c+1) = 0}` exactly. **I do not adjudicate J2.**

**OOS-2 (J2's joint).** The equal-degree boundary `d^{q+1} = p^{n'-r}` and the
degeneracy precondition `d = p^j, j(q+1) = n'-r` are **the same condition**,
because `d^{q+1} = p^{n'-r}` already forces `d` to be a power of `p`. So "no cell
of this experiment can produce a degenerate candidate" and "no cell of this
experiment sits at the equal-degree boundary" are one statement, not two.

**OOS-3 (J4's joint).** I confirmed the datum I was given: exactly **10** of the
65 complete splitters carry `i3_run: false`, all at
`(n, n', d, N) = (31, 5, 8, 32)`. Read from
`RUN-QSP-33b442-S2B/raw-result.json`. **Not adjudicated.**

**OOS-4 (J4-adjacent).** My three instruments agreed on 291,997 + 2,400
candidates — but they are *mine*. That is evidence about the mathematics and
**no evidence at all** about whether the producer's I1/I2/I3 share a failure
mode.

**OOS-5 (proves-too-much control's joint).** At `(7,4)` with `d = 3` the bound is
`max(9, 2) = 9 < 16 = 2^{n'}`, so (A) **forbids** a complete splitter there, and
the largest observed is `N = 8`. A live instance of the argument excluding
rather than merely permitting. **Not adjudicated.**

**OOS-6 (schema classification, on which the plan requires me to opine).**
Nothing I saw in J1, J3 or J5 contradicts `CORR-20260917-8b80cc`'s
classification of its fifteen errors as record-schema defects with no
measurement touched. The measurement-bearing files I recomputed from — S2B's and
S3's `raw-result.json` and the three S3 cell files — are complete and internally
consistent on every column I checked. On the one substantive item routed to J3, I
**confirm the "prose imprecision" classification and correct the number to
three** (3.2c).

---

## 7. What I did NOT do

- **J2, J4, J6 and the proves-too-much control.** Not reviewed. No verdict.
- **No whole-claim verdict.** I can see three of six joints; a whole-claim
  verdict from here would be an opinion built from a fraction of the evidence.
- **No `n = 131` count verified.** I did not recompute any `N` at `n = 131`, did
  not open a certificate file, and did not check `max N = 132`.
- **No Stage 2 `N` verified.** My M3 work is deliberately `N`-free.
- **Stage 1b and Stage 4 not touched.**
- **H1, `kappa`, Rojas' 4.876, M7, Proposition 8: not evaluated.** J6's.
- **The producer's implementation was never read**, by design (J1(c)), so I
  cannot and do not comment on its correctness, structure, or instrument
  independence.
- **`analysis/qsp-ecc2k130/explore/**` never opened.** No value anywhere in this
  report came from it, and no agreement with it is claimed as corroboration.
- **No sibling report or task directory read.** See the attestation's
  sibling disclosure.
- **No ledger record, run artifact, manifest, measured value or hypothesis
  status changed.** Everything I wrote is under
  `coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/`.
  I committed nothing.
- **I did not re-litigate the fifteen schema errors**; see OOS-6.

---

## 8. Artifact paths (all absolute)

```
/home/user/crypto-autoresearcher/coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/
  report.md                        <- this file
  code/j1_fp_sweep.c               <- the p != 2 sweep, three instruments (dense F_p[X], any p)
  code/j1_kcoef.c                  <- the K-coefficient twist arm at odd p
  code/j1_closure_check.py         <- third, independent route for the injection step
  code/j3_recompute_m3.py          <- all 65 M3 rows from (n, n', d), exact rationals
  code/j3_scope.py                 <- where n/(n+n'-r) > 1/2 holds and where it fails
  code/j5_census_enum.py           <- census re-enumeration, histograms, affine marking
  code/summarize.py  code/run_oddp.sh  code/cells_p{3,5,7}.txt  code/dbg.c
  out/j1_p2_stage1.txt             <- independent recomputation of M1 (0.52/0.56/1.00/0.25/0.25)
  out/j1_stage0_43_gate.txt        <- the two (4,3) Stage 0 hand cells
  out/j1_p3_sweep.txt              <- 24 cells, 5,616 candidates
  out/j1_p5_sweep.txt              <- 15 cells, 46,500 candidates
  out/j1_p7_sweep.txt              <- 11 cells, 184,338 candidates
  out/j1_boundary.txt              <- 8 equal-degree-boundary cells, 53,827 candidates
  out/j1_kcoef_oddp.txt            <- 2,400 K-coefficient draws at odd p
  out/j1_closure_check.txt         <- 6,980 candidates, injection re-check
  out/j1_grand_total.txt           <- the roll-up (raw, before deduplication: 292,105 over 205 rows;
                                      deduplicated 291,997 over 203 rows -- two rows appear in two cell lists)
  out/j3_m3_recompute.txt          <- the 65-row table, recomputed
  out/j3_scope.txt                 <- the 54,356-pair scope decision
  out/j3_scope_witness.txt         <- the (E)-quantifier witness objects
  out/j5_census_enum.txt           <- the 244-per-cell re-enumeration
```

Rebuild: `gcc -O2 -o j1_fp_sweep j1_fp_sweep.c` (same for `j1_kcoef`), then
`./j1_fp_sweep p n nprime dmin dmax brute_limit [verbose] [stride]` and
`./j1_kcoef p n nprime dmin dmax ndraws seed`. Every sweep is exhaustive and
seed-free except the two strided `p=7` boundary cells and the seeded
K-coefficient arm, both parameterised on the command line and printed in the
output.

---

**Nothing in this report promotes anything.** A passed joint means the receipt is
admissible on that joint and nothing more; `H-QSP-5540d7` remains at
`status: specified` and closure remains a committed Coordinator decision naming
the criterion met.

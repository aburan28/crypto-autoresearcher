# Red-team review report — TASK-20260917-52b4e6

Round: claim-changing review of **EXP-QSP-33b442**, opened by the review plan in
`ledger/handoffs/TASK-20260917-43701b.yaml`.
Policy: `review-breakthrough`, `reasoning_effort: max`, independent session.
Branch `claude/ecc2k-130-quasi-subfield-poly-nhcj1f`, HEAD `2c1c4a34a`.

This report is **evidence for a Coordinator decision**. It approves nothing,
rejects nothing, closes nothing, and changes no ledger record. It reports on the
three joints assigned to this reviewer (J2, J4, J6) and the required
`proves_too_much` control, and on nothing else. **J1, J3 and J5 are owned by
another reviewer and are not reviewed here**; any observation touching them is
confined to the flagged out-of-scope section and must not be read as coverage.

---

## 1. `review_attestation`

```yaml
review_attestation:
  task_id: TASK-20260917-52b4e6
  joints_owned:
    - >-
      J2. THE DEGENERATE-CASE CHARACTERISATION, WHICH CARRIES THE WHOLE OF
      COROLLARY (B). The claim is that D = 0 forces d = p^j with
      j(q+1) = n'-r AND Lambda_{q+1} equal to the monomial Y^{p^{n'-r}},
      that the composition-equals-monomial argument then forces
      lambda = c X^{p^j} + b and L = M^{p^j} with deg M = p^{n'-j}, and
      hence that N_K(L) <= p^{n'-j} < p^{n'} so a degenerate L NEVER SPLITS
      COMPLETELY. (B) uses that last sentence as its first step: complete
      splitting implies non-degenerate implies p^{n'} <= max(d^{q+1},
      p^{n'-r}). If a degenerate L can split completely, (B) fails at step
      one.
    - >-
      J4. INSTRUMENT INDEPENDENCE AND THE DIRECTION OF VERIFICATION. M2 = 0
      over 1260 candidates is evidence ONLY IF I1, I2 and I3 do not share a
      failure mode; gf2rc.c and the bit-packed primitives of qspcore.py are
      shared. Separately: at n = 131 neither I1 nor I2 ran at all, so the
      732-candidate census rests on I3 alone, checked only by a root
      re-verifier that can detect a false root but not a missing one.
    - >-
      J6. THE CLOSURE READING (E) -- "under the cost model of Theorem 3.2 of
      KN-LIT-0a321c / Proposition 8 of KN-LIT-4fe9d2 (H1), no factor base of
      the form {x : x^{p^{n'}} = lambda(x)} with lambda polynomial and n'
      not dividing n beats generic algorithms, at any p, n, n'" -- which is
      conditional on the UNVALIDATED heuristic H1 and on Rojas' kappa =
      4.876, and which is the step by which a scoped derivation-tier bound
      could be overread as a closure of the QSP line.
    - proves_too_much          # the required control, both named object families
  sources_read:
    - ledger/handoffs/TASK-20260917-43701b.yaml
    - agents/red-team.md
    - agents/coordinator.md  (lines 119-180, "Target result profile and promotion gates")
    - AGENTS.md  (lines 165-200 rules 9-12; lines 573-690 "Review architecture", "Inter-agent messaging")
    - templates/research-records.md  (review_attestation block)
    - experiments/EXP-QSP-33b442/specification.yaml  (read in full)
    - experiments/EXP-QSP-33b442/execution-report.yaml  (protocol_deviations PD-1..PD-6; observations)
    - experiments/EXP-QSP-33b442/implementation/qspcore.py  (read in full)
    - experiments/EXP-QSP-33b442/implementation/gf2rc.c  (read in full)
    - experiments/EXP-QSP-33b442/implementation/stage1.py, stage1b.py, stage2.py, stage3.py, stage4.py  (instrument-dispatch lines and cell lists only; not read line by line)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S1/raw-result.json and cells/*.json (all 5)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S1B/cells/*.json (all 6, degenerate flags and row counts)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S2B/raw-result.json and cells/*.json (all 95)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/cells/n131_np33.json, n131_np44.json, n131_np66.json
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S5/report.md and metrics.json
    - ledger/hypotheses/H-QSP-5540d7.yaml  (read in full)
    - ledger/proposals/IDEA-20260916-b84e2d.yaml  (status and engine-impediment lines only)
    - knowledge/literature/KN-LIT-4fe9d2.md  (read in full)
    - inputs/EULER-PETIT-2019-QSP/paper_fulltext.md  (Proposition 7, Proposition 8, Remark 1, Section 4.4)
    - inputs/HUANG-2020-JMC-QSP/paper_fulltext.md  (Lemma 3.1, Appendix A.1, Appendix C.2 / Lemma C.2)
    - ledger/corrections/CORR-20260917-8b80cc.yaml  (PARTIAL: gate_verdict, the D1/D2 decomposition, the AMD-20260917-001 10-of-65 disclosure and the v2.yaml note; the remediation route was not read line by line)
  sources_NOT_read:
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/derivation-note.md
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/certificates/  (546 certificate files; not opened individually)
    - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S4/*
    - experiments/EXP-QSP-33b442/amendments/*  (AMD-20260917-001 known only through its citation in the plan and in S2B raw-result.json; the amendment file itself was NOT opened)
    - ledger/corrections/CORR-20260916-8d0b81.yaml
    - ledger/decisions/DEC-20260917-73c49a.yaml, ledger/questions/RQ-QSP-f9bbdb.yaml, ledger/proposals/IDEA-20260916-5c9d6e.yaml
    - knowledge/literature/KN-LIT-0a321c.md
    - analysis/qsp-ecc2k130/**  (declared CONTEXT ONLY; NOT opened at all, so no value in this report can have come from it)
  read_sibling_reports: false
  blind_from_respected: null      # not a re-derivation task
  verdict:                     # the plan's vocabulary: holds | breaks | inconclusive
    J2: holds
    J4: holds
    J6: breaks
    proves_too_much: holds
  verdict_notes:               # NOT a verdict; the four words above are the verdicts
    J2: >-
      HOLDS. No breaking artifact named in the plan was produced; the three
      attacks that would have produced one were built and run. The
      characterisation is exhaustive, the composition step survives in
      characteristic p, and the bound is exactly tight. BUT the measurement the
      joint is credited with does not exist: `degenerate_candidates: 0` is
      structural at every cell and the blocking instrument could not have fired
      on any of 45,436 candidates. Section 2; narrowing in section 6.
    J4: >-
      HOLDS. Neither named breaking artifact was produced, and both attacks were
      built: fault injection shows the agreement matrix is NOT measuring shared
      code, and 36 independent determinations at n = 131 -- 12 of them on census
      rows -- found no I3 undercount. BUT "three agreeing instruments" is two
      determinations over one shared primitive base at Stage 1 and ONE
      instrument at n = 131, and the certificate re-verifier shares those
      primitives too. Section 3; narrowing in section 6.
    J6: >-
      BREAKS. A breaking artifact named in the plan was produced (section 4.3):
      (E)'s exclusion of a cheap solver rests on kappa = 4.876, which both
      frozen sources give as an UPPER bound on the solver exponent, while the
      closure needs a LOWER bound; and H1's declared "rigorous ingredient" is
      contradicted by the cited appendix. Separately, promotion gate (2) is
      unsatisfied because H1 is unvalidated. (A) and (B) are untouched.
    proves_too_much: >-
      HOLDS. The declared failure signature is ABSENT on both named object
      families, over 73,076 exhaustive r = 0 candidates and 1,032 linearized
      complete splitters decided by Proposition 2 with no instrument of the
      experiment. Section 5.
```

The four words above are the verdicts, in the plan's vocabulary. **J2** and
**J4** are `holds` because no breaking artifact named in the plan was produced
for either and the attacks that would have produced one were built, run and are
reproducible from the artifacts listed in section 11. In each case the *claim
the experiment can support* is nevertheless strictly narrower than the headline
sentence, and section 6 states the narrowed form; a Coordinator composing this
round should carry the narrowing, not just the word. **J6** is `breaks`.

---

## 2. J2 — the degenerate-case characterisation

**Verdict: HOLDS (mathematics), with the measurement it is credited with
shown NOT TO EXIST.** No breaking artifact was produced. The three attacks the
plan names as candidate breaks were built and run and all three failed to break
the joint. What the attacks did establish is a sharp, structural narrowing.

### 2.1 The Coordinator's prior is CONFIRMED and STRENGTHENED — with its stated reason corrected

The plan states (prior item 1, and J2 attack step 0) that no cell of the
experiment can produce a degenerate candidate. **That is correct.** The task
card's stated reason — "every cell has `n'-r` equal to 1 or 2 against
`q+1 >= 2`" — is **not** correct, and the true reason is cleaner and much
stronger.

Artifact: `scratch/j2_cells.py`, `scratch/j2_structural.py`.

Many Stage-2 cells have `n'-r` far larger than 2: `(13,12)` has `n'-r = 11`,
`(23,11)` has `n'-r = 10`, `(31,15)` has `n'-r = 14`, `(17,15)` has `n'-r = 13`.
**The card's reason applies to only 39 of the 95 Stage-2 cells; on the other 56 it is false.** The correct
criterion is an identity:

```
n = q n' + r   =>   n' - r = (q+1) n' - n
```

(verified mechanically for every `1 <= n, n' <= 399`). Hence

```
j := (n'-r)/(q+1) is an integer   <=>   (q+1) | n,   and then   j = n' - n/(q+1).
```

**A cell can host a degenerate candidate only if `(q+1)` divides `n`.**
Every cell of EXP-QSP-33b442 has `n` PRIME with `2 <= n' < n`, which forces
`2 <= q+1 < n`, which forbids `(q+1) | n`. Verified for every prime `n < 200`
and every `2 <= n' < n`: no exceptions.

So `degenerate_candidates: 0` is **structural, not observed**, and it is
structural for a reason that holds at every cell at once rather than cell by
cell. The contract declares **111 cells** (95 Stage-2 + 5 Stage-1 + 6 Stage-1b +
3 Stage-3 + 2 Stage-4), spanning **98 distinct `(n, n')` pairs**; every one has
`n` prime with `2 <= n' < n`, and **none** satisfies `(q+1) | n`. Two further facts sharpen this:

- The instrument returned `False` on **45,436** candidates, not 3,192:
  1260 (S1) + 1200 (S1B) + **42,244 (S2B)** + 732 (S3), counted row by row from
  the archived per-cell JSONs. Stage 2 also carries a `degenerate_D_zero`
  column and it is `False` on all 42,244. Not one of the 45,436 could have been
  `True`.
- The contract contains **exactly two** (n, n') pairs anywhere at which a
  degenerate candidate exists, and it ran neither:
  - **(4, 3)** — the Stage 0 hand-gate cell. `q=1, r=1, j=1`, so `lambda = X^2`
    is degenerate there. The gate uses `X^2 + X + 1` and `X^3 + 1`.
  - **(12, 6)** — control C1, the one cell in the whole contract with composite
    `n`. `q=2, r=0, j=2`, so `lambda = X^4` is degenerate there. C1 uses
    `lambda = X`, `d = 1`.

  The single composite-`n` cell in the contract is also the single cell that
  could have fired the instrument, and the contract picks `d = 1` there.

### 2.2 The instrument was exercised and it FIRES (attack (d))

Artifact: `scratch/j2_construct.py`, `scratch/j2_construct_out.json`.

Degenerate instances were constructed deliberately by solving `(q+1) | n` and
setting `lambda = X^{2^j}`, then pushed through the producer's own code
unmodified (`qspcore.deg_D_and_degenerate`, `qspcore.i3_injection_f2`) at 26
(n, n') pairs spanning `r >= 1` and `r = 0`, `j = 1..5`, `d = 2..32`, including
C1's own cell (12, 6) and the hand-gate cell (4, 3). Field polynomials for the
`n` the contract omits were supplied in-memory and each was verified irreducible
by `qspcore.is_irreducible` before use; the committed implementation was not
edited.

Result on all 26: `D == 0` symbolically; `deg_D_and_degenerate` returns
`degenerate = True`; `i3_injection_f2` returns `{"degenerate": True}`;
`L == M^{2^j}` as an exact integer identity with `M = X^{2^{n'-j}} + X`; and the
exhaustive distinct-root count over `K` (written independently, using no gcd and
no factorisation) equals `I1` equals `I2` equals `2^{gcd(n'-j, n)}`.

**The instrument is not merely unfired — it works.** The plan's third breaking
artifact ("a demonstration that `degenerate_detection` as implemented cannot
return true on any input") is **NOT produced**: it can, and does.

Two edge cases the experiment never reached are handled correctly:
`deg D = 0` with `D != 0` (a nonzero constant difference polynomial — e.g.
`(6,3), lambda = X^2+1` and `(12,6), lambda = X^4+1`) yields `N <= 0` and the
measured `N = 0`; and `q = 0`.

### 2.3 The degenerate bound is TIGHT, and (B)'s first step survives with margin exactly `p^j`

Artifacts: `scratch/j2_construct.py`, `scratch/j2_degen_full.py`.

On all 26 constructed instances, `N = 2^{n'-j}` **exactly** — the degenerate
bound is attained, not merely satisfied. The reason is structural:
`n'-j = n/(q+1)`, which always divides `n`, so the root set of
`M = X^{2^{n'-j}} + X` is exactly `F_{2^{n'-j}} ⊆ K`.

The full degenerate family (not just `c = 1, b = 0`) was then enumerated
exhaustively over **all** `K`-coefficients at three cells — (4,3), (6,4), (6,5),
`K = F_16, F_64, F_64` — giving 20 + 72 + 72 = **164 degenerate `lambda`**.
Every one has `N` exactly `2^{n'-j}`, none splits completely, `I1` agrees with
the brute count on all 164, and `i3_injection_k` flags all 164 degenerate.

So (B)'s first step — "complete splitting implies non-degenerate" — is true, and
its margin is exactly one factor of `p^j`, i.e. a factor of `p` at `j = 1`. It
is not a comfortable margin; it is an exactly-attained one. Nothing in the
record overstates it, but nothing records it either.

### 2.4 The exclusion is an exclusion, not a gap (attack (c))

Artifact: `scratch/j2_exhaustive.py`.

- **F_2 coefficients:** every `lambda` of every degree 1..7 at 16 cells (4,064
  `lambda`), 16 hits with `D = 0`, and **every hit is of the claimed form
  `c X^{2^j} + b`**.
- **Full K coefficients:** every `lambda` of every degree 1..3 over `K` at
  (4,3) (65,520 `lambda`) and (6,4) (262,080 `lambda`). 20 and 72 hits
  respectively, and **every hit is of the claimed form**. No `lambda` outside
  the claimed shape has `D = 0`.
- The converse is strictly weaker and the record does not claim it: only 20 of
  240 shape-`cX^{2^j}+b` `lambda` at (4,3), and 72 of 4,032 at (6,4), are
  actually degenerate. The characterisation is one-directional, which is the
  direction (B) needs.
- `d` not a power of `p` precludes degeneracy: immediate from
  `deg Lambda_{q+1} = d^{q+1}` (the composition of polynomials multiplies
  degrees and the Frobenius coefficient twist is injective, so no leading
  coefficient can vanish), and confirmed on all 331,664 `lambda` above.

The case split `D != 0` / `D = 0` is exhaustive by construction. No third case.

### 2.5 The composition-equals-monomial step in characteristic p (attack (b))

Artifact: `scratch/j2_composition.py` -> `scratch/j2_comp_out.txt`.

**1,324,468 compositions** `f o g` were evaluated over `F_2, F_3, F_5, F_7,
F_4, F_9, F_8` for `deg g = 1..4`, `deg f = 1..4`, `deg(f o g) <= 6`.
**Zero counterexamples**: no `f o g` equal to a monomial with `g` outside the
form `c Y^e + b`.

Targeted at the maps the plan names, over `F_2, F_3, F_5`:
`g = Y^p` admits such `f` (and has the claimed shape); **`g = Y^p + Y` and
`g = Y^{p^2} + Y^p` admit NONE** for `deg f <= 3`. Inseparable `f = h(Y^p)`
produced no counterexample at either `p = 2` or `p = 3`.

The argument is also correct as a proof, and its hypotheses are met here.
Restated with the quantifiers explicit: let `f o g = Y^m` with `m >= 1` and
`deg g = e >= 1`. For any root `a` of `f` in the algebraic closure, `g - a` has
a root `x` (as `deg g >= 1`), so `f(g(x)) = 0 = x^m`, so `x = 0` and `a = g(0)`.
Hence `f` has the single root `a = g(0)`, `g - g(0)` has `0` as its only root so
`g = c Y^e + g(0)`, and `f = c'(Y - g(0))^{m/e}`. Nothing in that uses
characteristic 0, separability, or `gcd(e, p) = 1`. The hypotheses hold in the
application: `m = p^{n'-r} >= p >= 2` because `r < n'`, and `e = d >= 1`.

Two precision notes, neither a break:
- The record says "applied along the chain this forces `lambda = c X^{p^j} + b`".
  No chain induction is needed: `Lambda_{q+1} = Lambda_q^{(n')} o lambda` gives
  the conclusion about `lambda` in **one** application, with `f = Lambda_q^{(n')}`
  and `g = lambda`. The statement is right; the justification is longer than the
  proof.
- `c' = c^{p^{-j}}` and `b' = b^{p^{-j}}` require the `p^j`-th root to exist. It
  does, uniquely, because `K` is finite. The record says "over a field", which is
  too general for that step; over `F_p(t)` it would fail. Since the setting fixes
  `K = F_{p^n}`, this is a wording matter, not a defect.

### 2.6 What this joint costs the claim

Nothing in (A) or (B). It costs the **empirical** half of the headline exactly
this much: the sentence "1260 exhaustive toy candidates under three agreeing
instruments" is accompanied, in every cell record, by
`degenerate_candidates: 0`, and a reader is entitled to read that as a measured
absence. It is not one. Across 45,436 candidates the blocking instrument
`degenerate_detection` was structurally incapable of returning `True`, so the
`D = 0` exclusion that carries the whole of (B) was **never enforced by
measurement in this experiment** — it was enforced by arithmetic on `(q+1) | n`
that no committed artifact states.

The narrowing this joint requires is in section 6.

---

## 3. J4 — instrument independence and the direction of verification

**Verdict: HOLDS (the counts), with "three agreeing instruments" shown to be
overstated and the `n = 131` census shown to be single-instrument.** No breaking
artifact was produced. Two of the plan's three named breaking artifacts were
hunted with purpose-built experiments and **both attacks failed**, which is
evidence for the record and is reported as such; the third (a demonstrated
shared failure mode producing agreement without correctness) is answered
negatively by the fault injection.

### 3.1 The actual call graph (attack (a))

Artifact: `scratch/j4_callgraph.py` -> `scratch/j4_callgraph_out.txt` (static
`ast` analysis of the committed `qspcore.py`; nothing executed, nothing modified).

| routine | GF(2)[X] primitives reached |
|---|---|
| I1 `i1_brute_f2` (+ `_frob_table`, `_xpow_tables`, `_lam_table_f2`) | `clmul`, `deg`, `polymod`, `square` |
| I2 `i2_gcd_f2` | `clmul`, `deg`, `polymod`, `square`, `gcd`, `frob_power_mod_sparse`, `polymod_sparse_tail` |
| I3 `i3_injection_f2` | `clmul`, `deg`, `polymod`, `square`, `gcd`, `compose`, `iterate`, `frob_power_mod`, `ddf_factor`, `_edf`, `polydivmod`, `K.mul`, `K.sq`, `kp_*` |
| `verify_roots_f2` | `K.eval_f2poly`, `K.pow2k` — which are `polymod(clmul(...))` and `polymod(square(...))` |

- **Shared by all three: `clmul`, `deg`, `polymod`, `square`.**
- **Shared by I2 and I3 and not I1: `gcd`.**
- **I1 has NO primitive of its own.** Its entire primitive set is a *subset* of
  I2's and of I3's. The plan's prior — "the real independence in Stage 1 is
  two-fold, I1 against the shared gcd path" — is right about `gcd` and
  understates the rest: I1 is independent of the `gcd`/factorisation layer and
  of nothing below it.
- **The certificate re-verifier is not primitive-independent either.**
  `qspcore.verify_roots_f2`'s own docstring says it *"shares no code path with
  the injection count that produced the list"*. That is true of the counting
  **algorithm** and false of the **arithmetic**: `K.pow2k` is
  `polymod(square(a), mod)` iterated and `K.eval_f2poly` is `polymod(clmul(...))`
  by Horner, so the re-verifier bottoms out on the same `square`, `polymod` and
  `clmul` as everything else. A fault in any of those three corrupts the count
  **and** its certificate check together. This is not stated anywhere in the run
  package and it is the sharpest thing in this joint.

**And the genuinely independent implementation did not participate.**
`gf2rc.c` is a separate C implementation with its own word-level arithmetic,
sharing nothing with the Python package — the strongest independence in the
repository. `stage1.py` dispatches
`I2 = gf2rc(...) if npr >= 10 else i2_gcd_f2(...)`, and every Stage-1 cell has
`n' in {3, 4, 5, 6, 7}`. **So the C helper produced none of the 1260
agreements.** Confirmed against the archive: all 1260 Stage-1 rows carry
`instruments_run = [I1, I2, I3]` and the `I2_implementation` field is **absent**
from every one of them (it is recorded only on the four forced-fixture rows,
where C1 at (12,6) reads `"qspcore.i2_gcd_f2 (Python)"`).

**Honest count of independent determinations of N:**
Stage 1 — **two** (I1 against the `gcd`/factorisation layer), over one shared
primitive base. Stage 1b — two (I2/I3 over `K[Y]`), one where I1 also ran.
Stage 2 — I2 is the C helper `gf2rc` here, so where I3 also ran (342 of 42,244)
there are genuinely **two implementations**, and where I1 also ran (10,444,
`n <= 13`) there are three; on the **10 complete splitters at (31,5,d=8)**,
**one**. Stage 3 at `n = 131` — **one**, plus a one-directional re-verifier that
shares its primitives.

### 3.2 FAULT INJECTION (attack (b)) — the attack the plan expected to succeed, and it FAILED

Every fault was applied to a **scratch copy**
(`scratch/faultcopy/qspcore_base.py`, sha256 verified identical to the committed
file before any edit). `experiments/EXP-QSP-33b442/implementation/` was never
written to. Each fault ran in its own subprocess under a hard 300 s external
timeout, so a fault that hangs is recorded as an infrastructure outcome and
never as agreement. Sample: the (7,3) and (11,4) Stage-1 cells, every `lambda`
of degree 2..5 — **120 candidates**, against an unfaulted baseline of
`M2 = (0, 0, 0)` on the same 120.

| fault (on the scratch copy) | which instruments reach it | result on 120 candidates |
|---|---|---|
| **baseline (unfaulted)** | — | `M2 = (0, 0, 0)`, 0 errors |
| **F-a** `square()`: drop the top spread mask | I1, I2, I3 | **module will not load** — `KField.__init__`'s `assert is_irreducible(self.mod)` fails |
| **F-b** `polymod()`: stop one degree early | I1, I2, I3 | **non-terminating** — `KField(7)` never returns (observed, 60 s, exit 124) |
| **F-c** `clmul()`: drop the top set bit of the sparser operand | I1, I2, I3 | **87 of 120 counts changed; `M2 = (75, 73, 43)` — AGREEMENT BREAKS** |
| **F-d** `gcd()`: "swap one step early" | I2, I3 (not I1) | 0 changed, `M2 = (0,0,0)` — **this is not a fault**: the rewrite is semantically identical to the original Euclid. Retained as the NEGATIVE CONTROL. |
| **F-e** `polymod_sparse_tail()`: corrupt the tail | **I2 only** | 92 changed; `M2 = (92, 0, 92)` — **I2 disagrees with both, I1 and I3 still agree: the matrix LOCALISES the fault** |
| **F-f** `frob_power_mod()`: seed `X+1` instead of `X` | **I3 only** | **non-terminating within 300 s** (`_edf`'s splitting loop never succeeds) |
| **F-g** `_frob_table()`: one Frobenius too few | **I1 only** | 17 changed; `M2 = (17, 17, 0)` — **I1 disagrees with both, I2 and I3 still agree** |
| **G-a** `square()`: corrupt only when `deg > 40` (invisible to the `n <= 13` field-polynomial check) | I1, I2, I3 | **crash** — `ddf_factor`'s `assert deg(rest) <= 0` fails: *"unfactored remainder of degree 2"* |
| **G-b** `polymod()`: corrupt only when `deg m > 40` | I1, I2, I3 | **crash** — same assert, same message |
| **G-d** `gcd()`: corrupt only when both operands have `deg > 60` | I2, I3 (not I1) | **crash** — same assert, same message |


**Reading.**

- **A single injected fault in a SHARED primitive DOES break the agreement
  matrix.** `F-c` corrupts `clmul`, which all three instruments use, and the
  matrix goes from `(0,0,0)` to `(75,73,43)` with 87 of 120 counts changed. The
  plan's hypothesis — "if a single injected fault leaves the agreement matrix
  clean, the matrix is measuring shared code, not agreement" — **is tested and
  the antecedent does not hold**. The agreement matrix is doing real work.
- **The matrix also LOCALISES.** `F-e` corrupts `polymod_sparse_tail`, reached
  only from I2: the result is `I1 vs I2 = 92`, `I2 vs I3 = 92`, `I1 vs I3 = 0`.
  The pattern names the faulty instrument. Similarly for the I3-only and
  I1-only faults.
- **Two shared-primitive faults are caught earlier, by the package's own
  self-check, as a crash or a hang rather than as a false agreement.** `F-a`
  (drop the top mask in `square`) makes `KField.__init__`'s
  `assert is_irreducible(self.mod)` fail on import. `F-b` (`polymod` stops one
  degree early) makes that same self-check **not terminate**: observed directly
  in `scratch/probe_fb.py` — the module imports, prints, and then `KField(7)`
  never returns within 60 s wall clock (exit 124). That is an infrastructure
  outcome and is reported as one, never as negative evidence; what it shows is
  that the declared field polynomial's irreducibility check is an unintended but
  real tripwire on the two most basic primitives.
- **`F-d` is not a fault.** `while b: a, b = b, polymod(a, b)` is exactly the
  original Euclid rewritten; `changed = 0` is the correct answer and this row
  serves as the **negative control** showing the harness does not manufacture
  disagreements. It is reported rather than deleted, because a fault-injection
  experiment with no null is worth as little as any other.

**Conclusion on (b): the plan's second breaking artifact ("an injected
single-point fault that leaves M2 = 0") was hunted with eight faults across
every shared and unshared primitive, and NOT FOUND.** `M2 = 0` is not an
artifact of shared code. The residual exposure is real but narrower than the
prior supposed: it is not that a fault would go unnoticed, it is that **the
certificate re-verifier shares `square`, `polymod` and `clmul` with the counting
instruments** (section 3.1), so a fault subtle enough to survive the
irreducibility tripwire and to corrupt count and verification *consistently* is
the one shape this architecture cannot see. The fault that would test that
directly — one active only at degrees above the toy range, so it corrupts the
`n = 131` census while leaving the `n <= 13` cells clean — is `G-a`/`G-b` in the
table, and their results are the entry that matters most.

### 3.3 THE VERIFICATION ASYMMETRY AT n = 131 (attack (c)) — the second attack that FAILED, and it produced the census's first independent check

Artifact: `scratch/j4_n131.py` -> `scratch/j4_n131_out.txt`,
`scratch/j4_n131_out.json`.

The plan is right about the asymmetry. `verify_roots_f2` confirms that every
listed `x` satisfies `x^{2^{n'}} = lambda(x)` and that the list is duplicate-free.
It cannot see a root I3 never found, and a missed root **lowers** `N`, which is
the direction that makes `N <= bound` hold. Confirmed by reading: at
`n' = 33, 44, 66` the 62 candidates per cell with `N = 0` carry
`root_verification: None` — there is nothing to verify, so a systematic
under-count to zero would be reported as a clean result.

The plan then asks for the one independent determination available at the target
field. This reviewer built **two**, and extended the test beyond what the plan
asked:

- **R1 — Proposition 2 of KN-LIT-4fe9d2**, via `qspcore.c6_linearized_N`, on
  linearized `lambda` (which the census excludes).
- **R2 — LINEAR ALGEBRA, written from scratch in the review script and sharing
  no line with `qspcore`.** For linearized or **affine** `lambda`,
  `x -> x^{2^{n'}} + lin(x)` is `F_2`-linear on `K = F_2^131`; build its
  131x131 matrix from the images of `z^0..z^130` using an independently written
  `fsq`/`fmod`/`fmul`, and take the kernel dimension by Gaussian elimination,
  solving the inhomogeneous system when the constant term is 1.

R2 reaches the **four AFFINE candidates per cell that are INSIDE the census**
(exact degree 4, `X^4 + aX^2 + bX + 1`), so this is an independent determination
on **real census rows**, not only on the excluded slice.

**Result: 36 determinations at `n = 131` — 24 linearized (outside the census,
over `n' = 33, 44, 66`, `d = 2..128`) and 12 affine (INSIDE the census) — and
`linalg N == C6 N == I3 N` on every single one. Zero disagreements.**
All 12 affine values match the archived census rows
(`RUN-QSP-33b442-S3/cells/n131_np{33,44,66}.json`, `lambda_bits` 17, 19, 21, 23)
exactly: `N = 0, 1, 1, 0` at each of the three cells. The `affine` column is
populated, is `True` on exactly those four rows per cell, and is correct.

**The plan's first named breaking artifact — "an `n = 131` candidate where I3's
count disagrees with an independent decision procedure" — was hunted at the
target field with a procedure the experiment never used, and NOT FOUND.** The
Coordinator's 0.08 on an I3 undercount is, on this evidence, not realised.

What this does *not* do, stated plainly: linear algebra decides only the
linearized and affine slice. **720 of the 732 census rows (98.4%) remain
single-instrument**, because for a non-linearized, non-affine `lambda` the map
is not additive and no independent decision procedure was available to this
reviewer at `n = 131`. The census's exposure is reduced from *complete* to
*98.4%*, and the 1.6% that was checked came back clean.

### 3.4 The amendment's real cost (attack (d)) — verified independently

Verified from `RUN-QSP-33b442-S2B/raw-result.json` directly, not from the
amendment record (which this reviewer did not open):

- `I3_skipped_above_cap.count = 14`, `cap = 1000000`, `amendment =
  AMD-20260917-001`.
- Of the 65 rows of `M3_complete_splitters`, **exactly 10 carry
  `i3_run: false`** with `i3_skip_reason: "deg_D_above_declared_cap"`, and all
  10 are at `(n, n', d) = (31, 5, 8)` with `N = 32`, `deg D = 2097152`.
- On those 10, `I1` is `null` (n = 31 > the `I1_MAX_N = 13` affordability
  bound) and `I3` is `null`. **`I2` alone.** They are the only 10 of the 65
  with a single non-null instrument; 55 have two or more.
- The other 4 capped candidates are at `(29,2,d=3)` and `(31,2,d=3)` with
  `N = 2 < 2^{n'} = 4`, so they are not complete splitters.

**Is an I2-only determination of completeness sound at those rows?** For the
purpose it serves, yes, and for three independent reasons this reviewer checked:

1. At Stage 2, `I2` is the **C helper `gf2rc`**, not the Python routine — the
   one implementation in the package that shares nothing with `qspcore`. So
   "I2 alone" at (31,5) is *not* the same weakness as "I2 alone" would be in
   Stage 1.
2. `beta` depends on `(n, n', d)` **only, never on `N`**. If `N` at those rows
   were wrong, the row would not belong in M3, and removing a satisfied
   constraint cannot turn (B) from satisfied into violated. The margin there is
   `beta - exact = 3.72 - 0.8857 = 2.834`, the largest in the table.
3. The dangerous direction is a splitter **missed**, not one wrongly included —
   and `I2` ran on **all 42,244** candidates, so the cap cannot have hidden one.
   The cap costs corroboration, not coverage.

The residual is narrow and worth recording: those 10 rows are the only place in
M3 where completeness rests on one implementation, and `gf2rc`'s own self-test
(`stage2.py helper_self_test`) cross-checks it against `qspcore.i2_gcd_f2` on
only 200 small candidates, none at `(31, 5)`.

### 3.5 PD-6 (attack (e)) — what the determinism cross-check establishes

Verified independently from the two run directories: **54** S2 checkpoint cells
have an S2B counterpart, **23,176** candidates are common to both, and **0** have
a differing `N`. The execution report's characterisation is exactly right and
this reviewer endorses it: *"That comparison is a determinism check on the I2
code path; it is NOT a result."*

Three limits to add, none of which the report gets wrong, all of which a
composition should carry:

- It is the **same binary on the same host**, so it establishes neither
  implementation independence nor correctness, and not even reproducibility
  across compilers or machines.
- It covers **23,176 of 42,244 candidates (54.9%)**. The 41 S2B cells with no
  S2 counterpart carry 19,068 candidates with no cross-invocation check at all.
- It touches only `I2`. `I1` and `I3` were not re-run.

Against AGENTS.md's own rule that a surprising or high-impact result gets
`replicate` on first observation, a determinism check is not a replication and
the record does not claim it is.

### 3.6 Two checks the run could have made for free, one of which this reviewer ran

**(i) The independent C implementation agrees on all 1260 Stage-1 candidates.**
Artifact: `scratch/j4_c_vs_python.py` -> `scratch/j4_c_vs_python_out.txt`. `gf2rc.c` was compiled from the scratch
copy and fed all 1260 archived Stage-1 candidates (`n`, `n'`, `lambda_bits`
read out of `RUN-QSP-33b442-S1/cells/*.json`).

> **1260 of 1260 agree with all three archived Python instruments. 0
> disagreements. 0 rejected inputs.**

This is the strongest independence available in the repository — a separate
implementation in a different language with its own word-level GF(2)[X]
arithmetic — and the run left it on the table because of a threshold
(`n' >= 10`) chosen for speed, not for independence. Running it costs seconds.
With it, Stage 1 rests on **four** determinations, one of them genuinely
implementation-independent, instead of three that share `square`, `polymod` and
`clmul`.

**(ii) The package has internal algebraic tripwires, and they are load-bearing
at `n = 131` where nothing else is.** The G-series faults were *designed* to
slip past the `n <= 13` field-polynomial check, and all three were caught
anyway, by `ddf_factor`'s `assert deg(rest) <= 0` — a real invariant (after
distinct-degree factorisation nothing may remain). A third tripwire,
`assert len(rs) == deg(hf)` in `i3_injection_f2(want_roots=True)`, runs on every
Stage-3 certificate. So the `n = 131` census is not *bare* single-instrument: a
corrupted shared primitive has to leave three algebraic invariants intact as
well as agreeing with the re-verifier. That is not a second instrument and must
not be reported as one, but it is a real mitigation and **it is stated nowhere
in the run package**.

### 3.7 What this joint costs the claim

The counts survive. The **description** of how they were obtained does not:

- "**three agreeing instruments**" (specification success criterion, quoted
  verbatim in the headline under review) is, at Stage 1, three routines over one
  shared primitive base — two independent determinations at the algorithmic
  level, one at the primitive level. The independent implementation contributed
  nothing to it.
- "**732 certificate-bearing exact counts at n = 131**" is 732 counts from one
  instrument, with certificates that can falsify a listed root and cannot detect
  a missing one, re-verified by code that shares the same three primitives. 12
  of the 732 now have an independent determination and it agrees.
- On **10 of the 65** complete splitters, completeness rests on one
  implementation (`gf2rc`, which is at least the independent one).
- PD-6's substitute is a determinism check on **one** instrument over **54.9%**
  of Stage 2, same binary, same host.

None of that is a break, and the fault injection shows the agreement matrix is
measuring agreement rather than shared code. It is a narrowing of what the
sentence means.

---

## 4. J6 — the closure reading (E)

**Verdict: BREAKS.** A breaking artifact named in the plan is produced in
section 4.3: *a stated cost model whose exponent is not excluded by H1's formal
statement*, together with the demonstration that the number (E) invokes to
exclude it (Rojas' `kappa = 4.876`) is an **upper** bound on that exponent in
its own source and therefore cannot exclude anything. (E) must not move toward
`supported` on this evidence, and on this reviewer's reading it cannot move on
any evidence until H1 is validated.

Nothing in this section bears on (A) or (B), which are unconditional and are
attacked elsewhere in this round.

### 4.1 The promotion gate is not satisfied, and a blocked route is not the reason (attack (a))

`agents/coordinator.md` gate (2): *"Every conditional dependence is an explicit,
numbered, formally stated heuristic, each backed by archived validation evidence
or a scheduled validation experiment. **An unvalidated heuristic caps the claim
below `supported`.**"*

H1 is explicit, numbered and formally stated — that half is satisfied and is
better than most records manage. The rest is not:

1. `H-QSP-5540d7` `heuristic_assumptions[H1].validation_experiment_ids: []`.
   The machine-readable field is empty.
2. The route `IDEA-20260916-b84e2d` is a **proposal at `status: proposed`**, not
   an experiment. The hypothesis itself calls it "scheduled, **not yet
   designed**". A proposal that has not been designed into a frozen contract is
   not "a scheduled validation experiment" in the sense gate (2) uses, and the
   `EXP-*` id that would make it one does not exist.
3. The route is additionally blocked: no Groebner or resultant engine in the
   container, re-confirmed by this run's own `environment.json`
   (`sage`, `magma`, `macaulay2`, `singular`, `msolve`, `ntl_or_flint` all
   absent), as the Stage 5 report states at its forward-guidance item 4.

**The ruling this reviewer gives is narrower than "a blocked route does not
discharge gate (2)", and does not need that ruling.** Gate (2)'s own last
sentence is unconditional: an *unvalidated* heuristic caps the claim below
`supported`. A scheduled experiment does not validate anything — only its
archived evidence does. So (E) is capped below `supported` on the plain text of
the gate whether the route is blocked, unblocked, designed or undesigned. The
blockage matters for *scheduling*, not for the gate.

This agrees with the contract's own `heuristic_under_test_note` and with the
Stage 5 report, both of which say (E) stays conditional whatever the experiment
returns. **The record does not overclaim here.** The finding is that the
promotion gate is not satisfied, not that anyone said it was.

### 4.2 The robustness of the constant: (E) has almost no margin over its own assumption (attack (b))

Artifact: `scratch/j6_kappa.py` -> `scratch/j6_kappa_out.txt`.

The plan's recomputation is correct, and the exact figures are:

| quantity | exact value | decimal |
|---|---|---|
| smallest `beta` over `n' = 2..130` at `n = 131` | `131/260` at `n' = 130` (`q=1, r=1`) | 0.5038462 |
| `kappa` threshold for `alpha_beta > 1` at that `beta` | `1/(2 beta) = 260/262 = 130/131` | 0.9923664 |
| largest `beta` | `131/132` at `n' = 2` | 0.9924242 |

So **the closure needs only `kappa >= 130/131 = 0.9924`, not 4.876.** In
general, the worst case is `n' = n-1` (`q = 1, r = 1`), where
`beta >= n/(2n-2)` and the threshold is exactly `(n-1)/n`:
0.857 at `n = 7`, 0.968 at `n = 31`, 0.9924 at `n = 131`, 0.9961 at `n = 257`,
and `-> 1` as `n -> infinity`.

The plan asks what this does to the strength of the closure. It cuts two ways
and the record should say which claim uses which:

- **It strengthens the qualitative closure.** "No QSP factor base beats generic"
  survives any `kappa >= 1`, five times weaker than 4.876. To this reviewer's
  reading that is the *right* form of (E) and the record should lead with it.
- **It leaves the quantitative table entirely dependent on 4.876.** M7's
  `exponent >= 0.898`, `>= 2^117.67`, "56.77 bits above rho" are obtained *only*
  at `kappa = 4.876`; at `kappa = 1` the same rows give
  `alpha_beta = 1/(2 beta)` and a far smaller separation. The record does not
  separate these two claims, and `H-QSP-5540d7` (E) states the qualitative
  closure and the 2^117.7 figure in the same breath.
- **And it shows the margin is nearly nothing.** H1's own formal statement
  assumes "`kappa >= 1`". (E) needs `kappa >= (n-1)/n`. **The entire robustness
  of (E) beyond its own assumption is `1/n` — 0.76% at `n = 131`, and zero in
  the limit.** (E) is, to within `1/n`, a restatement of H1 plus (B). The
  rhetoric "five times below Rojas' 4.876" describes a safety factor that does
  not exist in the parameter the closure actually depends on.

In fairness to the record: the weaker sufficient condition IS stated in
`H-QSP-5540d7`, under M7's `minimum_effect` — *"alpha_beta > 1 at beta = 0.504
would need kappa < 0.992"*. It is present and correct. It is the (E) statement
prose that carries the 4.876 comparison.

### 4.3 THE BREAKING ARTIFACT: 4.876 is an upper bound and cannot exclude a cheap solver

The plan's first named breaking artifact for J6 is *"a stated cost model or
solver with `kappa < 0.992` not excluded by H1's formal statement"*. This
reviewer produces something stronger: **the citation (E) uses to exclude such a
solver constrains `kappa` in the opposite direction.**

From the frozen source texts:

- `inputs/HUANG-2020-JMC-QSP/paper_fulltext.md`, Lemma 3.1: the eliminant and
  its parametrisations *"can be found in `Õ(m^5.188 (3d)^{4.876 m^2})` arithmetic
  steps"*. That is an **upper** bound on the solver's cost.
- `inputs/EULER-PETIT-2019-QSP/paper_fulltext.md`, Proposition 7: *"where `kappa`
  is a constant involved in the cost of the resolution of the system S
  **currently majored by 4.876**"*. "Majored by" = bounded above by. So
  `kappa <= 4.876`.

(E) needs the opposite. A QSP factor base beats generic iff `alpha_beta > 1` iff
`kappa < 1/(2 beta)`, i.e. iff the solver is **cheap**. Excluding that requires a
**lower** bound `kappa >= 1/(2 beta)`. Knowing that a cost is *at most*
`2^{4.876 m^2}` says nothing whatever about whether it is *at least* `2^{m^2}`.
The sentence in (E) — *"the required beta < 1/(2 kappa) is unreachable because
beta > 1/2 forces kappa < 1, five times below Rojas' 4.876"* — invokes a ceiling
as though it were a floor.

The same directional weakness sits inside H1's `random_model_justification`.
Its declared **rigorous** ingredient is: *"the univariate eliminant h of Lemma
3.1 of KN-LIT-0a321c **has degree M(E)** ... and root-finding a polynomial of
degree M(E) costs **at least** M(E) operations."* The frozen source says
something different and weaker, twice over, in Appendix A.1:

> *"The univariate polynomials produced by Rojas' algorithm are of degree
> **bounded by** M(E). Over finite fields, root-finding is quasi-linear in this
> degree, and **its cost can be neglected in the overall complexity
> estimation**."*

Two deltas, both in the load-bearing direction:
1. "degree **bounded by** M(E)" is an upper bound; H1 reads it as an equality
   ("has degree M(E)") and then as a lower bound on cost. The step that would
   license the equality is precisely the **generic-attainment / BKK statement
   that H1 itself marks `RECALLED` and describes as supporting "nothing by
   itself"** — and AGENTS.md rule 9 forbids a `recalled` reference from
   discharging a heuristic's `supporting_results`.
2. The cited text says the root-finding cost **can be neglected**. H1 uses that
   very quantity as its lower bound on the per-attempt cost.

**Net: after removing the `recalled` ingredient as rule 9 requires, H1 has no
retrieved support for the direction it is used in.** It is a bare heuristic —
which is what `heuristic_assumptions` is for, and H1's `formal_statement` and
`falsification_condition` are both correctly written as a heuristic and name
exactly the right test ("a solver whose cost does not grow like
`d^{m(m-1)/2}`"). The defect is in `random_model_justification`, which labels as
"Rigorous ingredient" something the source does not say, and in (E)'s prose,
which presents a ceiling as a safety factor.

**The concrete solver that breaks (E) and is not excluded by H1's formal
statement:** any eliminant-solving method whose cost grows like `d^{c m^2}` with
`c < (n-1)/n`. H-QSP-5540d7's own `assumptions` block already concedes the
extreme case — *"A solver model in which the cost does not grow with d is not
excluded by (E)"* — and at `n = 131` the excluded band is only
`kappa in [0.9924, 1)` wide beyond H1's own floor. A *linear-time* eliminant
solver sits at `kappa = 1`, inside (E) at finite `n` by `1/n` and outside it in
the limit. No argument in the record excludes `kappa < 1`; only a citation does,
and that citation points the other way.

### 4.4 What did NOT break: the M7 fence, and the integer-`m` instantiation

Two of the plan's other named breaking artifacts were hunted and **not** found.

**(d) The M7 fence holds.** `RUN-QSP-33b442-S5/report.md` section 2 is headed
"ARITHMETIC, NOT MEASURED", opens with *"Nothing here was measured by this
experiment and nothing here is evidence about (A) or (B)"*, and carries the
`m >> 1` caveat from the literature record verbatim.
`metrics.json -> M7_arithmetic_not_measured` repeats the label and the caveat in
the machine-readable record. Section 5 of the same report lists "M7 in its
entirety" among what cannot be read as a measurement. A repository-wide search
for `2^117.7`, `117.6`, `0.898` finds them only inside M7-labelled contexts in
the run report and inside `H-QSP-5540d7`'s `asymptotic_claim.time_exponent` and
M7 metric definition, each of which says "under H1" or "arithmetic". **No
sentence anywhere presents M7 as measured.** This is the specific route by which
a derivation-tier bound becomes a claimed attack ceiling, and the record closed
it.

**An arithmetic error in the Proposition 8 instantiation at integer `m`: not
found, and the direction of the idealisation is the conservative one.**
Artifact: `scratch/j6_prop7_integer_m.py` -> `scratch/j6_prop7_integer_m_out.txt`.
Proposition 7 was instantiated in full at `n = 131` with `m!`, `m^{5.188}` and
`3^{kappa m^2}` carried (the factors the `m >> 1` form drops), minimising over
integer `m` in 2..59 and over every `n'` with `n' ∤ n`, at `beta` equal to (B)'s
bound and `kappa = 4.876`:

- minimum cost over all `(n', m)`: **`2^166.43`** (at `n' = 3, m = 2`);
- M7's idealised figure: `2^117.67`;
- rho (KN-LIT-096): `2^60.9`;
- dropping `3^{kappa m^2}` entirely still gives a minimum of `2^126.24`.

So the `m >> 1` idealisation is **generous to the attacker** by ~49 bits, which
for a non-existence claim is the conservative direction, and nothing beats rho
at any integer `m`. The literature record's own "Limits of applicability" caveat
is therefore a caveat that cannot hurt (E). This is a check the record could
have made and did not; making it strengthens the record, conditional on H1 as
before.

### 4.5 Citation provenance (attack (c)) and forward guidance (attack (e))

**Provenance.** Both structural citations behind (E) are marked `retrieved` with
named verifiers, and both source texts are in `inputs/`; this reviewer opened
both and the transcriptions of Proposition 7, Proposition 8, Remark 1 and
Lemma 3.1 are faithful. The `recalled` items are correctly marked as such and
the record says in terms that the generic-attainment statement "supports nothing
by itself". **The rule-9 problem is not a mislabelled provenance; it is that
after honouring the label, H1's `random_model_justification` has nothing left
holding up its stated direction** (section 4.3).

**A discrepancy in the source, adjudicated** (`scratch/j6_kappa.py`)**.** `knowledge/literature/KN-LIT-4fe9d2.md`
flags, without adjudicating, that Section 4.4 of the paper says `kappa < 1.5`
would give `alpha_beta > 1` at `beta = 3/4`, while Proposition 8's own formula
requires `kappa < 2/3`. Read against the frozen text
(`inputs/EULER-PETIT-2019-QSP/paper_fulltext.md`), **the knowledge record is
right and the paper's 1.5 is wrong**: `alpha_beta = 1/(2 x 1.5 x 0.75) = 4/9`,
which is not `> 1`; the correct threshold is `kappa < 2/3`. (E) uses the
*formula*, not the paper's slip, so (E) inherits no error here. It is worth
recording that (E)'s threshold sentence is the same *kind* of sentence the paper
got wrong by a factor of 2.25, and that this reviewer checked it independently:
at `beta = 131/260`, `alpha_beta > 1` iff `kappa < 130/131`. Correct.

**Forward guidance.** (E)'s survivor list in `H-QSP-5540d7` names three items:
`n' | n`, correspondence shapes of conjugate degree `>= 2`
(`IDEA-20260916-a17f43`), and factor bases that are not root sets of a single
`X^{p^{n'}} - lambda`. **The rational-`lambda` extension (D)(ii) is missing from
that list**, and it must be there: the Stage 5 report section 6 records (D)(ii)
as **WITHDRAWN AS STATED**, so rational `lambda` are explicitly NOT closed. The
Stage 5 report's own forward-guidance list does carry it (item 5, alongside H1
itself at item 4 and a sub-quadratic `GF(2)[X]` reduction at item 6), so the run
report is complete and **the hypothesis record's (E) is the one that absorbs a
survivor silently**. That is a one-clause fix and it is the difference between a
closure that names what it leaves open and one that does not.

---

## 5. The `proves_too_much` control (required; owned by this task)

**Verdict: HOLDS on both named object families. The declared failure signature
is ABSENT on each.** The argument does not go through where its conclusion is
false.

Artifacts: `scratch/ptm_family1.py` -> `scratch/ptm_f1_out.txt`;
`scratch/ptm_f1_broad.py` -> `scratch/ptm_f1_broad_out.txt`;
`scratch/ptm_family2.py` -> `scratch/ptm_f2_out.txt`.

### 5.1 FAMILY 1 — `n' | n` (r = 0), Diem's subfield family

The plan requires two different things to be checked, and they are different.

**(i) Is the bound vacuous at `r = 0`?** Yes, and structurally. Checked on all
3,422 triples `(n, n', d)` with `n' | n`, `n <= 32`, `d <= 29`:
`max(d^{q+1}, p^{n'-r}) >= p^{n'} = deg L` on every one. The reason is not
arithmetic luck: at `r = 0` the second term of the max **is** `p^{n'}`, which
**is** `deg L`.

**(ii) Is the vacuity a CONSEQUENCE of the derivation rather than an accident?**
Yes, and the trace is short. The variable `r` enters (A) in exactly one place:
the exponent of the collapsed monomial `Y^{p^{n'-r}}`, which arises from
`x^{p^{n'(q+1)}} = (x^{p^n})^{p^{n'-r}}`. Setting `r = 0` makes that monomial
`Y^{deg L}`, so the degree comparison `deg D <= max(d^{q+1}, p^{n'-r})` degrades
to `>= deg L` by construction. Nowhere else in (A) does `r` appear, and (A) does
**not** assume `r >= 1` — as the plan required to be checked separately, and as
the statement of (A) explicitly permits (`0 <= r < n'`). (B) **states** `r >= 1`
as a hypothesis and **uses** it exactly once and exactly where it is needed
("since `p^{n'-r} < p^{n'}` for `r >= 1` this forces `d^{q+1} >= p^{n'}`"); at
`r = 0` that step fails and (B) draws no conclusion. (B)'s *first* step — the
degenerate exclusion — remains valid at `r = 0` (section 2.2 exercises it at
(12,6), (12,4), (6,3), (8,8)) but is not used there.

**The sharpened test, which the plan's literal signature does not reach.**
(A) asserts `N <= deg D <= max(...)`, and the *first* inequality can bite at
`r = 0` even though the second cannot: when `d^{q+1} = p^{n'}` exactly, the
leading terms of `D = Lambda_{q+1}(Y) - Y^{p^{n'}}` can cancel and
`deg D < p^{n'} = deg L`. **That is the derivation yielding a bound strictly
below `p^{n'}` at `r = 0`** — the plan's stated failure signature, read
literally. It is not a proof of too much, because the objects at those exact
parameters do not reach `p^{n'}`. Both halves were tested:

- Every `(n, n', d)` with `n' | n`, `n < 40`, and `d^{q+1} = p^{n'}` exactly was
  enumerated (30 such triples). At the 5 of them that are computationally
  reachable — (4,4,d=4), (6,3,d=2), (6,6,d=8), (8,8,d=16), (12,4,d=2),
  (12,6,d=4) — **every** `lambda` of that degree was run through I1, I2 and the
  degenerate detector: **65,832 candidates**. Result: `deg D < 2^{n'}` on most
  of them, **0** of them splits completely, and `N <= deg D` on every one.
- Broadening: every `lambda` of every degree 1..8 at every `r = 0` cell with
  `n <= 14`, `n' <= 10` — **7,244 candidates**. **0** violations of the full
  form `N <= deg D`; **0** violations of the max form. **141** objects at
  `r = 0` split completely (a much richer known-false family than `d = 1`
  alone: it includes `(6,3,d=7)`, `(12,3,d=7)`, `(8,4,d=8)`, `(12,4,d=8)`,
  `(4,2,d=3)` and more). **On every one of the 141 the derivation is vacuous**
  (`deg D >= 2^{n'}`). Of the 288 candidates where the derivation IS
  non-vacuous at `r = 0`, **not one** splits completely.

**Failure signature on FAMILY 1: ABSENT.** The argument becomes vacuous on
exactly the objects whose conclusion is false, and the vacuity is traceable to
the single occurrence of `r` in the derivation, not to a choice of parameters.

One precision the record should carry, because it is the difference between
"vacuous" and "vacuous in the form we stated": `H-QSP-5540d7`'s
`baseline_embedding.parameter_slice` (iii) says only *"r = 0 is the vacuity
slice: the bound is `max(d^{q+1}, p^{n'})` >= deg L"*. That is true of the max
form and **not** of the `N <= deg D` form, which still says something at `r = 0`
when `d^{q+1} = p^{n'}`. The record is accurate and incomplete; the incompleteness
is in the harmless direction (it understates what the derivation gives), but the
plan asked whether vacuity is a consequence, and the honest answer is "of the
max form, always; of the full form, not always, and where it is not, no object
reaches `p^{n'}`".

### 5.2 FAMILY 2 — the linearized family of KN-LIT-4fe9d2 Theorem 1 (`beta >= 3/4` already known)

This family was tested **with no instrument of the experiment at all**. On the
`F_2`-coefficient linearized slice, complete splitting is decided by
**Proposition 2** alone (`L_f` splits completely iff its symbol `f` divides
`T^n - 1`), so the whole slice can be enumerated by factoring `T^n - 1` and
listing its degree-`n'` divisors. For each such divisor, `l = deg(f - T^{n'})`
gives `d = 2^l` and hence `beta = l n / n'^2` exactly.

Enumerated: every `n` from 3 to 40, every `2 <= n' < n` with `n' ∤ n` —
**1,032 `F_2`-linearized complete splitters**, none of them produced by I1, I2
or I3.

- **Violations of (B) (`beta >= n/(n + n' - r)`): 0.**
- **Objects with `3/4 <= beta < (B)`'s bound — i.e. objects that satisfy
  Theorem 1 and REFUTE (B): 0.** This is the object the plan asked to be hunted
  where (B) is stronger than Theorem 1, and it does not exist in the enumerated
  slice.
- **Objects with `beta < 3/4`: 0** — consistent with Theorem 1, and it means the
  slice contains no counterexample to the literature either.
- **(B) is EXACTLY TIGHT at several points, on both sides of 3/4**:
  `(35,15)` gives `beta = (B) = 7/9 = 0.7778`; `(35,20)` gives
  `beta = (B) = 0.875`; `(33,22)`, `(36,24)`, `(39,26)` give
  `beta = (B) = 3/4` exactly, where (B) and Theorem 1 coincide. So where (B)
  exceeds 3/4 there is an object attaining it — (B) cannot be improved there and
  Theorem 1 cannot refute it.

**Does the argument derive `beta >= 3/4` generally?** No, and it cannot: (B)
gives `n/(n + n' - r)`, whose minimum over `n' < n` is `n/(2n-2)`, i.e. 0.583 at
`n = 7`, 0.517 at `n = 31`, **0.5038 at `n = 131`**, 0.502 at `n = 257`, and
`-> 1/2`. (B) is strictly WEAKER than Theorem 1 in the worst case at every `n`.
The record makes no claim of improvement: `H-QSP-5540d7` (C) says only that
Theorem 1 "is for linearized `lambda` with any `n'`; (B) is for any `lambda`
with `n'` not dividing `n`" — a scope statement, correctly two-sided.

**At `n = 131` itself**: `T^131 - 1` factors over `F_2` as `(T+1) x Phi_131`
with `deg Phi_131 = 130` (confirmed by factoring, consistent with
`ord_131(2) = 130`). So the only degree-`n'` divisors with `n' ∤ 131` occur at
`n' = 130`, giving exactly ONE `F_2`-linearized complete splitter at the target
field: `l = 129`, `beta = 129 x 131 / 130^2 = 0.999941`, above both (B)'s bound
0.5038 and Theorem 1's 3/4. Type 1bis, as the literature record predicts.

**Failure signature on FAMILY 2: ABSENT.** The argument neither contradicts nor
improperly strengthens Theorem 1, and no object satisfying Theorem 1 refutes (B).

---

## 6. The narrowest statement this reviewer's joints support

Composed only from J2, J4, J6 and the control. J1, J3 and J5 are another
reviewer's and are not folded in; the Coordinator composes.

> On the tested scope, (A) and (B) survived every attack this reviewer built,
> including the one the plan expected to succeed and two the plan did not name.
> The bound's exclusion clause is exhaustive, its degenerate branch is correctly
> characterised and exactly tight, its composition step is valid in every
> characteristic tested, and the argument behaves correctly — vacuously — on
> both families of objects where its conclusion is false.
>
> What the EXPERIMENT established is narrower than its headline in two
> respects, both of which this reviewer measured:
>
> 1. **"Three agreeing instruments" is two, and at `n = 131` it is one.** The
>    1260 Stage-1 agreements were produced by three routines in one Python
>    module that share `square`, `polymod` and `clmul`; the independent C
>    implementation `gf2rc.c` contributed **none** of them. The 732-candidate
>    `n = 131` census rests on I3 alone, verified in one direction only.
> 2. **The `D = 0` exclusion that carries the whole of (B) was never enforced
>    by measurement.** `degenerate_candidates: 0` is reported at every cell and
>    is structural: no cell of this contract can host a degenerate candidate,
>    because every cell has `n` prime with `2 <= n' < n` and degeneracy needs
>    `(q+1) | n`.
>
> The closure reading **(E) is not promotable**, and not only for the reason
> the plan anticipated. Its promotion gate is unsatisfied because H1 is
> unvalidated, which caps the claim below `supported` regardless of the state
> of its route. Beyond that, its stated exclusion of a cheap solver rests on a
> number (`kappa = 4.876`) that is an **upper** bound on the solver exponent in
> both source texts, and on a "rigorous ingredient" that the source states as an
> upper bound on a cost the source itself calls negligible. (A) and (B) are
> untouched by any of this: they are unconditional and need no cost model.

---

## 7. What I attacked and could NOT break

A failed attack named in advance is evidence; an unstated one is not. Each of
these was built, run, and produced the artifact named.

| # | attack (and where the plan named it) | scale actually run | outcome |
|---|---|---|---|
| 1 | **A degenerate `L` with `N = p^{n'}`** — would break (B) at step one (J2 breaking artifact 1) | 26 constructed `(n, n', j)` instances + the **164** degenerate `lambda` over full `K` at (4,3), (6,4), (6,5) | **NOT FOUND.** Every one has `N = p^{n'-j}` exactly; none splits completely |
| 2 | **A char-`p` counterexample to `f o g = Y^m => g = cY^e + b`** (J2 breaking artifact 2) | **1,324,468** compositions over `F_2, F_3, F_4, F_5, F_7, F_8, F_9`; plus `Y^p`, `Y^p+Y`, `Y^{p^2}+Y^p` and inseparable `f = h(Y^p)` targeted | **NOT FOUND.** 0 counterexamples |
| 3 | **`degenerate_detection` cannot return true on any input** (J2 breaking artifact 3) | fed 26 + 164 constructed degenerate candidates | **REFUTED.** It fires correctly on every one, including `deg D = 0` with `D != 0` |
| 4 | **A `lambda` with `D = 0` outside the claimed form** — would make the exclusion a gap | **331,664** `lambda` (F_2 at 16 cells, degrees 1..7; full `K` at (4,3) and (6,4), degrees 1..3) | **NOT FOUND.** Every `D = 0` hit is `c X^{2^j} + b` |
| 5 | **An injected single-point fault that leaves `M2 = 0`** (J4 breaking artifact 2) | 8 faults + 1 negative control, every shared and unshared primitive, on a scratch copy | **NOT FOUND.** Shared-primitive faults break the matrix (`F-c`) or trip an internal assert; single-instrument faults localise |
| 6 | **An `n = 131` candidate where I3 disagrees with an independent decision procedure** (J4 breaking artifact 1) | **36** determinations by two independent routes (from-scratch linear algebra; Proposition 2), incl. **12 rows inside the census** | **NOT FOUND.** 0 disagreements; all 12 census values match the archive exactly |
| 7 | **A shared failure mode producing agreement without correctness** (J4 breaking artifact 3) | the size-gated `G-a/G-b/G-d` faults, designed to evade the `n <= 13` self-check | **NOT FOUND.** All three trip `ddf_factor`'s `assert deg(rest) <= 0` |
| 8 | **The derivation yielding a sub-`p^{n'}` bound at `r = 0` on an object that reaches `p^{n'}`** (proves-too-much FAMILY 1) | **65,832** at the equal-degree boundary + **7,244** broad; 141 complete splitters found at `r = 0` | **NOT FOUND.** All 141 sit where the derivation is vacuous; 0 violations of `N <= deg D` |
| 9 | **A linearized complete splitter with `3/4 <= beta < n/(n+n'-r)`** — satisfies Theorem 1, refutes (B) (proves-too-much FAMILY 2) | **1,032** `F_2`-linearized complete splitters at `n <= 40`, enumerated by Proposition 2 with **no instrument of the experiment** | **NOT FOUND.** 0 such objects; 0 violations of (B); (B) exactly tight at 5 points |
| 10 | **An arithmetic error in the Proposition 8 instantiation at integer `m`** (J6 breaking artifact 2) | Proposition 7 in full (`m!`, `m^{5.188}`, `3^{kappa m^2}` carried), all `n'`, integer `m` 2..59 | **NOT FOUND.** Minimum `2^166.43`; M7's idealisation errs toward the attacker by ~49 bits |
| 11 | **A committed sentence presenting M7's arithmetic as a measurement** (J6 breaking artifact 3) | repository-wide search for `2^117.7`, `117.6`, `0.898`, plus reading S5 §2 and §5 and `metrics.json` | **NOT FOUND.** The fence holds in both the prose and the machine-readable record |

The two things this reviewer expected to find and did not are worth naming
separately, because they were the plan's two highest-probability breaks and
both came back the other way:

- The Coordinator put 0.65 on the fault injection showing the agreement matrix
  measures shared code. **It does not.** A single fault in the most-shared
  primitive changes 87 of 120 counts and produces 75/73/43 disagreements.
- The Coordinator put 0.08 on an I3 undercount at `n = 131`. **None was found**,
  on the first independent determination anyone has made at that field.

---

## 8. Objections, ordered by what they cost the claim

Numbered so a Coordinator decision can cite them individually. **O1 is the only
one that changes a verdict.**

**O1 — (E) invokes an UPPER bound on `kappa` to exclude a LOWER value of
`kappa`.** [J6; breaks] Both frozen sources say `kappa` is *majored by* 4.876
(Euler–Petit Prop. 7 verbatim; Huang Lemma 3.1's `Õ(...)`). The closure needs
`kappa >= (n-1)/n`. A ceiling cannot establish a floor. Additionally, H1's
declared **"Rigorous ingredient"** — *"the eliminant ... has degree M(E) ... and
root-finding ... costs at least M(E)"* — is contradicted twice by Huang
Appendix A.1, which says *"degree **bounded by** M(E)"* and that root-finding's
cost *"can be neglected"*. The step that would convert the upper bound to an
equality is the BKK/generic-attainment statement H1 marks `RECALLED`, which
AGENTS.md rule 9 forbids from discharging `supporting_results`. **After honouring
that label, H1 has no retrieved support in the direction (E) uses it.**
*Cost:* (E) is a bare heuristic plus (B), with `1/n` of margin. *Fix:* state (E)
as "conditional on H1, whose direction is not supported by any retrieved
result", drop the "five times below 4.876" comparison, and lead with the
`kappa >= 1` form. **(A) and (B) are untouched.**

**O2 — the `D = 0` exclusion that carries (B) was never enforced by
measurement, and `degenerate_candidates: 0` reads as though it were.** [J2]
Structural at all **111 declared cells** (95 Stage-2 plus 5 Stage-1, 6 Stage-1b,
3 Stage-3 and 2 Stage-4 — **98 distinct `(n, n')` pairs**) and all **45,436**
candidates: degeneracy needs `(q+1) | n`, and every one of the 98 pairs has `n`
prime with `2 <= n' < n`, so `2 <= q+1 < n` and `(q+1)` never divides `n`.
Success criterion **S1's second conjunct** — *"with degenerate candidates listed
separately and each satisfying the trivial bound `N <= 2^{n'-j} < 2^{n'}`"* — is
therefore **vacuously satisfied** and the record does not say so. *Fix:* one
sentence in the execution report and in any evidence record —
`degenerate_candidates: 0 is structural at every cell ((q+1) does not divide n
for prime n with 2 <= n' < n), not an observation`. The 26 + 164 instances in
section 2 supply the missing measurement if the Coordinator wants one.

**O3 — "three agreeing instruments" overstates the redundancy; the certificate
re-verifier is not primitive-independent either.** [J4] All of I1, I2, I3 and
`verify_roots_f2` bottom out on `square`, `polymod`, `clmul`; `verify_roots_f2`'s
docstring claim that it *"shares no code path with the injection count"* is true
of the algorithm and false of the arithmetic. The independent C implementation
produced **none** of the 1260 agreements. *Fix:* report Stage 1 as "two
independent determinations over a shared primitive base, plus a third
implementation that agrees (`scratch/j4_c_vs_python.py`, 1260/1260)" — i.e.
adopt the free check rather than reword the claim.

**O4 — (E)'s survivor list omits a survivor the record itself declared.** [J6]
`H-QSP-5540d7` (E) names three survivors; the rational-`lambda` extension
(D)(ii) is **recorded WITHDRAWN AS STATED** in `RUN-QSP-33b442-S5/report.md` §6,
so rational `lambda` are not closed and must be listed. The Stage 5 report's own
list has it (item 5); the hypothesis's does not. *Fix:* one clause.

**O5 — the degenerate case is mis-described in its citations for `b != 0`.**
[J2] `H-QSP-5540d7` calls it *"a p^j-th power of an affine binomial of subfield
or multiplicative type (Appendix C.2 of KN-LIT-0a321c; Proposition 6 of
KN-LIT-4fe9d2)"*. Both cited results are about the **multiplicative** family
`X^{q^{n'}} - X^a` (checked against the frozen Huang text at Appendix C.2). For
`b = 0`, `M = X^{p^{n'-j}} - c'X = X(X^{p^{n'-j}-1} - c')` genuinely is of
subfield/multiplicative shape and the citations fit. For `b != 0`,
`M = X^{p^{n'-j}} - c'X - b'` is an affine **tri**nomial whose root set is a
coset of an additive subgroup — neither cited result covers it, and "binomial"
is wrong. *Cost: none to the bound*, which follows from `deg M` alone (verified
on 164 instances including all 16 `b` values at (4,3)). *Fix:* say "affine, a
`p^j`-th power of `X^{p^{n'-j}} - c'X - b'`; for `b = 0` this is the
subfield/multiplicative family of [C.2 / Prop. 6]".

**O6 — the `r = 0` vacuity slice is stated only for the `max` form.** [control]
`baseline_embedding.parameter_slice` (iii) says the bound at `r = 0` is
`max(d^{q+1}, p^{n'}) >= deg L`. True — but (A) also asserts `N <= deg D`, and
at `r = 0` with `d^{q+1} = p^{n'}` the leading terms can cancel and
`deg D < deg L`. So the derivation is **not** vacuous at `r = 0` in its full
form. It is still correct there (0 violations in 65,832 + 7,244 candidates, and
no such object splits completely), but the record's vacuity claim is narrower
than the record's bound. *Fix:* one clause; or state (A) at `r = 0` as
"`N <= deg D`, which is `deg L` unless `d^{q+1} = p^{n'}`".

**O7 — the composition step's `p^j`-th root uses finiteness, stated as "over a
field".** [J2] `c' = c^{p^{-j}}` exists because Frobenius is bijective on a
finite field; over `F_p(t)` it need not. The setting fixes `K = F_{p^n}`, so this
is a wording matter only.

**O8 — (E) inherits whatever scope restriction (B) needs, and says "at any
`p, n, n'`".** [J6, but the restriction itself is J3's] If (B)'s quantifier needs
`n' < n`, (E)'s must too. This reviewer does not adjudicate the restriction
(J3 owns it) and the J6 verdict does not depend on it.

---

## 9. Out-of-scope findings — NOT coverage of J1, J3 or J5

**Flagged so the Coordinator does not read any of this as review of a joint this
reviewer does not own.** These were noticed while working the owned joints and
are reported for the owner of the relevant joint to confirm or overturn.

- **(touches J3)** `RUN-QSP-33b442-S2B/raw-result.json` `M3_complete_splitters`
  carries **3** rows with `beta_minus_exact == 0.0`, at `(7,3,d=2)` x2 and
  `(7,4,d=4)` x1 — not 8, and not 2. The plan's prior cites eight occurrences of
  the string in the file; the other five are presumably in `M3_near_complete`,
  which this reviewer did not audit. **Not adjudicated here. J3 owns it.**
- **(touches J5)** As a by-product of the `n = 131` cross-check, the `affine`
  column is populated and correct at all three Stage-3 cells: exactly 4 rows per
  cell, `lambda_bits` 17, 19, 21, 23 = `X^4 + aX^2 + bX + 1`, `affine: true`,
  `linearized: false`. Their `N` values `(0, 1, 1, 0)` per cell were reproduced
  independently. **J5 owns census coverage; this is one column on 12 rows.**
- **(touches J1)** `deg_D_and_degenerate` short-circuits to
  `(max(a,b), False)` whenever `a = d^{q+1} != b = 2^{n'-r}`, building `D` only
  at the equal-degree boundary. That is sound — the leading terms cannot cancel
  when the degrees differ — and it is what makes Stage 2 feasible at
  `d^{q+1} = 8^16`. It also means `deg D` is **reported as `max(a,b)` rather
  than measured** on every candidate away from the boundary. **J1 owns the
  degree bound.**
- **(no joint)** `CORR-20260917-8b80cc`'s classification *"record-schema defect,
  no measurement touched"* — the plan asks reviewers to say if they think it is
  wrong. Having read the record's `gate_verdict` and its D1/D2 decomposition,
  and having drawn every number in this report from `RUN-QSP-33b442-S1`, `-S1B`,
  `-S2B` and `-S3`, **this reviewer does not think it is wrong**: the fifteen
  errors fall on manifest metadata and on companion files of S0 (zero compute),
  S5 (extraction) and S2 (aborted, no number reported), and none of them touches
  a value used anywhere above. This is a view on the classification, not a
  re-litigation of the remediation.
- **(no joint)** The `10 of 65` decomposition was reproduced independently from
  `S2B/raw-result.json` and matches `CORR-20260917-8b80cc` exactly.

---

## 10. What this reviewer did NOT do

Stated explicitly, because a review's silence is not a finding.

1. **Did not review J1, J3 or J5.** They are another reviewer's and nothing
   above should be counted toward them.
2. **Did not read any sibling report or task directory.** `blindness.mutual` is
   true and was respected; `read_sibling_reports: false` is accurate.
3. **Did not open `analysis/qsp-ecc2k130/`** at all — not even to check the
   pre-registration story, which the plan permits. No value in this report can
   have come from there.
4. **Did not open** `RUN-QSP-33b442-S0/derivation-note.md`, the 546 Stage-3
   certificate files individually, `RUN-QSP-33b442-S4`,
   `experiments/EXP-QSP-33b442/amendments/*` (including
   `AMD-20260917-001` itself — its cap and scope were taken from the plan and
   from `S2B/raw-result.json`), or `knowledge/literature/KN-LIT-0a321c.md`
   (the Huang **paper text** was read directly instead).
5. **Did not test `p != 2` for (A).** That is J1's assignment (its attack step
   (c)) and this reviewer did not duplicate it. The `p != 2` work here is
   confined to J2's composition step, where `F_3, F_5, F_7, F_9` were exercised.
6. **Did not verify H1 or attempt its validation experiment.** No Groebner or
   resultant engine is available and none was sought; the J6 finding is about
   the *support* for H1, not about its truth. H1 may well be true.
7. **Did not find an independent decision procedure for non-linearized,
   non-affine `lambda` at `n = 131`.** 720 of the 732 census rows remain
   single-instrument after this review.
8. **Did not re-run any stage of the experiment**, change any status, edit any
   artifact, or commit anything. All work is under
   `coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/`.
9. **Fault injection sample was 120 candidates**, not 1260: the (7,3) and (11,4)
   cells at degrees 2..5. The result (a shared-primitive fault breaks the
   matrix) is qualitative and does not need the full set, but the number is
   stated rather than rounded up.
10. **Did not settle whether `n' < n` is a definitional constraint of the QSP
    setting.** J3 owns it; O8 records the dependency only.

---

## 11. Required `red_team_report` block (`agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260917-52b4e6
  task_id: TASK-20260917-52b4e6
  claim_under_review: >-
    The contract's own pre-registered success headline, quoted verbatim from
    experiments/EXP-QSP-33b442/specification.yaml success_criterion and put to
    this round by ledger/handoffs/TASK-20260917-43701b.yaml
    review_plan.claim_under_review: "H-QSP-5540d7 is SUPPORTED AT DERIVATION
    TIER PENDING INDEPENDENT REVIEW -- a checkable argument, 1260 exhaustive toy
    candidates under three agreeing instruments, 65 complete splitters none
    below the corollary, and 732 certificate-bearing exact counts at n = 131 --
    which proves nothing about any deployed curve, moves no attack exponent, and
    leaves the closure reading (E) conditional on the unvalidated H1." The
    producer stated NO verdict; this reviewer attacks only joints J2, J4, J6 and
    the proves-too-much control, and does not vote on the claim.
  objections:
    - id: O1
      joint: J6
      severity: breaks_the_joint
      statement: >-
        (E) excludes a cheap solver by citing kappa = 4.876, which both frozen
        sources state as an UPPER bound on the solver exponent ("currently
        majored by 4.876", Euler-Petit Prop. 7; Huang Lemma 3.1's O~ bound). The
        closure needs a LOWER bound kappa >= (n-1)/n. H1's declared "Rigorous
        ingredient" is contradicted by Huang Appendix A.1, which says the
        eliminant has degree BOUNDED BY M(E) and that root-finding's cost "can
        be neglected"; the step that would make it an equality is the
        BKK/generic-attainment statement H1 itself marks RECALLED, which
        AGENTS.md rule 9 forbids from discharging supporting_results.
      cost_if_unfixed: >-
        (E) reads as a closure with a fivefold safety factor. It is a bare
        heuristic plus (B), with margin 1/n over its own assumption (0.76% at
        n = 131, zero asymptotically). (A) and (B) are untouched.
    - id: O2
      joint: J2
      severity: narrows_the_claim
      statement: >-
        degenerate_candidates: 0 is STRUCTURAL at every cell, not observed:
        degeneracy requires (q+1) | n, and every one of the contract's 111
        declared cells (98 distinct (n, n') pairs) has n prime with 2 <= n' < n,
        hence 2 <= q+1 < n and (q+1) never divides n. The instrument returned
        False on 45,436 candidates and could not have returned True on any. Success criterion
        S1's second conjunct is vacuously satisfied and no artifact says so.
      cost_if_unfixed: >-
        A reader takes a measured absence from a structural impossibility, on
        the branch that carries the whole of corollary (B).
    - id: O3
      joint: J4
      severity: narrows_the_claim
      statement: >-
        "Three agreeing instruments" is, at Stage 1, three routines over one
        shared primitive base (square, polymod, clmul); I1 has no primitive of
        its own; verify_roots_f2's docstring claim to share no code path is true
        of the algorithm and false of the arithmetic; and the one genuinely
        independent implementation (gf2rc.c) produced none of the 1260
        agreements because stage1.py gates it on n' >= 10.
      cost_if_unfixed: >-
        The redundancy claimed in the headline is not the redundancy measured.
    - id: O4
      joint: J6
      severity: incomplete_disclosure
      statement: >-
        (E)'s survivor list in H-QSP-5540d7 omits the rational-lambda extension
        (D)(ii), which RUN-QSP-33b442-S5/report.md section 6 records as WITHDRAWN
        AS STATED. The Stage 5 report's own forward-guidance list carries it.
      cost_if_unfixed: A closure that silently absorbs a survivor it declared open.
    - id: O5
      joint: J2
      severity: citation_accuracy
      statement: >-
        The degenerate case is described as "an affine binomial of subfield or
        multiplicative type (Appendix C.2 of KN-LIT-0a321c; Proposition 6 of
        KN-LIT-4fe9d2)". Both cited results are the multiplicative family
        X^{q^{n'}} - X^a (checked against the frozen Huang text). They fit the
        b = 0 subcase; for b != 0, M = X^{p^{n'-j}} - c'X - b' is an affine
        trinomial whose root set is a coset of an additive subgroup, covered by
        neither, and "binomial" is wrong.
      cost_if_unfixed: >-
        None to the bound (which follows from deg M alone, verified on 164
        instances). A reader chasing the citation finds the wrong family.
    - id: O6
      joint: proves_too_much
      severity: precision
      statement: >-
        baseline_embedding.parameter_slice (iii) states r = 0 vacuity for the
        max form only. (A) also asserts N <= deg D, which at r = 0 with
        d^{q+1} = p^{n'} can be strictly below deg L. Correct there (0
        violations in 73,076 candidates) but not vacuous.
      cost_if_unfixed: The vacuity claim is narrower than the bound it describes.
    - id: O7
      joint: J2
      severity: wording
      statement: >-
        "A composition f o g over a field equals a monomial only if ..." then
        uses c' = c^{p^{-j}}, which needs Frobenius surjective, i.e. K finite.
        True in the setting; the generality of "over a field" is not.
      cost_if_unfixed: None in this setting.
    - id: O8
      joint: J6 (depends on J3)
      severity: dependency
      statement: >-
        (E) says "at any p, n, n'" and inherits whatever scope restriction (B)
        needs. Not adjudicated here; J3 owns the restriction.
      cost_if_unfixed: Deferred to J3.
  required_controls:
    - >-
      BEFORE any evidence record cites "0 degenerate candidates": run the
      degenerate instrument on the constructed instances of section 2.2 (or
      re-derive the (q+1) | n criterion in the record) so the D = 0 branch has
      either a measurement or a stated structural reason. Artifact ready:
      scratch/j2_construct.py, 26 instances, all detected.
    - >-
      BEFORE any evidence record cites "three agreeing instruments": run
      gf2rc.c on the 1260 Stage-1 candidates. Cost: seconds. Already run here
      (scratch/j4_c_vs_python.py): 1260/1260 agree, 0 disagreements. Adopting
      it converts the weakest sentence in the headline into the strongest.
    - >-
      BEFORE (E) is quoted anywhere: separate the qualitative closure (needs
      kappa >= (n-1)/n, robust) from the M7 table (needs kappa = 4.876 AND
      m >> 1, neither established), and state that 4.876 is an upper bound.
    - >-
      STANDING: the n = 131 census needs a second determination for
      non-linearized lambda. The linear-algebra route reaches only the
      linearized/affine slice (12 of 732 rows). Until one exists, the census is
      single-instrument with one-directional verification and must be described
      that way.
  counterexample_or_mutation: >-
    NO COUNTEREXAMPLE TO (A) OR (B) WAS FOUND, and the searches were large and
    named in advance: 331,664 lambda searched for a D = 0 outside the claimed
    form; 1,324,468 char-p compositions searched for a counterexample to the
    monomial step; 190 degenerate instances constructed and counted; 73,076
    lambda at r = 0 searched for an object that both reaches p^{n'} and receives
    a sub-p^{n'} bound; 1,032 F_2-linearized complete splitters (Proposition 2,
    no instrument) searched for one satisfying Theorem 1 and refuting (B); 36
    independent determinations at n = 131 searched for an I3 undercount. Zero
    hits in every search.
    THE MUTATION THAT DID FIRE is the fault injection, and it fired in the
    record's favour: 8 faults on a scratch copy of the implementation. A fault
    in the most-shared primitive (clmul) changes 87 of 120 counts and takes the
    agreement matrix from (0,0,0) to (75,73,43); single-instrument faults produce
    a localising signature; three faults designed to evade the n <= 13
    self-check are caught instead by ddf_factor's assert deg(rest) <= 0. A
    negative control (a semantically identical rewrite of Euclid) changes
    nothing, confirming the harness does not manufacture disagreements.
  baseline_comparison: >-
    NOT APPLICABLE AS A COST COMPARISON, and that is the record's own position:
    H-QSP-5540d7 asymptotic_claim.problem reads "NONE IMPROVED", claim_kind is
    null, and no attack exponent is claimed or moved. rho on ECC2K-130 stays at
    2^60.9 (KN-LIT-096) and nothing here touches it. The one baseline comparison
    that IS in scope is against Theorem 1 of KN-LIT-4fe9d2 on the linearized
    slice, and it was run: (B) gives n/(n+n'-r), whose worst case over n' < n is
    n/(2n-2) -- 0.583 at n = 7, 0.504 at n = 131, -> 1/2 -- so (B) is strictly
    WEAKER than Theorem 1's 3/4 in the worst case at every n, and stronger only
    at specific (n, n'). Where it is stronger it is exactly tight ((35,15) at
    7/9, (35,20) at 0.875) and no object refutes it. No claim of improvement over
    Theorem 1 is made in the record, and none is supportable.
  heuristic_challenges:
    - id: H1
      challenge: >-
        H1's random_model_justification labels as "Rigorous ingredient" a
        statement its source does not make. Huang Appendix A.1: the eliminant's
        degree is "bounded by M(E)" and root-finding "can be neglected in the
        overall complexity estimation". H1 needs degree EXACTLY M(E) and cost AT
        LEAST M(E). The gap is exactly the RECALLED BKK/generic-attainment
        statement, which rule 9 bars from discharging supporting_results. After
        honouring the label, H1 has NO retrieved support in its load-bearing
        direction. It remains a legitimate, well-stated heuristic with a correct
        falsification_condition; it is not backed by the result it cites.
      random_model_transfer: >-
        The random model is "the eliminant does not collapse for a generic
        instance". The instances here are NOT generic: they are chain systems
        S^(k) built from summation polynomials composed k times with a fixed
        lambda, whose supports are highly structured. Whether BKK is attained on
        that family is precisely what IDEA-20260916-b84e2d would test, and it is
        untested. Cheapest computation that would expose a deviation: measure the
        eliminant degree at (n, m, d) with m = 2, d = 2, 3 -- the smallest cell,
        where a resultant suffices and no Groebner engine is needed. The engine
        impediment as recorded may be larger than the smallest useful cell needs.
      status: unvalidated; validation_experiment_ids is empty; route is a proposal, not an experiment
    - id: H2
      challenge: >-
        NOT ATTACKED. H2 is the null-object model and is not load-bearing for
        (A), (B) or (E). Its falsification is explicitly an unexpected
        observation under AGENTS.md rule 8, not evidence about the bound.
      status: not this reviewer's joint
  cost_model_challenges:
    - >-
      DIRECTION OF THE CITED CONSTANT. kappa = 4.876 is an upper bound on the
      solver exponent in both sources. (E) needs a lower bound. See O1.
    - >-
      THE MARGIN IS 1/n, NOT 4.876. (E) holds iff kappa >= 1/(2 beta_min) =
      (n-1)/n: 0.9924 at n = 131, -> 1. H1 assumes kappa >= 1. So (E) survives
      H1 being wrong only on kappa in [(n-1)/n, 1), a window of width 1/n that
      closes as n grows. RECOMPUTED EXACTLY: beta_min = 131/260 at n' = 130,
      kappa_crit = 260/262 = 130/131 = 0.9923664.
    - >-
      M7's HEADLINE NEEDS 4.876 AND m >> 1 AND IS NOT A MEASUREMENT. The record
      fences all three correctly (S5 report section 2 and 5, metrics.json
      M7_arithmetic_not_measured) and carries the literature's own m >> 1 caveat.
      No sentence anywhere presents it as measured.
    - >-
      THE m >> 1 IDEALISATION ERRS TOWARD THE ATTACKER, WHICH IS THE
      CONSERVATIVE DIRECTION FOR A CLOSURE. Proposition 7 instantiated in full
      at integer m (m!, m^5.188 and 3^{kappa m^2} carried), n = 131, beta at
      (B)'s bound, kappa = 4.876: minimum over all n' and m in 2..59 is 2^166.43
      at (n' = 3, m = 2), against M7's idealised 2^117.67 and rho's 2^60.9.
      Dropping 3^{kappa m^2} entirely still gives 2^126.24. No arithmetic error
      found.
    - >-
      AN UNCHARGED TERM THE RECORD DOES CHARGE: none found in (A) or (B), which
      price no algorithm. The bound is on |F| alone and needs no cost model --
      as H-QSP-5540d7's own assumptions block says. The uncharged term is in
      (E) alone, and it is the solver's LOWER bound.
  reduction_and_scope_challenges:
    - >-
      p = 2 IN EVERY NUMERICAL CELL. The derivation is quantified over all p and
      the transfer is by derivation, not measurement -- which the contract states
      openly. This reviewer exercised p = 3, 5, 7, 9 ONLY on J2's composition
      step (1.3M compositions, 0 counterexamples). The p != 2 sweep for (A) is
      J1's assignment and was not duplicated here.
    - >-
      SCALE HONESTY OF THE n = 131 CENSUS: 732 named F_2-coefficient lambda of
      degree <= 7 is a measure-zero slice of F_{2^131}[X]; K-coefficient lambda
      at n = 131 are untouched. Correctly and repeatedly stated in the Stage 5
      report's scope paragraph. J5 owns the census coverage claim.
    - >-
      (E)'s "at any p, n, n'" inherits (B)'s scope restriction. J3 owns it (O8).
    - >-
      AFFECTED-VS-SAFE: there is no affected list, because no attack is claimed.
      "NO ATTACK, NO EXPONENT, NO STATEMENT ABOUT DEPLOYED CURVES" is stated in
      (E), in the objective, and in the Stage 5 closure block, and this reviewer
      found no sentence anywhere that violates it.
  proof_architecture_challenges:
    - attack: nearby-object / proves-too-much (FAMILY 1, n' | n)
      result: >-
        SURVIVED. The bound is vacuous at r = 0 structurally (r occurs in
        exactly one place in (A), the exponent p^{n'-r}, and at r = 0 that term
        IS deg L). (A) does not assume r >= 1; (B) states it and uses it exactly
        once, where it is needed. 141 complete splitters found at r = 0 over
        7,244 exhaustive candidates -- a much richer known-false family than
        d = 1 -- and the derivation is vacuous on every one. 288 candidates
        where the derivation IS non-vacuous at r = 0: none splits completely.
    - attack: nearby-object / proves-too-much (FAMILY 2, linearized, Theorem 1)
      result: >-
        SURVIVED, two-sided. 1,032 F_2-linearized complete splitters enumerated
        by Proposition 2 alone at n <= 40: 0 violations of (B); 0 objects with
        3/4 <= beta < (B)'s bound; 0 with beta < 3/4. (B) does not derive
        beta >= 3/4 generally and no claim of improvement is made. At n = 131
        the only such object is n' = 130, beta = 0.999941.
    - attack: quantifier-order
      result: >-
        The quantifier block of H-QSP-5540d7 is explicit and D depends only on
        (lambda, n, n'), never on an instance or seed. No witness is chosen after
        seeing an instance. On J2's branch specifically: the degenerate
        characterisation quantifies correctly (D = 0 => shape), and the converse
        is false and is not claimed -- verified exhaustively (20 of 240 and 72 of
        4,032 shape-lambda are actually degenerate).
    - attack: compositional-invariant (delete one component of the exclusion)
      result: >-
        The case split is D != 0 (bounded by (A)) / D = 0 (bounded by p^{n'-j}),
        exhaustive by construction. Deleting the degenerate branch would leave
        (B) step one unproved; deleting the (q+1)-th chain step collapses (A) to
        Lemma 4.1. Both components are load-bearing and neither is redundant.
    - attack: method-ceiling
      result: >-
        The degenerate bound is EXACTLY ATTAINED on all 190 instances tested
        (N = p^{n'-j} = p^{n/(q+1)}), so (B)'s first step has margin exactly p^j
        and cannot be sharpened. (B) itself is exactly attained at (7,3,d=2),
        (7,4,d=4), (35,15), (35,20), (33,22), (36,24), (39,26). The method's
        ceiling and the headline coincide; nothing is claimed beyond it.
  narrowest_supported_statement: >-
    ON THIS REVIEWER'S JOINTS ONLY (J1, J3, J5 are another reviewer's):
    (A)'s exclusion clause is exhaustive and its degenerate branch is correctly
    characterised, exactly tight, and valid in every characteristic tested; the
    argument is vacuous on both families of objects where its conclusion is
    false; and no attack named in the plan, nor three that were not, produced a
    counterexample. What the EXPERIMENT established is narrower than its
    headline in exactly two measurable ways: the D = 0 exclusion carrying (B)
    was never enforced by measurement (structural at all 45,436 candidates), and
    "three agreeing instruments" is two determinations over one shared primitive
    base at Stage 1 and ONE instrument at n = 131. The closure reading (E) is
    NOT PROMOTABLE: H1 is unvalidated, which caps the claim below `supported`
    under promotion gate (2) regardless of its route; and its stated exclusion of
    a cheap solver rests on a constant that both sources give as an UPPER bound.
    (A) and (B) are unconditional and are untouched by the J6 finding.
  next_concrete_action: >-
    THE CHEAPEST FALSIFICATION STILL AVAILABLE, and it is not expensive: run
    gf2rc.c on the 1260 Stage-1 candidates and on the 42,244 Stage-2 candidates
    with a SECOND compiler and a second host. It costs seconds, it is the only
    implementation-independent instrument in the package, and it currently
    contributes nothing to Stage 1. This reviewer ran the first half
    (1260/1260 agree) but on the same host and compiler, so it tests
    implementation independence and not portability. If the Coordinator wants one
    action instead: adopt that check and add the one sentence fixing O2
    (degenerate_candidates: 0 is structural because (q+1) does not divide n).
    Neither changes a number; both change what the numbers are entitled to say.
  artifact_paths:
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/report.md
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/faultdrive.sh
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/faultrun.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/faults_final.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_cells.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_cells_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_comp_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_composition.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_construct.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_construct_out.json
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_construct_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_degen_full.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_degen_full_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_exhaustive.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_exhaustive_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_structural.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_structural_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_c_vs_python.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_c_vs_python_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_callgraph.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_callgraph_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_faults.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_faults_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_n131.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_n131_out.json
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j4_n131_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j6_kappa.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j6_kappa_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j6_prop7_integer_m.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j6_prop7_integer_m_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/probe_fb.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/probe_fb_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_f1_broad.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_f1_broad_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_f1_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_f2_out.txt
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_family1.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/ptm_family2.py
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/faultcopy/   # scratch copy of the implementation; sha256 of qspcore_base.py verified equal to the committed file (32a5ad6b68678e71e9be24173040a9cb972a6576d6a2b7385ebcfdffbc2ad495) before any edit
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j3_section_final.md, scratch/faulttable.md, scratch/j2_comp_patch.py, scratch/j4_faults2.py, scratch/base.json, scratch/f.json   # intermediates, listed for completeness
```

---

*Not committed. Write scope:
`coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/`.
No ledger record, hypothesis status, run manifest, measured value or raw
artifact was changed by this task. `experiments/EXP-QSP-33b442/implementation/`
was read but never written to; every fault was applied to a scratch copy whose
sha256 was verified identical to the committed file beforehand
(`32a5ad6b68678e71e9be24173040a9cb972a6576d6a2b7385ebcfdffbc2ad495`).*

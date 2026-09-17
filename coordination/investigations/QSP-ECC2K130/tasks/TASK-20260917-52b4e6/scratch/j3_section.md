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

Artifact: `scratch/j4_callgraph.py` (static `ast` analysis of the committed
`qspcore.py`; nothing executed, nothing modified).

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

FAULT_TABLE_PLACEHOLDER

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


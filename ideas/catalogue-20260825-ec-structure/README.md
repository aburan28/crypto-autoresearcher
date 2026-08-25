# Elliptic-curve structure-search proposal batch, 2026-08-25

25 proposals in `ledger/proposals/IDEA-20260825-*.yaml`, all anchored to
`RQ-ECDLP-002` under `GOAL-ECDLP-001`. The brief was to propose many new ideas
for the elliptic-curve lanes with the search focused on **algebraic structure,
or structure in general**.

## What these records are, and are not

- **Not dispatched.** No batch, no frozen handoff, no Coordinator authority. Every
  record carries `provenance.dispatched: false` and says so in its own text. They
  are candidates for the Coordinator's queue, nothing more.
- **Nothing is approved and nothing has been run.** Every record is
  `status: proposed`, `experiment_runs: 0`, with `implementation_authorized`,
  `execution_authorized`, `scientific_status_change_authorized` and
  `breakthrough_claim_authorized` all false. Only the Coordinator approves an
  experiment (AGENTS.md rule 1).
- **Every record is `novelty_status: unverified`.** No literature screen was run
  for this batch. Several records rest on facts that are very likely standard
  folklore; each says so in its own `novelty_note` and states what it claims is
  new — usually a unification, a gate, or a measurement, not the underlying
  mathematics. External citations are `provenance: recalled`, which under this
  program's rules is a pointer for a reviewer and never support.
- **The knowledge index was not queried.** This worktree has no ingested Qdrant
  index, so `search_knowledge` would have returned nothing. Screening was done by
  reading `ledger/proposals` (all 320 elliptic-curve-adjacent records),
  `knowledge/findings`, `knowledge/open-problems`, and the campaign goal record
  directly. Each record's `why_this_is_not_a_variant` names the nearest existing
  records and states the delta against them.
- **No record claims an attack, a break, a speedup, or a security consequence.**
  Nine of the 25 expect a *negative* result and say so in their own predictions;
  under the inventor protocol a controlled null with a named mechanism is a
  first-class deliverable.

## The organizing move

The elliptic-curve campaign's own findings converge on one characterization:
prime-field ECDLP is hard because it has *minimal algebraic structure* —
`KN-FIND-5c1a03` (three-way convergence), `KN-FIND-9d2f56` (Betti-Yield duality),
`KN-FIND-c93d45` (DL circularity), `KN-FIND-7e4b90` (Wesolowski needs a 4D
quaternion algebra), `KN-OPEN-020` (the algebraic factor-base no-go).

Rather than propose more mechanisms against that wall, this batch attacks the
*characterization*. Each cluster takes one named obstruction and asks a question
the ledger has not: is it an absence or an isotropy; is it a class bound or a
parameter bound; are two recorded obstructions one obstruction; and what is the
price of the thing said to be missing. Section 4 of `docs/inventor-protocol.md`
is the standard being aimed at — a named obstruction, an argument, and a
redirection — rather than another screening report.

Six records are deliberately **anti-structure**: they propose measurements that
would *remove* a claimed advantage rather than add one (`b48ad8`, `297f47`,
`49f8e8`, `dbf58a`, `c109b5`, `f054db`). That balance is intentional. The
program's own records note that its baselines are unmeasured and its nulls
under-run, and several proposals in this batch would be uninterpretable without
them.

## The clusters

### C1 — What an instance actually reveals (5)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-7260b2` | theory | **The rank-one action deficit.** An instance pins `[k]` on one line of `E[N]`; non-scalar endomorphism action, Cheon auxiliary inputs and Kani/Robert torsion recovery all consume rank 2. One obstruction, three corollaries, with the missing rank priced. The batch's anchor record. |
| `IDEA-20260825-f054db` | barrier | **Scalar collapse as a standing gate.** Require every future `End(E)`-leverage proposal to exhibit a non-scalar action on the object it uses, and re-audit the lane against that one question. |
| `IDEA-20260825-b48ad8` | control | **No instance is ever special.** `AGL(1,N)` acts computably and transitively on instances, so all exploitable structure is curve-level — turned into a universal null every mechanism measurement should pass. |
| `IDEA-20260825-9ad045` | theory | **A four-axis tracked-object taxonomy** (arity, equivariance, value target, propagation mode) with the ledger's own closures placed in its cells. Discharges `KN-OPEN-019`, which the protocol names as a prerequisite for any closure claim. |
| `IDEA-20260825-72b411` | audit | **The (p,t) weakness locus.** Every published structural weakness as an explicit condition on the Frobenius trace, with its density and the curve-level analogue of the closure question. |

### C2 — Where the quaternion analogy dies (4)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-39511f` | barrier | **Split is the wrong kind of non-commutative.** `End⁰(E×E) = M₂(K)` *is* a quaternion algebra, so "ordinary curves have only a 2D commutative endomorphism ring" is false above dimension one — but it is the split one, its reduced norm is isotropic, and KLPT-style reduction returns zero divisors. Absence and isotropy have different escapes. |
| `IDEA-20260825-81ec4b` | mechanism | **The theta (Heisenberg) group** is the one canonical non-commutative object every curve carries; its commutator is the Weil pairing, trivial on exactly the subgroup the ECDLP concerns. Does a non-isotropic level escape the collapse below rho? |
| `IDEA-20260825-378ff6` | measurement | **"Absent" is not "unreachable".** Price every route from an ordinary prime-field curve to definite quaternionic endomorphisms; produce a bound or name the cheapest bridge. |
| `IDEA-20260825-426c6e` | mechanism | **Name the subproblem, not the barrier.** Define SECOND-EIGENSPACE-ACTION, state the reduction through the higher-dimensional embedding, and impose the interface condition that stops it being circular. |

### C3 — What "algebraically described" actually bounds (4)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-b9f064` | mechanism | **Low-weight factor bases on the Solinas primes every deployed curve uses.** Not algebraically describable, so Bezout does not reach it; strongly additively structured, which is the ingredient Betti-Yield says is missing. The decisive null is the same construction over a *random* prime of the same size. |
| `IDEA-20260825-a2b76c` | theory | **A sum-product dichotomy.** Multiplicative structure makes the linear algebra nearly free and is forbidden the yield by a *theorem*; additive structure gives computable yield and no symmetry. The two stages compete for the same structural budget, and one horn is unconditional. |
| `IDEA-20260825-249f7e` | mechanism | **Bezout bounds description degree, not a class.** The pullback of a degree-`d` base along a degree-`ℓ` isogeny has degree `O(ℓd)`, so the constant is not isogeny-invariant. Is description degree the same currency as yield? |
| `IDEA-20260825-c109b5` | audit | **Are Bezout and DL-circularity one barrier?** Compare the largest Weil-tractable algebraic base against the largest Bezout-permitted one. If they meet, the frontier is one line. |

### C4 — Attacking DL circularity head-on (3)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-1aff4d` | theory | **The dual side is not circular.** Sums over the *index* of an algebraic coordinate admit classical bounds; the H-PSEUDO sums put the DL in the exponent. Does Parseval over the correct dual pair transfer anything, or is the transfer provably vacuous — and by exactly what factor? |
| `IDEA-20260825-a4b62c` | measurement | **Harmonic analysis on the isogeny class.** The class is a `Cl(O)`-torsor, so every per-curve cost functional is a function on a finite abelian group. Compute its spectrum; flat is a controlled null, concentrated is an `O(√h)` descent. |
| `IDEA-20260825-5ad12c` | measurement | **An algebraic compressibility exponent for the DL map.** Christol's theorem makes automaticity a measurable proxy for algebraicity; measure the minimal automaton size of `k ↦ x(kP)` *relative to N*, with `k ↦ gᵏ` as an unusually clean positive control. |

### C5 — Why the anomalous attack is isolated (2)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-eddac9` | barrier | **The canonical section is a homomorphism, so the lift carries zero information.** When `gcd(N,p)=1` the reduction `E(Z/p²) → E(F_p)` splits canonically and `σ(kP) = kσ(P)`; the anomalous case escapes precisely because coprimality fails. Closes the whole p-adic lifting family with one mechanism, and is the batch's cleanest worked example of the lossy-projection test producing a closure at zero compute. |
| `IDEA-20260825-9232ce` | theory | **Which subgroup of `(Z/N)*` can a solver act with?** Every instance operation is affine in `k`, so the only non-affine resource is `Aut(E)`, of order at most 6 — the exact reason Cheon's attack has no plain-ECDLP analogue. |

### C6 — What the rigidity closure leaves open (3)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-dbf58a` | representation | **The arity-two table.** The rigidity closure forbids arity-one objects; enumerate arity-two candidates and run the lossy-projection test on each at zero compute, reporting equivariance under the diagonal, the antidiagonal and `[-1]`. |
| `IDEA-20260825-0a1168` | theory | **How much of the graph of `[k]` does one instance reveal?** The graph is a curve in `E×E` whose numerical class determines `k`; an instance is one point on it. An algorithm-independent measure of the deficit, which should agree with C1's module-theoretic one. |
| `IDEA-20260825-49f8e8` | control | **A worked lossy-projection audit** of the Riemann–Roch subspace family and four neighbours. The base family fails in two lines by injectivity; the deformations that survive are the deliverable. |

### C7 — What structure the real curves actually carry (4)

| ID | class | idea |
|---|---|---|
| `IDEA-20260825-d950be` | measurement | **A free, exact, zero-secret structural census** of the deployed and challenge-sized curves: `D`, the conductor of `Z[π]`, `|Aut|` and `ord(λ)`, embedding degree, twist structure, small-isogeny degrees, and the shape of `p`. The program reasons about "generic prime-field curves" while secp256k1 has `D = −3` and P-256 does not. |
| `IDEA-20260825-239ec1` | mechanism | **Approximate multiplicative symmetry from the prime's shape.** On a Solinas prime, doubling nearly preserves low weight; measure the symmetry defect and the displacement rank it induces. Unlike a designed relation support, this symmetry costs nothing in relation probability. |
| `IDEA-20260825-297f47` | control | **Measure the baseline first.** A fully charged rho constant for `\|Aut\| ∈ {2,4,6}` with the fruitless-cycle penalty charged. The ledger records that this has never been measured here, and cluster 2 cannot be read without it. |
| `IDEA-20260825-0c9597` | barrier | **Two torsors that never meet.** Class-group DLP is subexponential and point DLP is not; ask whether any natural map relates the two torsors, and record the no-go with its mechanism and its named escape. |

## Dependencies inside the batch

Three records are prerequisites for reading others and should be sequenced first:

- `297f47` (rho baseline) — every constant-factor reading in C2 and C7 is
  meaningless without it.
- `b48ad8` (instance randomization null) — `b9f064` and `81ec4b` both require it
  *before* any positive is reported, and both say so in their own mechanism.
- `d950be` (structural census) — supplies the `ord(λ)` column that `9232ce`
  consumes and the Solinas-shape column that `b9f064` and `239ec1` consume.

The cheapest decisive records, all zero-run: `eddac9`, `c109b5`, `dbf58a`,
`49f8e8`, `39511f`.

## Honest expected yield

Stated up front so it cannot be adjusted afterwards. Of the 25, the author
expects: two or three to survive review as recordable closures with named
mechanisms (`eddac9`, `39511f`, and one of `a2b76c`/`c109b5`); most of the
measurement records to return controlled nulls, which is a useful outcome under
the protocol but not a positive one; and at most one — `b9f064` — to have any
chance of a genuine positive, which if it occurred would bear on H-PSEUDO
directly and would require independent replication at `review-breakthrough`
before any claim whatsoever.

Several records will likely be judged duplicates once a proper novelty screen is
run against the 1332-record proposal corpus. Each one's
`why_this_is_not_a_variant` field names the records it was screened against and
states the delta, so that judgement can be made against a stated claim rather
than a guess.

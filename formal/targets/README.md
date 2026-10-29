# Formalization targets

One file per frozen formal task, consumed by
`autoresearch formal formalize --task-file <path>` and turned into a dispatch
queue stanza by `tools/formal_task.py`.

A target is a **pointer plus a claim, not an approval**. Writing one here
queues nothing and approves nothing; the Coordinator decides what runs, and a
machine-verified result is still pending semantic-fidelity review.

A target that builds on other targets, or takes a statement as given without
proving it, records that in an optional `proof_map` block
(`docs/formal-research-lane.md`, "Hypothesis deltas, proof maps and errata"):

```yaml
proof_map:
  depends_on: [semaev-frobenius-collapse.yaml]   # sibling specs, checked to exist
  prerequisites:                                  # copied into the stanza's constraints
    - "Semaev S3 vanishes exactly on x-coordinates of collinear triples"
```

Add `proof_map` only to **new** targets. A committed spec is frozen: its
verification receipts bind its SHA-256 (`orchestration/formal/receipts.py`,
"spec hash"), so adding the block to an old spec would make every receipt for
it stale. Record the dependency map of an existing chain in this README
instead, as the Semaev S₃ chain does below.

Every `claim` here is quoted or tightly paraphrased from a committed theory
note, and `source` names the note it came from. Do not write a claim that is
not traceable to one: a formalization of a claim nobody made proves nothing
about this program's research.

## What is here, in ascending difficulty

| target | kind | from | expectation |
| --- | --- | --- | --- |
| `ncp-affine-normal-form` | `formalize_claim` | THM-COMMUTATOR-KERNEL1 Lemma 1 | tractable — the pipeline smoke test |
| `ncp-reachability` | `formalize_claim` | THM-COMMUTATOR-KERNEL1 Lemma 2(b) | moderate |
| `ncp-commutator-ideal-refutation` | `formal_counterexample` | THM-COMMUTATOR-KERNEL1 Prop 1 | hard; a failure here is informative, not a defect |

## Semaev degree-fall attribution (RQ-DREG-bd6c86)

| target | kind | from | expectation |
| --- | --- | --- | --- |
| `semaev-frobenius-collapse` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 1 | tractable — the smoke test for this lane |
| `semaev-decomposition-certificate` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 3 | moderate; trivial mathematically, valuable operationally |
| `semaev-symmetrization-degree` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 2 ((b) required; (a) if graded FTSP is available) | hard; may come back blocked on Mathlib's graded symmetric-polynomial support, which is a useful result about reach |

All three are **per-instance identities or decision procedures, never growth
statements**. `RQ-DREG-bd6c86` asks how the solving degree of the Weil-descended
Semaev systems grows; that is open, there is no proof to formalize, and a build
here is not evidence toward it. Read `THM_SEMAEV_FALL1` §4 before reviewing one:
the attribution procedure these lemmas support is sound and **not complete**, so
a failing check never certifies that a degree fall is unexplained.

## Fall-degree invariants (RQ-DREG-bd6c86)

| target | kind | from | expectation |
| --- | --- | --- | --- |
| `lastfall-is-max-degree-fall` | `formalize_claim` | THM_FALLDEG_INVARIANTS1 Thm 2.8 (= Caminata–Gorla Thm 2.8) | moderate; the first statement in this lane about the invariants themselves rather than one identity in one system |
| `semaev-s3-degree2-fall-witness` | `formalize_claim` | FFD_SEMAEV_MEASUREMENT1 §3a | Historical frozen target; its Lean theorem proves trace cancellation for nonzero `x_R`, not a uniform nontrivial first fall |
| `semaev-s3-boolean-parity-finite-20261022` | `formalize_claim` | 2026-10-22 corrected replay | Exact executable Boolean-rank certificate for one `n=4,n'=4,s=1,x_R=1` draw; semantic bridge to general vector-space dimension remains open |

`lastfall-is-max-degree-fall` was chosen because its proof needs **no Gröbner
machinery** — Definition 1.5 is a closure condition on vector subspaces and the
proof is two inclusions plus finiteness. The frozen
`semaev-s3-degree2-fall-witness` target mentions no polynomial system at all:
its checked theorem is a char-2 trace identity. The 2026-10-22
[corrected replay](../../docs/reports/2026-10-22-semaev-first-fall-replay/report.md)
found that the archived multiplier failed F₂ cancellation. The same 80 seeds
give 68 degree-two and 12 degree-three first falls with proper parity, seven
of the latter at nonzero `x_R`. Thus the trace identity does not certify the
historical uniform first-fall wording. The new finite target checks one
transcribed counterexample's executable ranks; its semantic limits are stated
in that target and the [open problem](../../problems/semaev-degree-two-fall-nonzero-bridge.md).
The [independent semantic review](../../docs/reports/2026-10-25-semaev-semantic-review/composition.md)
confirmed the finite degree-three first fall and the narrower trace theorem.
Its [dated target correction](corrections/2026-10-25-semaev-s3-degree-two.md)
withdraws the frozen target's uniform degree-two inference while preserving
the original target bytes.

### Proof map of the Semaev S₃ first-fall chain (recorded 2026-10-29)

The finite chain was split into these targets after a hidden prerequisite
surfaced: the map from equations to row space. The arrows follow the Lean
`import` graph. The prerequisites are what each step takes as given without
a Lean proof.

```text
semaev-s3-degree2-fall-witness          (DegreeTwoFall; standalone trace identity)
  prerequisite: the descended degree-two coefficients have the form t^2 + t*x_R
                (FFD_SEMAEV_MEASUREMENT1; a model of the S_3 descent, not formalized)
  prerequisite: a vanishing degree-two part gives a new class outside V_1
                (refuted as a uniform statement: corrections/2026-10-25-semaev-s3-degree-two.md)

semaev-s3-boolean-parity-finite-20261022        (BooleanParityFiniteCertificate)
  prerequisite: the transcribed equations are the archived n=n'=4, x_R=1 draw
                (bound by source-binding receipts, not by Lean)
├── semaev-s3-finite-equation-semantics-20261022   (FiniteEquationSemantics)
└── semaev-s3-semantic-rank-degree2-20261022       (BooleanParitySemanticRankCertificate)
    └── semaev-s3-semantic-rank-degree3-20261022   (BooleanParityDegreeThreeRankCertificate)
        └── semaev-s3-finite-filtration-20261022   (BooleanParityFiltrationCertificate)
            └── semaev-s3-concrete-first-fall-20261023 (ConcreteFirstFallWitness)
```

What is still open is a generic descent from abstract `S₃` and a general
first-fall statement (`problems/semaev-degree-two-fall-nonzero-bridge.md`).
That statement would also need Semaev's correspondence: `S₃` vanishes exactly
on the x-coordinates of collinear triples. No target here proves that
correspondence. `semaev-decomposition-certificate` checks the group law
directly instead.

**Its uniqueness clause is deliberately narrow** — the annihilating functional
is NOT unique; only the root of `μ^{1/2} + μ x_R = 0` is. Caminata–Gorla **Theorem 3.1** (`sd_σ(F) = max{d_F, max.GB.deg_σ(F)}`)
is the deeper result and is deliberately not specced: it needs reduced Gröbner
bases, degree-compatible term orders and row-echelon Macaulay matrices.

Note the direction, corrected in `CORR-20260916-0c9c0a`: the last fall degree is
a **lower** bound for the solving degree, not an upper one.

## Batch-five discriminant wording

The frozen `endosweep-dk-exact-batch5-discriminants.yaml` target proves exact
integer and abstract-order statements. Its notes call the listed-factor
product the squarefree part unconditionally; the theorem makes factor
primality an explicit premise for fundamentality. The [dated correction](corrections/2026-10-25-endosweep-batch5-squarefree.md)
records the conditional wording and named-curve model boundary without
changing the frozen target or its Lean proposition. The [independent review](https://github.com/aburan28/crypto-autoresearcher/blob/c613c3b2173a05e46fbd3cf8e967581b9878e5fa/docs/reports/2026-10-25-batch5-semantic-review/composition.md)
binds the source, theorem and blind arithmetic.

## FROB C4 conditional order arithmetic

`frob-c4-null-curve-order.yaml` targets five conditional integer uniqueness
statements from the [C4 replay](../../docs/reports/2026-10-22-frob-provenance-audit/REPORT.md).
The Lean proof takes the Hasse intervals and point-order LCM divisors as
hypotheses; executable replay checks those inputs, but the curve arithmetic
and Hasse application are not formalized here. Historical C4 sampled residues
are missing, so this target does not complete C8.

## FROB C5 finite-field trace

`frob-c5-order-five-trace-kernel.yaml` proves the abstract order-five
linear-map identity. `frob-c5-finite-field-trace.yaml` connects that polynomial
to Mathlib's finite-field Frobenius and trace, proves kernel dimension four,
and instantiates the three archived base primes. The
`frob-c5-factors-q11.yaml`, `frob-c5-factors-q13.yaml`, and
`frob-c5-factors-q19.yaml` targets prove the nontrivial factor-kernel sums
and trace dimension four in those canonical fields. The bridge to the
archived quotient-field implementation remains open; these targets do not
certify the historical C5 run verdict.

`frob-c5-characteristic-five-control.yaml` is a negative control requested by
the C5 bridge problem: over `ZMod 5`, `X^5 - 1 = (X - 1)^5` is not squarefree.
It marks the characteristic boundary of the coprime-factor argument, not a
verdict about the archived q=11, 13, or 19 run cells.

## FROB C5 archived quotient matrices

`frob-c5-quotient-matrices.yaml` certifies the exact 5×5 q-power Frobenius
matrices for the three frozen quotient moduli in Lean. Its generated polynomial
division identities are checked by Lean and bound to the source-bound replay
receipt. `frob-c5-quotient-matrix-kernels.yaml` applies the exact q=11, q=13
and q=19 factor polynomials to those matrices. Lean proves their factor-kernel
direct sums equal the five-term trace kernels of dimension four. The historical
Sage driver and original source custody still need independent code-to-model
review; these targets do not promote the frozen C5 run verdict or performance
metrics.

`frob-c5-quotient-frobenius-map.yaml` identifies the full base-field-linear
q-power endomorphism of each polynomial quotient with the certified matrix
using Mathlib's Frobenius algebra homomorphism and the quotient power basis.
It closes the mathematical full-map representation obligation; historical
Sage refinement, source custody and independent semantic review remain open.

`frob-c5-quotient-kernel-transport.yaml` proves the actual q-power quotient
endomorphisms satisfy the frozen C5 factor-kernel sums and trace-kernel
dimension four, have fifth power one, and have one-dimensional fixed kernels
disjoint from trace. Matrix rank and fifth-power certificates are transported
through the checked power basis; the factor identities apply directly to
the endomorphisms. The moduli are not proved irreducible in Lean, and historical
Sage refinement, execution-source custody and independent review remain open.

## BINSTD toy yield ceiling

`binstd-x17-factorization.yaml` checks the exact product of the three
polynomials recorded as bitmasks 3, 313 and 471 in the n=17 Stage-1
admissible-dimension files. It proves their product is `X^17+1` over
`ZMod 2`. `binstd-x17-degree-eight-irreducible.yaml` uses that product,
the seventeenth cyclotomic polynomial, and the order of 2 modulo 17 to
prove both archived degree-eight factors irreducible. These targets do
not prove that the field Frobenius has the asserted normal-basis module
structure or that the listed dimensions exhaust all invariant subspaces.

`binstd-canonical-frobenius-minpoly.yaml` proves that the Frobenius on
Mathlib's canonical `GaloisField 2 17` has order 17 and minimal polynomial
equal to the source-bound three-factor product. It does not identify the
archived runner's polynomial-basis field or subspace constructor with
this canonical model; the exhaustive dimension classification is still open.

`binstd-encoded-divisors.yaml` kernel-checks the archived integer masks
131081, 313 and 471 against every monic bitmask divisor through half their
degrees, using the exact XOR-and-shift remainder function in its Lean source.
The three concrete Boolean equalities use `decide` and depend only on
`propext`. This certifies the finite encoded computation; it does not prove
the remainder function correct for `(ZMod 2)[X]` or that the masks denote the
polynomials in `Factorization.lean`. The irreducibility and Frobenius-model
obligations remain open.

`binstd-yield-ceiling.yaml` targets the conditional arithmetic in
`KN-FIND-48f0ae`: if a positive-count open arm hit every target and the tau
arm cannot exceed the target count, its tau/open ratio is strictly below the
frozen 1.25 band. The proof also instantiates the four archived hit-count
pairs. It does not prove the counts, runner correctness, or any large-field
transfer; those remain empirical and require separate review.

All three NCP targets come from one note that was read end to end. Do not add targets by
skimming a note for a quotable sentence — the surrounding definitions are the
part the engine has to get right, and a claim detached from them formalizes
into something that is not the claim.

## Quotient translation commutation

`quotient-translation-descent.yaml` proves the group-law identity of
`THM_QUOTIENT_DESCENT1`: τ_T commutes with ι_S = [−1] ∘ τ_S, for every S,
exactly when 2T = 0. It is stated in any additive commutative group. The
[independent semantic review of 2026-10-29](../../docs/reports/2026-10-29-quotient-translation-descent-review/review.md)
finds it faithful to the target's claim (`faithful_scoped`, `validated_scoped`
for that claim only). It does **not** support the note's descent Lemma as
titled: degree-2 maps as quotients by ι_S, and descent ⟺ commutation, are
prose. It does not support the summation-polynomial Corollary either.

## Natural follow-ups, deliberately not specced yet

`THM_INCBARRIER1` §8 states three open gaps (G1, G2, G3) in precise form, and
G2 in particular — the worst-case chord constant, proved between 3/4 and 1 and
undetermined in between — is the shape `find_proof_gap` exists for. They are
not specced here because faithfully stating them needs §3–§5's definitions
read in full, and a paraphrase would be a different claim.

## Scoped torsion obstruction

`scoped-odd-torsion-translation.yaml` targets the odd-scalar kernel exclusion
in the dependency-free `formal/scoped-obstructions` workspace. Its source note
is `research/ten-lead-evidence/torsion-proof-note.md`. A successful check concerns
explicit additive laws and does not instantiate an elliptic curve or close lead6.

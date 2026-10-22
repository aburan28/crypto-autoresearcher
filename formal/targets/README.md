# Formalization targets

One file per frozen formal task, consumed by
`autoresearch formal formalize --task-file <path>` and turned into a dispatch
queue stanza by `tools/formal_task.py`.

A target is a **pointer plus a claim, not an approval**. Writing one here
queues nothing and approves nothing; the Coordinator decides what runs, and a
machine-verified result is still pending semantic-fidelity review.

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

**Its uniqueness clause is deliberately narrow** — the annihilating functional
is NOT unique; only the root of `μ^{1/2} + μ x_R = 0` is. Caminata–Gorla **Theorem 3.1** (`sd_σ(F) = max{d_F, max.GB.deg_σ(F)}`)
is the deeper result and is deliberately not specced: it needs reduced Gröbner
bases, degree-compatible term orders and row-echelon Macaulay matrices.

Note the direction, corrected in `CORR-20260916-0c9c0a`: the last fall degree is
a **lower** bound for the solving degree, not an upper one.

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

## BINSTD toy yield ceiling

`binstd-x17-factorization.yaml` checks the exact product of the three
polynomials recorded as bitmasks 3, 313 and 471 in the n=17 Stage-1
admissible-dimension files. It proves their product is `X^17+1` over
`ZMod 2`. `binstd-x17-degree-eight-irreducible.yaml` uses that product,
the seventeenth cyclotomic polynomial, and the order of 2 modulo 17 to
prove both archived degree-eight factors irreducible. These targets do
not prove that the field Frobenius has the asserted normal-basis module
structure or that the listed dimensions exhaust all invariant subspaces.

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

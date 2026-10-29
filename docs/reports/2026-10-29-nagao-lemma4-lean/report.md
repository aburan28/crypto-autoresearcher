# Lean `decide` certificate for the Nagao 2015/984 Lemma 4 counterexample

Date: 2026-10-29. Source finding: `knowledge/findings/KN-FIND-936151.md`
(write-once, not edited). Diagram: [diagram.svg](diagram.svg). PDF: [report.pdf](report.pdf).

**Scope, first.** This is a machine check of a finite computation over `F_2`
with N <= 3 variables. It asserts **nothing about Nagao's Proposition 5**,
nothing about Semaev's Assumption 1, nothing at `p >= 3` or `N > 3`, nothing
under the literal `>=` reading of condition (1) (where the lemma is true and
empty), and nothing about any elliptic curve. The Lean theorem is no stronger
than the Python certificate it mirrors.

## What was added

| item | path |
|---|---|
| Lean module | `formal/CryptoResearch/Nagao/Lemma4Witness.lean` |
| frozen target spec (with `proof_map`) | `formal/targets/nagao-lemma4-inside-counterexample-20261029.yaml` |
| verification receipt | `verification.json` in this directory (see "Receipt") |
| Python certificates mirrored | `tools/lemma4_inside_form.py` (witness B), `.../read-nagao-2013-549/recheck.py` (witness A) |

## The theorem

Reading: `F_2[X_1..X_n]` (not the Boolean quotient); field equations
`X_i^2 + X_i` are generators of the true system; **equality** reading of
condition (1) of Definitions 5/6; **inside form** (`d_F` and `d'_F` of the same
system `S = {f_1, f_2} u S_fe`). `Lemma4Inside n S := d_F(S) <= d'_F(S)`.

| witness | ring | `f_1`, `f_2` | `d'_F` | `d_F` | theorem |
|---|---|---|---|---|---|
| A | `F_2[X,Y]` (not multilinear) | `X^2 Y`, `XY + X` | 2 (`g = (XY, X)`) | 3 (`g = (0, X, Y, 0)`) | `lemma4_inside_false_A : ¬ Lemma4Inside 2 SA` |
| B | `F_2[X_1,X_2,X_3]` (multilinear) | `X_1X_2 + X_3`, `X_1X_3 + X_2` | 2 (`g = (1, X_1+1)`) | 3 (`g = (1, X_1+1, X_3, 0, 0)`) | `lemma4_inside_false_B : ¬ Lemma4Inside 3 SB` |

Corollary `lemma4_inside_false : ¬ ∀ n S, Lemma4Inside n S`. "No fall at `D`" is
decided over *all* admissible cofactor tuples, enumerated by `tuples`, whose
membership is proved equivalent (`mem_tuples`) to the transparent `Forall₂`
definition. All kernel goals use `decide +kernel`; no `native_decide`.
Axioms (`#print axioms`): `propext`, `Classical.choice`, `Quot.sound` only.

Controls (run, not committed as theorems): the false claims
`¬ FallAt 3 true SB 2` and `¬ FallAt 2 true SA 2` are rejected by `decide`
("proved that the proposition is false").

## Hypothesis-delta table (lean-review.md §3)

Declaration: `lemma4_inside_false` (and `_A`, `_B`). Claim: finding §1, equality
reading, inside form.

| binder / side condition in the elaborated type | claim states it? | status |
|---|---|---|
| `Poly` = duplicate-free exponent-vector list, `norm` keeps odd multiplicities | the claim says "over `F_2`" | implied (it is the standard sparse `F_2` model; no Lean bridge to `MvPolynomial (Fin n) (ZMod 2)`) |
| equality reading of condition (1) (`∃ product of degree exactly D`) | finding §3 declares it | implied by the claim; the `>=` reading is outside scope |
| cofactor domain: monomials of degree `<= D`, multilinear on the fake side | not stated | **scoping**: justified by leading-form degree additivity over a domain (not a Lean theorem); matches the Python certificate |
| fake side drops generators that reduce to zero (`gens`) | finding §2 (inertness) | **scoping**: such generators contribute `0`; only `reduce_fe_zero_2/3` are checked |
| `n` is a free `Nat`; exponent vectors are not length-checked | N/A | implied (data are literal, length `n`) |
| `FirstFall` ranges over `D >= 1`; `FallAt` demands sum `≠ 0` | matches Definitions 5/6 | implied |
| quantification over `d d'` in `Lemma4Inside` is existential-free | N/A | implied |

Two `scoping` rows cap fidelity at `partial`: any record citing this theorem
must say "for the list-of-monomials model with the stated cofactor domain".
The transcription of Nagao's Definitions into this model is the unformalized
step recorded under `proof_map.prerequisites`.

## What this adds and does not add

Adds: a kernel-checked (not Python-only) confirmation that both witnesses give
`d_F = 3 > 2 = d'_F` in the stated model, resting on no interpreter. Does not
add: any independence from the definitions chosen (the Lean and Python
certificates encode the same reading), any statement about Lemma 4 under the
`>=` reading, the outside form, or any consumer's instances (finding §5.4).

## Receipt

`autoresearch formal verify --task-file formal/targets/nagao-lemma4-inside-counterexample-20261029.yaml --artifact-out docs/reports/2026-10-29-nagao-lemma4-lean/verification.json`

Result: `machine_verified` (build PASS, axiom audit PASS, theorem
`CryptoResearch.Nagao.Lemma4Witness.lemma4_inside_false`), `needs_semantic_review: true`,
semantic review `pending` — this report's delta table is the producer's draft, not an
independent review. Receipt bindings: task spec SHA-256 `fb4715b3…b21`, theorem file
SHA-256 `73bbc30d…eb`, Lean 4.35.0-rc1, Mathlib pin from `formal/lake-manifest.json`.
`provenance.source_commit` is `f598670f` (the base `main` commit; the new files were
uncommitted when the receipt was produced, and are bound by the file hashes above).
The full project `lake build` also ran to completion on this host (one unrelated Semaev
module needed >14 GB RAM and was built with a temporary swap file).


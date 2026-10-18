# Lean retrospective, 2026-10-18

Status: **partial retrospective**. This batch supplies the decomposition
certificate target, the word-action affine-normal-form target, and the
commutator-ideal refutation target. It also rechecks existing frozen formal
targets. Independent semantic-fidelity review and the full historical review
remain open; no official hypothesis or ledger status is changed.

## Request and baseline

The owner requested retroactive review and Lean proofs of past claims in
`aburan28/crypto`, `aburan28/cryptanalysis`, and `aburan28/crypto-autoresearcher`.
The autoresearcher baseline is `6edd9e1ea14450fcb5a168137407ecf303e48773`.
[inventory.json](inventory.json) records all 66 frozen formal targets and the
47 tracked Lean source paths excluding self-test fixtures at that revision.
Four target files initially lacked source. This is a formal-source inventory,
not an extraction of every claim in the research archive or earlier Git history.

| Requirement | Status and evidence |
| --- | --- |
| Exact Git-tree inventory of existing formal targets | [inventory.json](inventory.json), reproducible with `inventory.mjs` |
| Recheck declared targets | Per-target [receipts](receipts/); final current-source status in [verification-summary.json](verification-summary.json) |
| Fill the certificate target | [Certificate.lean](../../formal/CryptoResearch/Semaev/Certificate.lean) |
| Fill the affine-normal-form target | [AffineNormalForm.lean](../../formal/CryptoResearch/NCP/AffineNormalForm.lean) |
| Fill the commutator-ideal refutation | [CommutatorIdeal.lean](../../formal/CryptoResearch/NCP/CommutatorIdeal.lean) |
| Exact shadow reachability iff | Open: `formal/targets/ncp-reachability.yaml`; the matching construction and length lower bound are not yet formalized |
| Full prose-claim inventory and independent semantic review | Open: [coverage problem](../../problems/lean-retrospective-historical-coverage.md) |

## Statements and readable proofs

The [proof map](proof-map.json) gives exact declarations, source revisions,
hypotheses, and verification evidence. The frozen target specs are preserved.

**Semaev Lemma 3**, from
[`THM_SEMAEV_FALL1.md`](https://github.com/aburan28/crypto-autoresearcher/blob/6edd9e1ea14450fcb5a168137407ecf303e48773/research/THM_SEMAEV_FALL1.md#lemma-3-certificate-soundness--proved-trivially-and-decidable):
the coefficient field k is finite, K is a decidable field extension, and the
declared finite family spans the subspace. Membership is decided by enumerating
the finite coefficient tuples. `inDeclaredSpan_iff` proves that this predicate
is exactly Mathlib linear-span membership. A certificate is an arbitrary finite
tuple of checked nonsingular affine points on an arbitrary Weierstrass curve.
The checker tests the explicit curve equation, every x-coordinate's subspace
membership, and the sum using Mathlib's actual elliptic-curve group law.
`checkDecomposition_iff` proves soundness and completeness for this predicate.
The nonsingularity proofs are checked inputs to point construction; a parser
for untrusted serialized coordinates is not supplied.

The computational instance is `instDecidableValidDecomposition`. The frozen
target name `decidable_validDecomposition` names a theorem supplying a Boolean
decision and its correctness contract. This distinction matters because the
existing verifier requires a theorem declaration, while `Decidable` instances
are data. The initial instance-only attempt and a subsequent elaboration
failure are preserved as failed receipts, followed by the corrected recheck.
The verifier was not relaxed. No relation-existence, solving-degree, complexity,
or attack-success claim follows from certificate decidability.

**NCP Lemma 1**, from
[`THM_COMMUTATOR_KERNEL1.md`](https://github.com/aburan28/crypto-autoresearcher/blob/6edd9e1ea14450fcb5a168137407ecf303e48773/research/THM_COMMUTATOR_KERNEL1.md#lemma-1-affine-normal-form--proved):
letters execute left to right. Each translation occurrence is assigned the
sign of its suffix; `wordSign_eq_negOne_pow` proves this is minus one to the
number of negations to its right. Induction on a word proves
`action(w,x)=sign(w)*x+sum(count_i(w)*s_i)` over every commutative ring.
Consequently equal shadows give equal actions, and evaluation at 1 gives the
source's orbit formula in ZMod n. The formal action uses the cyclic scalar
model; concrete curve-point implementations and the source's stronger kernel
and cost claims are not certified by this lemma.

**NCP Proposition 1**: in the genuine free associative integer algebra,
v squared minus 1 maps to zero under translation/negation evaluation into
the group algebra of the affine permutation group of ZMod n. It is outside
the two-sided ideal of all commutators: the algebra homomorphism sending
every free generator to the integer 2 kills commutators but sends this
witness to 3. Therefore the two ideals are unequal. This is the main
refutation, not the source's full presentation of the evaluation kernel.
No surjectivity hypothesis is needed. Companion witnesses involving v*t_i,
and a complexity-level simulation theorem, are not proved here.

## Verification and retained failures

The existing Lean `v4.35.0-rc1` and Mathlib
`7fa22735254ddf7e11f119250a9f2d0352bc7c3a` pins are unchanged. The scoped
torsion workspace retains its separate Lean `v4.22.0` pin. See each receipt
for the exact source/spec/toolchain/manifest hashes, build log, namespace
audit and requested-declaration audit. The final main-workspace audit covers
498 theorem declarations using standard foundations only. Semantic review
remains explicitly pending in every verifier receipt.

```sh
python tools/verify_formal_targets.py --artifact-dir /tmp/fresh-retrospective-receipts
```

Run from the repository root with `lake` and all pinned toolchains available.
Use a fresh receipt directory; never overwrite the historical attempts here.
The initial broad-run transcript is [verify-all.log.gz](verify-all.log.gz)
(read with `gzip -dc`); later
targeted rechecks resolve the documented instance/theorem mismatch and missing
toolchain without rewriting that transcript. [summarize.mjs](summarize.mjs)
accepts a successful receipt only if its theorem, spec, toolchain and manifest
hashes match the current files.

The existing `formal-workspace` CI workflow discovers the added target files.
`lean4checker` is not installed; fresh external rechecking was not performed.

## Cross-repository coverage

Crypto's new batch proves conditional subgroup DLP transport on actual point
groups and factor-base range containment; cryptanalysis's batch proves both
rho collision formulas and a zero-denominator counterexample. Their separate
reports identify assumptions and implementation gaps. A complete historical
claim extraction, all remaining crypto-project builds, concrete geometric
bridges, empirical replay and independent semantic review remain outstanding.
The [problem record](../../problems/lean-retrospective-historical-coverage.md)
keeps the original all-repositories requirement open.

[Diagram](proof-chain.svg), [editable data](proof-chain.json), and
[report PDF](report.pdf) illustrate the proof boundary. The reviewed theory
notes' measured tables and the README's performance descriptions receive no
new measurements; no performance graph, curve identity, or isogeny-route edge
is changed by these proof additions. Historical scientific state is preserved.

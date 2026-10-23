# NCP affine normal form: Lean proof and archive replay — 2026-10-21

**Scope.** This change formalizes Lemma 1 of
[`THM_COMMUTATOR_KERNEL1`](../../../research/THM_COMMUTATOR_KERNEL1.md) for frozen
target [`TASK-20260822-a0e34f`](../../../formal/targets/ncp-affine-normal-form.yaml).
The theorem source was committed at `4aaabd517b` and checked after merging
main at `6bf1c406aa305d02cc7cea33fb85756c63be9cf6`. It is a proof of
the word-action formula, not a proof of the note's kernel presentation,
reachability formula, code refinement, or performance conclusions. No new
scientific trial or timing measurement was made.

## Exact formal statement and boundary

The new [`AffineNormalForm.lean`](../../../formal/CryptoResearch/NCP/AffineNormalForm.lean)
defines a word over translations `t_i` and negation `ν`, applied **leftmost
letter first**. `negCount` counts `ν`; `signedCount w i` sums one contribution
for each `t_i`, with sign `(-1)` to the number of `ν` letters **to its right**.
`shadowSign = (-1)^negCount`. This is the word and shadow convention in the
[frozen NCP instrument](https://github.com/aburan28/crypto-autoresearcher/blob/6bf1c406aa305d02cc7cea33fb85756c63be9cf6/experiments/EXP-NCP-001/ncp1_quiver_gb.sage).

`word_action_affine_normal_form` proves, for every `n`, factor-base size `B`,
scalar list `s : Fin B → ZMod n`, word `w`, and `x : ZMod n`, that

```text
wordAction s w x = shadowSign(w) * x + Σ_i signedCount(w,i) * s_i.
```

`orbit_value_eq_shadow` specializes to the chosen generator `x = 1`.
`same_shadow_same_action` proves that equal shadows induce identical actions.
The stronger `cyclic_word_action_affine_normal_form` proves the same formula
for translations `s_i • P` in **any additive commutative group**:

```text
groupWordAction (s_i • P) w x
  = shadowSign(w) • x + (Σ_i signedCount(w,i) * s_i) • P.
```

Its proof is induction on the word. A translation adds one signed term; a
negation flips the sign and all earlier translation contributions. The
[statement and axiom printouts](evidence/statement-and-axioms.log) show the
elaborated propositions; the new declarations depend only on `propext`,
`Classical.choice`, and `Quot.sound`. [The diagram](diagram.svg) separates
this universal algebraic result from the archived implementation checks.

## Machine and archive checks

| Check | Result | Evidence and limit |
|:--|:--|:--|
| Pinned `lake build` | **PASS, 2,012 jobs** | [Full build log](evidence/full-build.log); Lean 4.35.0-rc1 and the unchanged Mathlib lockfile were used. |
| `lake env lean AxiomAudit.lean` | **PASS, 484 theorem declarations**, allowed standard axioms only | [Axiom audit log](evidence/axiom-audit.log). |
| Exact frozen target verifier | **machine_verified**; independent semantic review pending | [Source-bound receipt](evidence/target-receipt.json) checks the named theorem and binds task/source SHA-256, toolchain, manifest, and commit. |
| Archived `commutator_kernel1_check.py` in scratch | **12/12 frozen instances matched; 12,000 shadow words, 0 mismatches** | [Replay log](evidence/archive-replay.log) and [result JSON](evidence/archive-replay-results.json). The strict-inclusion row remains 350/439 NC versus 437/439 commutative. This rechecks the archived affine rule and counts, not elliptic-curve point arithmetic or a new speed result. |
| Complete formal target verifier | **63 machine verified, 0 failed, 0 infrastructure, 3 undischarged** | [Full corpus log](evidence/full-target-verification.log). The three absent files are NCP reachability, NCP commutator-ideal refutation, and Semaev decomposition certificate. Every present target still requires independent semantic review. |

The replay used the committed 26,842-byte
`experiments/EXP-NCP-001/runs/RUN-NCP-001-a/raw.json` unchanged, SHA-256
`f3af5001099ae26ffd0481c7dbf1a96941305160ac2ed1d6d105057fc6aa57ce`.
The replay script SHA-256 is
`2f2a07f7dcbc0a3b28ab07ad795e75489e09ac767c7cbe76b3793b9a8480e66c`.
All substantive JSON fields matched the committed replay result; host,
Python version, and elapsed time are environment-dependent. The theorem
source SHA-256 is
`bc634798b1acb9236695880688a306dbc0ddac8fd484967d0acf9f2fc3038eed`.

## Remaining proof and validation work

The frozen NCP reachability and commutator-ideal refutation targets still lack
Lean files. The new theorem does not prove the note's full group/path-algebra
kernel claims, search-cost bound, elliptic-curve implementation refinement,
or behavior outside the single-vertex translation/negation model. The archived
NCP positive control compared point arithmetic on sampled words; it was not
rerun here and is not a universal software-correctness proof. The target
receipt deliberately retains `semantic_review: pending`; official claim
promotion requires the repository's independent review process.

No canonical performance graph or dashboard changed: this proof and replay
produce no new timing datum. The only visual added here is the proof-boundary
diagram, also embedded in the [PDF](report.pdf).

## Reproduction

```sh
python3.12 tools/rebuild_formal_root.py
cd formal
lake build
lake env lean AxiomAudit.lean
cd ..
python3.12 -m orchestration.formal.cli verify \
  --task-file formal/targets/ncp-affine-normal-form.yaml \
  --artifact-out /tmp/ncp-affine-receipt.json
```

The archive replay command is
`python3.12 research/verification/commutator_kernel1_check.py`, but it writes
its result JSON beside the script. This audit ran an exact copy of that script
and its frozen input under `/var/tmp` to preserve committed evidence.
To rebuild the PDF from the SVG and TeX sources, run `python3.12 render.py`
in this report directory with `svglib`, `reportlab`, and `tectonic` installed.

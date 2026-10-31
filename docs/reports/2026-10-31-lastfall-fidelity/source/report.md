# LastFall source theorem and hypotheses review — T-1105

Date: 2026-10-31. Reviewer: independent source session `/root/lastfall_source`.

**Assigned-joint verdict: holds.** The conditional mathematical claim in the
frozen target faithfully states Caminata–Gorla Theorem 2.8. Its explicit
finiteness assumption exposes an ingredient the paper establishes earlier.
The hypothesis that a degree fall exists is essential to a greatest-element
conclusion. The paper and target quantify the maximum over the generated
ideal, rather than merely over the original generators.

This verdict covers the source theorem, Definition 1.5, and their hypotheses.
It is not a machine verification or an evaluation of the finite-profile claim.
No Lean source, build receipt, or sibling review was read; no Lean build ran.
The coordinator owns the combined outcome.

## Immutable inputs and primary-source access

- Review plan: commit `2b0cfe1401831c9493cfe047a515955f38d037b8`,
  `docs/reports/2026-10-31-lastfall-fidelity/review_plan.yaml`;
  SHA-256 `8326616dea35f3fa45f3957fa8650338598a7fcf9d42ff274afaedcb48cb156e`.
- Claim snapshot and fetched `origin/main`:
  `199f3aaaa6d37d2fce59f4d8c8fe8d2eb8b50672`.
- Target: `formal/targets/lastfall-is-max-degree-fall.yaml`, especially lines
  27–31 and 41–73; SHA-256
  `74ecb7ee9f8dcf67e14e732bd8382498f648147a6a002d258e1d7b634e065ea9`.
- Producer note: `research/THM_FALLDEG_INVARIANTS1.md`, especially lines
  24–35; SHA-256
  `18a9ffd4c94288c097bb25d1908fbac1bd23348ed69dc3508b61ddbc5a9a4331`.
- Primary source: Alessio Caminata and Elisa Gorla, *Solving degree, last fall
  degree, and related invariants*, [ePrint 2021/1611](https://eprint.iacr.org/2021/1611),
  final revision dated 2022-06-01. The ePrint landing page was read; PDF access
  returned HTTP 403 through both web and curl.
- The authors' corresponding [arXiv:2112.05579v2 PDF](https://arxiv.org/pdf/2112.05579v2),
  dated 2022-06-01, was downloaded and read in full, including the references.
  SHA-256 `9e9323db0cd2f755a375c1baa836b999972fc38eebca3e6f55f63dfecb226177`.
  The matching title, authors, revision date, 16-page extent, and theorem
  numbering support use of this primary-source version; byte identity with
  the inaccessible ePrint PDF was not checked.

Paper citations below use the printed page number. Local extraction line
numbers refer to `pdftotext -layout` output from that exact PDF: setting on
p. 3, lines 128–142; Definition 1.5 and finiteness on p. 6, lines 245–264;
Definitions 2.5–2.6 and Lemma 2.7 on p. 9, lines 373–388; Theorem 2.8 and
proof on pp. 9–10, lines 392–406. Pages 6 and 9 were also visually inspected.

## Source correspondence

| Clause | Primary source | Frozen target | Assessment |
| --- | --- | --- | --- |
| Field and ring | p. 3, §1: arbitrary field; finitely many variables | lines 42–43 | Matches; no finite-field or characteristic restriction is needed. |
| Input system | p. 3 writes a finite list of generators | line 42 permits a subset | A mild generalization, justified below under the target's explicit finiteness hypothesis. |
| Initial vectors | p. 6, Definition 1.5 | lines 45–47 | Same degree-truncated generator inclusion. |
| Closure | p. 6, Definition 1.5 | lines 48–49 | Same multiplication closure for every element already in the space. |
| Last-fall quantifier | p. 6, Definition 1.5 | lines 51–52 | Both quantify over every element of the generated ideal with budget max(d, deg f). |
| Individual entry degree | p. 9, Definition 2.5 | lines 54–56 | Same least membership budget and strict inequality defining a fall. |
| Existence of a fall | p. 9, Theorem 2.8 | line 58 | Explicit in both; it makes the fall-degree set nonempty. |
| Finiteness | p. 6, paragraph following Definition 1.5; used on p. 9 | lines 27–31, 58 | Paper supplies it from Gröbner-basis existence; target assumes it. This is an explicit conditional scope. |
| Greatest fall degree | pp. 9–10, Theorem 2.8 | lines 60–73 | Same ideal-wide maximum and both inequalities. |

The paper defines auxiliary budgets at infinity and at −1. The target omits
those auxiliary values and asks for a finite last-fall degree. They do not
enter the finite maximum argument. The omission would matter for a claim to
formalize all of Definition 1.5, but does not alter this conditional theorem.
In particular, the paper's special `V_{F,-1} = empty set` should not be
silently identified with the zero vector subspace.

## Derivation checked in this review

This is a source-aware check, not the plan's blind re-derivation.
Let `I=(F)`, use nonnegative total degree with `deg(0)=0`, and let `V_i` have
the stated generator and multiplication closure. Then `V_i` lies in
`I ∩ R_{≤i}`, since that intersection is itself an admissible space. Also
`V_i ⊆ V_j` for `i≤j`: `V_j` satisfies every defining obligation for `V_i`.

For every `f∈I`, finite `d_F` gives membership at
`max(d_F,deg f)`, so the set defining `d_f` is nonempty. The degree bound on
`V_i` gives `d_f ≥ deg f`. No finiteness of the set of generators was used
in these deductions. Thus the target's arbitrary-subset wording is a valid
extension of this conditional argument, even though the paper's global
setup names a finite system.

Write `S={d_f : f∈I and deg f<d_f}`. For any witness in `S`, if
`d_F<d_f`, both `d_F` and `deg f` are less than `d_f`. Definition 1.5
would put `f` in a space with budget smaller than its minimum entry degree,
a contradiction. Consequently `S` is bounded above by `d_F`.
The fall hypothesis makes `S` nonempty, so this subset of natural numbers
has a maximum `mu`. For any ideal element, either `d_f=deg f`, or
`d_f≤mu`. Monotonicity gives membership in `V_{max(mu,deg f)}` in both
cases. Hence `mu` is an admissible last-fall budget, giving `d_F≤mu`.
Together the inequalities prove the target claim.

There is a local typo in the paper's first proof sentence on p. 9: it
starts with `f∈F`, whereas its displayed supremum and the argument require
`f∈(F)`. This was checked in the PDF image, not inferred from OCR alone.
Every generator already enters at its own degree, so restricting this step
to generators cannot bound all ideal-element falls. The target's proof
sketch uses the correct ideal-element reading. This source typo does not
supply a counterexample to the theorem; the preceding argument repairs
that quantifier explicitly.

## Empty and no-fall controls

These are exact mathematical checks, not measured trials.

| System in k[x] | Closure spaces | Last-fall degree | Fall-degree set | Theorem 2.8 applies? |
| --- | --- | --- | --- | --- |
| `F=empty` | `V_i={0}` for all natural i | 0 | empty | No: fall hypothesis fails. |
| `F={0}` | Same spaces as empty F | 0 | empty | No. |
| `F={x}` | `V_i=(x)∩R_{≤i}` | 0 | empty | No. |
| `F={1}` | `V_i=R_{≤i}` | 0 | empty | No. |
| `F={x^2,x^2+x}` | `V_0=V_1={0}`; `V_i=(x)∩R_{≤i}` for i≥2 | 2 | `{2}` | Yes. |

For `{x}`, multiplying the generator by every polynomial of degree at most
`i−1` gives exactly the polynomials in `(x)` of degree at most `i`.
Each nonzero ideal element therefore has `d_f=deg f`. For the positive
control, subtraction produces `x` at budget 2, while budget 1 contains no
nonzero generator and stays zero. Multiples of `x` fill the truncated ideal
at every budget at least 2. Thus both hypotheses are jointly satisfiable:
`d_F=2` and `d_x=2>1`.

An empty set has no greatest element. Giving an empty supremum the value
zero in an ordered type is a separate convention and cannot satisfy the
membership part of a greatest-element assertion. The no-fall branch is
instead covered by Lemma 2.7 (p. 9), which yields `d_F=0`.
The paper does not explicitly spell out the zero-polynomial degree convention.
The nonnegative convention used here makes `d_0=deg(0)=0`; alternatively,
exclude zero from fall witnesses. Counting zero as a strict fall using
`deg(0)=-infinity` would conflict with the paper's no-fall lemma and its
homogeneous examples. The concrete Lean convention is the other reviewer's
assignment.

## Adjacent source qualifications for the coordinator

These are source observations, not a verdict on the measurement joint.
On p. 4, `M_d` is the output after repeatedly reducing and adjoining
permitted multiples of newly produced lower-degree rows until closure.
Equation (1) on p. 6 refers to that object and a degree-compatible order.
The phrase “after reduction” in producer-note line 27 does not itself
spell out that iteration. Page 7 also expressly warns against stopping at
one equality of adjacent truncated spaces; Example 2.4 illustrates the
failure on pp. 8–9. The formal target's measurement prose at lines 13–16
therefore needs the separate review already assigned to T-1107.

The producer note's separate Theorem 2.9 line 35 omits the paper's explicit
fall-existence condition (p. 10). This is an adjacent source transcription
issue: for `{x}` its displayed maximum is empty unless a convention is
added. It does not change the correctly conditional Theorem 2.8 row.
No verdict is offered here on the note's other invariant or Weil-restriction
claims.

## Procedure, artifacts, and next action

The Conductor task T-1105 was claimed. The reviewer worked from the pushed
plan in a separate sparse worktree and wrote only this `source/` directory.
The checkout was compared with the claim snapshot for both target and note;
no differences were found. No sibling reports were opened. Repository
worktree metadata was listed for orientation; that did not expose sibling
report contents. The initial broad filename-only search was interrupted and
returned no files. No machine-verification verdict is claimed.

`review_attestation.yaml` lists actual source and instruction reads;
`source_manifest.yaml` binds the external PDF and local claim inputs.
`diagram.svg` and `report.typ` are editable visual sources; `report.pdf`
is the rendered source review. `visual-inspection.json` records inspection.
The canonical source note and target were checked as above. No canonical
graph was changed: this source joint confirms the existing conditional
theorem, and the reviewer's write scope excludes shared artifacts.

Next action: combine this source verdict with the independent Lean and
measurement reports; preserve the no-fall branch and the explicit finiteness
hypothesis when describing the conditional theorem. Any adjacent note
correction should be additive and separately scoped.

# PFSE WP0/WP1 source and family gate

**Date anchor:** 2026-10-31

**State:** partial planning artifact; no experiment approval, run, scientific
status transition, speedup, lower bound beyond a cited model, or universal
nonexistence claim is recorded here.

This artifact advances the first two work packages in
`docs/research/prime-field-subexponential-barrier-program.md`. It records exact
source access and freezes a reviewable draft of one family quantifier. It does
not materialize the document-local `PFSE-WP*` labels into official ledger IDs.

## Requirement-to-evidence table

| Requirement | State | Evidence or remaining gate |
| --- | --- | --- |
| Primary-source baseline for the generic lower bound | verified for this planning pass | Shoup full text and Theorem 1, below |
| Primary-source baseline for the original summation-polynomial proposal | verified for this planning pass | Semaev full text and Section 3, below |
| Exact scope of the isogeny random-reduction result | verified for this planning pass | Jao-Miller-Venkatesan full text, below |
| Exact Yokoyama et al. statistical assumptions and theorem boundary | blocked on full-text retrieval | gold-OA metadata and abstract retrieved; publisher returns an AWS WAF challenge; no theorem promoted |
| Exact Galbraith-Gaudry survey wording | blocked on file retrieval | HAL metadata and exact PDF path retrieved; file endpoint returns HTTP 403 |
| Choose one family quantifier | implemented as a draft | average case under `PFSE-FAMILY-AVG-ORDINARY-PRIMEORDER-V1` |
| Machine-check family/model/cost metadata | implemented and locally validated | `schemas/prime-field-ecdlp-family.v1.json` |
| Positive and negative curve fixtures | not implemented | seven required fixtures remain `verification_state: missing` |
| Independently checked sampler distribution | not attempted | requires a proof/review of conditional uniformity and termination assumptions |

## Sources actually read

### Shoup 1997 — generic algorithms

- **Source:** Victor Shoup, *Lower Bounds for Discrete Logarithms and Related
  Problems*, EUROCRYPT 1997, DOI `10.1007/3-540-69053-0_18`.
- **Retrieved artifact SHA-256:**
  `23490869d0a025360a642d754b953f2d589b73466b4a9e0ad183bcaf6e293e42`.
- **Read scope:** full 11-page paper, with Theorem 1 checked directly.
- **Theorem boundary:** for `Z/n`, where `p` is the largest prime divisor of
  `n`, a generic algorithm using at most `m` oracle queries has success
  `O(m^2/p)` when the hidden logarithm and injective encoding are random.
  Constant success therefore requires `Omega(sqrt(p))` generic queries.
- **Does not cover:** explicit affine/projective coordinates, base-field
  arithmetic, rational maps, factor-base predicates, polynomial-system
  solving, or other representation-dependent operations.

The theorem supports PFSE model `M0`. It is not a lower bound for the `M1-M4`
models in the parent program and does not establish that Pollard rho is optimal
among algorithms using the explicit curve representation.

### Semaev 2004 — summation-polynomial proposal

- **Source:** Igor Semaev, *Summation polynomials and the discrete logarithm
  problem on elliptic curves*, IACR ePrint 2004/031.
- **Retrieval:** the PDF endpoint returned HTTP 403, while the source's
  PostScript endpoint `https://eprint.iacr.org/2004/031.ps.gz` was accessible.
- **Retrieved PostScript SHA-256:**
  `991f85d58ab68551a229266d03c2f88a5fc42e81b2a5f8f4432937bcceff16df`.
- **Local PDF conversion SHA-256:**
  `3f610a38cb8c0546f2618c7527c0d18ee9c1bbae5f6987acdb90d39baa77fa4`.
- **Read scope:** full six-page paper.

Theorem 1 constructs the symmetric summation polynomials recursively and gives
degree `2^(m-2)` in each variable for `m >= 3`. Section 3 then fixes an arity
`m` (the paper writes `n`) and proposes finding bounded solutions to

```text
f_(m+1)(x_1,...,x_m,x) = 0 mod p.
```

The proposed factor-base coordinates are bounded by approximately
`p^(1/m+delta)`. The paper states that about `p^(1/m+delta)` nontrivial
relations are needed and gives the essential total-cost expression

```text
t_(p,m) p^(1/m+delta) + p^(2/m+2 delta),
```

where `t_(p,m)` is the cost of the bounded-solution algorithm. The text notes
that for `m >= 5` this could beat `O(p^(1/2))` even for some exponential
`t_(p,m)`, and immediately asks whether the required solver exists.

Thus the paper supplies a conditional architecture and an explicit open solver
obligation. It does not supply a subexponential prime-field ECDLP algorithm.
Any modern claim must additionally charge relation verification, independent
rank, complete linear algebra, target descent/recovery, memory, failed attempts,
and growing arity.

### Jao-Miller-Venkatesan 2004/2009 — isogeny random reduction

- **Source:** David Jao, Stephen Miller, and Ramarathnam Venkatesan, *Do All
  Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log?*,
  arXiv `math/0411378`, version 3.
- **Retrieved artifact SHA-256:**
  `c80586caaa2e4129b250d612b9f257cc1156cc839f2a17d791eb77ebfb5ab54e`.
- **Read scope:** full 26-page paper, including Theorem 1.1, Corollary 1.2,
  and the conductor-level discussion.

Under GRH, Theorem 1.1 gives expander mixing for small-degree isogeny graphs
inside one fixed endomorphism-ring level. Corollary 1.2 reduces DLP on any
curve in that level to an algorithm succeeding on a fixed positive proportion
of curves in the same level, with polylogarithmically many random queries.
Moving between levels requires separately constructible vertical isogenies;
the stated efficient bridge applies when conductor differences are
polynomially smooth. This is a random-reducibility result, not a generic cheap
map between arbitrary curves of equal order and not a source-scale ECDLP
speedup.

The transfer skill's six obligations remain separate for every future path:
existence, explicit construction, map correctness, subgroup preservation,
computational advantage, and scaling support. No future registry row may infer
the latter five from geometric existence alone.

### Yokoyama-Yasuda-Takahashi-Kogure 2020 — unresolved full-text gate

- **Source metadata:** *Complexity bounds on Semaev's naive index calculus
  method for ECDLP*, DOI `10.1515/jmc-2019-0029`, CC-BY, Journal of
  Mathematical Cryptology 14(1), 460-485.
- **Retrieved:** Crossref record, DOAJ record, OpenAlex record, and abstract.
  OpenAlex identifies a published-version PDF and GROBID XML.
- **Blocked:** the De Gruyter/De Gruyter Brill HTML, XML, and PDF endpoints
  return an AWS WAF challenge with an empty automated response. OpenAlex's
  content endpoint returned HTTP 401. The repository literature entry
  `KN-LIT-4558` names a local PDF under `downloads/`, but no such tracked or
  materialized file exists in the current checkout.

The abstract says that the authors analyze the PDP ideal, interpret its
Groebner-basis computation as an extension of the extended Euclidean
algorithm, obtain a lower bound on that computation, and under simple
statistical assumptions conclude that the **naive** method cannot outperform
generic methods. Until the full theorem is read, the exact ensemble,
probability space, cost unit, factor-base class, arity regime, solver class,
and preprocessing boundary remain unverified. `KR-IC-401ebf` therefore remains
an abstract-level heuristic pointer; it cannot close all prime-field index
calculus.

### Galbraith-Gaudry 2016 — unresolved survey file gate

- **Source metadata:** *Recent progress on the elliptic curve discrete
  logarithm problem*, DOI `10.1007/s10623-015-0146-7`.
- **Retrieved:** OpenAlex metadata and HAL record `hal-01215623`, including the
  exact author-manuscript path `DCC-survey.pdf`.
- **Blocked:** the HAL file and document endpoints returned HTTP 403 in this
  environment. No section-level survey claim is upgraded by this artifact.

## Reproduction commands for this gate

The successful Semaev retrieval and the family-schema validation used:

```sh
curl -L --fail --silent --show-error -A 'Mozilla/5.0' \
  https://eprint.iacr.org/2004/031.ps.gz -o /tmp/semaev-2004.ps
sha256sum /tmp/semaev-2004.ps
ps2pdf /tmp/semaev-2004.ps /tmp/semaev-2004.pdf
pdftotext -layout /tmp/semaev-2004.pdf /tmp/semaev-2004.txt

python3 -m json.tool schemas/prime-field-ecdlp-family.v1.json
python3 -m json.tool \
  research/prime_field_subexponential/family/baseline-average-family-v1.json
python3 -m jsonschema \
  -i research/prime_field_subexponential/family/baseline-average-family-v1.json \
  schemas/prime-field-ecdlp-family.v1.json
```

The commands completed with exit status zero using Python 3.12 and
`jsonschema` 4.26.0. The `jsonschema` command emitted only its CLI-deprecation
warning. Source downloads remain temporary reading artifacts and are not
ledger evidence or vendored publication copies.

## Draft family decision

The first concrete family chooses **average case**, because it supplies a
reproducible probability space for experiments without pretending that finite
sampling establishes a density-one theorem. The exact draft is
`research/prime_field_subexponential/family/baseline-average-family-v1.json`.

For each input scale `n`, the sampler conditionally samples:

1. an `n`-bit prime `p`;
2. a uniform nonsingular short-Weierstrass pair `(a,b)` over `F_p`;
3. a prime-order full group `#E(F_p)=r` with `bit_length(r)=n`;
4. a uniformly sampled nonidentity generator `P`; and
5. a uniform nonzero scalar `s`, with target `Q=[s]P`.

The resulting success probability averages, in declared order, over the curve
sampler, generator, target scalar, and algorithm coins. Results for this family
do not imply worst-case or density-one results.

### Exception boundary

The sampler rejects and retains as controls:

- singular coefficient pairs;
- non-prime or wrong-bit-length group orders;
- anomalous curves;
- supersingular curves;
- curves whose embedding degree is at most the conservative threshold
  `K(n)=floor(n^2/(log2 n)^3)`; and
- the immediately visible `j=0` and `j=1728` extra-automorphism families.

The embedding-degree rule is source-scaled. For a finite-field target
`F_(p^k)` and an `L[1/3]` destination algorithm,

```text
log T = Theta((k n)^(1/3) (log(k n))^(2/3)).
```

The condition for this expression to be `o(n)` is
`k(log(k n))^2=o(n^2)`. Every `k<=K(n)` satisfies a conservative instance of
that condition, so requiring a certified lower bound above the displayed
`K(n)` removes one explicit subexponential pairing-transfer range. It does not
remove every schedule satisfying the little-o condition. It is only a
classifier rule for that route, not a proof that admitted curves have no other
transfer.

### Cost and uniformity boundary

The draft requires a uniform classical randomized algorithm and disallows
nonuniform advice. Preprocessing may inspect the public family, curve,
subgroup, generator, and target, but every bit operation and stored bit is
charged. Single-target complexity is primary. Any reusable multi-target setup
must state the target count and remain a separate claim.

All of the following phases are mandatory: instance generation, setup,
preprocessing, transfer construction/evaluation, relation collection and
verification, solver, rank updates, linear algebra, descent, recovery, final
verification, repetitions, memory, persistent data, processors, and
communication.

## Cheap audits of the draft

The following audits must occur before `status: frozen`:

1. **Conditional-distribution proof.** Check that each rejection sampler gives
   the stated conditional distribution and document any unproved termination
   or prime-order-density assumption.
2. **Generator proof.** Check uniformity of the `x`/square-root/sign procedure
   under the odd prime-order condition.
3. **Embedding guard.** Independently verify that the finite range test really
   proves `k>K(n)` and benchmark only its classifier cost, not ECDLP hardness.
4. **Proves-too-much controls.** The classifier must reject verified anomalous,
   supersingular, small-embedding-degree, smooth-order, and special-`j`
   fixtures while accepting one ordinary prime-order fixture.
5. **Identity mutation.** Mutating `p`, `a`, `b`, `r`, the generator, or family
   revision must change or invalidate the `curve_uid`/certificate binding.
6. **Independent certificate replay.** Primality, point count, ordinarity, and
   embedding lower-bound certificates require a verifier independent of the
   producer implementation.

Schema validation alone discharges none of these mathematical obligations.

## Status and next bounded action

WP0 is partial: Shoup, Semaev, and Jao-Miller-Venkatesan have full-text support;
Yokoyama et al. and Galbraith-Gaudry remain retrieval-blocked. WP1 is
implemented as a schema-valid draft, but no fixture or independent review
exists, so it is not frozen.

The next bounded Coordinator action is to materialize two non-execution tasks:

1. retrieve and audit the Yokoyama full text, recording its exact assumptions
   and theorem coverage; and
2. implement the seven family-classifier fixtures and an independent
   certificate verifier against the draft schema.

Neither task authorizes a scientific run. Official IDs, queue placement,
approval, and status changes require the repository's authorized Coordinator
workflow.

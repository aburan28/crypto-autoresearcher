# Lifting residuals, circular linearizations, and equivalent-model controls

This is an implementation and navigation note for the bounded software controls
in `crypto_autoresearcher.index_calculus`. Search terms: Smart's attack,
anomalous curves, p-adic lifting error, formal logarithm, circular lifting,
factor-base correction, cocycle, equivalent models, and CM trace filters.

The instrument implements the proposed priority order: circularity checks,
equivalent-model comparisons, and a small residual exploration. It also includes
a constrained toy CM search. Its outputs are software diagnostics, not approved
experiment receipts, independent scientific review, or an attack-cost bound.
No goal, hypothesis, experiment, or knowledge confidence is changed.

## Locate and run the instrument

From the repository root after the normal editable install:

```sh
python -m crypto_autoresearcher.index_calculus representation-controls --help
python -m crypto_autoresearcher.index_calculus representation-controls \
  --experiment controls --out /tmp/lifting-controls-1.json
python -m crypto_autoresearcher.index_calculus representation-controls \
  --experiment models --out /tmp/model-controls-1.json
python -m crypto_autoresearcher.index_calculus representation-controls \
  --experiment residuals --out /tmp/residual-controls-1.json
python -m crypto_autoresearcher.index_calculus representation-controls \
  --experiment filters --out /tmp/cm-controls-1.json
```

Omit `--experiment` to run all four suites. Without `--out`, stdout contains one
JSON object. An existing output path is refused before work starts; use a new
path for each diagnostic. Scientific execution and archival still go through
the existing `run` workflow and the applicable experiment contract.

The implementation is in
[`representation_controls.py`](../src/crypto_autoresearcher/index_calculus/representation_controls.py),
with independent affine and projective arithmetic in
[`representation_arithmetic.py`](../src/crypto_autoresearcher/index_calculus/representation_arithmetic.py).
The private arithmetic restricts fields to `11 <= p <= 10000`, requires
prime-order reduction for lifts, and supports precision `N=2,3,4` only. Tests
also cross-check it against the existing index-calculus curve implementation.
It adds no dependencies or alternative execution skill.

## Circularity controls

For a public section `s`, the calibrated map is

\[
\phi_s(R)=\log_E([r]s(R))/p\pmod p.
\]

The section and projected map have separate addition and scalar diagnostics.
An arbitrary section need not preserve addition upstairs for the anomalous
projected map to work. Treating those two tests as interchangeable would reject
the positive control for the wrong reason.

| Control | Required interpretation |
| --- | --- |
| Anomalous curve with `r=p` | Calibrates a nonzero projected map and recovery |
| Ordinary curve with a naive lift and `r!=p` | Tests addition, scalar and lift-choice failures |
| Ordinary curve with public prime-to-p torsion splitting | A compatible lift can have zero projected signal |
| Compatible target lift forced using the known `k=12` | Compatibility is circular when its construction needs the answer |

The test set includes identity, inverse, wraparound, scalar `[r]P`, lift
perturbations, and all supported precisions. Fresh hidden-scalar challenges
use OS randomness; the candidate API receives only the curve, subgroup order,
base and target. Public challenge points and candidate answers are retained
for replay in the original group. Labels never enter the candidate API.

For prime `r!=p`, any additive map into `F_p` satisfies
`r*phi(P)=phi([r]P)=0`, hence is zero. This obstruction concerns the specified
codomain and additive law. It does not rule out coordinate methods in general.

`audit_additive_map(curve, mapper, seed=..., samples=...)` accepts a proposed
public-point-to-`F_p` callable for the same bounded algebraic checks.
Repeated evaluation of each sampled point also checks determinism.
`check_dependencies` rejects declared secret-scalar, secret-label and DLP-oracle
inputs. Neither sampled identities nor declared dependencies prove source-code
independence, efficient construction, or isolation. Candidate exceptions are
software failures and propagate; they are not negative mathematical evidence.

## Residual correction and its null control

For a known relation

\[
[a]P+[b]Q-\sum_i[c_i]F_i=O,
\qquad D=[a]s(P)+[b]s(Q)-\sum_i[c_i]s(F_i),
\]

`D` lies in the formal kernel. The experiment compares equal-size random,
small-coordinate and low-degree-function bases, splitting distinct relations
into training and held-out sets. It records finite-precision residual
valuations, exact degree-two coordinate fitting, a per-point linear fit,
analytic corrections, construction costs, and precision consistency.

The essential negative control is already explained by
[`KN-TECH-73630e`](../knowledge/techniques/KN-TECH-73630e.md): prime-to-`p`
torsion lifting preserves the group but supplies no new group-theoretic
information. Writing `s(R)=tau(R)+e(R)` with `tau(R)` the torsion lift gives

\[
\log_E(D)/p=a c(P)+b c(Q)-\sum_i c_i c(F_i),
\qquad c(R)=\log_E([r]s(R))/(rp).
\]

Thus one correction value per point predicts these fixed-instance residuals
exactly. Perfect held-out prediction by that model is a calibration result,
not a new mechanism. After splitting off the error, `[r]tau(R)=O` and the
projected formal signal is zero. Held-out relations reuse the same `P`, `Q`
and factor base; they do not establish fresh-target generalization.

The unresolved question is whether a structured factor base enables a
correction or decomposition method that **reduces the complete cost of the
matched, frozen index-calculus pipeline**, including construction. The broader
coordinate/valuation question remains
[`KN-OPEN-3417fc`](../knowledge/open-problems/KN-OPEN-3417fc.md). This note and
these software tests do not close it. Report the gap to matched rho separately;
beating rho is not a gate for recognizing an index-calculus improvement.

For the supported short-Weierstrass models and precisions,
`log_E(t)=t mod p^N`, with `t=-X/Y`: the next term starts in degree five and
`p>=11`. Higher precision is rejected. A zero residue is reported as valuation
at least `N`, not as exact zero upstairs. Projective operations use the
[RCB formulas](https://hyperelliptic.org/EFD/g1p/auto-shortw-projective.html);
source provenance is retrieved, with independent affine cross-checks in tests.

## Equivalent models and constrained search

Models are related by `(x,y)->(u^2*x,u^3*y)` for `u=1,2,3,5`, with the same
target points transported explicitly. Transported bases must produce identical
relation transcripts on a shared coefficient stream. Fresh coordinate bases
have matched sizes but can select different subsets. Reports retain exact EC1
source/model identities, the transport parameter, actual factor-base points
and their set digest, misses, successful relations, rank, verification, and
construction/search/solving CPU columns. Quadratic twists are excluded.

This is a two-factor-sum toy implementation, not the production Semaev pipeline
or its performance baseline. CPU timings are diagnostic observations, not
measured bounds or a stable ranking; memory accounting and a matched complete
pipeline comparison remain necessary before a cost claim.

The filter suite uses `j=1728` curves `y^2=x^3+a*x`. It checks necessary Hasse,
CM trace/norm and subgroup divisibility constraints before point counting.
Both search arms cache counts per curve across requested subgroup orders and
compare complete accepted sets. A subgroup-valid candidate is not thereby a
useful transfer or descent candidate.

## Search integration and source status

This top-level `docs/*.md` note is covered by the existing repository-corpus
staging rule in `kb/src/crypto_kb/ingest/repo_corpus.py`. The integration test
checks the actual staged document and its conservative repository-document
metadata. The normal corpus staging/ingestion path makes it available to
`search_knowledge`; this PR does not contact or mutate a hosted vector index.
Local source navigation also works immediately:

```sh
rg -n -i 'lifting residual|circular|factor.base correction' \
  docs/lifting-representation-controls.md
```

The user's source pointer is `bMATH_2020_HofmanSJ.pdf`, described as S. J.
Hofman's 2020 thesis on anomalous elliptic curves. That filename and the cited
sections/pages remain **user-reported, unverified pointers**: no readable
attachment or primary-source PDF was available in the initial workspace.
No literature record or author claim is inferred from it. The research
proposals above are proposed extensions, not novelty attributed to the thesis.

Repository retrieval used source-file search because this session exposed no
`search_knowledge` endpoint. The cited corpus entries were read directly at
base `47307afd2d4743c4b88e78da53f1e31ffd8b4de7`; an absent search hit would not
establish that a method had never been tested. Earlier standalone diagnostics
are not imported as scientific evidence or used to promote an internal finding.

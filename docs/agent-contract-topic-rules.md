# Topic-specific agent contract rules

These four sections are incorporated by reference from [AGENTS.md](../AGENTS.md). Their requirements remain normative for work in their topics. The text below is relocated from AGENTS.md; relative Markdown links are rebased for this directory.

## Intermediate-cost and asymmetric-access hypotheses

User instruction, 2026-10-06. In assessments of supplied or published claims
of hidden mathematical advantage, include costly intermediate advantages:
a hypothetical reduction from subgroup-size work r^(1/2) to r^alpha with
alpha < 1/2 may matter even when recovery remains expensive. The example
alpha = 1/3 is a threat-model assumption, not a discovered algorithm or a
required outcome. Do not dismiss a claim solely because it fails to make
recovery trivial; do not infer practical recovery from its exponent alone.

Keep mathematical existence, executable transfer, subgroup preservation,
destination-solver advantage, practical resources, and asymmetric access as
separate obligations. A hypothesis about agency capabilities or motives is
not evidence that a trapdoor exists. Distinguish a deliberately selected
weak instance from an unpublished method applying to honestly generated
instances, and distinguish both from implementation compromise.

Account for curve-specific construction and preprocessing, per-target work,
transfer and recovery, verification, failed attempts, memory, hardware, and
the exact number of targets reusing setup. Report cold-start and genuinely
amortized costs separately. Separate exponent changes, constant factors,
primitive costs, and hardware throughput. Faster known-scalar multiplication
alone does not establish faster unknown-scalar recovery.

Under the user's hidden-route scenario, public discovery must require
substantial deliberate work rather than routine inspection or accidental
rediscovery. An illustrative reconstruction cost near 2^60 operations is a
scenario parameter, not a measured bound or evidence of agency capability.
Define the operation unit, algorithm, success probability, memory, parallelism,
and uncertainty before interpreting that number. Keep public discovery cost,
designer setup with a retained witness, map evaluation, and destination solving
separate. Isogeny degree alone establishes none of these costs. Assess cheaper
equivalent routes as well as reconstruction of the exact withheld map; one
comparably useful public shortcut can defeat the claimed access asymmetry.

Treat secrecy as a separate hypothesis: identify the withheld information,
whether it can be reconstructed from public parameters, and whether a
comparably useful public route exists. A high-degree map is not automatically
cheap to evaluate or hard to reconstruct. State field and construction-family
restrictions; do not transfer composite-degree binary-field conclusions to
prime fields or prime-degree binary extensions without justification.

When the user stipulates layered adversary capability, assess a portfolio
rather than one all-purpose vulnerability. Record each hypothetical technique's
prerequisites, coverage, cost, reusable setup, access requirements, secrecy,
and failure conditions. Distinguish independent alternatives from methods
sharing the same dependency; do not assume independence or multiply speculative
probabilities. Include redundancy, complementary combinations, and what
remains available if one technique is disclosed, patched, or loses its advantage.

Model reserved capabilities and exceptional-use scenarios explicitly, including
activation constraints, scarcity, exposure risk, and the cost of losing secrecy.
These are stipulated game-theoretic assumptions, not observations of agency
behavior or proof of any particular mathematical capability. Alternative
implementation or protocol compromises do not refute an algebraic hypothesis
and do not replace an algebraic workstream the user has requested. Preserve
each requested track and its unresolved obligations.

Apply existing transfer, evidence, run-routing, and review rules. Missing
formulas or measurements remain open obligations. Bounded failure is not
universal nonexistence. This assessment rule adds no autonomous key-recovery
campaign, production-target exploitation, or scientific state transition.

## Papers

Manuscripts generated from this repository's results live under `papers/`,
one directory per paper, and nowhere else. The layout is the same in
`aburan28/cryptanalysis`, `aburan28/crypto`, `aburan28/crypto-autoresearcher`
and `aburan28/ml-cryptanalysis`:

- `papers/README.md` is the index: one row per paper (directory, title,
  status). Add a row when adding a paper; never add a paper outside `papers/`.
- `papers/paper.mk` is the shared build. A paper's `Makefile` sets `TEX`,
  `SECTIONS`, `BIB` and, for figures or other files the build reads,
  `ASSETS`, and includes it; the targets are `make`, `make check`,
  `make arxiv`, `make eprint`, `make deanonymize` and `make clean`.
- `papers/.gitignore` ignores LaTeX auxiliaries and submission bundles. The
  built PDF is committed next to its sources and rebuilt whenever a cited
  number, conclusion or figure changes.
- `papers/AUTHORS.example` is the author-block template. Sources stay
  anonymized (`\author{Anonymous}`); `make deanonymize` restores the authors
  from an untracked `AUTHORS` file.
- Each paper directory holds the root `.tex` (or the `.md` of a draft that is
  not typeset yet), its sections and bibliography, `README.md` (status banner,
  what it says, what it does not say, how to build, reproduction pointers, and
  the checklist owed before submission), `abstract.txt` (title, keywords,
  category) and the PDF.
- Claims follow the repository's evidence rules: every number cites a
  committed artefact in this repository or a sibling (prefix the path with
  `crypto:`, `cryptanalysis:` or `crypto-autoresearcher:`); a stage
  diagnostic is never reported as a speedup; every end-to-end row has
  verified answers; each change is classed as advance, engineering,
  relabelling or accounting. A draft is not submitted, posted or cleared for
  either until its README says so, and its README names the novelty audit
  and the measurements still owed.
- `make check` must pass (references and citations resolved, no LaTeX errors,
  no overfull boxes) before a PDF is recommitted.

## Knowledge retrieval

`kb/` is a derived, read-only MCP index over the corpus; no agent writes to it.
Call `search_knowledge` before asserting an avenue was tested or known to fail,
citing a paper or prior experiment, proposing a likely duplicate, or changing an
authoritative conclusion: start with 4–6 results, use exact identifiers, filter
by `field_type`/`source_type`, call `get_context` only where it affects the
conclusion, read `claim_status`, `evidence_level` and `authority`, report
contradictions rather than pick one, and never treat retrieval score as evidence
quality. A passage points to a record and is not a citation; a remembered paper
stays `recalled` until rule 9 is met. No result is not evidence of absence.
Deduplicate against the ledger with the generated `ledger/.index/*.jsonl`
(`tools/build_ledger_index.py`), not the corpus. Read only what a step needs:
tools and indexes before records, sizes before contents, run outputs by receipt
(`docs/agent-runtime-core.md`, "Reading discipline"). A path off disk in a
sparse checkout still exists (`docs/sparse-checkout.md`).

For the ten-lead campaign, the advisory handoff is
[`research/ten-lead-evidence/README.md`](../research/ten-lead-evidence/README.md).
Retrieve one lead with `python3 tools/scoped_evidence.py lead N --json` and keep
its scope, assumptions, non-implications and artifact bindings with citations.
This supplements KB retrieval; it changes no official research state and adds
no prerequisite to `run`. Missing private artifact access is an access gap,
never mathematical evidence against a lead.

## Weak-curve and isogenous-representative audits

Before weak-curve, CM/GLV/GLS, or isogeny-chain claims, follow [the loop
rules](../docs/endomorphism-rules.md),
[`audit-curve`](../.claude/skills/audit-curve/SKILL.md),
[`transfer`](../.claude/skills/transfer/SKILL.md), and
[`KN-TECH-6a2ef9`](../knowledge/techniques/KN-TECH-6a2ef9.md). They bind scope,
evidence, controls, costs, statistics, and labels. Evaluate
factored/mixed-degree loops with explicit working-field maps, subgroup action,
closure/recovery, bounds, and paired baseline costs. Trials use `run`; audits do
not change state. Structure or bounded-null evidence proves neither speedup,
impossibility, nor unknown-scalar recovery.

For ordinary curves record
`Delta_pi=t^2-4q=f_pi^2 D_K` and
`Z[pi]=O_(f_pi) subseteq End(E)=O_(f_E) subseteq O_K` separately.
`f_E|f_pi`; independently certify `f_E` unless `f_pi=1`. Label separable
`ell!=char(F_q)` edges from certified endpoint conductors:
`horizontal|ascending|descending|unresolved`. Koblitz
`tau`/characteristic-power Frobenius are inseparable. Conductors are leads,
not ECDLP-bit discounts. On a Koblitz subgroup, compare an isogenous endpoint
with the source's usable signed-Frobenius rho baseline, not a negation-only
baseline: an exact action of order `m` saves `sqrt(m)` expected transitions
over negation-only rho in the random-map model. Charge orbit handling before
calling that structural discount a measured advantage. Compare any per-step
transported action with the simpler control that maps the DLP once to the
Koblitz representative, solves there with native Frobenius, recovers the
same discrete-log scalar, and verifies it on the endpoint.

Koblitz calibration ladders separate collision-walk operations from fixed
target setup, walk starts, recovery, and verification; pair identical targets
and seeds across arms. Report `m`, `log2(r)`, and cofactor together because
degree alone is not the experimental scale. Keep negation-to-signed-`tau`
bits distinct from plain-to-signed-`tau` bits. Counts with differently omitted
canonicalisation costs do not yield a one-sided cost-ratio bound, and local
trail-cap restarts are retained diagnostics rather than failed overall solves.

The verified 2026-10-14 [conductor-gap
panel](../research/conductor_gap_panel_20261014/REPORT.md) retains 43 prime
directions, 102 order levels, and 131 conditional placements.  Its `m*k`
direct-torsion field values are ambient upper bounds unless an explicit
absolute-Frobenius orbit certificate says otherwise.  K-163/45,641 and
K-283/1,697 have exact abstract-representative x-orbit degrees 3,260 and
239,984; the retained K-163 relative-tower witness additionally certifies the
concrete degree-3,260 kernel line and reaches an endpoint, but stops before a
map.  A same-degree K-163 horizontal endomorphism control passes both
compositions on 1,024 targets and demonstrates that degree alone is not
evaluation cost.  None of these artifacts supplies a complete NIST vertical
map/dual transfer, charged attack, or weak-curve result.

Treat the completed 160,000-solve `m=37,41` [volcano-level
replication](../research/isogeny_volcano_level_replication_20261013/README.md)
and its [archive](../research/isogeny_volcano_level_replication_20261013/ARCHIVE.md)
as bounded proxy evidence. All six lower-level/crater negation-only pointwise
and simultaneous 95% bit intervals include zero. The three `m=37`
simultaneous 90% ratio intervals fit the frozen `[0.97,1.03]` equivalence
margin; the three wider `m=41` intervals do not, so global six-contrast
equivalence is false. No tested large-prime edge or interaction resolves from
zero. The crater negation-versus-native-`tau` total-operation gaps are 2.487
bits at `m=37` and 2.685 bits at `m=41`. These operation-count observations
establish no conductor-only weakness, executable transfer, or NIST-scale
claim; explicit maps, subgroup preservation, recovery, and complete pricing
remain separate obligations.

The completed `m=51` degree-271 [replication](../research/isogeny_volcano_m51_rho_20261013/README.md),
[archive](../research/isogeny_volcano_m51_rho_20261013/ARCHIVE.md), and
[machine-readable analysis](../research/isogeny_volcano_m51_rho_20261013/analysis.json)
add 25,600 verified solves across the crater and all 16 sampled floor
Frobenius orbits. The primary matched-`tau17` floor/crater association was
`+0.005762506` bits (fixed-orbit 95% CI
`[-0.032170483,+0.043374391]`; hierarchical sensitivity
`[-0.045717517,+0.059596468]`): the frozen `+/-0.10`-bit equivalence margin
was met and zero was not excluded. The matched-negation association was
`-0.019007692` bits (family-adjusted 98.75% CI
`[-0.065652733,+0.028717680]`). Action-control contrasts were compatible
with their frozen random-map predictions. The 16 primary orbit points ranged
descriptively from `-0.115702` to `+0.165501` bits; they are not per-orbit
inferences. All five fixed-orbit A/A gates passed, while the non-gating
hierarchical sensitivity crossed `+/-0.15` for `floor-tau17` and marginally
for `crater-tau51`, so it does not support an orbit-superpopulation claim.
This degree-271 prime-factor conductor level did not resolve a same-action
effect in this exact proxy scope. Its statement that the `f_E=120,871` level
and the `f_E=271*120,871` bottom were untested describes that earlier study,
not the later four-level run below. The result does not establish causal
conductor irrelevance, transfer, NIST scaling, an end-to-end advantage, or a
weak curve.

The completed `m=51` [deep endpoint scan](../research/isogeny_volcano_m51_deep_scan_20261013/README.md)
exhausted its frozen 3.6-billion-rank interval, certified 42 bottom/unique-
ascent-parent orbit pairs, and froze the first 32 distinct eligible pairs with
zero admitted or blocking failures. Every pair has source/bottom
`f_E=32,756,041=271*120,871`, parent `f_E=120,871`, and a certified
degree-271 ascending relation. These are endpoint and direction certificates:
the artifacts deliberately contain no serialized evaluator or dual and permit
no transfer claim.

The subsequent four-level [native-rho result](../research/isogeny_volcano_m51_deep_rho_20261013/RESULTS.md)
contains 20,480 verified solves over `f_E` equal to `1`, `271`, `120,871`,
and `32,756,041`. Scientific execution and integrity passed, but inferential
validity failed: the predeclared all-arm A/A release gate missed its
`+/-0.15`-bit boundary for A by `0.003036` bit and for B by `0.009038` bit.
All dependent primary-contrast inferential and equivalence labels are
therefore withheld. The largest pairwise point difference, `0.026350` bit
(about 1.8% in mean walk
operations), whole-gap `B-C=-0.000024` bit, large-factor summary
`M120871=-0.006404` bit, and ordinary difference-in-differences
`2I=+0.039892` bit are descriptive diagnostics only. They establish neither a
large-prime conductor effect nor its absence, and no weak-curve, transfer,
security-bit, or NIST-scaling claim follows.

A failed or non-estimable preregistered A/A or negative-control gate makes its
dependent empirical lane indeterminate. Preserve all records and descriptive
summaries, but withhold nonzero, null, equivalence, practical-significance,
conductor-effect, and weakness labels. The control failure is an instrument
alert, not evidence for or against weakness. Do not relax the margin post hoc
or run a conditional follow-up whose frozen prerequisite was a passing gate;
use a newly frozen independent replication, which can release only its own
inference.

Transfers require explicit maps, subgroup preservation, and complete costs;
advice supports only its holder. Singular/invalid formula-compatible companions
establish only **implementation-weak**; confirmation-only oracles need explicit
reductions. Use only **class-weak**, **weak representative exists**,
**source-transfer-weak**, **implementation-weak**, or **no weakness found in
scope**. Bounded or zero-hit statistics do not prove absence.

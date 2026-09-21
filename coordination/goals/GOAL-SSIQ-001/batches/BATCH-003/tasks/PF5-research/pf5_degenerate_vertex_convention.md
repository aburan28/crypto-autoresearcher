# PF-5 pre-freeze research + six-fix verification — EXP-SSIQ-58b642 / BATCH-003

Bounded, zero-compute research task per the Coordinator handoff. No experiment
runs, no solver, no graph construction were performed. All network fetches
below went through the pre-configured proxy (CA bundle
`/root/.ccr/ca-bundle.crt`); every fetch succeeded (no infrastructure
failures to record).

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified (orchestration.adapter doctor --probe not run)
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit, so the resolved
    identifier is self-reported rather than probed against
    orchestration/model-bindings.yaml.
```

Write scope for this task was exclusively this file. No other file in the
repository was modified.

---

## Part A — PF-5 research finding

### A.0 What the draft is asking (read from `experiments/EXP-SSIQ-58b642/specification.yaml`)

`inputs.graph_construction.degenerate_j_handling` and
`degenerate_j_handling_fallback` ask for two things, pinned before freeze:

1. The general convention at `j=0`/`j=1728` (multigraph-with-multiplicity,
   vs. degree-reduced simple graph, vs. something else) — with a citation.
2. The EXACT numeric multiplicity/degree pattern at `j=0` and `j=1728` in the
   2-isogeny (`l=2`) supersingular graph, **and its dependence on `p mod 12`**
   — specifically because the pre-registered prime-balance rule forces
   `p ≡ 11 mod 12` into the set, the one residue class where **both** `j=0`
   and `j=1728` are simultaneously supersingular.

### A.1 What I found and verified (with verbatim quotations)

**Source 1 — Sutherland, "Isogeny volcanoes," ANTS X (2012), arXiv:1208.5370.**
Retrieved as an HTML rendering via `ar5iv.labs.arxiv.org/html/1208.5370`
(cross-checked against `arxiv.org/abs/1208.5370`; the repository already
lists this paper as `KN-LIT-360` in `knowledge/sources.json`, `citation_verified: read`,
but its `knowledge/literature/KN-LIT-360.md` entry is a shallow
bulk-seeded stub with no content on this point, so the full text was
re-fetched here rather than relied on).

- **Definition 3 (the multigraph convention — resolves question 1):**
  > "The l-isogeny graph G_l(k) has vertex set k and directed edges (j1,j2)
  > present with multiplicity equal to the multiplicity of j2 as a root of
  > Phi_l(j1,Y)."

  and immediately after:
  > "Edges (j1,j2) not incident to 0 or 1728 occur with the same multiplicity
  > as (j2,j1). Thus the subgraph of G_l(k) on k\{0,1728} is bi-directed, and
  > we may view it as an undirected graph."

  This directly answers question 1: the standard convention is **(b)** —
  root multiplicity of `Phi_l(X,Y)` IS edge multiplicity, in a directed
  multigraph, and the graph is only guaranteed symmetric (hence
  undirected-viewable) away from `j=0` and `j=1728`. The draft's own text
  ("the standard treatment builds the modular-polynomial graph as a
  MULTIGRAPH where a root multiplicity of Phi_2(X,j) at a vertex is an edge
  multiplicity, not something to deduplicate") is confirmed correct by this
  source.

- **Section 2.5, on supersingular components (resolves the "does out-degree
  stay uniform" sub-question):**
  > "Thus the supersingular components of G_l(F_{p^2}) are regular graphs of
  > degree l+1 (every vertex has out-degree l+1, vertices not adjacent or
  > equal to 0 or 1728 also have in-degree l+1)."

  This is unconditional: **every** vertex, including `j=0`/`j=1728` when
  supersingular, has out-degree exactly `l+1` (=3 for `l=2`), counted with
  multiplicity — this follows purely from `deg_Y Phi_l(j,Y) = l+1`, an
  algebraic fact independent of automorphisms. It is **in-degree** that can
  fail to equal `l+1`, and only at `0`, `1728`, and their immediate
  neighbours. Later in the same paper (Section 3.2, on identifying
  supersingular curves): "If we attempt to 'find the floor' on the
  supersingular component of G_l(F_{p^2}) we will never succeed, since every
  vertex has degree l+1" — consistent restatement.

- **Remark 8 ("Special cases"), on the mechanism behind the asymmetry:**
  > "This 3-to-1 (resp. 2-to-1) discrepancy arises from the action of Aut(E)
  > on the cyclic subgroups of E[l] when j(E)=0 (resp. 1728)."

  This states the *general mechanism* (automorphism-group action on
  `l`-torsion subgroups) that produces the asymmetric multiplicity, and
  gives an explicit formula for the **ordinary-volcano** case (Theorem 7's
  setting: `j=0`/`j=1728` as an *ordinary* CM point of discriminant `-3`/`-4`,
  with `l` the varying isogeny degree): the number of distinct level-1
  neighbours is `(1/3)(l - (-3/l))` at `j=0` and `(1/2)(l - (-1/l))` at
  `j=1728`, with each such neighbour having a stated in/out multiplicity
  discrepancy.

### A.2 What I explicitly did NOT resolve, and why I stopped rather than reconstruct it

I attempted to evaluate Remark 8's formula at `l=2` by hand (Kronecker
symbols `(-3|2)`, `(-1|2)`) to get a numeric table for the supersingular
case. I stopped and discarded that attempt, for a concrete, checkable
reason: Remark 8's formula is stated **inside Theorem 7's setting**, where
`0`/`1728` is treated as an *ordinary* CM point and `l` is the isogeny
degree that varies (the volcano's "level" parameter) — not our setting,
where `l=2` is fixed and `0`/`1728` is itself *supersingular*, varying over
`p mod 12`. When I tried to sanity-check my hand evaluation against the
unconditional out-degree fact from A.1 (out-degree from `0` must sum to
exactly 3 across however many distinct targets exist), the "each target has
3 incoming edges from 0" phrasing in Remark 8 did not self-consistently
combine with the target-count formula for a general split/inert/ramified
case — only for the specific case I first tried did the arithmetic happen to
close. That is exactly the shape of a result I would be constructing myself
rather than reading off the page, which is what this task's instructions
and AGENTS.md rule 9 forbid. **I am not reporting a numeric per-(p mod 12)
multiplicity table**, because I could not obtain one directly stated for
the `l=2` supersingular case from this source, and constructing one myself
by extrapolating a formula given in a different (ordinary-volcano,
general-`l`) regime is exactly the guess this task told me not to make.

### A.3 A second, directly relevant primary source that changes the shape of the answer

**Source 2 — Charles, Goren, Lauter, "Cryptographic Hash Functions from
Expander Graphs," J. Cryptology 22(1):93–113 (2009).** This is the
foundational paper defining the Pizer-graph construction the draft contract
is built on (the draft's own `degenerate_j_handling` text cites "Pizer's
original construction papers"; this CGL paper is the standard modern
reference for exactly that construction, built directly on Pizer [Bull. AMS
1990, "Ramanujan graphs"] and Pizer [Ramanujan graphs and Hecke operators]).
Retrieved as a full-text PDF from the McGill-hosted author copy
(`https://www.math.mcgill.ca/goren/PAPERSpublic/CharlesGorenLauterHash.pdf`;
the IACR eprint mirror `eprint.iacr.org/2006/021` returned HTTP 403 through
the proxy — logged as an infrastructure outcome, not pursued further since
the McGill copy is the identical peer-reviewed published text, J. Cryptol.
2009, DOI 10.1007/s00145-007-9002-x).

Section 4 ("Pizer's Ramanujan Graphs"), verbatim:

> "The edge set is as follows: given a supersingular j-invariant j1, choose
> an elliptic curve E1 with j(E1) = j1 and a subgroup H1 ⊆ E1 of order
> l ≠ p ... Connect j1 to j2 := j(E2) where E2 is the elliptic curve
> E1/H1. A priori, since there are l+1 subgroups of order l, this gives a
> directed l+1-regular graph. **However, if we assume that p ≡ 1 (mod 12),
> then the graph can be made into an undirected graph** as follows: for
> each subgroup H1 ⊆ E1 of order l, there is a canonical choice of subgroup
> H2 ⊆ E2 (of order l) such that E2/H2 ≅ E1. We can identify the edge
> associated with H1 with the edge associated with H2. **The reason for the
> assumption p ≡ 1 (mod 12) is that, to say the subgroup H gives an isogeny
> Ei → Ej is not precise because you need to choose an identification of
> Ei/H with Ej, and that is not canonical (and the more automorphisms Ej
> has, the more noncanonical it is). If we assume that p ≡ 1 (mod 12), then
> the elliptic curves have no automorphisms other than ±1.** This
> non-canonicity is just up to automorphisms ±1, this works because the
> dual isogeny to −f is minus the dual isogeny of f."

This is the single most load-bearing finding of this task, and it changes
what "resolving PF-5" can honestly mean: **the foundational Pizer/CGL
construction does not give a general numeric multiplicity table for the
degenerate-vertex case either — it sidesteps the question entirely by
restricting the prime set to `p ≡ 1 (mod 12)`, specifically and explicitly
BECAUSE that residue class is the one where every supersingular curve has
automorphism group exactly `{±1}`, which is exactly what makes the
directed-to-undirected identification (and, by the same mechanism, the
edge-multiplicity bookkeeping) canonical and simple.** The paper states this
as its literal reason for the restriction, not as an aside.

The same page also states the CGL vertex-count formula, matching the
classical mass-formula fact independently confirmed in De Feo, "Mathematics
of Isogeny Based Cryptography" (arXiv:1711.04062, Theorem 47, citing
Silverman AEC2 Chapter V Thm 4.1):

> "The number of vertices of G(p,l) ... is `floor(p/12) + epsilon`, where
> `epsilon ∈ {0,1,2}` depending on the congruence class of p modulo 12
> ([Silverman AEC2, Chap. 5, Thm 4.1]). Later, we will impose p ≡ 1 (mod
> 12), in which case epsilon = 0."

De Feo's Theorem 47 gives the same formula explicitly by residue:
`floor(p/12) + 0` if `p ≡ 1 mod 12`; `+1` if `p ≡ 5, 7 mod 12`; `+2` if
`p ≡ 11 mod 12`. This is a solid, independently-corroborated, two-source
answer to the **vertex-count** half of the `p mod 12` dependence (and is
consistent with `M-DEGSEQ`/`C-CONNECTIVITY`'s existing WISDE cross-check),
but it is a count of *isomorphism classes*, not a per-vertex edge-multiplicity
table — it does not by itself give the exact multiplicity pattern PF-5 asks
for either.

**Which residues make `j=0` and `j=1728` individually supersingular** (the
standard facts `j=1728` supersingular iff `p ≡ 3 mod 4`, `j=0` supersingular
iff `p ≡ 2 mod 3` — jointly giving `p ≡ 11 mod 12` for "both") is classical
CM theory (Silverman, *Advanced Topics in the Arithmetic of Elliptic
Curves*, Ch. V) that both papers above cite but do not restate in the
passages I read; I have **not** located and quoted a primary-source passage
stating this specific criterion verbatim in this task, so I report it here
as a standard, widely-cited fact consistent with the draft contract's own
`inputs.graph_construction.method` text ("j = 1728 if p = 3 mod 4, j = 0 if
p = 1 mod 3" for the *ordinary*-seed branch, whose complement is exactly
this criterion) rather than as an independently re-verified citation.

### A.4 Bottom line for PF-5

- **RESOLVED, with primary-source citation and verbatim quotation:** the
  general convention is multigraph-with-root-multiplicity (Sutherland
  Definition 3); every vertex including `0`/`1728` has out-degree exactly
  `l+1`; only in-degree/undirected-symmetrization can fail at `0`/`1728` and
  their neighbours; and — the key new finding — **the standard published
  construction this contract descends from (CGL/Pizer) does not solve the
  general multiplicity case at all: it explicitly restricts to `p ≡ 1 (mod
  12)` so that the problem never arises**, because that is exactly the
  residue class where `Aut(E) = {±1}` for every supersingular curve.
- **NOT RESOLVED, and not fabricated:** an exact numeric multiplicity table
  at `j=0`/`j=1728` for `l=2`, broken out by the `p mod 12` residues where
  they ARE supersingular (`5`, `7`, `11`) — including the specific case the
  draft's prime-balance rule forces, `p ≡ 11 mod 12`. Neither source
  reached states this table; Sutherland's Remark 8 gives a formula for a
  different regime (ordinary volcanoes, general `l`) that I found does not
  safely transfer by hand-evaluation (§A.2), and CGL's paper explicitly
  avoids the case by construction rather than resolving it.

**Recommendation carried into the freeze decision (not a decision I am
authorized to make):** the underlying finding — that the paper the
contract's own convention is drawn from treats `p ≡ 1 (mod 12)` as a load-
bearing simplifying assumption specifically to avoid this exact problem —
is itself evidence relevant to `EXP-SSIQ-58b642`'s design, not just to
citing a number. The contract's prime-balance rule *deliberately* forces the
harder case (`p ≡ 11 mod 12`) precisely because avoiding it would bias the
degenerate-vertex risk out of the tested set; that tradeoff is a Coordinator
decision, not resolved by this research task, but the fact that the
foundational literature does not provide a ready-made numeric answer for
that harder case should inform how much independent verification effort the
Executor budgets for `M-DEGSEQ`/`C-DEGSEQ` at run time, and supports
`degenerate_j_handling_fallback`'s STOP-and-report instruction being taken
seriously rather than treated as a remote edge case.

---

## Part B — Six-fix verification (against RT-PREFREEZE §10)

Read in full from the current
`experiments/EXP-SSIQ-58b642/specification.yaml`. This is a verification
pass against each fix's own required text in RT-PREFREEZE-EXP-SSIQ-58b642.md
§10, not a fresh critique.

| Fix | Required (RT §10) | Location in current spec | Verdict |
|---|---|---|---|
| PF-1 | Pre-registered C-CAL-GAP control, gating before Phase 1, with a stated recovery tolerance | `controls[0]` id `C-CAL-GAP` (lines 236–280): `order: "PHASE 0 -- runs BEFORE any real graph is built..."`; two synthetic pairs (constant-offset with ≥2 `c` values; saturating/capped variant tied to the sentinel rule); `failure_consequence` says STOP before Phase 1; explicit `+-0.10` recovery tolerance (line 261); also gated in `stopping_rules` (lines 394–398) and `invalidation_rules` (line 411) | **PASS** |
| PF-2 | Non-reaching greedy-start handling specified (population-wide median + sentinel), `trapped_fraction` reported, a void threshold | `metrics.primary[0].pf2_censoring_rule` (lines 131–149): population-wide median over ALL N starts, never survivor-restricted; sentinel = graph's own BFS-computed diameter; `trapped_fraction(N)` computed and reported for both real and shuffled labels; void threshold `trapped_fraction(N) > 0.5` → prime's `gamma_greedy` reported VOID; also in `invalidation_rules` (lines 414–417) | **PASS** |
| PF-3 | Prime selection matches the ~2000-vertex ceiling (not the 5000–24000 contradiction), staying inside WISDE's exhaustive block | `inputs.primes.selection_rule_pf3_corrected` (lines 96–112): `p <= 22000`, `p/12` spread few hundred to ~1800 vertices, inside WISDE's exhaustive block, `p mod 12` balanced across `{1,5,7,11}`; old bound retained but struck-through-in-substance as `superseded_size_bound_note` (lines 113–120), not silently deleted | **PASS** |
| PF-4 | Tie-break rule named explicitly and content-derived (not discovery-order-derived), with a tie-frequency diagnostic | `tie_break_rule.pf4_fix_applied` (lines 188–201): sha256 over `(delta_E value, tied neighbours' own j-invariant field-element representations, sorted)`, explicitly independent of BFS order/vertex ID; `metrics.secondary[2]` `M-TIEFREQ` (lines 178–187) reports tie frequency for both real and shuffled-label arms alongside M-GAP | **PASS** |
| PF-6 | `required_artifacts` lists `command.txt` not `code.txt`; manifest-body obligation stated as separate from companion files | `required_artifacts` (lines 445–456) lists `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json` (no `code.txt`, no `inputs.json`); `required_artifacts_note` (lines 457–472) states the five companion files explicitly AND states "THIS IS A SEPARATE OBLIGATION FROM THE FIVE COMPANION FILES: manifest.yaml's BODY must independently satisfy RUN_REQUIRED_TOP ... with code.commit and code.command populated as sub-keys" | **PASS** |
| PF-7 | `falsification_criterion` avoids "falsified"/"refuted" in favor of "unresolved by this test" / "not supported at this scale" | `falsification_criterion` (lines 436–444): "NOT SUPPORTED AT THIS SCALE if ... Record this outcome as 'unresolved by this test,' NEVER as 'falsified' or 'refuted'" — the forbidden words appear only as named prohibitions, not as assertions | **PASS** |

No new blocking finding was raised outside the original seven; nothing found
contradicts a fix's own stated intent.

---

## Overall recommendation

**NOT READY-TO-FREEZE — PF-5 is not resolved to the standard the draft
itself set (`degenerate_j_handling`: "the EXACT multiplicity pattern ...
must be pinned from a cited primary or secondary source ... BEFORE this
contract may be frozen").**

What IS now available for the Coordinator, from this task:

1. A cited, quoted, primary-source-confirmed general convention
   (multigraph/root-multiplicity; uniform out-degree `l+1`; asymmetry
   confined to `0`/`1728` and neighbours) — §A.1, sufficient to replace the
   draft's uncited "the standard treatment" language with a real citation.
2. A cited, quoted, primary-source finding that the literature this
   contract's convention is drawn from (CGL/Pizer) does **not** solve the
   general-`p`-mod-12 multiplicity case, and instead avoids it by
   restricting to `p ≡ 1 (mod 12)` — §A.3, directly relevant to why no exact
   table for `p ≡ 11 mod 12` was found.
3. An honest, explicit non-result: no exact numeric multiplicity table for
   `l=2` at `j=0`/`j=1728` by `p mod 12` class, despite a real attempt
   against the three named sources plus one additional directly-relevant
   primary source — §A.2, §A.4.

The six other fixes (PF-1, PF-2, PF-3, PF-4, PF-6, PF-7) all PASS
verification against RT-PREFREEZE §10's own required text.

**Concrete options for the Coordinator, not a decision this task is
authorized to make:**

- (a) Route PF-5 back for an amendment: either commission an actual
  independent verification (computing the `l=2` multiplicities at `j=0`/
  `j=1728` directly, e.g. from Vélu's formulas over the relevant residue
  classes — the CGL paper (pp. 97–99) gives the exact Vélu formulas needed
  for such a computation) as part of the run's `C-EDGELIST` pre-run
  correctness gate rather than as a pre-freeze literature fact, since the
  literature itself treats this as a computation to avoid rather than a
  fact to look up; or
- (b) Accept `degenerate_j_handling_fallback`'s STOP-and-report path as the
  intended behavior for this contract's `p ≡ 11 mod 12` case specifically —
  i.e., freeze the contract on the understanding that if the Executor
  cannot independently verify the exact multiplicity at run time (which
  this task confirms is a real risk, not a hypothetical one, since even the
  foundational literature avoids the general case), the run STOPs and
  reports the underspecification per `invalidation_rules`, rather than
  guessing.

Either path is a Coordinator decision; this task's write scope did not and
should not choose between them.

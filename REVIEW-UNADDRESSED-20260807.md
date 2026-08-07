# Evidence review and gap register — 2026-08-07

**Scope of the request.** Review all the evidence in this repository and propose new
ideas for every problem that has not been addressed or explored.

**What this document is.** An evidence review that separates three things the ledger
currently conflates — work that was *designed and never run*, work that was *closed
without a successor*, and questions *nobody has framed* — and a register of the third
and second kinds. Thirty-two new `IDEA-20260807-*` records in `ledger/proposals/`
carry the proposals; this document is the register and the audit trail behind them.

**Authority.** Nothing here changes a hypothesis status, approves an experiment,
adopts a convention, or transitions a goal. Several findings below *are* Coordinator
actions and are reported rather than taken (AGENTS.md rule 1). No hypothesis, run,
evidence, or knowledge record was edited; the branch adds files only.

**Base commit.** `e34afdd0`, branch `claude/unaddressed-problems-ideas-1d77zi`,
0 commits ahead of and behind `origin/main` at review time.

---

## 1. Method

A deterministic pass over the committed ledger built the linkage graph
(`RQ → H → EXP → EV`, plus knowledge-corpus reference counts). Ten independent
readers were then dispatched over disjoint slices of the evidence corpus with a
common instruction set: cite only records actually opened, name the nearest existing
record for every claimed gap and say why it does not cover the gap, and grep all 278
existing proposals before reporting anything.

**Five of the ten slices completed** (ECDLP core, ECDLP-adjacent orphans, supersingular
isogeny, lattice schemes, and the multivariate/code/hash/symmetric family), reading
402 records between them and returning 37 gaps. **Five did not**: `never-launched`,
`closed-and-paused`, `methodology`, `literature-debt`, and `cross-cutting` all failed
on a session usage limit, as did the automated consolidation step. Consolidation,
dedupe and ranking were done directly instead.

The five failed slices are **partly** covered by the top-level session's own
deterministic analysis — all 14 draft goals' `next_action` fields were read directly,
as were every paused and closed-at-budget goal's, the source-gate constraint on all
52 questions, and a 400-entry sample of the unreferenced literature. They are **not**
fully covered: see §6 for what remains unexamined.

---

## 2. What the evidence corpus actually looks like

| Records | Count |
|---|---|
| Research questions | 52 |
| Hypotheses | 249 |
| Proposals (before this review) | 278 |
| Evidence | 286 |
| Decisions | 412 |
| Goals | 45 (21 active, 14 draft, 2 paused, 5 completed, 3 closed at budget) |
| Knowledge | 7,819 literature · 89 techniques · 52 findings · 28 open problems |

**Claim tier of the evidence:** `toy` 188, `theory` 44, `medium` 10, `crypto` 2.
**Direction:** the modal outcome is `neutral` (124); `supports` 64; `refutes` 3.
**Proof status:** `derivation` 112, `empirical_only` 108, **`certificate` 1.**

That last row is the shape of the whole corpus: a large, careful, almost entirely
toy-scale body of measurement with one certificate in it.

---

## 3. Execution debt — designed, never run. Not an idea problem.

This is the largest single category and it needs **dispatch, not proposals**. Counted
across the five completed slices:

- **ECDLP core:** 18 frozen contracts with zero run directories, including
  `EXP-IC-002` (the yield-charged descent control that `DEC-20260727-008` says has
  "NO MEASURED REPLACEMENT") and `EXP-TLD-0a6b4d` + `EXP-AOM-e057f7`, the two
  contracts that would attack `KN-OPEN-019`'s enumeration.
- **Isogeny:** 14 contracts, 4 of them `approved` and dispatchable now — including
  `EXP-SSI-9b542d`, which `GOAL-SSI-001`'s own `next_action` names as *the* single
  next action, and `EXP-P13-NC36`, whose dispatch contingency was explicitly cleared
  when FC-4 did not fire in `EV-WESO-b6ceff` and which has still never run.
- **Lattice:** 35 frozen contract directories; every HAWK, FN-DSA and FrodoKEM
  hypothesis has no evidence record.
- **Multivariate / code / hash:** 15 contracts stuck at `review_required` — designed,
  never approved, never run.
- **ECDLP-adjacent:** 7, including `EXP-PMA-001` and `EXP-JMV-001`, both on `approved`
  hypotheses.

**One correction to the framing this review started from.** The "26 of 52 questions
have zero evidence" figure that motivated the survey is **partly an artifact**. Two
distinct causes:

1. `EXP-TTN-001/002`, `EXP-NCP-001`, `EXP-EQJ-001`, `EXP-TRA-001` and `EXP-INCB-001`
   *did* run and carry evidence at the legacy path `ledger/EV-*.yaml` rather than
   `ledger/evidence/`. A path artifact, not execution debt.
2. More seriously — the evidence schema has **no `question_id` field at all**.
   `RQ-SSI-001` produced 49 `EV-SSI-*` records through `GOAL-SSI-001` and not one is
   traceable to it. Two evidence records put `IDEA-*` proposal ids in the
   `hypothesis_id` slot. This is `IDEA-20260807-d7ef50`.

---

## 4. The gap register

Each row names the proposal that now carries it. "Cheap" means the decisive first
step needs little or no compute.

### 4.1 Prime-field ECDLP

| # | Gap | Proposal |
|---|---|---|
| 1 | **The path-algebra negative was forced before it ran.** `EV-NCP-001`'s boundary names the tested object: "quiver {T_Pi}+{neg} only (no isogeny arrows)". A one-vertex quiver whose arrow group is virtually abelian abelianizes by construction. Both `KN-OPEN-008` and `KN-TECH-014` define the intended object as including *correspondences*; that arrow class was never built. `DEC-20260804-139a86` nonetheless lists "NCP" among directions closed program-wide. | `IDEA-20260807-0085af` |
| 2 | **The transfer-operator barrier is a property of the partition, not the walk.** x-interval cells identify `P` with `−P`, which is exactly what forces reversibility (residual 2.5e-17) and a real spectrum (max \|Im λ\| 3.7e-16). `EV-TRA-001`'s own confounds say non-symmetric partitions are untested. Zero sampling needed to check. | `IDEA-20260807-018769` |
| 3 | **Bond tensors were measured DRAMATICALLY low-rank and only ever gated on lossy truncation.** Ranks 3, 6, 15 where full would be 3, 25, 81; `χ(m) = C(2^{m−3}+2, 2)` exactly, field-size independent. The exact `χ(m)`-term factorization was never costed as a construction algorithm. `KN-OPEN-007`'s "Current state" says *"bond ranks near full"* — the opposite of the committed evidence. | `IDEA-20260807-049ed4` |
| 4 | **`KN-OPEN-018` names its own cheapest closure route and records "Neither has been attempted here."** The GGM simulability screen exists and has closed four oracle families; a lattice-embedding oracle has never been defined as a class. | `IDEA-20260807-0f49b6` |
| 5 | **`H-ENDO-001`'s only two claims with algorithmic content were never measured.** `EV-ENDO-001` reports ZERO RUNS and refutes only the eigenvalue *source*; `DEC-20260728-005` records "RC-6 IS NOT DISCHARGED". No successor exists. | `IDEA-20260807-285ff4` |
| 6 | **The relation matrix has never been measured as an object**, although `FINDING-PF-IC-001` says the linear-algebra stage *dominates* the cost. The only end-to-end run records one datum ("45/54 FB discrete logs solved"), never followed up. | `IDEA-20260807-291968` |
| 7 | **Arity m ≥ 4 has zero measured cost cells anywhere.** The cost model is *decreasing* in m; `EV-R6-001` censored every m=4 arm; under AGENTS.md rule 3 those timeouts are not evidence. `EXP-ICEX-146ff5` sits in a three-decision routing deadlock. | `IDEA-20260807-32f96d` |
| 8 | **Every banded statistic is calibrated on one curve instance per cell.** `DEC-20260801-015` calls this "THE SINGLE LARGEST HOLE THE CAMPAIGN HAS DECLARED" and prices the fix at ten minutes. It was orphaned by a batch-label collision (`CORR-20260803-77d5da`), not by a decision on its merits. It silently scopes four evidence records. | `IDEA-20260807-347a83` |
| 9 | **A 152-σ signal was filed as "not the kill" and dropped.** `EV-EQJ-001`'s negative control did not fire; `DEC-20260718-006` logged the distinct-row collapse "for the idea pool" and the idea pool never received it. | `IDEA-20260807-394cf4` |
| 10 | **A one-sided gate cannot see a deficit.** `EV-INCB-001` found EC 15–35 % *below* its own uniform-x prediction, systematic in sign in every fittable cell, "recorded, not explained" — outside the predeclared gate's direction. | `IDEA-20260807-490c34` |
| 11 | **`KN-OPEN-009`'s exploitable branch was disposed of in one clause.** The monodromy is `C_2^{m−2}` — *smaller* than symmetric, which under the entry's own framing is the exploitable case. No cost model, no measurement. `GOAL-MONO-001`'s committed `next_action` says the opposite of the closure, and the corpus entry still asserts the refuted premise. | `IDEA-20260807-5126f4` |
| 12 | **Seven headline barrier claims exist only as unreviewed decision prose.** The 2026-08-04 closure series' batches contain a `tasks/` directory and **no `reviews/` directory at all**. `DEC-20260805-7b3e91` converted their `promoted` lists to `owed_promotions`, recording that they "made the record assert the opposite of the truth". `KN-OPEN-005` and `KN-OPEN-009` still read `status: open`. | `IDEA-20260807-5a8d61` |
| 13 | **Two approved hypotheses rest on "the paper is not in the corpus" — and it is.** `KN-LIT-171` *is* Jao–Miller–Venkatesan, bulk-seeded from a PDF's first two pages two days before `RQ-JMV-001` was admitted. The question's `knowledge_gap` is wrong in every particular (wrong DEC id, an already-taken KN-LIT id, a false "no entry" claim). Gap G3 has no hypothesis and reaches the queue only behind two unapproved experiments. | `IDEA-20260807-63ab15` |

### 4.2 Supersingular isogeny

| # | Gap | Proposal |
|---|---|---|
| 14 | **The entire exponent programme is classical-only.** The word "quantum" occurs **zero** times in `GOAL-SSIQ-001`'s record and all 13 checkpoint shards, in `GOAL-P13-001`, and in every `EV-SSIQ-*` / `EV-WESO-*` record — while the 2^{120–123} figure is compared against a NIST-I target anchored to AES-128 key search. | `IDEA-20260807-6c89a8` |
| 15 | **The one avenue the campaign's own producer called "The only open avenue" was closed by a sibling artifact from the same task**, without doing the action that artifact called "zero-compute, decisive, and maximal-payoff": read `KN-LIT-7641`. That entry is cited by **zero** records. The contradiction was never adjudicated. | `IDEA-20260807-6cdff2` |
| 16 | **CSIDH has no goal anywhere**, and its only lane was deferred as "requires quantum resources" — which is wrong, since a collimation-sieve cost estimate is classical analysis. `KN-OPEN-014` has no hypothesis, no experiment, no evidence. | `IDEA-20260807-726e55` |
| 17 | **Levers L2 and L3 are `OPEN, changed_this_batch: false` in all thirteen checkpoints.** Thirteen batches went to L4 at a single prime. L2 is the only lever that moves *time and memory together*, and memory is what `EV-SSI-59f7a2` identifies as making the attack physically impossible. | `IDEA-20260807-7424a9` |
| 18 | **`KN-OPEN-015` is used only as a scope fence.** Its actual question — which auxiliary data is fatal, in general — is framed by no record. The exclusion discipline actively pushes away from studying it. | `IDEA-20260807-7d8ba9` |
| 19 | **SQIsign, the only isogeny Round-3 candidate, has two never-launched goals and zero evidence** — while the program publishes a "SQIsign NIST-I" figure that `GOAL-SSI-001`'s own `next_action` records as a still-owed correction, because it labels a OneEnd cost as a scheme security level. | `IDEA-20260807-86e43e` |

### 4.3 Lattice

| # | Gap | Proposal |
|---|---|---|
| 20 | **Eighteen ML-KEM batches ran on relayed cost constants** (`c_T = 0.292`, `c_M = 0.2075`, crossover 70). `GOAL-MLKEM-003` closed with C1 unmet because "no measurement of sieve behaviour exists anywhere in this campaign"; `GOAL-MLKEM-004` then built a working sieve instrument and pointed it at *score geometry* for six batches. Separately, **no lattice claim has ever been positioned against a public challenge record** — `KN-TECH-049` prescribes exactly that and is cited by zero records, as are `KN-TECH-041/042/043/045`. | `IDEA-20260807-8fbc86` |
| 21 | **HAWK's unconditional reduction bottoms out in exact SVP at dimension 257 / 513, and nobody here has costed it.** The 2^108 / 2^182 figures are relayed from the paper's own gate model. The goal is dormant with criterion 1 unmet, a week before a recorded tweak deadline. | `IDEA-20260807-90479e` |
| 22 | **`RQ-FHE-001` has zero hypotheses, zero proposals and zero evidence**, and the one step its own constraints do *not* block — extracting shipped default parameters from library source, its declared fifth method — has never been taken. | `IDEA-20260807-a06996` |
| 23 | **Seven lattice goals rest on MLWE hardness and none prices the quantum reduction route.** `KN-OPEN-8a5965`'s Q2 is a reduction-*reach* question answerable independently of whether Simon's proof stands. `KN-TECH-d1bc4f` and the entry itself are cited by zero records; "dihedral" and "DCP" return nothing across 278 proposals. | `IDEA-20260807-abacec` |
| 24 | **`GOAL-MLKEM-004` closed saying "THIS IS BUDGET EXHAUSTION, NOT A METHOD CEILING … A successor should open", named that successor's first batch concretely, and no successor opened.** The surviving 4–9 % residual is the only quantity in five batches to survive every ablation either reviewer could construct. | `IDEA-20260807-aea945` |

### 4.4 Multivariate, code-based, hash-based, symmetric

| # | Gap | Proposal |
|---|---|---|
| 25 | **Four Round-3 goals declare a shared plain-UOV accounting basis a prerequisite; it does not exist; three hypotheses have already each derived their own** — the exact divergence `GOAL-UOV-001` warned against, now committed three times. Separately, three proposals independently assert exponent-neutrality for whipping, quotient-ring and matrix-ring structure, and **none cites the other two**; the conjunction is stated nowhere. | `IDEA-20260807-b63f08` |
| 26 | **The AES campaign's Tier-1 publication candidate rests on a localisation `CORR-20260803-8fa302` records as "HALF ESTABLISHED, HALF NOT"** (by nesting, removing the 13 excess k=4 events leaves z = +0.69). The record prices the fix at 2^38 trials; the conditional statistic `P(k=4 \| k=3)` is far cheaper. The k-profile measurement exists only as a coordination artifact, never reached a validator, and has no claim tier. | `IDEA-20260807-bbefda` |
| 27 | **ISD-FC-2026 — complete, independently reviewed, genuinely scheme-independent — has no adopting decision.** One task already *declined* to transcribe published data, deferring to the non-existent binding. Three code-based goals cannot produce comparable figures. `DEC-20260803-a5b9b1` calls it "the THIRD occurrence of the error family". | `IDEA-20260807-c3267e` |
| 28 | **Hash and permutation primitives are ideal objects in every record and probed in none.** `RQ-SLHDSA-001` says the scheme's assumption is hash properties only, then lists four targets, none of which is the hash. `KN-TECH-066` is cited by zero records. The scheme-specific axis — a fixed public seed over a publicly computable ADRS-domain-separated index set — is where a result could exist that the general literature would not contain. | `IDEA-20260807-c4f1fc` |

### 4.5 Harness and sources

| # | Gap | Proposal |
|---|---|---|
| 29 | **The evidence schema has no `question_id` field**, so 49 records bear on `RQ-SSI-001` and none is traceable to it; two put `IDEA-*` ids in the `hypothesis_id` slot. Every zero-evidence count the program uses to choose its next batch inherits the error — including the one that framed this survey. | `IDEA-20260807-d7ef50` |
| 30 | **Zero of the 28 `KN-OPEN` entries concern multivariate, code, hash or symmetric cryptanalysis**, although that slice holds 13 goals and 15 frozen contracts. Three well-characterized open questions sit in decision prose that no ideation session reads by default. | `IDEA-20260807-e051e7` |
| 31 | **The source gate is measurably not shut.** See §5. | `IDEA-20260807-f73d98` |
| 32 | **7,573 of 7,819 literature entries are cited by nothing, novelty screens are keyword greps over that corpus, and no record has measured whether they find prior art the corpus already contains.** | `IDEA-20260807-fa706a` |

---

## 5. The source gate — measured, not assumed

22 of 52 research questions carry a constraint of the form *"No experiment may be
designed until the relevant primary sources are read and filed as KN-LIT entries."*
Eleven of the fourteen never-launched goals name that gate in `next_action` as the
reason they have not opened. `GOAL-FRODO-001`: **"THE SOURCE GATE IS SHUT AND MUST BE
OPENED FIRST."**

`PUBLICATION-CANDIDATES.md` (2026-08-02) states the premise:

> "no primary source is reachable from this environment (eprint.iacr.org,
> csrc.nist.gov, arxiv.org all blocked)"

**Measured from this environment on 2026-08-07:**

| Source | Result |
|---|---|
| `nvlpubs.nist.gov` FIPS 203 | 200 — 1,252,341 B, valid PDF 1.7 |
| `nvlpubs.nist.gov` FIPS 204 | 200 — 3,291,746 B, valid PDF 1.7 |
| `nvlpubs.nist.gov` FIPS 205 | 200 — 1,055,752 B, valid PDF 1.6 |
| `csrc.nist.gov` | 200 |
| `arxiv.org` PDF | 200 — 706,116 B, valid 6-page PDF |
| `eprint.iacr.org` abstract page | 200 — correct title, authors, abstract |
| `eprint.iacr.org` `/NNNN.pdf` | 403 — **Cloudflare JS challenge**, not a policy block |

`GOAL-MLDSA-002` is blocked on acquiring FIPS 204. `GOAL-SLHDSA-001` on FIPS 205.
Both download today.

The gate itself is the right prohibition — designing experiments on secondhand
figures is exactly what should be forbidden. What is wrong is that it opens and
closes on an **inherited, undated premise** rather than on a measurement. The proposal
builds a per-source dated reachability probe that a gate can cite. Note also that the
weekly `GATHER` pipeline reaches eprint listings and the arXiv API successfully and
records DBLP as unreachable *with the routes tried* — that discipline already exists
in one place and is what this generalizes.

---

## 6. Reported, not proposed — and limits

**Coordinator actions (rule 1) — reported only:**

- **`GOAL-FIND-001` is paused on a rule that has since been suspended.** Its
  `next_action` reads: *"Criterion appears met on the ledger, but status stays paused
  — three distinct resolved-model CONCUR attestations are not yet recorded, and
  AGENTS.md forbids closing without that quorum."* AGENTS.md now heads that section
  **SUSPENDED**; CLAUDE.md rule 8 agrees. The record carries no `completion_quorum`
  block. The stated blocker no longer exists.
- Adopting ISD-FC-2026, opening any source gate, and the evidence-schema change are
  all Coordinator acts. The proposals supply their inputs.

**Two candidate findings I withdrew after checking** — both already covered, and worth
recording because they show how easily this exercise produces false positives:

- The contradictory `C(p) ~ p^{0.055}` (`KN-FIND-d4f820`) versus `p^{0.079}`
  (`KN-FIND-e7a3b1`) exponents, neither superseding the other, are already the subject
  of `IDEA-20260805-c4f675` — which goes further and argues the null was never
  subtracted at all.
- `GOAL-MONO-001`'s missing factor-base-sublocus statistic is already supplied by
  `IDEA-20260805-a9a95d`, via an exact Fourier identity.

**What this review did not examine.** Five of ten survey slices failed on a usage
limit. Their targets were only partly recovered by direct analysis:

- **Not systematically examined:** the 14 draft goals' *framings* (as opposed to their
  `next_action` fields, which were read); the ~7,500 unreferenced literature entries
  beyond a 400-entry sample; cross-primitive mechanism transfer; whether any shared
  cost-model object (memory, bandwidth, non-uniform/preprocessing) exists across
  lanes; and what `ROADMAP.md` Phases 3–5 promise that has no ledger record.
- **`H-PSEUDO` has no `KN-OPEN` entry** despite `KN-FIND-e7a3b1` calling it "a new
  open problem" and `KN-FIND-9d2f56` making it "the exact condition for sub-rho
  combinatorial ECDLP". It does have hypotheses and proposals, so it is not orphaned —
  but the register a later session reads does not contain the program's most
  load-bearing conjecture. Noted; no proposal filed.

**Standing limits.** Every proposal carries `novelty_status: unverified`. None claims
an exponent improvement. Most predict a negative result, and several say so in their
titles. Priors of survival are stated per record and are mostly low — which is the
honest shape of a gap register, not a weakness of it.

---

## 7. Verification

- `tools/validate_ledger.py`: **zero new errors.** Baseline and post-change runs both
  report the same 122 pre-existing failures; the sorted error-line diff is empty.
- `tools/allocate_id.py --check`: all 32 identifiers verified free before use, minted
  with `--next idea --date 20260807` (no state scanned for a maximum).
- Schema: all 32 parse; all carry the six validator-required `idea` fields; every
  filename matches its `id`.
- `tools/check_merge_hygiene.py` reports 6 unparseable records — `EXP-P13-NC2b`,
  `EXP-P13-NC2d`, `DEC-20260805-364e9e`, `DEC-20260805-48b52e`, `DEC-20260805-661790`,
  `EV-HAWK-af783e`. **All six are pre-existing on `main` and untouched by this branch**
  (`git status --porcelain` reports no modification for any of them). This branch adds
  files only.

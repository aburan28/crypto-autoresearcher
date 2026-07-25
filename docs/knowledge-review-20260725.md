# Knowledge Base Review — 2026-07-25

A read-only review of `knowledge/` and the machinery that is supposed to fill
it, written one day after `docs/knowledge-assessment-20260724.md` and scoped to
the question *what else do we need?*

**This document is not evidence.** It makes no mathematical claim about the
ECDLP or any isogeny/lattice assumption, changes no hypothesis status, and
promotes nothing. It is a documentation-layer review.

It does not repeat the 2026-07-24 assessment. That audit stands; where its
findings are unchanged this review says so in one line and moves on. The new
material here is: the inventory of where this program's own knowledge actually
lives, the reason the promotion gate has never fired, a matching fail-open hole
in the claim-tier ceiling, and the coverage gaps that block the *currently
active* campaign.

## Method

Direct filesystem inspection plus the repository's own validators
(`tools/validate_ledger.py`, `tools/build_knowledge_index.py --check`), and
three independent audit passes (promotion debt, corpus integrity, coverage).
Every count below was measured, not estimated. Statements I could not check are
labelled in §8.

---

## 1. Delta since 2026-07-24

| | 2026-07-24 | 2026-07-25 |
| --- | --- | --- |
| Knowledge entries | 190 | **190 (unchanged)** |
| `knowledge/findings/` | 0 | **0** |
| Evidence records | 47 | 48 (`EV-SSI-001`) |
| Decision records | 64 | 65 (`DEC-20260725-002`) |
| Active goals | 4 active, 1 paused | same, plus `GOAL-SSI-001` BATCH-001 closed |

Nothing was added to `knowledge/` in the last day. One new campaign opened:
`GOAL-SSI-001`, supersingular-isogeny cryptanalysis after the SIDH break, which
closed BATCH-001 with `DEC-20260725-002` (`revise`) and is now waiting on a
BATCH-002 derivation gate.

Everything the 2026-07-24 assessment left open is still open. The two closure
records in that document (§6 classical ECDLP, §7 lattice cryptanalysis) did
real work — the corpus went 125 → 151 → 190 — but both closures added
*external* material. The internal half was untouched then and is untouched now.

---

## 2. The corpus is high quality, and it is the wrong half of the job

The 190 entries are in genuinely good shape, and this should be stated plainly
because the rest of this document is critical:

- **190/190 parse.** Zero missing required fields, for any type. All 49
  `KN-TECH` carry substantive `complexity:` and `applicability:` values; all 18
  `KN-OPEN` carry `status:` and `source_refs:`; all 123 `KN-LIT` carry all
  twelve literature fields.
- **`INDEX.md` is byte-identical to a regeneration.** `--check` exits 0.
- **Immutability is perfect.** Across 14 commits touching `knowledge/`, no entry
  has ever been modified after its introducing commit.
- **No stubs.** Pairwise body comparison across all 190 entries found zero
  near-duplicates (difflib ≥ 0.75), zero duplicate titles, zero duplicate
  identifiers. Sampling 13 entries across the full range found none that were
  boilerplate — even the thinnest (`KN-OPEN-003`, 111 words) states a
  falsifiable question with its required controls.
- **No dangling `KN-*` references**, and 49/49 techniques cite at least one
  literature entry.

Against that: **`knowledge/findings/` contains zero entries.** 190 entries
record what other people have established. Not one records what this program
has established. The standing test in `knowledge/README.md` — *a fresh agent
reading only `knowledge/` and the ledger should be able to rediscover
everything this program has proven* — fails on the `knowledge/` half entirely.

This is not a curation backlog. It is a structural break between where the
program produces knowledge and where it stores it, documented in §3–§4.

---

## 3. Where this program's knowledge actually lives

The program has produced a great deal. It is scattered across at least five
locations, none of which is the knowledge corpus and three of which are outside
the ledger's ID space and validator coverage entirely.

### 3.1 `ledger/FINDING-PF-IC-001.md` — the flagship result, unfiled

A **2,776-line** consolidated negative result: *"Candidate quantitative negative
result for prime-field index calculus."* It consolidates EXP-REP-001/002,
EXP-ISO-001, EXP-FB-001 plus an externally-firmed R6 result, and states a
bootstrap-CI total-cost exponent of **2.05, 90% CI [1.86, 2.29]**, against
rho's 0.5 — with the entire confidence interval far above the baseline. It
carries its own scope limits, an informal structural derivation, and a table of
four matched-control invariances (curve model, isogeny class, factor-base
structure, explicit membership).

It is a loose markdown file at `ledger/` root. It is not a typed ledger record,
so `tools/validate_ledger.py` does not see it. It is not a `KN-FIND`. Nothing in
`knowledge/` references it. The only files in the repository that cite it are
nine archived rejected-idea documents under `focus/archive/`.

This is the single clearest instance of the gap: the program's headline finding
is written, replicated, scoped, and invisible to every retrieval path an agent
uses.

### 3.2 `research/THM_*.md` — four theorem notes, ~106 KB, uncited

| File | Size | Content |
| --- | --- | --- |
| `research/THM_BKKMV1.md` | 25.8 KB | Exact mixed-volume law `MV_m = (m-1)!·2^((m-1)(m-2))`; proved m ≤ 5 |
| `research/THM_COMMUTATOR_KERNEL1.md` | 23.5 KB | Commutator-collapse kernel theorem (T1–T2 proved) |
| `research/THM_INCBARRIER1.md` | 27.3 KB | Incidence barrier |
| `research/THM_JETBARRIER1.md` | 30.0 KB | Jet barrier |

`research/verification/` holds independent check scripts and result JSON for
three of the four (`thm_bkkmv1_verify.sage`, `commutator_kernel1_check.py`,
`thm_incbarrier1_check.sage`, with results files). So these are exactly the
`proof_status: derivation` artifacts that `docs/claims-and-verification.md`
describes, already produced and already machine-checked.

`grep -rl 'THM_' knowledge/` returns nothing.

### 3.3 `research/dreg-linear-law/` — a complete finding package, never filed

Contains `FINDING.md` (7.7 KB), `FINDING_v2.md` (24.6 KB), `RED-TEAM.md`,
`VALIDATION.md`, and — notably — **`EV-DREG-DRAFT.yaml` (11.2 KB), a drafted
evidence record that was never filed into the ledger.** The producer, red team,
and validator all did their work; the record stopped one step short of the
ledger and never reached the corpus.

### 3.4 `research/pollard-rho-generic/` — a shadow research thread

Contains `RQ-RHO-001.yaml`, `H-RHO-001.yaml`, `EXP-RHO-001-contract.yaml`,
`TASK-20260718-RHO-REDTEAM.yaml`, and a `literature.md`. **None of those IDs
appear anywhere in `ledger/`**, and `tools/validate_ledger.py` contains no
reference to `research/` at all, so this thread is outside validation entirely.

This matters beyond bookkeeping: `KN-TECH-001`, the Pollard rho baseline entry
that every advantage claim in the program is measured against, is the
**thinnest technique entry in the corpus at 136 words** — while a dedicated
rho baseline thread with its own literature note sits unmerged in `research/`.

### 3.5 `ideas/` and `focus/archive/` — 410 prior ideas, zero retrievable

`ideas/` holds 860 files; **410 distinct `ECDLP-IDEA-*` IDs** exist across the
repository, with archived cohorts under `focus/archive/` including explicit
`rejected/` directories. `grep -rl 'ECDLP-IDEA' knowledge/ ledger/proposals/`
returns **0**. Four hundred prior ideas, many explicitly rejected with
reasoning, are invisible to both the corpus and the current proposal ledger.

### 3.6 The eleven replicated evidence records

`EV-BKK-001`, `EV-BKKMV-001`, `EV-BKKMV-002`, `EV-EQJ-001`, `EV-FB-001`,
`EV-NCP-001`, `EV-REP-002`, `EV-SIG-002`, `EV-SIG-003`, `EV-SIG-004`,
`EV-SIG-005` — unchanged from the 2026-07-24 assessment, still unpromoted.
Fifteen decisions pair one of these with a promotion-triggering outcome
(`supported`, `supported_scoped`, or `reject_scoped`).

---

## 4. Why the promotion gate has never fired

The 2026-07-24 assessment established *that* promotion never happens. This
review establishes *why*, and the answer is that every layer of the mechanism
is fail-open.

**4.1 `not_warranted` accepts any string.** `tools/validate_ledger.py:191`
requires only that an empty `promoted` list be accompanied by a non-empty
`not_warranted`. It never checks whether the obligation was actually incurred.
Five decisions discharge the field with:

```yaml
knowledge_promotion:
  promoted: []
  not_warranted: Historical ID remap only; promotion was not reassessed.
```

Two of those five (`DEC-20260724-009`, `DEC-20260724-011`) close out the
program's **two proved theorems** — the BKKMV mixed-volume law and the
commutator-collapse kernel. The strongest results in the repository are closed
by a waiver whose text says promotion was not considered.

**4.2 Twelve of the fifteen obligated decisions have no field at all.** They
predate the field's introduction and were grandfathered. Overall, 36 of 65
decision records lack `knowledge_promotion` entirely.

**4.3 The schema has no slot for two of its three triggers.** `/curate-knowledge`
and `knowledge/README.md` define three promotion triggers: `KN-FIND` (proven
result), `KN-OPEN` (crystallized unknown), `KN-TECH` (matured method). The
`knowledge_promotion` field is `{promoted, not_warranted}`, and every one of the
30 compliant records reasons *only* about evidence strength for `KN-FIND`. The
open-problem and technique obligations are structurally undischargeable. Two
concrete consequences:

- **No `KN-OPEN` entry cites any internal `EV-`/`DEC-` ID.** All 18 are seeded
  from literature. The program's sharpest self-generated open question — the D6
  semi-regular baseline repair from `DEC-20260720-002`, which the Red Team
  ranked #1 — has no representation in the corpus at all.
- **No `KN-TECH` entry cites any internal `EV-`/`DEC-` ID.** All 49 are
  external. At least three instruments qualify for promotion under the
  two-or-more-experiments rule: the support-matched semi-regular null control
  (used across EXP-SIG-001…005 and EXP-DREG-001/002, and notable for having
  caught its *own* breakdown at D6), the checkpointable block-m4ri Macaulay rank
  instrument, and the canonical rank-exact syzygy reduction from EXP-SIG-004.

**4.4 A schema deadlock blocks promotion even if someone tried today.** The
validator fully supports `KN-FIND` (`tools/validate_ledger.py:441-453`): it
requires `internal_refs` resolving to real records, a `proof_status` in
`{certificate, derivation, empirical_only, not_applicable}`, and a `proof_refs`
list. `/curate-knowledge` says the finding copies `proof_status` from its
evidence record. But **none of the 11 replicated evidence records has a
`proof_status` field** — it is absent from all 28 root-level `EV-*.yaml`, and
appears only on the newer subdirectory records, all of which are `preliminary`.

So a compliant `KN-FIND` cannot be written by copying, and the ledger's own
correction precedent (`CORR-20260724-001…003`) covers only merge/ID-collision
remapping, not content supersession. Backfilling `proof_status` onto immutable
evidence records is an unresolved policy question, and it is on the critical
path for every promotion.

---

## 5. The claim-tier ceiling has the same fail-open shape

This is new, and it matters because the claim-tier ceiling is one of the two
mechanisms `docs/claims-and-verification.md` names as keeping claims honest.

Measured across all 48 evidence records:

| | count |
| --- | --- |
| Zero `run_ids` (tier check has nothing to evaluate) | **18 / 48** |
| No `claim_tier` field at all | **26 / 48** |
| Both `claim_tier` present *and* `run_ids` non-empty | **4 / 48** |

The CI check described as *"no evidence record's `claim_tier` exceeds what its
runs' parameters allow"* is therefore live on four records: `EV-DREG-003`,
`EV-SIG-005`, `EV-MLKEM-004`, `EV-SEMAEV-001`.

Three specific consequences:

1. **Unknown tier values are silently accepted.** `TIER_ORDER = {"toy": 0,
   "medium": 1, "crypto": 2}` (`tools/validate_ledger.py:84`), and the check is
   `declared = TIER_ORDER.get(...)` followed by `if declared is not None and
   ...`. `EV-SSI-001` declares `claim_tier: theory`, which is in neither the
   enum nor `docs/claims-and-verification.md`. It is not rejected — the ceiling
   check is skipped. An undocumented tier is the one input that turns the guard
   off.
2. **Two records assert `claim_tier: crypto` on zero runs** (`EV-MLKEM-002`,
   `EV-MLKEM-003`). That may well be legitimate for literature-derived evidence
   about published parameter sets, but nothing checks it, and `crypto` is the
   top of the ceiling.
3. **The program has shifted to exactly the evidence mode the machinery does
   not cover.** All 12 `EV-CRYPTO-*`, both `EV-ECDLP-*`, three of four
   `EV-MLKEM-*`, and `EV-SSI-001` are `theoretical` or `literature` type with no
   runs. The certificate discipline and the tier ceiling both key off runs; the
   recent campaigns produce derivations and literature reviews. The honesty
   machinery guards the path the program has largely stopped walking.

None of this says any current claim is wrong. It says the guard would not catch
it if one were.

---

## 6. Coverage gaps

### 6.1 The blocking gap: the active SSI campaign

`GOAL-SSI-001` is scoped to *surviving* supersingular assumptions **after** the
SIDH break, and `DEC-20260725-002` sets BATCH-002's technical content as:
separate F_p² MITM full-cost from F_p Delfs–Galbraith, and **define or falsify a
low-memory isogeny-graph collision-search analogue**.

The corpus cannot support that derivation. Grep over all of `knowledge/`:

| Term | Hits |
| --- | --- |
| `golden collision` | **0** |
| `vOW` | **0** |
| memory-charged claw-finding / RAM-model quantum cost | **0** |
| SIKE practical cryptanalysis | **0** |
| `Bonnetain`, `SQALE` (CSIDH concrete quantum cost) | **0** |
| `SQIsignHD` / post-2023 SQIsign line | **0** |
| `oriented curve` (RQ-SSI-001 lists orientation as in-scope) | **0** |

The isogeny block (`KN-LIT-062`…`079`) stops at the 2023 break itself; the
SQIsign entry is 2020. The campaign is asking a question about the state of the
art in 2026 using a corpus that ends where its own subject began. That is also
the highest-risk configuration for a **false novelty verdict**: 2024–2025 is
precisely the window in which post-break constructions and cryptanalysis
appeared.

The specific literature needed is the memory-charged classical and quantum
cost analysis of supersingular path-finding — van Oorschot–Wiener golden-collision
search applied to isogeny graphs, MITM-versus-vOW-versus-Delfs–Galbraith
comparisons under charged memory, and RAM-model quantum claw-finding costs.
Candidate sources exist and are well known in the area, but **every citation
must be verified against a primary index before an entry is written**, per
`knowledge/SEEDING.md`; none should be entered from recall.

### 6.2 The methodological gap: no extrapolation discipline, anywhere

The program's stated core epistemic risk is toy-scale-to-crypto-scale
extrapolation (`AGENTS.md` rules 6–7). Grep over `knowledge/`:

```
confidence interval → 0    regression → 0        model selection → 0
AIC → 0                    BIC → 0               cross-validation → 0
scaling exponent → 0       curve fit → 0         asymptotic fit → 0
experimental design → 0    power analysis → 0    hypothesis test → 0
p-value → 0                multiple comparison → 0
```

`bootstrap` returns 3 hits, all FHE *bootstrapping*. Meanwhile `EXP-ICI-001`
reports a bootstrap 90% CI on a fitted cost exponent, `FINDING-PF-IC-001` rests
on `[1.86, 2.29]`, and `EXP-DREG-001` must distinguish a real degree-of-regularity
departure from small-`n` noise. Roughly 20 of 26 threads are extrapolations.
There is no corpus entry on how to do any of it soundly.

This is the highest-value missing topic in the review, because it is the one
that governs whether the program's own numbers mean what they are taken to mean.

### 6.3 The self-citation gap: the solver behind the headline exponent

`crossbred` returns **0 hits corpus-wide**, as do `XL`, `mutant`, and `MQ`. The
ICI thread's headline total index-calculus exponent (~0.863) comes from a
crossbred solver path named in `experiments/EXP-ICI-001/specification.yaml`. The
corpus has no entry for the solver family that produced the program's most
quoted number.

### 6.4 Live threads with ≤ 1 supporting entry

| Thread | Status | Corpus support |
| --- | --- | --- |
| **SIG** (5 experiments, largest family, `supported_scoped`) | active | `syzyg*` → 2 files, both incidental; `yokoyama` 0, `semi-normal` 0, `FGLM` 0, Castelnuovo–Mumford regularity 0 |
| **JET / JETB** (2 RQ, 2 H, 2 experiments) | closed scoped | `dual number` 0, `tangent` 0, `formal group` 0 — zero KN-LIT/KN-TECH |
| **ISO** | closed scoped | No ordinary-curve isogeny entry at all: `modular polynomial` 0, `elkies` 0, `isogeny volcano` 0. All 30 isogeny files are supersingular |
| **IMON / MONO** | orphaned | One entry (`KN-LIT-039`, Chebotarev) + `KN-OPEN-009`; `primitive group` 0, Lang–Weil 0 |
| **TRA** | closed scoped | `KN-LIT-040` is Koopman **1931**; no interval/kangaroo baseline (`pollard lambda` 0) though TRA's premise is sub-√n interval localization |
| **DREG** tooling | inconclusive | Concept well covered; `m4ri` 0, `msolve` 0 |

### 6.5 Other absences worth recording

- **Verification/certificate literature**: `docs/claims-and-verification.md` is
  the harness's central honesty device and has **zero** corpus backing
  (`formal verification` 0, `snark` 0, `coq` 0, `lean` 0).
- **Quantum post-2017**: coverage is Shor 1997 + one 2017 resource estimate.
  Regev's 2023 factoring/DL algorithm and its follow-ups are absent; so is
  anything on fault-tolerant cost models.
- **Last fall degree / post-2016 Semaev-adjacent work**: `last fall degree` 0.
  The strand that challenges the first-fall-degree assumption bears directly on
  DREG, SIG, and `KN-OPEN-002`.
- **Higher-genus / hyperelliptic index calculus**: `theriault` 0, `nagao` 0,
  `double large prime` 0.
- **Record landscape stops in 2016**; no current Certicom challenge state.
- **Cost-model economics**: `cloud` 0, `watt` 0, `hardware cost` 0 — while
  "fully charged cost" is the acceptance gate of two active goals.

### 6.6 Recency

Year histogram over all 123 literature entries: **6 entries from 2023 or later
(4.9%), and a complete 24-month blackout — zero entries dated 2024 or 2025.**
The two newest (2026) are ML-KEM papers ingested only because `EXP-MLKEM-001`
source-locks them. The core ECDLP block (`KN-LIT-001`…`029`) has a newest entry
of 2019; the prime-field frontier entry and the field survey are both 2016.

All three currently active goal areas — isogeny, lattice/ML-KEM, ECDLP — have
corpora that stop before the window their questions are about.

---

## 7. Retrieval defects

The corpus is a retrieval substrate. These are the defects that degrade
retrieval specifically.

**7.1 The ECDLP spine is 100% unread.** Citation verification across 123
literature entries: `web` 90 (73%), `read` 30 (24%), `full_text` 2, `false` 1.
But all 30 `read` entries are `KN-LIT-082`…`123` — the recently-added lattice,
records, and quantum material. **`KN-LIT-001`…`079`, the ECDLP and isogeny
spine, is 78 `web` + 1 `false` and zero `read`.** The exact region a novelty
check bites on is entirely abstract-level relay.

**7.2 Thirty-five entries combine `confidence: established` with
`citation_verified: web`.** `SEEDING.md` reserves `established` for claims you
can reconstruct the argument for; asserting that from a paper never fetched
collapses the two honesty axes in the direction the protocol exists to prevent.
Among them are `KN-LIT-008` (rho), `KN-LIT-011` (generic lower bound), and
`KN-LIT-012` (parallel collision search) — the three entries that anchor every
baseline comparison.

**7.3 `citation_verified: false` — one entry**, `KN-LIT-007` (GHS Weil descent).
It self-flags in its body, but `SEEDING.md` says it must be verified before any
novelty judgment relies on it, and it is the corpus's only Weil-descent
foundation.

**7.4 Vocabulary split.** `full_text` (`KN-LIT-080`, `-081`) is not in
`SEEDING.md`'s `web | read | false` vocabulary, and the index passes it through
verbatim — so a query for `read` silently misses the two most deeply-read
entries in the corpus. Flagged on 2026-07-24; unresolved.

**7.5 Tag drift.** 531 unique tags over 190 entries; 219 (41%) used exactly
once. The prescribed core vocabulary is healthy; the periphery is not. Two
failure modes:

- *Silent omission* — bare-versus-qualified pairs where a query on one misses
  entries tagged only with the other. The largest: **`adjacent` (43) versus
  `ecdlp-adjacent` (7)**, splitting the 51 entries that declare themselves
  adjacent to the mission. Also `descent`/`weil-descent`,
  `endomorphism`/`endomorphism-ring`, `wiedemann`/`block-wiedemann`,
  `heuristic`/`heuristics`, `groebner`/`groebner-basis`/`groebner-complexity`,
  and ~25 more pairs.
- *Silent pollution* — substring collisions where grep on the short tag returns
  unrelated entries. **`sidh` (8) is matched by `csidh` (4)** — different
  assumption, different security story, and the two are the subject of the
  active campaign. **`commutative` (2) is matched by `noncommutative` (4)**, so
  the query returns the opposite concept. Also `svp` matched by
  `usvp`/`core-svp`/`exact-svp`/`ideal-svp`, and `lwe` by ten compounds.

**7.6 The corpus is near-write-only.** Only **18 of 190 entries (9.5%) are ever
cited from `ledger/`**. Seven are cited by nothing in either direction. Half the
open problems (9 of 18) carry no program-record link at all — including
`KN-OPEN-001`, the program's central question — and no `KN-OPEN` carries a
program reference in frontmatter, so nothing structured can traverse
open-problem → hypothesis.

**7.7 One dangling program reference.** `EXP-COPP-001` is cited by
`KN-LIT-037:36` and `KN-TECH-015:25` as though it exists. There is no such
experiment directory and no ledger record; it appears only in
`research_directions_20260718.md` as a *planned* contract.

**7.8 Novelty labels are asserted, not performed.** `/propose-ideas` requires a
novelty check against `knowledge/` before any label stronger than `unverified`.
Across the 10 proposals in `ledger/proposals/`, seven cite **zero** knowledge
entries — including both proposals labelled `novelty_status: known`
(`IDEA-20260723-001`, `-002`), which is precisely the label that must point at
the prior art making it known.

| Proposal | novelty_status | KN- refs |
| --- | --- | --- |
| IDEA-20260722-001 | speculative | 0 |
| IDEA-20260722-002 | adaptation | 0 |
| IDEA-20260722-003 | adaptation | 0 |
| IDEA-20260723-001 | **known** | **0** |
| IDEA-20260723-002 | **known** | **0** |
| IDEA-20260723-003 | unverified | 0 |
| IDEA-20260723-004 | unverified | 0 |
| IDEA-20260723-005 | unverified | 2 |
| IDEA-20260723-006 | speculative | 1 |
| IDEA-20260725-001 | methodological | 1 |

With `findings/` empty, the internal half of that check is impossible anyway —
an Idea Generator grepping `knowledge/` today would find the jet split, the
AP-supported structured solve, the transfer-operator localization, the
elliptic-net route, and the factor-base structure lever all apparently novel.
All five are closed, replicated, scoped negatives.

---

## 8. What this review could not check

- **Whether the 90 `web` citations describe real papers.** That needs per-entry
  network verification against IACR ePrint / DOI / DBLP. What was verified:
  field values, internal consistency, and the absence of duplicate DOIs,
  ePrint numbers, or URLs.
- **Whether entry content faithfully reflects its cited source**, at any
  verification tier. That needs reading the papers.
- **Whether any mathematical conclusion in the ledger is correct.** No
  certificate was re-verified, no experiment re-run, no cost arithmetic
  re-checked. Coverage of a topic in `knowledge/` is not evidence it was handled
  correctly, and absence is not evidence it was handled incorrectly.

---

## 9. What we need — prioritized

Ordered by how much each item degrades the program's ability to know what it
knows. Items 1–3 are prerequisites for everything else.

### P0 — make the program's own knowledge retrievable

1. **Unblock promotion by resolving the `proof_status` deadlock.** Decide, and
   write down, how `proof_status`/`proof_refs` get onto the 11 replicated
   evidence records that lack them: a new correction class, a superseding
   evidence record, or Coordinator assignment at promotion time with recorded
   rationale. Nothing else in this list can proceed first. *(Coordinator
   authority; policy decision, not curation.)*

2. **Promote the backlog.** At minimum: `FINDING-PF-IC-001` (the flagship
   negative result), the two theorem-backed results (BKKMV mixed-volume law,
   commutator-collapse kernel — both with existing verification scripts, so both
   can carry `proof_status: derivation`), and the five replicated scoped
   negatives that future ideation must not re-cross (BKK/Newton saturation,
   isotypic decomposition, curve-model invariance, factor-base invariance,
   commutator collapse). Deduplicated, roughly **9 `KN-FIND` entries**. Re-run
   the five decisions whose promotion was waived as "not reassessed".

3. **Close the gate so it cannot silently reopen.** Teach
   `tools/validate_ledger.py` to *compute* the obligation — decision outcome in
   `{supported, supported_scoped, reject_scoped}` AND cited evidence strength in
   `{replicated, strong}` ⇒ require either a `KN-FIND` in `promoted` or a
   `not_warranted` that is not a deferral. Today the rule lives only in prose
   and the field accepts any string, which is why it has never fired.

4. **Add `KN-OPEN` and `KN-TECH` slots to `knowledge_promotion`.** The field
   currently has no way to discharge two of its three documented triggers, which
   is why 18 open problems and 49 techniques contain zero internal provenance.
   Then file the D6 baseline-repair question (`DEC-20260720-002`) as the first
   internally-sourced `KN-OPEN`, and the support-matched null control and
   block-m4ri rank instrument as the first internally-sourced `KN-TECH` entries.

### P0 — the methodology gap

5. **Seed extrapolation and experimental-statistics entries.** Sound estimation
   of scaling exponents from small-range data; confidence intervals under model
   misspecification; model selection between competing growth laws; the validity
   limits of power-law extrapolation. This governs the interpretation of nearly
   every thread and the corpus currently has nothing on it.

### P1 — unblock the active campaign

6. **Seed memory-charged isogeny path-finding literature for `GOAL-SSI-001`
   BATCH-002** — vOW golden-collision search on isogeny graphs, MITM vs
   Delfs–Galbraith under charged memory, RAM-model quantum claw-finding, CSIDH
   concrete quantum cost, and the post-2023 SQIsign line. Verify every citation
   against a primary index before writing; do not enter any from recall.

7. **Refresh 2024–2025 across all three active goal areas.** The 24-month
   blackout is most dangerous where a campaign is live and asking about the state
   of the art: isogeny post-SIDH, lattice/ML-KEM, and quantum DL including
   Regev-2023 and follow-ups.

8. **Add the crossbred/XL/MQ solving family**, which produced the ICI thread's
   headline exponent and has zero corpus presence.

### P1 — fix retrieval

9. **Upgrade the load-bearing citations from `web` to `read`.** Priority:
   `KN-LIT-007` (the only `false`, and the sole Weil-descent foundation), then
   `KN-LIT-008`/`-011`/`-012` (the baseline anchors, all `established` + `web`),
   then the rest of the ECDLP spine. Re-examine the 35 `established` + `web`
   pairs and downgrade to `reported` where the argument cannot be reconstructed.

10. **Normalize tags and add a tag-lint to CI.** Merge `adjacent`/`ecdlp-adjacent`
    and the ~25 bare-versus-qualified pairs; resolve the `full_text`/`read`
    vocabulary split; add distinguishing prefixes or a documented convention for
    the substring collisions (`sidh`/`csidh`, `commutative`/`noncommutative`).

11. **Fix `EXP-COPP-001`** — either create the record or correct the two entries
    that cite it as existing.

12. **Enforce the novelty screen.** Require proposals with a label stronger than
    `unverified` to cite the `KN-*` entries that justify it. Two proposals are
    currently labelled `known` with no citation at all.

### P2 — depth and consolidation

13. **Fold the shadow threads into the ledger or explicitly park them**:
    `research/pollard-rho-generic/` (RQ/H/EXP records outside the ID space and
    outside validation), `research/dreg-linear-law/EV-DREG-DRAFT.yaml` (a drafted
    evidence record never filed), and the four orphaned experiments the
    2026-07-24 assessment named (`EXP-IMON-001`, `EXP-ISADV-001`, `EXP-MONO-001`,
    `EXP-XEDN-001`).

14. **Deepen the baseline entries.** `KN-TECH-001` (rho) at 136 words is the
    thinnest technique entry in the corpus and the measuring stick for every
    advantage claim; `KN-OPEN-001`, the program's central question, is 135 words.
    The corpus is deepest where the program is least active — the newer lattice
    entries have a median of 334 body words against 233 for the core — and
    thinnest where it works every day. Fold in `research/pollard-rho-generic/`.

15. **Fill the thin live threads** (§6.4): syzygy/free-resolution/regularity for
    SIG; jets and dual numbers, plus the algebraic group model, for JET/JETB;
    ordinary-curve isogeny structure (modular polynomials, Elkies, volcanoes)
    for ISO; monodromy and Galois-group computation for IMON/MONO; an interval
    /kangaroo baseline for TRA.

16. **Back `docs/claims-and-verification.md` with literature** — certificates,
    verifiable computation, proof-carrying results — and record the current
    ECDLP challenge/record landscape, which presently stops in 2016.

### Separately: the honesty machinery

17. **Close the claim-tier fail-open** (§5): reject unknown `claim_tier` values
    instead of skipping the check, decide whether `theory` is a legitimate tier
    and document it if so, and define what the ceiling means for
    literature/derivation evidence with no runs — which is now the program's
    dominant evidence mode, covering 18 of 48 records.

---

## 10. Closure record — the three P0 topic gaps (2026-07-25)

Items 5, 6 and 8 of §9 were addressed the same day this review was written.
Twenty-two entries were added, taking the corpus from 190 to 212. Nothing in
§§1–5 or §7 is addressed: the promotion debt, the `proof_status` deadlock, and
the claim-tier fail-open all stand exactly as described.

### A constraint that changes what verification is achievable

This session's egress policy **blocks every direct outbound fetch**. IACR
ePrint, Springer, arXiv, DBLP, DOI resolution, Semantic Scholar and even
author-hosted PDFs all returned HTTP 403; only web search was available.

Under `knowledge/SEEDING.md`'s vocabulary that caps honest verification at
`citation_verified: web` — bibliographic details corroborated against
primary-index *listings surfaced by search* — and makes `read` unreachable. All
22 entries are therefore `web`, and each one's `## Not verified here` section
records specifically what could not be obtained rather than leaving the reader to
assume.

Two consequences worth stating plainly:

- **§9 item 9 cannot be executed in this environment at all.** Upgrading the
  ECDLP spine from `web` to `read` requires fetching papers. It needs either a
  session with wider egress or a human with library access.
- **No entry in this batch asserts a complexity constant, security level, or
  cost figure**, because none could be read from a primary source. Where a
  number arrived through a search summary it is either omitted or explicitly
  flagged as unconfirmed — see `KN-LIT-132`, where a quantum complexity range
  returned by search was internally inconsistent and was deliberately not
  recorded, and `KN-TECH-053`, where the BooleanSolve exponents are marked as
  quoted-but-unconfirmed.

The verification method also justified itself immediately: the author list this
review would have written from memory for `KN-LIT-124` was wrong on two of five
names. Nothing was entered from recall.

### Batch 1 — supersingular isogeny cost models (§6.1)

Ten literature entries and two techniques, targeting the live `GOAL-SSI-001`
BATCH-002 derivation gate: `KN-LIT-124` (Adj et al., vOW versus MITM for CSSI),
`KN-LIT-125` (Costello et al., the optimised vOW implementation), `KN-LIT-126`
(Jaques–Schanck, RAM-model quantum claw-finding), `KN-LIT-127` (Peikert,
collimation sieve on CSIDH), `KN-LIT-128` (Bonnetain–Schrottenloher, CSIDH
quantum analysis), `KN-LIT-129` (SQALE, resource-constrained re-costing),
`KN-LIT-130` (Wesolowski, orientations), `KN-LIT-131` (Page–Wesolowski, 2024),
`KN-LIT-132` (Benčina et al., fixed-degree isogenies, 2024), `KN-LIT-133`
(SQIsignHD, 2024); plus `KN-TECH-050` (memory-charged path-finding cost models)
and `KN-TECH-051` (CSIDH quantum cost and the resource-constraint dispute).

**The decision-relevant finding for BATCH-002**: `EV-SSI-001` records that the
low-memory isogeny-graph collision-search analogue is "underspecified relative to
the group setting," and `DEC-20260725-002` makes defining or falsifying it the
gate's main technical content. It is **not** undefined in the literature — it is
van Oorschot–Wiener golden collision search, applied to CSSI in `KN-LIT-124` and
implemented in `KN-LIT-125`, with a 2024 memory-free competitor in `KN-LIT-132`.
The gate should start from that work rather than construct the analogue from
scratch.

Three entries are dated 2024, the corpus's first, against the 24-month blackout
in §6.6. `KN-LIT-130` is the corpus's first orientation entry, filling a line
`RQ-SSI-001` declares in scope and that had zero coverage.

### Batch 2 — extrapolation and inference methodology (§6.2)

`KN-LIT-134` (Efron, the bootstrap), `KN-LIT-135` (Clauset–Shalizi–Newman,
power-law distributions), `KN-LIT-136` (Benjamini–Hochberg, false discovery
rate), `KN-LIT-137` (Hoffmann et al., recorded explicitly as a cross-domain
cautionary case), and `KN-TECH-052`, which states the discipline the program
needs.

`KN-TECH-052` carries the distinction that does the work: **a confidence interval
is not an extrapolation interval.** `FINDING-PF-IC-001`'s exponent CI
`[1.86, 2.29]` says the exponent is tightly determined at `p ≤ 2^16` and that the
gap to rho's 0.5 far exceeds sampling noise *there*; it carries no information
about crypto scale, because nothing in the resampling saw that range. The finding
itself scopes this correctly — the entry exists to keep it scoped as the result
propagates.

### Batch 3 — MQ and Boolean polynomial-system solving (§6.3)

`KN-LIT-138` (XL), `KN-LIT-139` (Joux–Vitse crossbred), `KN-LIT-140`
(BooleanSolve), `KN-LIT-141` (Fukuoka MQ Challenge), and `KN-TECH-053`.

`KN-TECH-053` records the category error the entries exist to prevent: an MQ
solver's exponent is stated in Boolean variables, an index-calculus exponent in
the group order, and `EXP-ICI-001`'s 0.863 is the latter. It also bounds the
result's reach — a faster per-decomposition solve does not touch
`FINDING-PF-IC-001`'s structural argument that the total is dominated by
`|F|`-size linear algebra rather than by the solve.

### What remains open

Unchanged from §9: everything in P0 items 1–4 (the promotion debt, which needs
Coordinator authority rather than curation), P1 items 9–12, and all of P2 and
item 17. Of the topic gaps, §6.4's thin live threads (SIG syzygies, JET/JETB,
ISO, IMON/MONO, TRA) and §6.5's absences (verification literature, quantum
post-2017 including Regev-2023, last fall degree, higher-genus, the current
record landscape, cost-model economics) are untouched, as is the 2024–2025
refresh for the lattice and ECDLP areas — batch 1 refreshed only the isogeny
side.

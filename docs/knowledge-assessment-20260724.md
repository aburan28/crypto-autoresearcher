# Knowledge Assessment — 2026-07-24

A read-only audit of what this repository knows, where that knowledge is
recorded, and where the record is thinner than the harness contract requires.

**This document is not evidence.** It makes no mathematical claim about the
ECDLP, changes no hypothesis status, and promotes nothing. It is a
documentation-layer review of coverage and completeness, produced after
`GOAL-CRYPTO-001` paused on the exhausted twelve-batch budget
(`DEC-20260724-014`).

## Scope and method

Audited: `knowledge/` (125 entries), `ledger/` (277 YAML records across the
subdirectory layout plus 103 frozen root-level legacy files), `experiments/`
(34 experiment directories, 144 run manifests), `docs/`, `templates/`,
`agents/`, `.claude/`, `tools/`, and the remaining top-level directories.

Every count below was obtained by direct filesystem inspection or by running
the repository's own validators (`tools/validate_ledger.py`,
`tools/build_knowledge_index.py --check`). Statements that are inference
rather than measurement are labelled as such.

## Summary verdict

The repository is strong where it has invested tooling — bibliographic
discipline, run immutability, dispatch verification, certificate checking on
the harness path — and weak wherever a lifecycle step depends on an agent
choosing to write prose. The single largest gap is that **the corpus has no
internal findings at all**: everything this program has actually proven lives
in evidence records and experiment directories, and nothing has been distilled
into `knowledge/findings/`.

`knowledge/README.md` states the standing test:

> a fresh agent reading only `knowledge/` and the ledger should be able to
> rediscover everything this program has proven.

That test currently fails, and it fails by construction rather than by
oversight: the promotion step exists in policy, has a skill, has a decision
field, and has never once produced an entry.

The table below records the state at the time of the audit. One row has since
changed: the topic gaps in §1.6 were filled by 26 new entries, taking the
corpus to 151 — see the closure record in §6.

| Layer | State |
| --- | --- |
| Knowledge corpus breadth | 125 entries at assessment time, index in exact sync with disk (190 after the §6 and §7 closures) |
| Knowledge corpus depth | Uniformly shallow: median 230 body words, max 330 (pre-closure entries unchanged) |
| Internal findings | **0 entries** (`findings/` holds only `.gitkeep`) |
| Evidence → knowledge promotion | 11 `replicated` evidence records, 0 `KN-FIND` promotions |
| Ledger cross-references | 7 dangling IDs; 5 decision IDs duplicated across two layouts |
| Run artifacts | 12 of 144 manifests match the documented canonical schema |
| Validator debt | 1,138 grandfathered errors, 289 legacy warnings |
| Documented roles | Reviewer specified in `AGENTS.md`, never instantiated |

---

## 1. Knowledge corpus

### 1.1 The findings gap (highest severity)

`knowledge/findings/` contains no entries. No decision record in the
repository has ever named a `KN-FIND-*` ID in its
`knowledge_promotion.promoted` list. The only promotion that has ever fired
was `DEC-20260723-005`, which promoted two literature notes
(`KN-LIT-080`, `KN-LIT-081`).

This matters because eleven evidence records carry strength `replicated`,
which per `knowledge/README.md` and the `/curate-knowledge` skill *requires* a
`KN-FIND` entry or an explicit `not_warranted` justification:

`EV-BKK-001`, `EV-BKKMV-001`, `EV-BKKMV-002`, `EV-EQJ-001`, `EV-FB-001`,
`EV-NCP-001`, `EV-REP-002`, `EV-SIG-002`, `EV-SIG-003`, `EV-SIG-004`,
`EV-SIG-005`.

All eleven live at `ledger/` root and were closed by decisions written before
`knowledge_promotion` became a required field. Those decisions
(`DEC-20260716-*` through `DEC-20260720-*`) omit the field entirely, so the
obligation was never recorded, let alone discharged. The 28 newer decisions
under `ledger/decisions/` do carry the field, but 27 of them record
`promoted: []` with a `not_warranted` reason — almost always some variant of
"preliminary evidence, not a replicated/strong finding," which is accurate for
the CRYPTO batches but leaves the older replicated results permanently
unpromoted.

Concretely, a reader of `knowledge/` alone cannot learn that this program
established scoped negative results on BKK mixed-volume saturation, jet
tangency, incidence harvesting, noncommutative path algebras, or the signature
battery. Those are exactly the boundaries future ideation must not re-cross,
and the policy explicitly says proven negatives are findings too.

### 1.2 Depth

No entry is a stub in the sense of being empty, but the corpus is uniformly
thin. Body word counts: literature median 221 (range 136–319), techniques
median 257 (range 151–330), open problems median 268 (range 118–306). Total
corpus body text is roughly 28,800 words across 125 entries.

The thinnest tier is, unhelpfully, the foundational core: `KN-OPEN-003` (118
words), `KN-OPEN-002` (129), `KN-LIT-009` Semaev (136), `KN-LIT-004`
symmetries (137), `KN-LIT-003` Diem (143), `KN-LIT-002` Gaudry (146),
`KN-OPEN-001` — the program's central question — at 147, `KN-LIT-008` Pollard
rho (150), and `KN-TECH-001`, the rho baseline everything is measured against,
at 151.

An entry of 150 words can state what a paper is about. It cannot carry the
complexity constants, parameter regimes, and crossover conditions that a
baseline comparison needs. The rho baseline entry in particular is load-bearing
for every advantage claim the program makes, and it is the tenth-thinnest file
in the corpus.

### 1.3 Schema divergence between README and reality

`knowledge/README.md` documents a frontmatter schema with `source.citation`,
`source.url`, `internal_refs`, `proof_status`, and `proof_refs`. **Zero of the
125 entries use any of those fields.** The live corpus follows
`knowledge/SEEDING.md` instead: `authors`, `year`, `venue`,
`identifiers.url`, `citation_verified` for literature; `complexity`,
`applicability`, `source_refs` for techniques; `status: open` for open
problems.

The corpus is internally consistent and the generated index is correct, so
nothing is broken. But the README is the document an agent is told to read
first, and it describes a schema the repository does not use. The
`proof_status` / `proof_refs` fields are the ones that matter most, since
`docs/claims-and-verification.md` makes them the mechanism by which a
finding's evidentiary basis travels with it — and they exist only in the
aspirational schema.

### 1.4 Verification honesty

The bibliographic discipline is genuinely good: all 81 literature entries
carry `citation_verified`, and all 81 have a resolvable URL. But only **two**
entries were verified from full text (`KN-LIT-080`, `KN-LIT-081`, both ML-KEM
adjacent), 78 are `web` (bibliography confirmed against an index, paper not
read), and one is explicitly `false` (`KN-LIT-007`, GHS Weil descent, citation
recalled from memory).

Twenty-eight entries combine `confidence: established` with
`citation_verified: web` and a body section saying the full paper was not
read. The two-axis model in `SEEDING.md` permits this — `confidence` describes
claim strength in the field, `citation_verified` describes bibliographic
checking — but the combination means a quarter of the literature is treated as
textbook-settled on the basis of an abstract. For the entries that anchor cost
comparisons (`KN-LIT-008` rho, `KN-LIT-011` generic lower bounds, `KN-LIT-012`
parallel collision search), that is the wrong side of the line to be on.

### 1.5 Body structure

All 81 literature entries and all 15 open problems separate reported claims
from unverified ones, via `## Key claims (as reported)` plus `## Not verified
here`. **None of the 29 technique entries do**; they use `## Method` and
`## Applicability limits` with no verified/reported split, so 29 of 125 entries
(23%) lack the separation the README requires.

Ten of the 15 open problems have no scoping or limits section: `KN-OPEN-002`
through `KN-OPEN-011`. Three techniques lack an applicability-limits section:
`KN-TECH-002` (Semaev polynomials), `KN-TECH-003` (point-decomposition index
calculus), `KN-TECH-004` (Gröbner complexity indicators). Those three are
central to the program's main line of attack, and they are precisely the ones
where "when does this stop working" is the question that matters.

### 1.6 Topic coverage gaps

> **Status: addressed 2026-07-24.** The gaps identified in this section have
> since been filled by 26 new entries (`KN-LIT-082` … `KN-LIT-099`,
> `KN-TECH-030` … `KN-TECH-037`), built from verified primary sources. See
> §6 for the closure record and for what remains open. The table below is
> preserved as the original finding.
>
> This section audits coverage against the program's **ECDLP** work only. A
> second audit of the **lattice** half of the corpus, run after the focus was
> set on lattices and elliptic curves, found a wider gap of the same kind — see
> §7.

The corpus is deep on the index-calculus research frontier and on adjacent
post-quantum material (roughly 40 entries tagged `adjacent`), and correspondingly
thin on classical ECDLP fundamentals. Verified absences:

| Topic | Status |
| --- | --- |
| Pohlig–Hellman, small-subgroup, invalid-curve, cofactor, twist attacks | **Absent.** Zero matches anywhere in `knowledge/`. |
| MOV / Frey–Rück pairing attacks | **Absent.** Zero matches. `KN-LIT-018` covers Tate pairings via elliptic nets, not the attack. |
| Anomalous curves (Smart, Satoh–Araki) | **Passing mention only** — one line in `KN-TECH-005`. No entry. |
| Concrete rho record computations (Certicom challenges, ECC2K-130, named curves, secp256k1) | **Absent.** Zero matches for any of those terms. |
| Baby-step giant-step | **Passing mention only** in four entries. No dedicated technique entry. |
| Quantum ECDLP / Shor resource estimates | **Absent as a topic.** "Shor" appears only as a one-line PQC motivation in four adjacent lattice entries; no qubit or gate-count content. |
| Prime-field Weil-descent applicability criteria | **Partial.** `KN-LIT-007` covers GHS over binary composite fields and states prime fields are out of scope; nothing fills that gap. |
| Parallel collision search memory/communication cost models | **Present but shallow.** `KN-LIT-012` and `KN-TECH-006` cover distinguished points and the time-memory tradeoff; no detailed communication-bandwidth model. |

The first four are the ones I would flag hardest. The program's entire premise
is comparison against a well-characterized rho baseline on cryptographic-size
curves, and the corpus contains no entry describing what any real rho
computation has actually cost. The absence of Pohlig–Hellman and MOV also
means the novelty screen has no recorded basis for rejecting proposals that
rediscover special-curve weaknesses.

### 1.7 What is in good shape

`INDEX.md` is in exact 1:1 correspondence with disk (125 = 125,
`build_knowledge_index.py --check` exits 0). Every literature entry has a
resolvable identifier. The tag vocabulary (336 distinct tags) supports the
grep-based retrieval the README describes.

---

## 2. Ledger

### 2.1 Two coexisting layouts

The ledger exists in two layers: 103 frozen legacy files directly under
`ledger/` and 174 records in the typed subdirectories. The split is real and
consequential:

| Record class | Root (legacy) | Subdirectory |
| --- | --- | --- |
| Hypotheses | 20 | 2 |
| Evidence | 28 | 19 |
| Decisions | 35 | 29 |
| Questions | 20 | 4 |

`ledger/README.md` documents only the subdirectory layout. It does not mention
the root-level files, `corrections/`, or the migration policy. The validator
knows about the split — `tools/legacy_ledger_inventory.yaml` hash-freezes all
103 — but that mechanism is described nowhere in prose (grep for
`legacy_ledger_inventory` across all `*.md` returns zero hits).

Five decision IDs exist in **both** layers: `DEC-20260722-001` through
`DEC-20260722-005`. The subdirectory copies carry `knowledge_promotion`; the
root copies do not. `CORR-20260724-003` documents the remapping intent, but a
reader resolving one of those IDs by grep will find two files with different
content.

### 2.2 Dangling references

Seven IDs are referenced by ledger records but resolve to no file (verified
individually):

| ID | Referenced from |
| --- | --- |
| `EXP-SEMAEV-002` | `DEC-20260719-001` (`next_actions`) |
| `EV-ECDLP-001` | `TASK-20260721-006`, `TASK-20260721-012` |
| `EV-ECDLP-003` | `TASK-20260722-009` |
| `DEC-20260721-003` | `TASK-20260721-012` |
| `TASK-20260717-001` | `DEC-20260717-002` |
| `TASK-20260723-402` | `DEC-20260723-003`, `TASK-20260723-401` (`archived_by`) |
| `TASK-20260723-403` | `DEC-20260723-003`, `EV-CRYPTO-004` |

The `EV-ECDLP-*` sequence has holes at 001 and 003 while 002 and 004 exist,
which suggests records were planned and referenced but never written rather
than written and lost. `TASK-20260723-402` being cited as an `archived_by`
value is the most serious of these: an archival pointer that resolves to
nothing undercuts the durable-commit guarantee.

Three legacy files also have filename/ID mismatches — `ledger/H-NET-001.yaml`
declares `NET-H-001`, and likewise for `H-STR-001`/`STR-H-001` and
`H-TRA-001`/`TRA-H-001` — plus the corresponding `NET-EV-001` and
`TRA-EV-001`. Eight root hypothesis files additionally fail `yaml.safe_load()`
on inline-colon syntax, so they cannot be machine-read at all.

### 2.3 Experiment and hypothesis coverage

Of 34 experiment directories, five have no evidence record and four sit
entirely outside the review loop with neither evidence nor any decision
referencing them: `EXP-IMON-001`, `EXP-ISADV-001`, `EXP-MONO-001`,
`EXP-XEDN-001`. All four are smoke/prototype directories, but nothing in the
ledger says so — they are simply unaccounted for.

`EXP-FB3-001` is a different case: it has an approved frozen specification and
two decisions referencing it, but zero runs, no evidence, and no analysis. Its
hypothesis `H-FB3-001` remains in status `approved`, which is the only
hypothesis in the repository with no evidence attached.

Of 22 distinct hypotheses, two are non-terminal: `H-FB3-001` (`approved`, as
above) and `H-SEMAEV-001` (`analyzed`, with `DEC-20260719-001` deciding
`expand` toward a follow-up experiment `EXP-SEMAEV-002` that was never
created). One hypothesis, `H-SIG-001`, uses status `supported_scoped`, which is
not in the `AGENTS.md` state enum.

### 2.4 Evidence strength distribution

Across 47 evidence records: 11 `replicated`, 34 `preliminary`, 1 `single-run`,
1 `inconclusive`, and **zero `strong`**. Every CRYPTO-campaign record
(`EV-CRYPTO-001` through `EV-CRYPTO-012`) is `preliminary`, which is honest —
those batches produced screening dispositions, not measurements — but it means
the entire twelve-batch campaign generated no evidence above the level that
would trigger a knowledge promotion.

---

## 3. Run artifacts and reproducibility

### 3.1 Manifest schema fragmentation

144 run manifests exist across four mutually incompatible dialects:

| Dialect | Runs | Where |
| --- | --- | --- |
| Full canonical (`code` + `inference` + `result` + certificate) | 12 | `EXP-SEMAEV-001` only |
| Partial harness (`code` + `result`, no `inference`) | 28 | `EXP-DREG-001/002` |
| Flat legacy (`git_commit`, `validity_status`) | 93 | Everything else executed |
| Hash-frozen legacy inventory | 11 | `EXP-BKKMV-002`, `EXP-MLKEM-001`, `EXP-TTN-002` |

Only the 12 `EXP-SEMAEV-001` runs match the manifest documented in
`docs/evidence-and-reproducibility.md`. Semantic coverage is much better than
strict compliance — 100% record a git commit and dirty-tree state, 95% record
an exact command, 96% record validity status — but canonical artifact
filenames are the exception rather than the rule (`stdout.log` present in 41 of
144; most runs use `stdout.txt`, and `raw-result.json` appears in 30).

The `inference` block required by the `AGENTS.md` artifact policy (requested
policy, resolved model, fallback flag) is present in 16 of 144 manifests. For
deterministic Sage runs that is arguably immaterial, but the policy states it
unconditionally, and nothing in the repository records the exemption.

### 3.2 Certificates

The certificate machinery works where it is wired up. All nine runs that claim
a solve or a relation carry a certificate that `harness/runner.py` re-verified
by independent recompute: six `discrete_log` and three `decomposition`, all in
`EXP-SEMAEV-001`. Three further runs correctly declare `kind: none` when no
decomposition was found.

The gap is coverage, not correctness: 129 of 144 runs carry no certificate
field at all. `docs/claims-and-verification.md` requires measurement runs to
declare `kind: none` explicitly; only six do. Every run outside the harness
path — the Sage scripts, the DREG rank measurements, the SIG battery — asserts
correctness only through prose in `validity_reason`, with no machine-checkable
counterpart.

### 3.3 Reproducibility defects

Seven runs in `EXP-SIG-005` (`RUN-EXP-SIG-005-h` through `-n`) have
`command: ''` in the manifest and no `command.txt` on disk, despite the
manifest stating the record was reconstructed from that file. These seven runs
cannot be reproduced from their own records.

Against that: a full scan of all 144 manifests found **zero broken script
path references**. Every command that was recorded points at a file that still
exists.

`EXP-REP-001` retains two run directories (`RUN-REP-001-a`, `-b`) with partial
artifacts and no manifests; they are declared as `superseded_runs` in
`RUN-REP-001-c`, so this is documented rather than lost, but the directories
themselves carry no marker.

### 3.4 Validator debt

`tools/validate_ledger.py` reports `OK: validated 407 records, no new
violations`, but this is achieved by suppressing **1,138 grandfathered errors**
via `tools/validate_ledger_baseline.txt`, plus 289 read-only legacy schema
warnings. Run with `--no-baseline`, roughly 1,126 manifest errors surface.

This is a defensible engineering choice — it prevents new regressions without
demanding a rewrite of immutable history — but the size of the baseline is not
reported anywhere a reader would encounter it, and the baseline file itself is
122 KB with no accompanying prose explaining what classes of error it contains
or under what conditions an entry may be removed from it.

---

## 4. Documentation and process

### 4.1 The Reviewer role does not exist

`AGENTS.md` names six roles and defines Reviewer as the agent that
"independently challenges claims, experiment validity, and proposed state
transitions." `docs/dynamic-subagent-dispatch.md` assigns review verdicts to
it, and `orchestration/model-policies.yaml` routes it to `review-xhigh`.

There is no `agents/reviewer.md` and no `.claude/agents/reviewer.md`. In
practice review work is split between the Validator, the Red Team, and the
Coordinator's own `/review-evidence` skill. This is not merely cosmetic: during
`BATCH-011` a dispatched task specifying `role: reviewer` was refused by the
runtime for role/scope mismatch and had to be reassigned to `red-team`. The
contract describes an agent the harness cannot instantiate.

### 4.2 Undocumented directories

Nine substantial top-level directories have no README and no entry in the root
`README.md` repository map: `coordination/` (3.6 MB), `focus/` (5.7 MB),
`inputs/` (29 MB), `research/` (408 KB, partially documented), `src/` (60 KB),
`tools/` (572 KB), `tests/`, `orchestration/`, and `.github/`. `harness/` and
`ideas/` have their own READMEs but are absent from the root map.

`inputs/` at 29 MB is the most opaque: its purpose is stated only inside
`research_directions_20260717.md` and one nested research README.

The two research-direction documents at the repository root (72 KB and 93 KB)
are heavily cross-referenced from ledger records, experiment specifications,
and theorem notes, but appear in no index. They also reference a pre-migration
experiment layout (`experiments/ecdlp_jet/...`) that no longer exists.

### 4.3 Stale statements

- `CLAUDE.md` line 68 says "all three subagents use `model: inherit`"; there are five.
- `README.md`'s "next milestones" lists the immutable run wrapper and the goal-batch launcher as pending; both are implemented (`harness/runner.py`, `coordination/goals/`). The pluggable agent adapter, also listed, genuinely is not.
- `plan.md` is a frozen 2026-07-17 batch plan expecting `DEC-20260717-*` decisions and a `SYNTHESIS-20260717.md` that was never written (the repository has `SYNTHESIS-20260718.md`). Nothing marks it as historical.
- `ROADMAP.md` has no completion markers at all, so phases that are substantially done read identically to phases that have not started.

### 4.4 Undocumented procedures

Four operational procedures exist only as precedent in the artifacts that
performed them:

1. **Ledger ID collision and merge remapping.** Three `CORR-20260724-*` records perform it; no doc describes how to detect a collision, choose replacement IDs, or decide between a correction and a supersession.
2. **Legacy freezing.** `tools/legacy_ledger_inventory.yaml` and `tools/legacy_run_inventory.yaml` are enforced by the validator and explained in no markdown file.
3. **Resuming a paused goal.** `ledger/README.md` and the `coordinate-research-goal` skill say when to pause; neither gives the resume sequence.
4. **Root-versus-subdirectory ledger migration.** The de facto rule (root records are frozen, new records go in typed subdirectories) is enforced by code and stated nowhere.

### 4.5 Schema documentation gaps

`templates/research-records.md` has **no IDEA/proposal schema**, though
`tools/validate_ledger.py` requires proposals to carry `class`, `claim`,
`mechanism`, and `novelty_status`. Several record types have drifted past their
templates: hypotheses use `title`, `distinguishable_outcomes`, `selected_by`,
`status_detail`, `status_decision`, and `status_evidence`; corrections use
`affects`, `historical_bindings`, `decided_by`, and `record_type`; legacy
evidence uses `validity_status`, `validity_reason`, and `gate_arithmetic`. None
of those fields are documented.

Of 14 files in `tools/`, five are documented only by a module docstring and two
(the legacy inventories) not at all. The five scripts in `src/` have no
repository-level documentation. There is no documented way to run the CI checks
locally, though `.github/workflows/validate.yml` shows the exact sequence.

---

## 5. Prioritized remediation

Ordered by how much each gap degrades the program's ability to know what it
knows.

### P0 — the knowledge record does not reflect what was proven

1. **Promote the eleven replicated evidence records to `KN-FIND` entries**, or record an explicit `not_warranted` justification for each in a superseding decision. Proven scoped negatives are the highest-value entries here: they are what stops future ideation from re-walking closed routes. This requires Coordinator authority and should run through `/curate-knowledge` with an archival commit.
2. **Reconcile `knowledge/README.md` with `knowledge/SEEDING.md`.** Either adopt the README schema (adding `proof_status` / `proof_refs` to entries) or rewrite the README to document the schema actually in use. The current state tells a fresh agent to write frontmatter no existing entry uses.
3. **Resolve the seven dangling references.** `TASK-20260723-402` as an unresolvable `archived_by` target is an evidence-integrity issue, not a cosmetic one.

### P1 — structural integrity of the record

4. **Document the two-layer ledger** in `ledger/README.md`: root records are frozen legacy, typed subdirectories are canonical, and the five duplicated `DEC-20260722-*` IDs resolve to the subdirectory copy.
5. **Write down the merge/ID-collision and legacy-freezing procedures.** The precedent is good; it should not have to be reverse-engineered from three correction records.
6. **Close or explicitly park the four unaccounted experiments** (`EXP-IMON-001`, `EXP-ISADV-001`, `EXP-MONO-001`, `EXP-XEDN-001`) and the two non-terminal hypotheses (`H-FB3-001`, `H-SEMAEV-001`).
7. **Either create the Reviewer agent contract or remove the role** from `AGENTS.md`, `docs/dynamic-subagent-dispatch.md`, and `orchestration/model-policies.yaml`. A role the runtime cannot instantiate will keep producing dispatch failures.
8. **Repair or annotate the seven `EXP-SIG-005` runs** missing their command records.

### P2 — depth and coverage

9. **Deepen the baseline entries.** `KN-TECH-001` (rho), `KN-LIT-008`, `KN-LIT-011`, and `KN-LIT-012` are the measuring stick for every advantage claim and are among the thinnest files in the corpus. They need concrete constants, parameter regimes, and crossover conditions.
10. ~~**Add the missing classical-ECDLP entries**: Pohlig–Hellman and small-subgroup/invalid-curve/twist hygiene; MOV and Frey–Rück; anomalous curves (Smart, Satoh–Araki); a dedicated BSGS technique entry; concrete rho record computations (Certicom, ECC2K-130, and the current public records); Shor resource estimates for ECDLP.~~ **Done 2026-07-24** — see §6.
11. **Add verified/reported separation to the 29 technique entries** and limits sections to the ten open problems and three techniques that lack them.
12. **Document `templates/research-records.md`'s missing IDEA schema** and the undocumented fields on hypotheses, corrections, and legacy evidence.
13. **Add READMEs** for `coordination/`, `focus/`, `inputs/`, `src/`, `tools/`, and `tests/`, and update the root `README.md` map, its stale "next milestones" block, and `CLAUDE.md`'s subagent count. Mark `plan.md` as historical.
14. **Annotate the validator baseline**: what error classes the 1,138 suppressed entries cover and the conditions under which an entry may be removed.

## 6. Closure record — topic coverage (2026-07-24)

The topic gaps in §1.6 were filled the same day the assessment was written.
Twenty-six entries were added, taking the corpus from 125 to 151. Every
citation was checked against a primary index before the entry was written;
where the actual paper PDF was retrieved and its claims read, the entry
carries `citation_verified: read` rather than `web`.

### Literature added

| Gap from §1.6 | Entries |
| --- | --- |
| Pohlig–Hellman / small-subgroup / invalid-curve / twist | `KN-LIT-082` (Pohlig–Hellman 1978), `KN-LIT-091` (Lim–Lee small subgroup), `KN-LIT-092` (Biehl–Meyer–Müller invalid curve), `KN-LIT-093` (Bernstein, Curve25519 / twist security) |
| MOV / Frey–Rück pairing attacks | `KN-LIT-084` (MOV 1993), `KN-LIT-085` (Frey–Rück 1994), `KN-LIT-086` (Balasubramanian–Koblitz, genericity of large embedding degree) |
| Anomalous curves | `KN-LIT-087` (Semaev), `KN-LIT-088` (Satoh–Araki), `KN-LIT-089` (Smart) |
| Baby-step giant-step | `KN-LIT-083` (Shanks 1971) |
| Concrete rho record computations | `KN-LIT-095` (112-bit prime field, secp112r1), `KN-LIT-096` (Breaking ECC2K-130), `KN-LIT-097` (117.35-bit binary, the current public record) |
| Quantum ECDLP / Shor resource estimates | `KN-LIT-098` (Shor 1997), `KN-LIT-099` (Roetteler–Naehrig–Svore–Lauter concrete circuit counts) |
| Prime-field Weil-descent criteria | `KN-LIT-090` (Diem, GHS in odd characteristic) |
| Memory / communication cost models | `KN-LIT-094` (Wiener, *The Full Cost of Cryptanalytic Attacks*) |

### Techniques added

`KN-TECH-030` Pohlig–Hellman reduction and subgroup hygiene · `KN-TECH-031`
BSGS and the deterministic baseline · `KN-TECH-032` pairing transfers and the
embedding degree · `KN-TECH-033` anomalous curves and the additive transfer ·
`KN-TECH-034` curve and point validation · `KN-TECH-035` full-cost accounting ·
`KN-TECH-036` public record computations as baseline calibration ·
`KN-TECH-037` quantum resource estimation.

### Two findings that change how baseline claims should be read

The material was gathered to fill gaps, but two facts from it bear directly on
`GOAL-CRYPTO-001` and belong in the assessment rather than only in the corpus:

1. **The largest publicly completed ECDLP is 117.35 bits** (binary field, 2016,
   ~2^60 iterations, up to 576 FPGAs over six months). The largest prime-field
   solve — the class this program targets — is **112 bits**, from 2009. A
   256-bit curve needs roughly 2^128 iterations, a gap of about 2^68. No
   mechanism can be validated end-to-end at cryptographic size, which is
   independent confirmation that the goal's "advantage over a matched
   baseline" framing is the only workable one.
2. **Memory is not free, and the exponent proves it.** Wiener shows BSGS costs
   n^{1/2} processor steps but n^{2/3+o(1)} in full cost, and states explicitly
   that it is wrong to conclude Shanks's method and rho have the same full
   cost. Any index-calculus-style route that buys a lower step count with a
   factor base and relation matrix must be charged this way, or an apparent
   advantage may be an accounting artifact.

### Deliberate schema choices, and what remains open

- The new entries use `citation_verified: read` for retrieved-and-read sources,
  which is the vocabulary `knowledge/SEEDING.md` defines. The two pre-existing
  full-text entries (`KN-LIT-080`, `KN-LIT-081`) use `full_text` for the same
  meaning. This inconsistency is now visible in `INDEX.md` and should be
  resolved when §5 item 2 (README/SEEDING reconciliation) is done.
- The 29 technique entries flagged in §1.5 for lacking a verified-versus-reported
  split are unchanged, but the eight new technique entries each carry an
  explicit `## Verified vs reported` section, setting the pattern for
  retrofitting the others.
- Items **not** addressed: the `KN-FIND` promotion gap (§1.1), which requires
  Coordinator authority over evidence records rather than literature curation;
  the depth of the existing baseline entries (§5 item 9), which requires
  superseding entries rather than adding them; and everything in §2, §3 and §4.

## 7. Closure record — lattice cryptanalysis (2026-07-24)

§1.6 audited topic coverage against the program's ECDLP work. A second audit,
run after the program's focus was set on **lattices and elliptic curves**,
applied the same test to the lattice half of the corpus and found a gap of the
same class but wider.

### What the lattice audit found

Before this closure the corpus held 23 lattice-related entries (`KN-LIT-046`
to `-061`, `-080`, `-081`; `KN-TECH-020` to `-023`; `KN-OPEN-012`) totalling
5,838 words. They form a **post-quantum foundations and standards map** —
LLL/BKZ, LWE/SIS, Ring- and Module-LWE, the NIST schemes, a pointer to the LWE
estimator — plus two deeply reviewed 2026 ML-KEM-adjacent papers. They are not
an attack corpus. Thirteen specific attack topics were checked; **none had a
dedicated mechanistic entry and eight had no mention at all**:

| Topic | State before |
| --- | --- |
| Primal / uSVP attack (Kannan embedding) | Named in two entries, never described |
| Dual attack, and the 2023 dual-sieve dispute | "Dual attack" as a label only; no Ducas–Pulles, no MATZOV |
| Core-SVP methodology, `2^0.292β` / `2^0.265β` | `0.292n` present as a sieving exponent; no Core-SVP, no `0.265`, no NewHope |
| BKZ simulation, Geometric Series Assumption | BKZ 2.0 cited; GSA absent by name and unexplained |
| Enumeration: Kannan, extreme pruning | Pruning mentioned via a citation; no dedicated coverage |
| Sieving beyond BDGL (Nguyen–Vidick, GaussSieve, G6K) | Absent |
| Overstretched NTRU / fatigue point | One generic phrase in `KN-OPEN-012` |
| Ideal-SVP attacks (CDPR, CDW, Biasse–Song) | One generic phrase in `KN-OPEN-012` |
| LWE with hints / side information | Absent |
| Decryption-failure attacks | Modelling only (`KN-LIT-080`); no attack methodology |
| Lattice challenges and records | Absent |
| Sieving memory under full-cost accounting | Absent — `KN-TECH-035` and `KN-LIT-094` are ECDLP-only |
| ECDLP ↔ lattice links beyond `KN-OPEN-012` | Passing bridges only |

The asymmetry mattered: the program had a full-cost discipline on the curve
side and quoted lattice costs as if memory were free.

### What was added

Thirty-nine entries, taking the corpus from 151 to 190. Citations were verified
against IACR ePrint, publisher DOIs, DBLP and CryptoDB before writing; two
ePrint numbers suggested by search were wrong and were corrected by direct
lookup. `citation_verified: read` marks entries whose source was actually
retrieved and read; `web` marks bibliographic-only verification, used for four
entries.

- **Attack algorithms and cost models** — `KN-LIT-100` (Schnorr, the GSA),
  `KN-LIT-101` (BKZ 2.0), `KN-LIT-102` (extreme pruning), `KN-LIT-103`
  (Nguyen–Vidick), `KN-LIT-104` (List/Gauss Sieve), `KN-LIT-105` (dimensions for
  free), `KN-LIT-106` (G6K and the records), `KN-LIT-107` (NewHope / core-SVP),
  `KN-LIT-108` (uSVP success condition), `KN-LIT-122` (quantum sieve circuits),
  `KN-LIT-123` (Albrecht–Ducas survey).
- **The dual-attack dispute** — `KN-LIT-109` (Guo–Johansson), `KN-LIT-110`
  (MATZOV), `KN-LIT-111` (Ducas–Pulles).
- **Structure** — `KN-LIT-112` (subfield attack), `KN-LIT-113` (Kirchner–Fouque),
  `KN-LIT-114` (NTRU fatigue), `KN-LIT-115` (CDPR), `KN-LIT-116` (Stickelberger),
  `KN-LIT-117` (Biasse–Song).
- **Leakage and failures** — `KN-LIT-118` (LWE with side information),
  `KN-LIT-119` (decryption failures).
- **Calibration** — `KN-LIT-120` (Darmstadt lattice challenge), `KN-LIT-121`
  (LWE challenge).
- **Techniques** — `KN-TECH-038` primal attack · `-039` dual attack and the
  dispute · `-040` core-SVP and the cost-model zoo · `-041` basis profiles, GSA
  and BKZ simulation · `-042` enumeration, pruning and the sieving crossover ·
  `-043` the sieving family · `-044` charging memory in lattice attacks ·
  `-045` NTRU fatigue as an instance-validity check · `-046` structured-lattice
  attacks and the approximation-factor ceiling · `-047` integrating hints ·
  `-048` decryption-failure attacks · `-049` calibrating against public records.
- **Open problems** — `KN-OPEN-016` (is the dual attack's advantage real?),
  `KN-OPEN-017` (where does the enumeration/sieving crossover move under full
  cost?), `KN-OPEN-018` (does lattice machinery bear on the plain ECDLP at
  all?).

### Three things this material establishes about the program's own methods

1. **The cost model is part of the claim.** MATZOV's headline result — three
   NIST finalists below their required security levels, Kyber by 4 to 14 bits —
   is driven substantially by *re-costing an existing sieve*, not by a new
   attack. Core-SVP itself charges one SVP oracle call and no memory. Two
   "lattice attack costs" can differ by tens of bits with no algorithmic
   disagreement whatsoever.
2. **The dual-attack episode is the program's failure mode, executed in
   public.** A claimed advantage over a baseline, resting on an unexamined
   heuristic, independently reproduced by a second group, then falsified at the
   level of the heuristic rather than the code (`KN-LIT-111`). It also shows why
   independent replication of a *claim* is not independent validation of its
   *assumptions*.
3. **A memory-accounting inconsistency was live in this corpus.** Sieving needs
   at least `2^0.2075n` memory by a proven kissing-number bound; enumeration
   uses polynomial space; the measured crossover at dimension 70 is a step-count
   comparison. The program charges memory on the ECDLP side and had not on the
   lattice side. `KN-TECH-044` states the discipline and `KN-OPEN-017` states
   the unanswered quantitative question, which is self-contained and needs no
   new mathematics.

### What remains open after this closure

- **`KN-FIND` is still empty** (§1.1). Unchanged and still the highest-severity
  gap; it needs Coordinator authority over evidence records, not curation.
- **Baseline depth** (§5 item 9) is unchanged and now applies on both sides: the
  lattice foundations entries (`KN-LIT-051`, `-059`, `-060` at ~200 words) are as
  thin as the ECDLP baseline entries, and deepening them requires superseding
  entries rather than new ones.
- **The `read` / `full_text` vocabulary split** (`KN-LIT-080`, `-081`) is
  unresolved and now spans 50 entries.
- Nothing in §2, §3 or §4 is addressed.

## What this assessment does not establish

It says nothing about whether any mathematical conclusion in the ledger is
correct. It did not re-verify certificates, re-run experiments, or re-check
cost arithmetic. Coverage of a topic in `knowledge/` is not evidence that the
topic was handled correctly, and absence is not evidence that it was handled
incorrectly — only that the record does not show it either way.

# Tagging report — making "distinguisher is not break" grep-enforceable, and filing five deferred specification entries

**Task:** TASK-20260808-f9374d · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-a68f79
**Role:** coordinator · **Date:** 2026-08-08

**Inference record (verbatim, as required by the task card):** requested_policy
coordinator-orchestration-code; per CLAUDE.md per-role model selection is
process-level under Claude Code and subagents keep model: inherit, so the
resolved model is the session model; fallback_used: false; model_verified: false
(no adapter probe receipt for this session).

**Budget:** authorized 1 run, 2 GB, 3600 s. **Runs executed: 0.** This role has
no execute capability (`orchestration/roles.yaml`, `may_execute_experiments:
false`); the tool surface available here was read, search, write and edit. No
command was executed, no network request was made, no hash was computed, and no
git operation was performed. §7 lists every obligation of this task whose
*verification* requires execution by whoever drives the harness.

**Claim tier: toy, unchanged. `GOAL-MCE-001.active_hypothesis_ids`: empty,
unchanged.** Filing corpus entries establishes nothing about Classic McEliece, in
either direction. Nothing in this report or in the nine entries filed by it
asserts that any parameter set is secure, insecure, above or below any category
threshold, or that any attack cost is achievable.

**Not attempted, deliberately:** `iacr:2026/1232`'s PDF, by any route. The 403 is
path-scoped and reproducible, circumvention is FORBIDDEN, and AGENTS.md rule 5
makes a blocked route a recorded outcome. No route to it was tried in this task.

**Transcription convention:** `TASK-20260808-a9f648`'s
`transcription_convention.md` binds every quotation and table below and in the
nine entries. §6 of this report states, rule by rule, how the seven existing form
violations it names (V-1…V-7) were avoided rather than repeated.

---

## 1. JOB 1 — THE AUDIT COMMAND

### 1.1 The command

**Authoritative copy: `knowledge/TAG-CLAIM-CLASS.md` §2.** Reproduced here
byte-identically because the task card requires the exact command in this report.
The two files are both immutable once archived; a future change supersedes both
under a new task id rather than editing either.

```sh
cd "$(git rev-parse --show-toplevel)"
grep -rlE '^tags:.*(\[|,) ?distinguisher(,|\])' knowledge/ \
| xargs -r grep -lE '^tags:.*(\[|,) ?key-recovery(,|\])' \
| while read -r f; do
    grep -qE '^superseded_by: *KN-' "$f" && continue
    id=${f##*/}; id=${id%.md}
    grep -rhE '^supersedes:' knowledge/ \
      | grep -oE 'KN-[A-Z]+-[0-9A-Za-z]+' \
      | grep -qx "$id" || printf '%s\n' "$f"
  done
```

### 1.2 What its output means

**Empty output means the corpus is clean.** That is the entire contract, and it
is the only contract.

**Every line it prints is a violation.** The line is the path of a *live*
(non-superseded) knowledge entry whose front-matter `tags` carry both
`distinguisher` and `key-recovery` as exact list tokens. `RQ-MCE-e65b3c`'s
constraint — *"Distinguisher is not break … Any deliverable naming a
distinguisher states which it is"* — says an entry must not assert both claim
classes at once. Each printed path is an entry that does.

**Check the output, not the exit status.** `grep`'s exit codes are consumed
inside the pipeline; the last stage is a `while` loop whose status reflects the
loop, not the finding. A wrapper that tests `$?` will be wrong.

**A second command is part of the audit, not an optional extra:**

```sh
cd "$(git rev-parse --show-toplevel)"
grep -rlE '^[[:space:]]*-[[:space:]]+(distinguisher|key-recovery)[[:space:]]*$' knowledge/
```

AUDIT-1 reads one line per entry and is therefore blind to a claim-class token
written as a YAML **block** sequence item. 56 `knowledge/literature/` entries and
23 `knowledge/findings/` entries use block-style tags. AUDIT-2 prints any entry
that lists either token that way — i.e. any entry AUDIT-1 cannot see. It too
prints nothing when the corpus is clean. It is deliberately over-broad: it will
also fire on a body bullet that happens to read exactly `- distinguisher`. A
false positive costs one look; a false negative hides a violation.

### 1.3 Why the regex is shaped the way it is

The design decisions are the substance of this job, because a tag scheme that
needs human judgement to audit is not enforceable.

**Exact list tokens, not substrings.** The corpus already holds three legitimate
tags containing `distinguisher` as a substring: `structural-distinguisher`
(`KN-TECH-063`), `hybrid-distinguisher` (`KN-TECH-065`), `distinguisher-duality`
(`KN-TECH-069`). A naive `grep distinguisher` returns all three as false
positives. **An audit with known false positives is one nobody runs**, which is
how the constraint became unenforced in the first place. `(\[|,) ?TOKEN(,|\])`
matches only a whole list item.

**Two single-token greps, not one two-token regex.** A single regex must consume
the first token's closing delimiter before searching for the second, and then
fails on the adjacent case `[distinguisher, key-recovery]`, where that one comma
is simultaneously the first token's closing delimiter and the second's opening
one. Two independent matches have no shared consumption and no such blind spot.

**A third token for the genuine both-case.** A paper may honestly claim a
distinguisher *and* escalate it to key recovery; forcing mutual exclusion without
an outlet would push a transcriber to improvise, which
`transcription_convention.md` Rule 7 forbids. `knowledge/TAG-CLAIM-CLASS.md`
defines `distinguish-then-recover` for that case, and chooses that spelling
deliberately: it contains neither `distinguisher` nor `key-recovery` as a
substring, so even a careless `grep -c distinguisher` cannot mis-fire on it. An
entry carrying it must have a `## Claim class` section naming which result is
which.

**Identifiers are extracted from `supersedes:`, not pattern-matched inside it.**
This was a real defect in a first draft of the command, found by searching the
corpus rather than by reasoning: `supersedes:` already exists in **two** shapes.
Nine entries use a bare scalar (`supersedes: KN-TECH-9d21c4` in `KN-TECH-6c0e15`,
`KN-TECH-1a5b7e`, `KN-TECH-058`, `KN-OPEN-028`, `KN-LIT-7642`, `KN-LIT-7607`,
`KN-LIT-7640`, `KN-LIT-7674`, `KN-LIT-c41d8b`); the four entries filed today use a
flow list. A regex assuming either shape silently misses the other. The command
therefore pulls identifiers off the line with `grep -oE` and matches them whole
with `grep -qx` — whole-match because a substring test would let `KN-LIT-110` be
satisfied by a `supersedes:` line naming `KN-LIT-1105`, and the corpus's legacy
three-digit ids make that live rather than hypothetical.

**Both retirement mechanisms are honoured.** An entry is treated as retired if
some entry names it in `supersedes:` **or** it carries a non-null
`superseded_by:`. Only the first applies today, because the task card forbids
editing the four originals. The second is included so the command stays correct
if a later `/curate-knowledge` pass fills `superseded_by` as
`knowledge/README.md` asks — see §5.1, which is an open tension this task did not
resolve unilaterally.

### 1.4 What the audit does NOT do

- **It enforces form, not correctness.** It cannot tell whether an entry's claim
  class is the *right* one. Tagging a key-recovery paper `distinguisher` passes
  and is still wrong. The audit guarantees only that the corpus never asserts
  both at once.
- **It does not require classification.** Most entries carry no claim-class token
  and that is legal. Its silence must never be read as "the corpus is fully
  classified."
- **It checks tags, not prose.** An entry may still describe a distinguisher as a
  break in its body.
- **It is scoped to `knowledge/`.** Ledger records, experiment artifacts and task
  reports are not covered.

### 1.5 I DID NOT RUN EITHER COMMAND

**Stated plainly, because the deliverable is a command and the temptation is to
report its output.** This role has no execute capability. **Neither command above
has been run, by me or by anything else, and no output of either is reported
anywhere in this document.** The commands are untested *as written*: in
particular the `while`-loop shell quoting, `xargs -r`, and POSIX `grep -E`
behaviour have not been exercised.

**The harness-driving session must run both commands and confirm each prints
nothing** before this task's completion gate is treated as met.

What I *did* do is run the read-only search tool available to this role
(ripgrep, via the `Grep` tool) with the equivalent patterns over `knowledge/`.
That is a different engine from POSIX `grep` and a different pipeline, so it
corroborates the *corpus state* and not the *command*. Those searches returned:

| Search (ripgrep, over `knowledge/`) | Result |
|---|---|
| `^tags:.*(\[\|,) ?distinguisher(,\|\])` — before this task | 9 files |
| `^tags:.*(\[\|,) ?key-recovery(,\|\])` — before this task | 54 files |
| intersection of the two — before this task | **exactly 4**: `KN-LIT-13a01d`, `KN-LIT-71d1a0`, `KN-LIT-7ee1a9`, `KN-LIT-e37d4c` — the four named in the task card, and no others |
| `^tags:.*distinguisher` (substring) vs the exact-token form | 12 vs 9; the 3-file difference is exactly `KN-TECH-063`, `KN-TECH-065`, `KN-TECH-069`, i.e. §1.3's compound tags |
| `^tags:.*key-recovery` (substring) vs the exact-token form | 54 vs 54 — no compound tags, and no spacing anomalies anywhere in the corpus |
| AUDIT-2's pattern (block-style claim-class item) | **no files** |
| `^tags:.*(\[\|,) ?distinguisher(,\|\])` — after this task | 13 files: the 9 above plus the 4 superseding entries |

The fourth and fifth rows are the evidence that the `(\[|,) ?` spacing assumption
holds across the whole corpus and not merely across the files I read: for
`key-recovery` the substring and exact-token sets are identical at 54, so no
entry writes its tags with unexpected spacing.

**Expected post-state, which the harness must confirm rather than assume:**
AUDIT-1 prints nothing, because each of the four still-both-tagged originals is
now named in a superseding entry's `supersedes:` line; AUDIT-2 prints nothing,
because no entry lists either token in block style.

---

## 2. JOB 1 — THE FOUR SUPERSESSIONS

All four live in `knowledge/literature/`. **None of the four originals was opened
for write by this task.** Each superseding entry drops `key-recovery`, keeps
`distinguisher`, adds `claim-class-corrected`, names its predecessor in a
`supersedes:` flow list, and carries a `## Claim class` section stating the basis
for the classification and the condition that would falsify it.

| Superseding entry | Supersedes | Tags removed → added | Claim class, and its basis |
|---|---|---|---|
| `knowledge/literature/KN-LIT-3c9f21.md` | `KN-LIT-13a01d` — Faugère–Gauthier–Otmani–Perret–Tillich, *"A distinguisher for high rate McEliece cryptosystems"* | −`key-recovery`, +`claim-class-corrected` | `distinguisher`. The superseded entry states it outright: *"It does not recover keys; it distinguishes"* |
| `knowledge/literature/KN-LIT-a4d70e.md` | `KN-LIT-71d1a0` — Randriambololona, *"The syzygy distinguisher"* | −`key-recovery`, +`claim-class-corrected` | `distinguisher`, from the title and the superseded entry's description. **Flagged in the entry as the weakest of the four** |
| `knowledge/literature/KN-LIT-6b1fc8.md` | `KN-LIT-7ee1a9` — Lemoine–Mora–Tillich, *"Understanding the new distinguisher of alternant codes at degree 2"* | −`key-recovery`, +`claim-class-corrected` | `distinguisher`, and a step further removed: the subject is an *analysis* of someone else's distinguisher |
| `knowledge/literature/KN-LIT-d82a53.md` | `KN-LIT-e37d4c` — Wiemers, *"A note on the Goppa code distinguishing problem"* | −`key-recovery`, +`claim-class-corrected` | `distinguisher`. Both recorded titles name distinguishing; neither names recovery |

### 2.1 The basis for the reclassification, and its limit

**Stated without softening: this program has not read any of these four papers.**
The classification rests on each paper's title and on the superseded entry's own
recorded description — which is itself relayed from a bibliography line at
`confidence: reported`. It is as strong as a relayed abstract and no stronger.

Each superseding entry therefore carries an explicit falsification condition: if
a read of the full text shows a key-recovery claim, the correct token is
`distinguish-then-recover` and **that entry must itself be superseded under a new
id** rather than re-tagged in place.

`KN-LIT-a4d70e` (the syzygy distinguisher) is singled out inside its own entry as
the weakest of the four, for two concrete reasons rather than as a hedge: the
distinguisher line's whole historical pattern is escalation, and its author is a
co-author of `KN-LIT-7c4620`, the 2026 heuristic subexponential attack that is
`RQ-MCE-e65b3c`'s primary target.

### 2.2 Where the mis-tagging came from

All four were filed on 2026-08-03 by the GATHER-20260803 sweep and all four carry
the same `structural-attack, key-recovery, distinguisher` prefix. That has the
shape of a tag block applied to a cluster rather than a judgement made per paper.
**This is an inference from the pattern, not an established fact about how the
sweep ran**, and it is recorded as the former in each entry.

### 2.3 An inherited inconsistency, recorded not resolved (AGENTS.md rule 8)

`KN-LIT-13a01d` records `venue: IEEE Transactions on Information Theory`
alongside `doi: 10.1109/itw.2011.6089437`, whose `itw.2011` component has the
shape of an IEEE Information Theory *Workshop* proceedings identifier. Both
strings are carried forward unchanged into `KN-LIT-3c9f21` and the observation is
recorded there. **This task fetched neither record and asserts nothing about what
the DOI resolves to** — the observation is about two recorded strings, not about
the world. Reconciling them needs a retrieval and is a `/curate-knowledge` job.

---

## 3. JOB 2 — THE FIVE SPECIFICATION ENTRIES

All five live in `knowledge/literature/`. All five were proposed, and
deliberately not filed, by `TASK-20260803-f3aece` (BATCH-001) in
`proposed_kn_lit_entries.md`.

| Entry | Document | `citation_verified` | Reason |
|---|---|---|---|
| `KN-LIT-84b674.md` | Classic McEliece **cryptosystem specification**, `mceliece-spec-20221023.pdf`, sha256 `dcc68788…`, 16 pp. | **`web`** | Retrieved and read by `TASK-20260803-f3aece` on 2026-08-03 (log seq 5), re-fetched by that task after writing with the hash reproducing byte-identically. **Not read in this environment; this task fetched nothing.** Not raised to `read` because this task cannot attest a read |
| `KN-LIT-6da230.md` | **guide for security reviewers** (SEC), `mceliece-security-20221023.pdf`, sha256 `db17ef08…`, 36 pp. | **`read`** | **The one entry that earns it.** `TASK-20260808-1985f1` — same goal, same batch, this environment — retrieved it three times (twice curl, once python urllib under TLS verification), each HTTP 200 / 332574 bytes / sha256 `db17ef08…` / 36 pages, and transcribed Table 1 in full: 150/150 cells agreeing across six extractor configurations over two independent retrievals, verified after writing against a third |
| `KN-LIT-7d2077.md` | **guide for implementors**, `mceliece-impl-20221023.pdf`, sha256 `86225992…`, 19 pp. | **`web`** | Retrieved and read by `TASK-20260803-f3aece` (log seq 9); its Table 1 transcribed by two independent extractors reconstructing to the same 10×4 array. **Not read in this environment** |
| `KN-LIT-4fa25d.md` | **what plaintext confirmation means**, `mceliece-pc-20221023.pdf`, sha256 `9894108c…`, 1 p. | **`web`** | Retrieved and read by `TASK-20260803-f3aece` (log seq 15). **Not read in this environment** |
| `KN-LIT-eb2b9b.md` | **NIST IR 8545**, `NIST.IR.8545.pdf`, sha256 `d802f484…`, 34 pp. | **`web`** | Retrieved and read by `TASK-20260803-f3aece` (log seq 14, reached via the csrc.nist.gov landing page at seq 13). **Not read in this environment**, and the route is not known to be stable — see §3.3 |

### 3.1 Why exactly one entry is `read`

The task card's rule is *"Mark it true only for a source you actually read in
this environment"*, and its pointer is that `TASK-20260808-1985f1` has just
obtained SEC, *"so material resting on that source has a genuinely verified
provenance chain — check what each proposed entry actually rests on rather than
assuming."*

I checked, by reading `TASK-20260808-1985f1`'s four artifacts and
`TASK-20260803-f3aece`'s `source_access_log.yaml`, rather than by assuming the
proposal was right. What each entry rests on:

- **SEC only** is covered by a retrieval in this environment. Its sha256 was
  computed independently by two tasks on two different hosts from three
  retrievals, and they agree.
- **The other four** rest on retrievals made on 2026-08-03, in a different
  session, on a different host, on branch
  `claude/mceliece-bibliography-aggregate-7ogd0d`. That read is real, logged, and
  was independently corroborated (validator `TASK-20260803-409c5e` re-acquired 26
  sources for 25 hash matches and 0 fabrications). It is nonetheless **not a read
  in this environment**, and `RQ-MCE-e65b3c` carries a standing instruction
  inherited from `KN-OPEN-3f7a21` — where 7457 entries claimed `read` against a
  `downloads/` tree that was absent and never git-tracked — to treat unattested
  `read` provenance as unconfirmed.

`web` is the honest value for those four: their bibliographic line *was* verified
against the live web, by fetching it. It understates the strength of a logged,
hash-anchored, validator-corroborated retrieval, and it is chosen anyway because
understating is the safe direction under AGENTS.md rule 9. **Every one of the
four carries a `citation_verified_note` giving the full retrieval detail and a
concrete upgrade path** — re-fetch, compare against the recorded sha256,
transcribe under `TASK-20260808-a9f648`'s convention — so no reader is left
thinking the citation is unsupported. `KN-LIT-4fa25d` is flagged as the cheapest
upgrade: the document is one page.

### 3.2 Per-claim provenance inside the `read` entry

`citation_verified: read` on `KN-LIT-6da230` covers the entry, but the entry's
claims do not all rest on the same read, and collapsing them would be the error
the field exists to prevent. That entry therefore marks **every** claim with one
of three markers: `[SEC-READ]` (first-hand in this environment by
`TASK-20260808-1985f1`), `[B1-READ]` (read by `TASK-20260803-f3aece` from a
byte-identical retrieval, not re-read here), `[B1-DRAFT]` (stated only in the
BATCH-001 draft, with no supporting quotation in any transcription deliverable).

The scope of the first-hand read is stated in the entry's front matter and is
narrow: Table 1, its caption, its column header row, the §3.5 heading, the
sentence introducing the table on page 9, and cost-model and scope sentences on
pages 10–11. **31 of 36 pages were not read in this environment.** The security
*category* sentences (1, 3, 5, 5, 5 and 1, 2, 4, 4, 5) are `[B1-READ]`, not
`[SEC-READ]` — with one position independently corroborated, because
`sec_table1.md` quotes SEC naming 460896 as "Category 3" from printed page 11.

The same `[B1-DRAFT]` marker is applied in `KN-LIT-7d2077` to the private-key
compression and PQ-WireGuard claims, which appear only in the BATCH-001 draft.

### 3.3 One claim was deliberately dropped

The proposed NIST IR 8545 entry asserted that *"The report also records that SIKE
was broken early in the fourth round and removed from consideration."* **That
claim is not filed.** It is traceable to no quotation in any transcription
deliverable, and it sits inside the same draft's own admission that *"the
report's BIKE, HQC and SIKE analyses were not"* read. Relaying it would have been
an unsupported citation under AGENTS.md rule 9. The omission is recorded in the
entry's "Not verified here" section so the drop is visible rather than silent,
and the `sike` tag was removed with it.

The 17-name author list on the same entry **was** kept, and flagged: an author
list is exactly the field that gets invented, so its `authors_note` states that
it is copied from the BATCH-001 draft's claimed title-page transcription, is
quoted in no transcription deliverable, was not re-verified here, and is the
least-corroborated field in the entry.

---

## 4. IDENTIFIERS MINTED, AND HOW THEY WERE CHECKED

**This role cannot run `tools/allocate_id.py`.** No token below was allocated by
that tool, and the harness session must re-verify each with
`python3 tools/allocate_id.py --check <id>` before the archive.

**Four newly minted, for the supersessions.** Chosen as random 6-hex tokens
without scanning state for a maximum, per AGENTS.md rule 14 and CLAUDE.md:

`KN-LIT-3c9f21`, `KN-LIT-a4d70e`, `KN-LIT-6b1fc8`, `KN-LIT-d82a53`

**Five reserved by `TASK-20260803-f3aece`, re-verified free and reused.** The
proposal's own filing checklist requires re-checking them, and its
cross-references (`"see KN-LIT-6da230 and KN-LIT-7d2077"`) already bind them:

`KN-LIT-84b674`, `KN-LIT-6da230`, `KN-LIT-7d2077`, `KN-LIT-4fa25d`,
`KN-LIT-eb2b9b`

**How each was checked free — three independent checks, repo-wide:**

1. A repository-wide search for the bare 6-hex token across **all** paths.
   Result: the four new tokens appear nowhere as an identifier. They do appear as
   incidental substrings inside long sha256 hex strings in experiment JSON blobs
   (e.g. `3c9f21` inside `…4ec3c9f2134f…`), which are not identifiers and are
   recorded here so the raw hit count is not mistaken for a collision. The five
   reserved tokens appear only inside
   `…/BATCH-001/tasks/TASK-20260803-f3aece/proposed_kn_lit_entries.md`, which is
   the reservation itself.
2. A repository-wide search for the prefixed form `KN-[A-Z]+-<token>`. Result:
   six hits, all in that same proposal file; **zero** for the four new tokens.
3. A filesystem glob for
   `knowledge/**/KN-*-{3c9f21,a4d70e,6b1fc8,d82a53,48b4eb,7b78de,b7f8f8,209151,9a7860}.md`.
   Result: **no files found.**

**Scope limit on that determination, stated plainly:** these are string matches
over this worktree at one moment. They cannot see a concurrent worktree that has
minted the same token and not yet merged. That residual risk is exactly what the
random-token scheme bounds and does not eliminate; `--check` at archive time is
the last gate.

**No new `RQ-`, `H-`, `EXP-`, `EV-`, `DEC-` or `TASK-` identifier was minted.**

---

## 5. WHAT I COULD NOT RESOLVE, AND WHAT I DECIDED NOT TO DO UNILATERALLY

### 5.1 The originals keep both tags, and the audit works around that

`knowledge/README.md` says corrections supersede by *"a new entry, old one gets
`superseded_by`"*. The task card says the opposite for these four: *"Do not edit
the four both-tagged entries"*, and its completion gate says *"the originals are
not edited."* **I followed the task card and edited nothing.**

The consequence is that the four originals still literally carry both tags. The
audit resolves this by scoping to *live* entries, which is consistent with
AGENTS.md's retrieval policy (*"Superseded material is excluded by default and is
never deleted"*), and by treating an entry as retired on **either** signal so it
stays correct whichever way the tension is later settled.

**This is a decision the Coordinator should make explicitly rather than leave to
whoever next reads the two documents.** Filling `superseded_by` on the four
originals would be a one-field change using the corpus's own designated
mechanism, and would let AUDIT-1 drop its most complex stage. I did not do it,
because the task card forbade it and a completion gate is not mine to reinterpret
mid-task.

### 5.2 The vocabulary's home

The normative vocabulary is a **new file**, `knowledge/TAG-CLAIM-CLASS.md`. It is
new rather than an edit to `knowledge/README.md` on purpose: README is written by
many concurrent worktrees, and CLAUDE.md's concurrency section is explicit that
shared-file edits are the failure mode the layout exists to avoid. A new file
cannot conflict.

Two consequences a reviewer should check rather than take on trust:

- The file carries **no YAML frontmatter**, so `tools/build_knowledge_index.py`
  skips it (it requires a leading `---`), and it is outside the four directories
  `tools/validate_ledger.py`'s `check_knowledge_entries` globs. **I could not run
  either tool to confirm this**; it is read from their source.
- If the Coordinator prefers the rule to live in `knowledge/README.md` or under
  `docs/`, relocating it is a decision record plus a superseding file, not an
  edit to this one.

### 5.3 Duplicate identifiers will appear in `SOURCES.md`, and that is expected

The four superseding entries carry the same `eprint` and `doi` identifiers as the
originals. `tools/build_source_index.py` will list them in its §7, *"Identifiers
claimed by more than one entry"* — which that report itself describes as *"A
curation signal, not an error: one entry may supersede the other."* This is the
expected outcome, not a defect, and it is recorded here so it is not
mis-triaged.

The five specification entries carry a `sha256` key inside `identifiers`, which
is not one of the tool's five canonical kinds. Read from the tool's source, extra
kinds are handled by an explicit second pass and appended after the canonical
ones, so `primary_identifier` remains the URL. **I could not run the tool to
confirm this.**

---

## 6. THE SEVEN EXISTING FORM VIOLATIONS WERE NOT REPEATED

`transcription_convention.md` §12 names V-1…V-7. Each is a *form* violation in an
immutable BATCH-001 artifact; none is a value error. How this task avoided each:

| # | The violation | How it was avoided here |
|---|---|---|
| V-1 | Silent glyph restoration inside a verbatim block, beside a `markers set: 0` declaration | **This is the sharpest case, and it changed what got written.** The `pc` document's ciphertext-representation passage is *the* passage V-1 records. `KN-LIT-4fa25d` states the claim in prose and **quotes no verbatim block from it at all**, saying so explicitly, rather than reproducing a block that carries an undisclosed editorial step into a second document. Separately, `KN-LIT-6da230` states that SEC gives the 140.8 figure's memory as a printed power of two and **does not reproduce the exponent**, because the extraction flattened it and Rule 5.2.4 forbids a conjectured reading from travelling |
| V-2 | An em-dash joining a heading to body text inside a verbatim block | No verbatim block in any artifact of this task joins two source elements. Quotations are of single sentences or single clauses, each attributed at the point of use |
| V-3 | `rounding_rule` stated as "truncated/rounded to 6 places", which does not determine the digit | **No `rounding_rule` line appears anywhere in this task's artifacts, and none is needed: this task rounds nothing.** `KN-LIT-84b674` carries the five code rates as **exact rationals only** (85/109, 35/48, 157/209, 5413/6960, 51/64), which Rule 2.1.7 makes authoritative, and leaves every decimal rendering at its locus-bearing home in `parameter_sets.md` §2 |
| V-4 | Transcribed and derived columns in one table with no per-column `[DERIVED]` marker | `KN-LIT-84b674`'s rate table sits under a heading reading **"Code rates — DERIVED, NOT TRANSCRIBED"**, its one value column is marked `[DERIVED]`, and it states its formula, formula source and the location of the computation |
| V-5 | Unit stated in prose after a table rather than on it | This task transcribes no table of its own. Where a unit matters it is quoted from the source's caption at the point of use (`KN-LIT-7d2077`: *"All sizes are expressed in bytes"*), and `KN-LIT-6da230` records SEC's Table 1 as stating **no unit at any of the five loci** rather than supplying one |
| V-6 | A summary table repeating values without a `see:` pointer to their locus-bearing home | **No value is re-homed by this task.** `KN-LIT-7d2077` explicitly declines to restate its source's 40 size cells and points to `parameter_sets.md` §4; `KN-LIT-6da230` declines to restate SEC Table 1's 150 cells and points to `sec_table1.md` § TRANSCRIBED; `KN-LIT-84b674` points to `parameter_sets.md` §§1–2 |
| V-7 | Two hash-abbreviation forms in one batch | One form throughout: first-8 hex + `…`. Full 64-hex appears once per document, in that entry's `identifiers.sha256` |

**One thing this task's artifacts do not claim.** The convention's own §12
closing note applies here too: form conformance does not prevent asserting
something a source does not say. It is checked against the sources' committed
transcriptions, not against the sources — which this task did not read.

---

## 7. WHAT COULD NOT BE VERIFIED HERE, AND BY WHOM IT MUST BE

**Nothing below was run, and nothing below is claimed to have been run.**

1. **AUDIT-1 and AUDIT-2 (§1.1).** The deliverable of Job 1 is a command, and I
   could not execute it. The harness-driving session must run both and confirm
   each prints nothing. Until it does, the enforceability claim is a design
   claim, not a demonstrated one.
2. **`tools/build_knowledge_index.py` was NOT run.** This task adds nine entries,
   so `knowledge/INDEX.md` is stale and must be regenerated by the harness
   session. It is a `.gitignore`d generated artifact per CLAUDE.md, so it is
   rebuilt rather than committed; `tools/validate_ledger.py`'s
   `check_knowledge_index` invokes the builder in `--verify-corpus` mode and will
   fail if any of the nine has malformed frontmatter.
3. **`tools/build_source_index.py` / `make sources` was NOT run.**
   `/curate-knowledge` step 4 requires it whenever a `KN-LIT` entry is added, and
   nine were. See §5.3 for what it is expected to report.
4. **`tools/validate_ledger.py` was NOT run.** The nine entries are written
   against the schema `check_knowledge_entries` enforces (`id` matching the
   filename stem, `type: literature`, non-empty `title`/`tags`/`confidence`/
   `added`), read from that function's source, but this was not machine-checked.
5. **`tools/allocate_id.py --check` was NOT run** on any of the nine identifiers.
   See §4 for the three read-only checks that were performed instead and their
   stated limit.
6. **No git operation was performed.** Nothing was staged and no commit was made,
   per the task card's explicit instruction. Archival, push, and the PR naming
   these nine `KN-*` records belong to a separate archival task.
7. **`origin/main` was not fetched or compared**, and no branch sync was
   performed. This role could not run git.
8. **No primary source was read by this task.** Not SEC, not the specification,
   not NIST IR 8545, not any of the four distinguisher papers. Every quotation in
   the nine entries and in this report is quoted from this program's own
   committed or pending artifacts, each named at the point of use, and none is
   presented as a first-hand read of a primary source.
9. **Encoding conformance** (§8.5 of the convention: UTF-8, no BOM, LF, no
   trailing whitespace, final newline) is checkable by a one-line command; I
   could not run it and make no claim that any file written here was
   machine-checked against it.

---

## 8. ARTIFACTS WRITTEN BY THIS TASK

Ten files, all inside the declared write scope.

**Task directory** (`coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/tasks/TASK-20260808-f9374d/`):

- `tagging_report.md` — this file, the declared deliverable

**`knowledge/`:**

- `knowledge/TAG-CLAIM-CLASS.md` — the controlled vocabulary and the audit
  command (new file; not a knowledge entry; carries no frontmatter)
- `knowledge/literature/KN-LIT-3c9f21.md` — supersedes `KN-LIT-13a01d`
- `knowledge/literature/KN-LIT-a4d70e.md` — supersedes `KN-LIT-71d1a0`
- `knowledge/literature/KN-LIT-6b1fc8.md` — supersedes `KN-LIT-7ee1a9`
- `knowledge/literature/KN-LIT-d82a53.md` — supersedes `KN-LIT-e37d4c`
- `knowledge/literature/KN-LIT-84b674.md` — cryptosystem specification
- `knowledge/literature/KN-LIT-6da230.md` — guide for security reviewers
- `knowledge/literature/KN-LIT-7d2077.md` — guide for implementors
- `knowledge/literature/KN-LIT-4fa25d.md` — what plaintext confirmation means
- `knowledge/literature/KN-LIT-eb2b9b.md` — NIST IR 8545

**Files NOT written, listed so their absence is not mistaken for an omission:**
no ledger record, no goal checkpoint, no decision record, no hypothesis record,
no edit to any of the four superseded entries, no edit to `knowledge/README.md`,
no edit to any BATCH-001 artifact, and no regenerated `knowledge/INDEX.md`.

---

## 9. COMPLETION GATE, ITEM BY ITEM

| Requirement from the task card | Status |
|---|---|
| Each of the four both-tagged entries is superseded so no entry carries both tags; the originals are not edited | **Met as scoped, and the scope is stated.** Four superseding entries filed, each naming its predecessor and its reason; no original opened for write. "No entry carries both tags" holds for *live* entries — the originals retain their tags and are excluded by supersession. §5.1 records the tension with `knowledge/README.md` and leaves it to a Coordinator decision rather than resolving it silently |
| The report gives the exact audit command and states what its output means; it does not claim the command was run | **Met.** §1.1 gives both commands verbatim; §1.2 states the semantics; §1.5 states in terms that I did not run them and that the harness session must |
| The five specification entries are filed with `citation_verified` set honestly per entry | **Met.** One `read` (SEC, read in this environment by `TASK-20260808-1985f1`), four `web`, each with a `citation_verified_note` giving the retrieval that supports it and a concrete upgrade path. §3.1 gives the reasoning; §3.2 records that the `read` entry marks provenance per claim, not just per entry |
| The report states which ids were minted and how they were verified free | **Met** — §4, including the three checks, the incidental-substring hits recorded so a raw count is not misread, and the stated limit that a search cannot see an unmerged concurrent worktree |
| Follow the settled transcription convention; do not repeat V-1…V-7 | **Met** — §6, rule by rule. V-1 materially changed what was written, twice |
| `knowledge/INDEX.md` regenerated by `tools/build_knowledge_index.py` | **Not done, and could not be** — §7 item 2. The harness session must run it |
| Do not re-attempt `iacr:2026/1232`'s PDF by any route | **Met** — no route was tried. Recorded in the header and in `KN-LIT-6da230` |
| Claim-tier ceiling stays toy; `active_hypothesis_ids` stays empty | **Met** — header; and every one of the nine entries states it establishes nothing about Classic McEliece |
| Never fabricate a citation, quotation, page reference, timing or run | **Met.** §7 item 8 states the provenance of every quotation; §7 states that nothing was executed; §3.3 records the one claim dropped for being untraceable; no timing is reported because none was measured |
| Budget: 1 run, 2 GB, 3600 s | **0 runs executed.** No budget limit was reached and no budget figure is reported as a measurement |

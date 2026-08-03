# Red team — GOAL-MCE-001 BATCH-002

**Task:** `TASK-20260803-9ab856` · **Goal:** `GOAL-MCE-001` · **Batch:** BATCH-002
**Role:** red-team · **Date:** 2026-08-03
**Requested policy:** `review-adversarial` · **Resolved model:** `claude-opus-5` ·
**`fallback_used`: `true`**
**Reviewed object:** snapshot commit `b30400a9699e04a0aaca49d5278ab7c50027da13`
(parent `33750003`), the twelve paths in that commit's
`snapshot-receipt.json`. Working-tree-only artifacts were not accepted as
evidence. Repository HEAD at review: `89a60924`.

> **QUORUM INADMISSIBILITY.** This review is one independent session on ONE
> resolved model (`claude-opus-5`), identical to both producers, the validator
> and the Coordinator. It is **NOT admissible toward an AGENTS.md rule 13
> closure quorum**, no `completion_quorum` block may cite it, and **no
> attestation may be synthesized from it**, now or later.

> **SCOPE.** This report concludes **nothing about Classic McEliece's security
> in either direction**, and nothing in it may be read as such a conclusion —
> including by implication or juxtaposition.

---

## 0. Verdict

**PARTIALLY UPHELD.**

- **All five superseding entries fix their stated defect, introduce no
  substantive error about any source, and drop nothing the originals had
  right.** Checked line by line against the originals at `b30400a9` and against
  the BATCH-001 transcriptions they rest on. The producer's restraint on
  `KN-LIT-e37d4c` (removing an unsupported tag without asserting its negation)
  and on `KN-LIT-71d1a0` (refusing to retract a rate claim the entry never made)
  is better than the handoff that commissioned it. **Say this plainly: the
  corrections are right.**
- **Three defects in the entries themselves are minor and fixable before
  filing** (R-5, R-6, R-7), but entries are immutable once filed, so they must be
  fixed *now*.
- **One objection is material and lands on the batch's stated purpose, not on
  the producers: the tag correction does not do the thing the record says it
  does** (R-1). The grep-level defect survives the repair intact.
- **`BATCH-002-OPENING` §3's harm claim is undemonstrated and overstated**
  (R-2). **§4's "baseline half" framing is wrong** (R-3), and the correct
  position currently exists only inside a producer's task directory.
- **A fresh Coordinator mis-attribution of the same shape as D-2/D-4 is
  identified here** (R-4) — the fifth instance of the family — plus the
  producer-found `BATCH-002-OPENING` §1 error (R-9) which I independently
  confirm.

The corrections should be filed, with R-5/R-6/R-7 repaired first and with the
justification in R-1 struck from the decision.

---

## 1. Duty 3 — adjudicating the grep contradiction. **The producer is right; my predecessor was wrong.**

`TASK-20260803-08e883/red_team_report.md` §6a asserted: *"The word 'Goppa'
appears exactly once in the entry"*, and published as its cheapest control
(line 607): *"`grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md` → **1**"*.

`TASK-20260803-a53f73/superseding_entries.md` §1.2 reports **2** and says the
published control does not reproduce.

**Run at the reviewed snapshot:**

```
$ git show b30400a9:knowledge/literature/KN-LIT-4c8135.md | grep -c -i goppa
2
$ git show b30400a9:knowledge/literature/KN-LIT-4c8135.md | grep -o -i goppa | wc -l
2
$ git show b30400a9:knowledge/literature/KN-LIT-4c8135.md | grep -n -i goppa
25:Alternant codes are the family containing Goppa codes; the result is confined to
31:- The attack is **rate-scoped** — it does not claim to break alternant or Goppa codes at arbitrary rate.
```

**The count is 2. `TASK-20260803-a53f73` is right. `TASK-20260803-08e883` is
wrong.** The working tree reproduces the same 2.

**And the predecessor's error is self-refuting on its own page.** Its lines
576–581 *quote both occurrences* — the containment sentence and the
"rate-scoped … alternant or Goppa codes at arbitrary rate" bullet — in the same
paragraph that asserts "exactly once" and publishes the control result 1. It
printed the disconfirming evidence and did not read its own control. That is a
red team failing the standard it was enforcing, and I record it as such rather
than softening it.

**The error then propagated twice through the Coordinator, uncorrected:**
`DEC-20260803-a5b9b1` D-4 (*"The entry mentions Goppa codes once, in the
opposite direction"*) and `BATCH-002-OPENING` §2 (*"`KN-LIT-4c8135` mentions
Goppa once, in the opposite direction"*). Both are **false as committed**.

**On the second occurrence being the more damaging** — I uphold the substance
and reject the word. The sentence *"it does not claim to break alternant or
Goppa codes at arbitrary rate"* invites the reading that the attack *does* claim
to break Goppa codes at high rate, which `arXiv:2304.14757`'s own sentence
denies (`EV-MCE-332f99` O-5). That is a real and larger defect than the
containment sentence. But `¬(claims to break at arbitrary rate)` does not entail
`claims to break at high rate`; that is a scalar implicature, **not a
contrapositive**. See R-7.

**Consequence for the record:** `DEC-20260803-18d8f3` must carry this
correction explicitly, as `DEC-20260803-a5b9b1` carried its own retractions. A
decision that files the correction while leaving "mentions Goppa once" standing
in D-4 and §2 leaves a wrong number in the durable ledger with a right number in
a task directory.

**Cheapest control (for the filer, cost: one command):**
`git show b30400a9:knowledge/literature/KN-LIT-4c8135.md | grep -c -i goppa` →
must print `2`.

---

## 2. Duty 2 — every supersession assessed: fix / new defect / dropped content

Each new entry was diffed against the original at `b30400a9` and against the
BATCH-001 transcription it cites.

| # | Supersession | Fixes stated defect? | New defect? | Drops anything the original had right? |
|---|---|---|---|---|
| 1 | `KN-LIT-4c8135` → `KN-LIT-c4c2ac` | **Yes** | **Yes, minor** — R-5, R-6 | **No** |
| 2 | `KN-LIT-71d1a0` → `KN-LIT-819780` | **Yes, and re-diagnoses correctly** | **Yes, minor** — R-5 | **No** |
| 3 | `KN-LIT-13a01d` → `KN-LIT-6b5b72` | **Yes** | No | **No** |
| 4 | `KN-LIT-7ee1a9` → `KN-LIT-45b1b2` | **Yes** | **Yes, minor** — R-5 | **No** |
| 5 | `KN-LIT-e37d4c` → `KN-LIT-15c85b` | **Yes** | No | **No** |

### 2.1 `KN-LIT-c4c2ac` — the sharp case. All three conjuncts survive.

The handoff's trap (*"a replacement that leads with the exclusion while deleting
the rate scoping has traded one wrong entry for another"*) is **not** sprung.
The entry's §"The stated restriction is THREE conjuncts, not one" carries:

1. **Code family** — *"generic alternant"*, explicitly not Goppa, quoted from
   the paper's abstract and its own sentence (`EV-MCE-332f99` O-5).
2. **Field size** — `q ∈ {2,3}`, quoted. **This conjunct was absent from
   `KN-LIT-4c8135` entirely** (checked: the original's frontmatter and body
   contain no field condition). The correction adds it. It is a strict gain.
3. **Rate** — condition (6), quoted, **retained**, with the *"whole content of
   its practical reading"* claim retracted and nothing else.

**Dropped-content check.** The original's four content assertions — the
polynomial-time key recovery, the rate scoping, the IEEE TIT venue, and the
"precise rate threshold NOT recorded here" caveat — all survive in the
replacement, the last one strengthened to a **recorded extraction failure**
rather than an unattempted read. The original's teaching claim ("best example in
this sweep of a result genuinely strong and genuinely bounded") is replaced by a
procedure ("enumerate every conjunct … say which are unrecorded"), which is the
same lesson with the boundary corrected. **Nothing right is lost.**

**Fabrication check on the reconstructed fragment.** The entry states *"(6) is a
**lower bound on `n − 1`** … and `e := max{ i ∈ ℕ | r ≥ q^i + 1 } =
⌊log_q(r−1)⌋`"*. I verified this is copied, with its caveat, from
`TASK-20260803-292b99/rate_regime_extraction.md` §3.4 — including that source's
own label *"The qualitative reading is labelled as such and is not a substitute
for the formula."* It is not the producer's own reconstruction of damaged text.
The arithmetic is also correct (`max{i : q^i ≤ r−1} = ⌊log_q(r−1)⌋`). **No
objection.**

### 2.2 `KN-LIT-819780` — the producer contradicted the handoff and was right to

`BATCH-002-OPENING` §2 and this batch's own executor handoff both say
`KN-LIT-71d1a0` is *"wrong-typed"* and that *"any entry stating otherwise is
wrong"*. The producer's §2.1 replies: **no entry states otherwise** — the
original carries no rate figure at all and its "Not verified here" section says
*"the code families and rates for which it succeeds … are NOT recorded here"*.

**I confirm this against the original at `b30400a9`.** The mis-typing lives in
`BATCH-001-OPENING` §4's framing, which `DEC-20260803-a5b9b1` D-2
`also_wrong_typed` correctly attributes to *"the same framing"* — not to the
entry. The entry's defect is a **blank plus a wrong tag**. The correction fills
the blank from primary text and removes the tag. That is the right repair for
the right diagnosis, and refusing to retract a claim the entry never made is
exactly the discipline this batch exists to enforce.

The replacement's three flagged traps (dual vs primal rate; 0.277/0.141 as
Heuristic-1 null-model conditions not applicability bounds; conditions on the
*shortened* code) are each quoted from the paper and each left unadjudicated.
**Correct.**

`citation_verified` is upgraded `web → read` here and on `KN-LIT-c4c2ac`. The
`citation_verified_note` states in both cases that the *drafting* agent worked
from another task's committed transcription, not a fresh extraction. Given
`KN-OPEN-3f7a21`'s 7457 false `read` flags, I looked hard at this and **do not
object**: the flag points at a named task, a URL, a status, a byte count and a
sha256 that a validator re-acquired byte-identically, which is more provenance
than any of the 7457 carries. The note makes the transitivity visible rather
than hiding it.

### 2.3 `KN-LIT-6b5b72`, `KN-LIT-45b1b2`, `KN-LIT-15c85b`

- **`6b5b72`**: tag removed; body carried over verbatim; the one withdrawn item
  is the sentence *"The high-rate scoping repeats the pattern of
  [[KN-LIT-4c8135]] … the bound is the practically decisive part"*, withdrawn
  with a stated reason and with **this** paper's own high-rate scoping
  explicitly preserved. Correct on both halves.
- **`45b1b2`**: tag removed; adds the abstract's rate-regime sentences with the
  *"apparently"* hedge preserved, and adds a section stating the regime is
  announced but **not held**. Softens the original's *"bears **directly** on
  McEliece's structural assumption"* to *"bears on … what it bears is not
  established by this program"* — a scope tightening, not a loss. Correctly
  stays `citation_verified: web`.
- **`15c85b`**: the best-reasoned of the five. The paper is unread, so the
  removal is justified as *"nothing this program holds supports the
  `key-recovery` tag"* and **not** as a claim about the paper, with an explicit
  restoration route if someone reads it. The `unread` tag is added so the state
  is greppable (3 existing corpus entries already use it). This is how a
  correction under uncertainty should be written.

### 2.4 Mechanical checks

| Check | Result |
|---|---|
| All 5 new IDs well-formed 6-hex, free across the union (`python3 tools/allocate_id.py --check`) | **5/5 `OK: well-formed and free`** |
| All 5 specification-entry IDs (`48b4eb`, `7b78de`, `b7f8f8`, `209151`, `9a7860`) | **5/5 `OK`** |
| No `max+1` allocation | confirmed (`--next` rejects `KN-LIT`; `random_token()` used) |
| Wikilinks in new entries resolve (`KN-LIT-2127`, `7965a1`, and the four new IDs) | **all resolve** |
| `superseded_by` write-back specified for all 5 old entries, exact | **yes** (`superseding_entries.md` §4, `tag_defect_corrections.md` §5) |
| Scope firewall (`grep -rn -i "is secure\|is broken\|is threatened\|safe from\|unaffected"` over both packages) | **HELD.** Every hit is a self-prohibition or an attributed source statement. |
| `tools/validate_ledger.py` at review | 20 errors, **zero name an MCE record** — `BATCH-002-OPENING` §8 confirmed |

---

## 3. Objections

### R-1 — MATERIAL. The tag supersession does not make the constraint enforceable by grep. The stated purpose is not achieved.

**Contradicts:** `DEC-20260803-a5b9b1` `next_actions` bullet 2 — *"supersede the
four both-tagged entries … to remove `key-recovery`, **so RQ-MCE-e65b3c's
'distinguisher is not break' constraint is enforceable by grep**"* — and
`BATCH-002-OPENING` §3 — *"the corpus is the program's retrieval substrate, and
a substrate that answers this query wrongly will keep answering it wrongly."*

**Measured.** `tools/build_knowledge_index.py::collect_rows()` walks
`knowledge/**/*.md` and emits **every** entry. It reads `id, title, type,
confidence, citation_verified|status, tags`. It **does not read
`superseded_by`**, does not filter on it, and `INDEX.md` has **no superseded
column**. `knowledge/INDEX.md` is git-tracked (`git ls-files` returns it).

The corpus already contains four supersessions —
`KN-LIT-2414`→`7642`, `KN-LIT-7670`→`7674`, `KN-LIT-475`→`7607`,
`KN-OPEN-027`→`028`. **All four superseded entries appear in `INDEX.md`, with
no marker.** This is not a prediction; it is the observed behaviour of the
existing mechanism.

Because `knowledge/README.md`'s rule is *supersede, never edit*, the four
defective entries **keep their `key-recovery` tag permanently**. Therefore after
filing:

```
$ grep -c "key-recovery" knowledge/INDEX.md          # today
54
$ grep "key-recovery" knowledge/INDEX.md | grep -c -i distinguish   # today
4
```

both are **unchanged after the repair** — the four old rows persist, and four
new distinguisher-only rows are *added*. The quantity that the repair is
supposed to drive to zero stays flat at 4.

**This is the artifact tell of `docs/inventor-protocol.md` §3 applied to a
remediation rather than to a signal**: ask what the reported quantity should
have done. It should have gone 4 → 0. It goes 4 → 4. A repair whose stated
metric does not move is not a repair of that metric.

**What I am *not* saying.** I am not saying the corrections should be rejected.
Their independent justification is sound and does not depend on the grep story
at all: `KN-LIT-13a01d`'s tags contradict its own body and the RQ constraint it
anchors (`tag_defect_corrections.md` §2.3 rests the correction on exactly that
narrower ground, and is right to). What must go is the **claim about the effect**.

**Required of `DEC-20260803-18d8f3`:** either (a) strike "enforceable by grep"
and record the corrections as fixing the *entries*, not the *substrate*; or (b)
record that making the substrate correct additionally requires
`build_knowledge_index.py` to read `superseded_by` and either exclude such rows
or add a column — which is a **tools** change outside every BATCH-002 write
scope and must be dispatched, not assumed.

**Cheapest falsification control (one command, run after filing):**
`grep "key-recovery" knowledge/INDEX.md | grep -c -i distinguish`.
My prediction: **4**. If it returns 0, I am wrong and this objection falls.

---

### R-2 — `BATCH-002-OPENING` §3's harm claim is architecturally plausible, empirically undemonstrated, and overstated. (Duty 4)

**Contradicts:** `BATCH-002-OPENING` §3 — *"the constraint is **defeated** at the
grep level by exactly the entries meant to enforce it, and a future agent
grepping `key-recovery` to find breaks gets four distinguishers back."*

The producer explicitly declined to test it and rested no correction on it
(`tag_defect_corrections.md` §2.3: *"It does not establish that anything consumes
these tags. No consumer was looked for by this task … **This task does not assert
that harm and does not rest any correction on it.**"*). That restraint was
correct. The claim is therefore unowned by any producer and stands only in the
Coordinator's opening.

**Consumer search, run here.**

```
$ grep -rn "key-recovery\|distinguisher" tools/ Makefile .claude/ docs/
(no hit in any tool, skill, agent definition, or doc)
```

**No mechanical consumer of these tags exists in this repository.** The only
support for the harm model is design intent plus a generated artifact:

- `knowledge/README.md` line 5: *"stable immutable IDs, and **greppable tags**.
  Agents retrieve by `grep`/`glob`"* — the substrate is real and documented.
- `knowledge/INDEX.md` carries a `Tags` column across 7946 rows, so
  `grep key-recovery knowledge/INDEX.md` does return those four rows.

**And the harm as stated omits its own strongest counter-fact.** Of the 54 rows
a `key-recovery` grep returns, exactly **4** have "distinguish" in their title,
and all four also carry `distinguisher` **in the same tag list on the same
line**. The false positive is self-labelled at the point of retrieval. An agent
reading the row it grepped sees "A distinguisher for high rate McEliece
cryptosystems … distinguisher" in the returned text.

**Verdict:** the substrate is real, the query is plausible, no consumer has been
demonstrated, and *"defeated"* is too strong for a false positive that announces
itself in the returned line. §3 should read: the tags contradict the entries'
own bodies and the RQ constraint they anchor — which is sufficient, checkable,
and does not require a harm model.

**Cheapest control:** the two commands above. Cost: two commands.

---

### R-3 — `BATCH-002-OPENING` §4's "baseline half" framing is wrong, and the corrected position lives nowhere a reader will find it. (Duty 5)

**Contradicts:** `BATCH-002-OPENING` §4 — *"It is the **baseline half of
BATCH-001-OPENING §1's own justification**"* and *"the goal's second completion
criterion **becomes reachable**"* — and the same phrase in
`DEC-20260803-a5b9b1` D-3 `concrete_cost`.

**The producer already answered this and was right.**
`TASK-20260803-cb44ab/baseline_gap_statement.md` G1: *"'Computed' is not
satisfied by a citation. The criterion says **computed**. Nothing in this package
was computed."*

Measured against `GOAL-MCE-001.completion_criteria` item 2, which requires a
cost **computed** under a **stated** convention with **hidden overhead**,
**memory access** and **time–memory tradeoffs** accounted plus an
**affected-vs-safe scope statement** — the transcription delivers **zero of
six**, and the producer's G1–G12 shows why each one is blocked:

- **G2** — the convention is *named*, not *stated*: SEC's entire memory-charge
  specification is three phrases (*"free access"*, *"cube-root costs"*,
  *"plausible square-root costs"*) with **no formula, unit, or definition**. The
  cost model lives in `eprint 2021/1243`, **which nobody here has read**.
- **G3** — the source states its own overhead accounting is incomplete
  (*"Some cost components are ignored in all estimates"*) and **does not
  enumerate what it ignores**.
- **G4/G5** — one memory figure exists for **1 of 120** cost cells; three fixed
  `mem` points are not a tradeoff and there is no memory column.
- **G8/G9** — no estimator version or commit; the column labels `BC`, `BJMM`,
  `pdw`, `MO`, `BM` **appear nowhere else in the source** and are undefined.
- **G10** — a *second*, differently-accounted designer-published figure set
  (CryptAttackTester, `comparison.html`) exists and is unreconciled.

**The criterion is further away than it looked, not closer**, because the
transcription *discovered* G2, G8, G9 and G10. That is a genuine gain from the
task and the opposite of what §4 predicted.

**And as of the reviewed snapshot, this corrected position exists only in
`coordination/goals/GOAL-MCE-001/batches/BATCH-002/tasks/TASK-20260803-cb44ab/baseline_gap_statement.md`.**
It appears in no ledger record. `goal.yaml` lines 28 and 181 and
`checkpoints/BATCH-001.yaml` lines 57 and 104 still frame this as the baseline
step. A future agent reads `goal.yaml`, not a producer's task directory.

**Cheapest control (for the filer):** after the ledger archive, run
`grep -rn "not satisfied by a citation\|G1" ledger/evidence/EV-MCE-0fbb1a.yaml
ledger/decisions/DEC-20260803-18d8f3.yaml`. If G1's substance is absent, the
correction did not reach a durable record.

---

### R-4 — NEW COORDINATOR ERROR. "Esser–Bellini SEC Table 1" mis-attributes an interested party's table to a third party. Same shape as D-2 and D-4.

**Contradicts:** `BATCH-002-OPENING` §4 (*"Transcribe Esser–Bellini SEC Table
1"*), this batch's `TASK-20260803-cb44ab` handoff objective (*"Transcribe
Esser–Bellini's **published** memory-charged ISD cost table"*),
`DEC-20260803-a5b9b1` lines 72 and 191, `ledger/goals/GOAL-MCE-001/goal.yaml`
lines 28 and 181, and `ledger/goals/GOAL-MCE-001/checkpoints/BATCH-001.yaml`
lines 57 and 104.

**What the source actually is** (`cost_table_transcription.md` §1, §4, from a
hashed retrieval this task made itself):

- SEC = `https://classic.mceliece.org/mceliece-security-20221023.pdf`,
  *"Classic McEliece: conservative code-based cryptography: **guide for security
  reviewers**"* — **written by the Classic McEliece submitters**.
- Its Table 1 caption: *"Output of the Esser–Bellini estimator for the selected
  Classic McEliece parameter sets."*
- Esser–Bellini is the **estimator**, cited as `[33]`, `eprint 2021/1243`,
  **not read by anyone here**.

So the object is **an interested party's publication of a third party's tool
output**, not a third party's published table. The Coordinator's compression
loses exactly the qualifier that carries the provenance.

**This is the same failure the batch exists to correct, one level up.** The
BATCH-001 producer wrote it correctly —
`TASK-20260803-f3aece/parameter_sets.md:184`: *"SEC's Table 1 (Esser–Bellini
estimator output, three memory models per set)"* — and the Coordinator dropped
the parenthesis in six committed records and two BATCH-002 handoffs. Producer
right, Coordinator compresses, compression propagates: the D-2/D-4 pattern
exactly.

**Why it matters, on this program's own standard.** `EV-MCE-332f99` O-7 already
rules that *"a single source that is a party to the claim is not an independent
confirmation"* — applied there to the ISO claim from the designers' own site.
The same rule binds here: a memory-charged baseline for GOAL-MCE-001 drawn from
the designers' own security guide inherits that limit, and the phrase
"Esser–Bellini's published table" hides it. `cb44ab` recorded the attribution
correctly throughout and is not at fault.

**Cheapest control (one command):**
`grep -rn "Esser" ledger/ coordination/goals/GOAL-MCE-001/` — every Coordinator
record reads *"Esser-Bellini SEC Table 1"*; every producer record reads *"SEC's
Table 1 (Esser–Bellini estimator output)"*. Fix: the phrase in
`EV-MCE-0fbb1a`/`DEC-20260803-18d8f3` must be *"SEC Table 1, the Classic
McEliece submitters' guide for security reviewers, reporting Esser–Bellini
estimator output"*, with the interested-party limit stated.

---

### R-5 — NEW DEFECT IN THE CORRECTION. Three dangling internal references to `identifiers`, in entries that become immutable on filing.

**Contradicts:** `superseding_entries.md` §5, which correctly moves `sha256` out
of `identifiers:` into a new top-level `source_artifact:` block, with a measured
reason (`build_source_index.py::canonical_identifier()` would emit
`sha256:…` as a bibliographic identifier in the regenerated `SOURCES.md`). The
reason is right and I verified the mechanism. **But three body sentences were
not updated to match**, and each now points at a key that does not exist:

| File:line | Proposed entry | Text |
|---|---|---|
| `superseding_entries.md:223–224` | `KN-LIT-c4c2ac` | *"A reviewer wanting condition (6) must read the rendered PDF at the sha256 in `identifiers`."* |
| `superseding_entries.md:537` | `KN-LIT-819780` | *"every claim recorded here is scoped to the sha256 in `identifiers`."* |
| `tag_defect_corrections.md:399–400` | `KN-LIT-45b1b2` | *"Only the ePrint abstract was obtained, at the sha256 in `identifiers`."* |

In all three the `identifiers:` block contains no `sha256`; it is in
`source_artifact:`. The third is the worst: it is the **version-scoping anchor**
for a `read` flag, pointing at nothing.

`knowledge/README.md` makes entries immutable; a filed entry with a dangling
pointer can only be fixed by another supersession. **Fix before filing.**

**Cheapest control:** `grep -n -B1 "in \`identifiers\`" ` over both files → 3
hits; then confirm each proposed frontmatter has no `sha256:` under
`identifiers:`. Cost: two commands.

---

### R-6 — NEW DEFECT, and a fork the batch cannot escape: `KN-LIT-c4c2ac`'s tag line contains `goppa` twice, on the one paper that excludes Goppa codes.

**Contradicts:** `BATCH-002-OPENING` §3's own harm model, applied to
`superseding_entries.md` §1.4, whose proposed tags include **both**
`not-goppa` **and** `goppa-excluded`.

Two problems:

1. **Redundant synonyms.** Two tags for one fact, in a corpus whose retrieval is
   substring `grep` over a flat tag string. Nothing else in the corpus uses
   either.
2. **The fork.** A `grep -i goppa` over `INDEX.md`'s tag column matches both
   `not-goppa` and `goppa-excluded`. So an agent grepping `goppa` retrieves, in
   this cluster, the one entry whose paper *"does not work at all"* on Goppa
   codes — with `goppa` appearing **twice** in its tag line. **Either
   `BATCH-002-OPENING` §3's harm model is real, and this is a fresh instance of
   it created by the correction; or it is not real, and §3's justification is
   weaker than stated (R-2).** The package cannot have it both ways, and its own
   `tag_defect_corrections.md` §2.3 declines to assert the harm.

**Cheapest control:** on the proposed frontmatter tag line for `KN-LIT-c4c2ac`,
`grep -o -i goppa | wc -l` → **2**. Fix: one tag, and a positive vocabulary
rather than a negation, since negation tags are invisible to substring search
and actively harmful under it.

---

### R-7 — MINOR. "Contrapositive" is the wrong word, in a package about precision, and this handoff repeats it.

**Contradicts:** `superseding_entries.md` §1.2 and §"Why this entry supersedes
KN-LIT-4c8135" — *"Its natural contrapositive — the attack claims to break Goppa
codes at high rate — is precisely what the paper's own sentence denies"* —
reproduced verbatim in this task's own handoff.

`¬(claims to break at arbitrary rate)` does not entail `claims to break at high
rate`. The inference is a scalar implicature — the pragmatic reading a reader
takes from a scoped denial — not a contrapositive, which would be
`¬(breaks at high rate) → ¬(...)` and is not what is meant.

**The substantive point is upheld** (§1 above): the sentence does invite the
denied reading, and it is the more damaging of the two occurrences. Only the
label is wrong. In a correction batch whose subject is stating restrictions
precisely, using a logical term loosely is a defect worth one word of repair.

**Cheapest control:** read the sentence as a stated entailment. No command
needed. Fix: *"the reading it invites"*.

---

### R-8 — RECORDED, NOT AN OBJECTION. T4 gap between the concurrent producers, correctly pre-forgiven.

`transcription_convention.md` T4 requires *"extractor name, version, and
non-default settings"*. `TASK-20260803-cb44ab` records extractor and version
(`pypdf 6.14.2`, `pdfminer.six 20260107 high_level.extract_text`) but **not
`laparams` or non-default settings**, which is precisely validator finding Q4.
`transcription_convention.md` §2.4 anticipates this and rules it *"a gap against
a convention it could not see, not a producer defect"*. **I agree, and record it
so the filer notes it rather than a later reader discovering it.**

Also correct: §2.3's refusal to apply the new convention retroactively to
BATCH-001. Re-scoring completed work against a later rule is a failure mode, and
declining it is right.

---

### R-9 — CONFIRMED (producer-found). `BATCH-002-OPENING` §1's defect table is wrong about D-3.

**Contradicts:** `BATCH-002-OPENING` §1 table — *"D-3 — **already corrected** in
the BATCH-001 ledger archive"*.

`TASK-20260803-a53f73/rq_constraint_correction.md` §6.1 found this false.
**Independently verified at `b30400a9`:**

```
$ git show b30400a9:ledger/questions/RQ-MCE-e65b3c.yaml | grep -n -i "bind\|costing convention"
43:        under the same costing convention GOAL-HQC-001 and GOAL-SDITH-001 bind
136:      and verification charged. Bind to the costing convention produced under
```

`goal.yaml` **is** corrected (lines 42–44 carry the retraction). `RQ-MCE-e65b3c`
is **not**: it still instructs binding in both `scope.targets` and
`constraints`, an act `DEC-20260802-344883` D-6 and `DEC-20260803-a5b9b1` D-3
say cannot be performed. This is live *this batch*:
`TASK-20260803-cb44ab` transcribed under a convention explicitly not adopted
while the RQ told it to bind to one (`baseline_gap_statement.md` G7 records the
contradiction without resolving it — correct handling).

`TASK-20260803-3aa684`'s amended `named_duties` now instructs the double
correction, so the queue is repaired. **The opening's §1 table remains wrong in
a snapshot-committed artifact**, and `DEC-20260803-18d8f3` must retract that row
explicitly rather than silently superseding it.

**Cheapest control:** the two-line grep above. Cost: one command.

---

## 4. Duty 6 — is this a healthy pipeline, or a Coordinator outsourcing its checking?

**Both, and the honest answer is that it is currently the second wearing the
clothes of the first.**

Five Coordinator claims about prior records were found wrong in this batch. Not
one was found by the Coordinator:

| # | Wrong claim | Found by | Job that agent was given |
|---|---|---|---|
| 1 | "mentions Goppa **once**" (`DEC-20260803-a5b9b1` D-4, `BATCH-002-OPENING` §2) | `TASK-20260803-a53f73` | draft corrections |
| 2 | "`KN-LIT-71d1a0` is wrong-typed … any entry stating otherwise is wrong" (`BATCH-002-OPENING` §2) | `TASK-20260803-a53f73` | draft corrections |
| 3 | "D-3 — already corrected" (`BATCH-002-OPENING` §1) | `TASK-20260803-a53f73` | draft corrections |
| 4 | ledger-archive `write_scope` cannot reach the note's target | `TASK-20260803-a53f73` | draft corrections |
| 5 | "Esser–Bellini SEC Table 1" mis-attribution (6 records + 2 handoffs) | **this review (R-4)** | attack the corrections |

**What is healthy.** The producers did flag them, in their own deliverables,
against their own instructions, with citations — which is what AGENTS.md rule 8
asks and what most pipelines do not get. Item 4 produced a same-day scope
amendment recorded in `dispatch_queue.json` with the reason and the flag's
origin (*"Flagged by the producer, not by the Coordinator"*). Nothing was
suppressed. That is a real property and it should be said.

**What is not healthy, and the number that shows it.** Errors 1, 2 and 3 were
each cheap to check — one `grep`, one file read, one `grep` — and each was
checked *by an agent commissioned to write corrections, not to audit the
commission*. Error 1 in particular was published as a *cheapest control with its
result attached* by the BATCH-001 red team, which then quoted the disconfirming
evidence in the same paragraph; the Coordinator copied the number into a ledger
decision and again into a batch opening **without ever running the one-command
control that was printed next to it**. A control that is written down and not
run is not a control.

**The structural diagnosis.** BATCH-002's design places every check *downstream*
of the Coordinator's claims: producers draft, then two reviews. There is no step
at which the opening's own factual assertions are checked *before* they are
issued as instructions — and instructions carry more force than notes, because a
producer told *"any entry stating otherwise is wrong"* must spend budget
disproving it. The producer here did, and spent a section of a deliverable on
it. That cost is real and is charged to the Coordinator.

**So: not a fatigue report about the producers, and not exoneration.** The
pipeline catches these errors reliably. It catches them one stage too late, in
artifacts written by agents paid to do something else, and it has now done so
four batches running. `DEC-20260803-a5b9b1` D-3 `severity` already says naming
the precedent does not prevent it. **Naming it a fifth time will not prevent it
either.** The only thing that changes this class of error is a mechanical
pre-issue check.

**Concrete, cheap, and within an existing tool's reach:** before a batch opening
is committed, run every `grep`-shaped factual claim it makes and paste the
output into the opening. Every one of errors 1, 2, 3 and 5 would have been
caught by that, at a total cost of four commands.

---

## 5. What is right, stated plainly

Required by this task's constraints, and earned:

1. **The five superseding entries are correct.** Every conjunct of
   `arXiv:2304.14757`'s restriction survives, including the field condition the
   original never had. No original content that was right is lost.
2. **The `KN-LIT-e37d4c` reasoning is the best thing in the package**: removing
   an unsupported tag without asserting its negation, on an unread paper, with a
   named restoration route.
3. **The `KN-LIT-71d1a0` re-diagnosis is right and contradicts the handoff that
   commissioned it.** The producer refused to retract a claim the entry never
   made. That is the correct response to a wrong instruction.
4. **The tag prevalence was genuinely re-measured**, reproduced the red team's
   4/4 on the stated population, and **extended** it corpus-wide to find that
   the defect does not spread (4 both-tagged corpus-wide) and that 3 correctly
   tagged distinguisher-only entries already existed — narrowing the diagnosis
   rather than inflating it.
5. **`tag_defect_corrections.md` §2.3 declines the §3 harm claim on the record**
   and rests the correction on checkable ground instead. Producers refusing to
   inherit a Coordinator's unproven claim is the behaviour this program needs.
6. **The dedup determination was genuinely re-run** — 14 probes plus a hash
   probe the BATCH-001 task did not run — with each near-miss examined
   individually and the scope limit stated (*"the check is still a grep, not a
   proof"*).
7. **The cost-table transcription is exemplary.** Three independent extraction
   paths (including a geometry-only reconstruction that checks column
   assignment), 150/150 cell agreement, a measured justification for zero
   `[EXTRACTION-DAMAGED]` markers inside the table (one font size, 771 glyphs),
   0 `[RECALLED-NOT-READ]`, 0 arithmetic, and O-5's explicit refusal to resolve
   an ambiguous cross-reference it could easily have resolved by inference.
8. **`baseline_gap_statement.md` corrects its own Coordinator's framing in G1**
   and names twelve gaps without filling any.
9. **The scope firewall held in both packages.** No security predicate about
   Classic McEliece appears unattributed, including by juxtaposition.
10. **The transcription convention (D-10) is settled correctly**, choosing
    292b99's standard on a stated worst-case argument, adding T4 that neither
    producer met, and explicitly declining to apply it retroactively.

---

## 6. Scope limits on this report

- I re-ran the grep controls, the ID checks, the index-generator inspection, the
  wikilink resolution and `validate_ledger.py` myself. **I did not re-acquire any
  external source** — that is `TASK-20260803-8cf2b6`'s duty and my findings do
  not depend on it. If the validator finds a re-acquisition mismatch, my
  assessment of entry *content* stands but my assessment of *provenance* does
  not.
- R-1's prediction is about `INDEX.md` as generated by the current
  `build_knowledge_index.py`. If the filer changes that tool, R-1's control must
  be re-run.
- My objections are to **records and framings**, never to a mathematical claim
  about any code family, any parameter set, or any attack. **This report
  concludes nothing about Classic McEliece's security.**
- Everything here is scoped to snapshot `b30400a9` and to the corpus at HEAD
  `89a60924`. Another worktree may hold entries this one does not.

---

## 7. One next concrete action

**Before `TASK-20260803-3aa684` files anything: fix R-5, R-6 and R-7 in the
proposed entry text, then run the R-1 control and record its result in
`DEC-20260803-18d8f3`.**

Concretely, in order, total cost roughly six commands and three one-line edits:

1. Repair the three dangling `identifiers` references (R-5) and collapse
   `not-goppa`/`goppa-excluded` to a single positive tag (R-6); replace
   "contrapositive" (R-7).
2. Run `grep "key-recovery" knowledge/INDEX.md | grep -c -i distinguish` before
   and after filing. Record both numbers in `EV-MCE-0fbb1a`.
3. If the number does not fall to 0, **strike "enforceable by grep" from the
   decision's justification** and open a separate dispatch item for
   `build_knowledge_index.py` to read `superseded_by`. Do not let the batch
   close claiming an effect it did not produce.
4. Carry R-4 and R-9 as explicit retractions in `DEC-20260803-18d8f3`, the way
   `DEC-20260803-a5b9b1` carried its own — not as silent supersessions.

---

**Verdict: PARTIALLY UPHELD.** File the corrections; repair R-5/R-6/R-7 first;
strike the R-1 justification; retract R-4 and R-9 on the record.

**Not admissible toward an AGENTS.md rule 13 quorum. No attestation may be
synthesized from this report.**

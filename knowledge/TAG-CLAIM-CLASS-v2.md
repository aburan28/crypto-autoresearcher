# Claim-class tags v2 — the machine-enforceable form of "distinguisher is not break"

**Established by:** `TASK-20260809-3e30b8` (GOAL-MCE-001, BATCH-73a1b7), role
executor, 2026-08-09.
**Authority:** `RQ-MCE-e65b3c.constraints`, which reads:

> Distinguisher is not break. KN-LIT-13a01d distinguishes and does not
> recover keys; docs/claims-and-verification.md forbids promoting one to
> the other. Any deliverable naming a distinguisher states which it is.

The same authority that established `knowledge/TAG-CLAIM-CLASS.md`. This file
does not change the authority or the vocabulary it enforces — only the
enforcement mechanism.

**What this file is.** A controlled vocabulary and an audit command, exactly
as `TAG-CLAIM-CLASS.md` describes itself: it is not a knowledge entry, it
carries no YAML frontmatter, it is skipped by `tools/build_knowledge_index.py`
(which requires a leading `---`), and it is outside the four directories
`tools/validate_ledger.py` checks. It asserts nothing about any cryptosystem.

**What this file supersedes, and what it does not.** This file supersedes
**sections 2 and 3 only** of `knowledge/TAG-CLAIM-CLASS.md` — "AUDIT-1 — the
enforcement command" and "AUDIT-2 — the form guard that keeps AUDIT-1
complete." `knowledge/TAG-CLAIM-CLASS.md` is **not edited**: it remains
byte-for-byte identical to its committed version (verified by this task via
`git diff --exit-code -- knowledge/TAG-CLAIM-CLASS.md`, which reported no
difference) and stays archived as the immutable record of what AUDIT-1 and
AUDIT-2 were and why they were believed sufficient at the time. Section 1 (the
vocabulary, `R-CC-1` through `R-CC-6`) is **carried forward unchanged** and is
restated in full below, self-contained, so this file does not require the
reader to hold both documents open at once. Section 4 ("What the audit does
NOT do") is restated and updated for the new mechanism, including new
limitations the old section did not have and did not need.

**Why this file exists.** `TAG-CLAIM-CLASS.md` section 2 opened by describing
AUDIT-1 and AUDIT-2 as replacing "the hope" of human review "with a command."
That was true of what the two regexes covered, and false of what they
claimed: `TAG-CLAIM-CLASS.md`'s own closing section, "What the audit does NOT
do," lists four disclosed limitations (form-not-correctness, silence-means-
nothing, tags-not-prose, scoped-to-`knowledge/`) and does not mention a fifth,
undisclosed one — that AUDIT-1 and AUDIT-2 together enforce exactly **one YAML
serialisation** of a `tags` list, not the semantic constraint the vocabulary
states. `VAL-20260808-71bdb1` control_check `C-4` (the validator's own negative
control, run against a scratch corpus, method and results verbatim in
`coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/reviews/TASK-20260808-ea7bed/validation_report.yaml`
lines 600-698) constructed five legal, differently-serialised YAML documents
that PyYAML parses to the identical semantic value `{'tags': ['distinguisher',
'key-recovery']}` (four of the five; the fifth nests `tags` under a mapping
key and is discussed below) and showed both regex audits missed four of the
five. `ledger/evidence/EV-MCE-3d6e9a.yaml` observation `O-5b` records the
consequence directly and its own next sentence states what is and is not
supportable: *"NOT 'the distinguisher/break constraint is machine-enforceable'.
Only this: '...verified by two audit commands run independently... The audits
enforce ONE TAG ENCODING, not the semantic constraint; five legal YAML
encodings with identical semantics evade both.'"* `O-5b`'s own
`cheap_fix_identified` field named the fix this file and its accompanying
script perform: parse the frontmatter and test the tag **list**, not the tag
**line**. That is what `tools/claim_class_audit.py` does, and what this file
documents.

**Corrections supersede.** This file is immutable once archived, exactly as
`TAG-CLAIM-CLASS.md` itself states of its own convention (which it in turn
takes from `transcription_convention.md`, `TASK-20260808-a9f648` §7.2). A
future change to the vocabulary or to the command is a new file under a new
task id that cites this one; it is not an edit of this file or of
`TAG-CLAIM-CLASS.md`.

---

## 1. The vocabulary (carried forward unchanged from TAG-CLAIM-CLASS.md section 1)

Four states, of which at most one token may appear in an entry's `tags`.

| Token | The entry's SUBJECT claims | Never means |
|---|---|---|
| `distinguisher` | it can tell the structured object from a random one, and claims **no** key or message recovery | that a break follows |
| `key-recovery` | recovery of a key, or an equivalent total break | that a distinguisher exists or is implied |
| `distinguish-then-recover` | **both**: a distinguisher *and* an escalation of it to recovery | a licence to state the headline without saying which result is which |
| *(no claim-class token)* | not an attack-claim source, or the class has not been determined | that the class was determined and found empty |

**RULE R-CC-1 (mutual exclusion).** `distinguisher` and `key-recovery` are
mutually exclusive within one entry's `tags`. An entry carrying both is a
defect.

**RULE R-CC-2 (the both case has its own token, and it is grep-safe).** A
source that claims both gets `distinguish-then-recover` and **not** the other
two. That token deliberately contains neither `distinguisher` nor
`key-recovery` as a substring, so even a careless `grep -c distinguisher`
cannot mis-fire on it. An entry carrying it MUST have a `## Claim class` body
section naming which result is the distinguisher and which is the recovery,
and under what conditions the escalation holds.

**RULE R-CC-3 (silence is permitted and means nothing).** Most of the corpus
carries no claim-class token. That is legal. The audit checks that no entry
carries a *contradictory pair*; it does **not** check that any entry is
classified, and its silence must never be read as "the corpus is fully
classified."

**RULE R-CC-4 (compound tags are not claim-class tokens).** A tag that merely
*contains* one of these strings is a different tag and is unaffected. The
corpus already holds three such tags and they are all legitimate:
`structural-distinguisher` (`KN-TECH-063`), `hybrid-distinguisher`
(`KN-TECH-065`), `distinguisher-duality` (`KN-TECH-069`). The old regex audits
matched exact list tokens for this reason: a substring grep returns those
three as false positives, and an audit with known false positives is one
nobody runs. The new audit (section 2 below) satisfies this rule
structurally rather than syntactically: it compares the token `distinguisher`
against `set` membership of the *parsed* tags list, so a distinct string like
`structural-distinguisher` is simply a different set element and can never
match, with no regex boundary logic required at all.

**RULE R-CC-5 (form: flow-style tags).** Every new or superseding entry writes
`tags` as a YAML **flow** list on one physical line, `tags: [a, b, c]`, with
one space after each comma. This was what made R-CC-1 auditable by the old
line-oriented tool; the new audit does not depend on this rule for
correctness (it tests the parsed list under any legal serialisation), but the
rule is unchanged and still binds new and superseding entries, since it
remains good practice for human readability and for other line-oriented
tooling in this repository. 56 legacy `knowledge/literature/` entries and 23
legacy `knowledge/findings/` entries use block style; none of them lists
either claim-class token as of the corpus state this file's accompanying
script was run against (section 2).

**RULE R-CC-6 (correction is by supersession).** A wrongly-classified entry is
never re-tagged in place. A new entry is written, it names the old one in a
front-matter `supersedes:` field, and it says why. `TAG-CLAIM-CLASS.md`'s
AUDIT-1 treated an entry as retired when **either** some entry names it in
`supersedes:` **or** it carries a non-null `superseded_by:`. The new audit
(section 2 below) does **not** replicate that supersession-awareness — see
section 4, "What this audit does NOT do," for exactly what that means and
why it was left out deliberately rather than by oversight.

**`supersedes:` exists in two forms in this corpus.** Nine entries already use
a bare scalar — `supersedes: KN-TECH-9d21c4` (`KN-TECH-6c0e15`,
`KN-TECH-1a5b7e`, `KN-TECH-058`, `KN-OPEN-028`, `KN-LIT-7642`, `KN-LIT-7607`,
`KN-LIT-7640`, `KN-LIT-7674`, `KN-LIT-c41d8b`) — while entries filed by
`TASK-20260808-f9374d` use a flow list, `supersedes: [KN-LIT-13a01d]`, which is
a superset and admits multi-supersession. Neither form is deprecated here.
This detail is restated for completeness of the vocabulary; it is no longer
operative in the new audit's own logic, precisely because that audit does not
implement a supersession-drop stage at all (section 4).

---

## 2. THE AUDIT — one script, supersedes AUDIT-1 and AUDIT-2

`tools/claim_class_audit.py` replaces both regex-based commands with a single
YAML-frontmatter-parsing script. Run from the repository root:

```sh
python3 tools/claim_class_audit.py [root] [--report-skipped]
```

`root` defaults to `knowledge/` at the repository root and may be given
explicitly, including for a directory outside `knowledge/` (used here to run
the script against `tools/fixtures/claim_class_evasions/`, its own regression
fixture — see section 3). **It prints nothing on `stdout` when the scanned
tree is clean. Every line it prints on `stdout` is the path of a file whose
frontmatter's top-level `tags` carries both `distinguisher` and
`key-recovery`.** As with the audits it supersedes: exit status is not the
signal, `stdout` output is.

**What it does, precisely.** For every `*.md` file under `root`: if the file
begins with a `---`-delimited frontmatter block, `yaml.safe_load` that block;
if `{'distinguisher', 'key-recovery'}` is a subset of `set(frontmatter.get(
'tags') or [])` (accepting `tags` as a YAML list, tuple, or `!!set` node — see
`tag_set()`'s docstring in the script and GATE-A case G11 in the execution
report), print the file's path. Files with no frontmatter at all are silently
out of scope (this is the common case: most `*.md` files under `knowledge/`
are not frontmatter'd corpus entries — `README.md`, `INDEX.md`, this file, the
`gathers/` notes). Files that open a frontmatter block but cannot be read as
one — no closing `---`, invalid YAML, a block that parses to something other
than a mapping — are reported by path and reason (to `stderr`, with
`--report-skipped`) and skipped; **one malformed file never stops the scan**.

**Why this form is immune to the five evasions, structurally rather than by
patching each one.** AUDIT-1 and AUDIT-2 matched the `tags:` **line** with
regular expressions. Every one of the five evasions in
`VAL-20260808-71bdb1` `C-4` is a case where the source **line** does not look
like the pattern the regex expects, while the parsed **value** is identical to
what the regex was trying to catch. `tools/claim_class_audit.py` never reads a
line; it hands the whole frontmatter block to a real YAML parser and tests the
resulting Python value. There is consequently no line-continuation case, no
quoting case, and no trailing-comment case to enumerate, because none of those
distinctions survive parsing. This is a structural property of testing the
parsed list rather than a five-item checklist.

## 3. The regression fixture

`tools/fixtures/claim_class_evasions/` holds five files, reconstructed
verbatim from `VAL-20260808-71bdb1` `control_checks` `C-4` (lines 614-657 of
the cited validation report — the original scratch files lived outside the
repository and are not recoverable; this committed specification is the
authoritative source):

| File | Form | Caught by the new audit? |
|---|---|---|
| `b1_nested_flow.md` | `tags` nested one level under a `meta:` mapping key, flow style | **No — correctly.** See below. |
| `b2_multiline_flow.md` | legal multi-line YAML flow sequence (`tags: [distinguisher,` / newline / `  key-recovery]`) | Yes |
| `b3_quoted_flow.md` | `tags: ["distinguisher", "key-recovery"]` | Yes |
| `b4_block_trailing_comment.md` | block sequence, trailing `# claim class` comment on every item | Yes |
| `b5_block_quoted.md` | block sequence, quoted items | Yes |

They live under `tools/fixtures/`, **not** under `knowledge/`: putting them in
`knowledge/` would (a) be scanned by `tools/build_knowledge_index.py` as if
they were real corpus entries, corrupting the generated index, and (b) would
itself constitute a genuine `R-CC-1` violation of the *real* corpus if it were
ever scanned as a live entry — the fixtures exist specifically to carry the
banned pair.

**B1 is not caught, and that is correct, not a gap.** B1's frontmatter parses
to `{'meta': {'tags': ['distinguisher', 'key-recovery']}}` — there is no
top-level `tags` key; it exists only nested inside `meta:`.
`frontmatter.get('tags')` is `None`, and `{'distinguisher', 'key-recovery'}`
cannot be a subset of the empty set. The validation report's own note on B1
calls it "weakest of the five... the index builder wants a top-level `tags`,
so this entry would likely be rejected elsewhere. Listed for completeness, not
relied on." The new audit's contract, stated in section 2 above, is a
top-level `tags` list; B1 does not have one, by construction, so this is the
vocabulary's `R-CC-1` contract behaving exactly as specified, not blindness to
an evasion.

`tools/test_claim_class_audit.py` runs the new audit against this fixture
directory and asserts B2, B3, B4 and B5 are printed (caught) and B1 is not,
with the reasoning above pinned in the test's own docstrings so a future
reader does not mistake the B1 assertion for an unexamined gap.

## 4. What this audit does NOT do (supersedes TAG-CLAIM-CLASS.md section 4)

Stated because a clean run invites more weight than it can carry — the same
opening `TAG-CLAIM-CLASS.md` section 4 used, restated and extended for the
new mechanism's own, different limitations.

- **It enforces form, not correctness**, unchanged from before. It cannot
  tell whether an entry's claim class is the *right* one. Tagging a
  key-recovery paper `distinguisher` passes this audit and is still wrong.
- **It says nothing about entries with no claim-class token** (`R-CC-3`),
  unchanged from before.
- **It checks tags, not prose.** An entry may still describe a distinguisher
  as a break in its body. That is what `docs/claims-and-verification.md` and
  human review are for. Unchanged from before.
- **It is scoped to its `root` argument**, which **defaults** to `knowledge/`
  but, unlike the old shell pipeline, is a real parameter: pointing it
  elsewhere (as this file's own section 3 does, at
  `tools/fixtures/claim_class_evasions/`) scans that directory instead.
  Ledger records, experiment artifacts and task reports are still not covered
  **by default**, and nothing about this program's other tooling passes a
  different root to this script.
- **It does NOT replicate AUDIT-1's supersession-drop stage, and this is a
  deliberate scope decision, not an omission discovered later.** AUDIT-1's
  final pipeline stage dropped any file already retired — named in some other
  entry's `supersedes:` field, or itself carrying `superseded_by:` — before
  printing. `tools/claim_class_audit.py` does not: it reports the literal
  frontmatter tag state of every live file. **Consequence, verified by this
  task and stated plainly:** running `python3 tools/claim_class_audit.py`
  with no arguments against the real corpus, as it stood when this task ran
  (2026-08-09), prints four lines —
  `knowledge/literature/KN-LIT-13a01d.md`, `KN-LIT-71d1a0.md`,
  `KN-LIT-7ee1a9.md`, `KN-LIT-e37d4c.md` — **not** silence. These are exactly
  the four entries `VAL-20260808-71bdb1` control_check `C-3` named as the
  real hits AUDIT-1's supersession filter correctly retired
  (`EV-MCE-3d6e9a.yaml` observation `O-5a`); they are not a newly discovered
  defect, and this run found zero files reported as unparseable
  (`--report-skipped` produced no output against `knowledge/`). A reader of
  this script's output must cross-check any printed path's `supersedes:` /
  `superseded_by:` status by hand, or against `BATCH-73a1b7` scope item
  `SUB-2` once the corpus-wide `superseded_by` convention it is chartered to
  settle exists, before treating a hit as a live `R-CC-1` violation.
- **A `tags` value that is a YAML mapping (not a list, tuple, or `!!set`) is
  a disclosed non-catch, found and left unfixed on purpose during this task's
  GATE-A break-attempt.** `tags: {distinguisher: true, key-recovery: true}`
  is not treated as carrying either token: it is a different frontmatter
  shape than `R-CC-5`'s documented list convention and than every real entry
  in this corpus, and deciding whether a *key's presence* or its *boolean
  value* constitutes "carrying" a tag is an ambiguous reading this script
  does not invent an answer for. If this shape is ever found in a real entry
  it needs a human read. See `tag_set()`'s docstring in
  `tools/claim_class_audit.py` and GATE-A case G12 in the execution report.
- **A `tags` value given via an explicit unsafe YAML type tag (e.g.
  `!!python/tuple`) is refused by the parser, not silently accepted or
  crashed on.** `yaml.safe_load` (never `yaml.load` or `full_load`) raises
  `yaml.YAMLError` for such a node, which this script catches and reports as
  an unparseable file rather than executing or constructing an arbitrary
  Python object. See GATE-A case G13.
- **It is scoped to `*.md` files**, matching both predecessor audits and the
  corpus convention; a claim-class tag inside a non-`.md` file (there are
  none in `knowledge/` as of this task) would not be seen.

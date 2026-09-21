# Claim-class tags — the machine-enforceable form of "distinguisher is not break"

**Established by:** `TASK-20260808-f9374d` (GOAL-MCE-001, BATCH-a68f79), role
coordinator, 2026-08-08.
**Authority:** `RQ-MCE-e65b3c.constraints`, which reads:

> Distinguisher is not break. KN-LIT-13a01d distinguishes and does not
> recover keys; docs/claims-and-verification.md forbids promoting one to
> the other. Any deliverable naming a distinguisher states which it is.

**What this file is.** A controlled vocabulary and an audit command. It is not a
knowledge entry: it carries no YAML frontmatter, it is skipped by
`tools/build_knowledge_index.py` (which requires a leading `---`), and it is
outside the four directories `tools/validate_ledger.py` checks. It asserts
nothing about any cryptosystem.

**Why it exists.** The constraint above was already binding and was already
violated: four corpus entries carried the tags `distinguisher` **and**
`key-recovery` at the same time, so the only way to audit the constraint was for
a human to read every entry. A constraint whose audit is human reading is not
enforced; it is hoped for. This file replaces the hope with a command.

**Corrections supersede.** This file is immutable once archived. A change to the
vocabulary or to the command is a new file under a new task id that cites this
one, exactly as `transcription_convention.md` (`TASK-20260808-a9f648` §7.2)
requires of itself.

---

## 1. The vocabulary

Four states, of which at most one token may appear in an entry's `tags`.

| Token | The entry's SUBJECT claims | Never means |
|---|---|---|
| `distinguisher` | it can tell the structured object from a random one, and claims **no** key or message recovery | that a break follows |
| `key-recovery` | recovery of a key, or an equivalent total break | that a distinguisher exists or is implied |
| `distinguish-then-recover` | **both**: a distinguisher *and* an escalation of it to recovery | a licence to state the headline without saying which result is which |
| *(no claim-class token)* | not an attack-claim source, or the class has not been determined | that the class was determined and found empty |

**RULE R-CC-1 (mutual exclusion).** `distinguisher` and `key-recovery` are
mutually exclusive within one entry's `tags`. An entry carrying both is a defect.

**RULE R-CC-2 (the both case has its own token, and it is grep-safe).** A source
that claims both gets `distinguish-then-recover` and **not** the other two. That
token deliberately contains neither `distinguisher` nor `key-recovery` as a
substring, so even a careless `grep -c distinguisher` cannot mis-fire on it. An
entry carrying it MUST have a `## Claim class` body section naming which result
is the distinguisher and which is the recovery, and under what conditions the
escalation holds.

**RULE R-CC-3 (silence is permitted and means nothing).** Most of the corpus
carries no claim-class token. That is legal. The audit below checks that no
entry carries a *contradictory pair*; it does **not** check that any entry is
classified, and its silence must never be read as "the corpus is fully
classified."

**RULE R-CC-4 (compound tags are not claim-class tokens).** A tag that merely
*contains* one of these strings is a different tag and is unaffected. The corpus
already holds three such tags and they are all legitimate:
`structural-distinguisher` (`KN-TECH-063`), `hybrid-distinguisher`
(`KN-TECH-065`), `distinguisher-duality` (`KN-TECH-069`). This is why the audit
matches **exact list tokens** and not substrings: a substring grep returns those
three as false positives, and an audit with known false positives is one nobody
runs.

**RULE R-CC-5 (form: flow-style tags).** Every new or superseding entry writes
`tags` as a YAML **flow** list on one physical line, `tags: [a, b, c]`, with one
space after each comma. This is what makes R-CC-1 auditable by a line-oriented
tool. 56 legacy `knowledge/literature/` entries and 23 legacy
`knowledge/findings/` entries use block style; none of them lists either
claim-class token, and AUDIT-2 below is what keeps that true.

**RULE R-CC-6 (correction is by supersession).** A wrongly-classified entry is
never re-tagged in place. A new entry is written, it names the old one in a
front-matter `supersedes:` field, and it says why. The audit treats an entry as
retired when **either** some entry names it in `supersedes:` **or** it carries a
non-null `superseded_by:` — both, so the audit stays correct whether or not a
later `/curate-knowledge` pass fills `superseded_by` on the old entry as
`knowledge/README.md` asks.

**`supersedes:` exists in two forms in this corpus and the audit must read
both.** Nine entries already use a bare scalar — `supersedes: KN-TECH-9d21c4`
(`KN-TECH-6c0e15`, `KN-TECH-1a5b7e`, `KN-TECH-058`, `KN-OPEN-028`,
`KN-LIT-7642`, `KN-LIT-7607`, `KN-LIT-7640`, `KN-LIT-7674`, `KN-LIT-c41d8b`) —
while the entries filed by `TASK-20260808-f9374d` use a flow list,
`supersedes: [KN-LIT-13a01d]`, which is a superset and admits multi-supersession.
Neither form is deprecated here. AUDIT-1 below therefore **extracts identifiers
from the line rather than assuming its shape**, and matches them whole with
`grep -x`: a substring match would let `KN-LIT-110` be satisfied by a
`supersedes:` line naming `KN-LIT-1105`, and the corpus's legacy three-digit ids
make that a live hazard rather than a hypothetical one.

---

## 2. AUDIT-1 — the enforcement command

Run from anywhere in the repository. **It prints nothing when the corpus is
clean. Every line it prints is a violation of R-CC-1: the path of a live entry
carrying both claim-class tokens.**

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

Stage by stage, so the command is reviewable rather than trusted:

1. `grep -rlE '^tags:.*(\[|,) ?distinguisher(,|\])'` — entries whose `tags` line
   carries `distinguisher` **as an exact list token**. `(\[|,) ?` is the opening
   delimiter (`[` at the head of the list, or `,` plus one space between items);
   `(,|\])` is the closing delimiter. This is what excludes R-CC-4's three
   compound tags.
2. `xargs -r grep -l …key-recovery…` — of those, the ones that also carry
   `key-recovery` as an exact token. Two independent single-token matches are
   used rather than one two-token regex on purpose: a single regex has to consume
   the first token's closing delimiter, and then fails on the adjacent case
   `[distinguisher, key-recovery]` where that comma is also the second token's
   opening delimiter.
3. `grep -qE '^superseded_by: *KN-' && continue` — drop entries already retired
   the `knowledge/README.md` way.
4. `grep -rhE '^supersedes:' | grep -oE 'KN-…' | grep -qx "$id"` — drop entries
   some other entry declares superseded. This is the branch that matters while
   the four originals stay unedited. It reads identifiers **out of** the
   `supersedes:` line instead of assuming the line's shape, so it works for both
   the scalar and the flow-list form (R-CC-6), and `grep -qx` makes the match
   whole-identifier so a legacy three-digit id cannot be satisfied by a longer
   one that contains it.

**Portability notes, stated rather than assumed.** `xargs -r` is a no-op on
BSD/macOS `xargs`, which already declines to run the utility on empty input, and
is required on GNU `xargs`, which does not; either way the printed output is
empty. `grep -o`, `grep -x`, `grep -L` and POSIX ERE alternation are available on
both. The regexes deliberately avoid bracket expressions containing `]`, which
GNU and BSD `grep -E` and Rust-based tools all parse differently.

**Exit status is not the signal; output is.** `grep` exit codes are consumed
inside the pipeline, so check for empty output, not for `$?`.

## 3. AUDIT-2 — the form guard that keeps AUDIT-1 complete

AUDIT-1 reads one line per entry, so it is blind to a claim-class token written
as a YAML block sequence item. AUDIT-2 is what makes that blindness safe.
**It prints nothing when the corpus is clean. Every line it prints is an entry
AUDIT-1 cannot see, which must be classified by hand or converted to flow style
by supersession.**

```sh
cd "$(git rev-parse --show-toplevel)"
grep -rlE '^[[:space:]]*-[[:space:]]+(distinguisher|key-recovery)[[:space:]]*$' knowledge/
```

AUDIT-2 is deliberately over-broad: it also fires on a body bullet that happens
to be exactly `- distinguisher`. A false positive here costs one look; a false
negative hides a violation.

## 4. What the audit does NOT do

Stated because a clean run invites more weight than it can carry.

- **It enforces form, not correctness.** It cannot tell whether an entry's claim
  class is the *right* one. Tagging a key-recovery paper `distinguisher` passes
  AUDIT-1 and is still wrong. The classification is a reading judgement; the
  audit only guarantees the corpus never asserts both at once.
- **It says nothing about entries with no claim-class token** (R-CC-3).
- **It checks tags, not prose.** An entry may still describe a distinguisher as
  a break in its body. That is what `docs/claims-and-verification.md` and human
  review are for.
- **It is scoped to `knowledge/`.** Ledger records, experiment artifacts and
  task reports are not covered.

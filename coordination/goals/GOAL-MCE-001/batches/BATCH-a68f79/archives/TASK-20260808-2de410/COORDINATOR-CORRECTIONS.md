# Coordinator corrections to the BATCH-a68f79 snapshot receipt

Written 2026-08-08 by the harness-driving session, after validator
`TASK-20260808-ea7bed` (VAL-20260808-71bdb1) returned `failed — scoped`.

**This is a superseding record. `snapshot-receipt.json` is NOT edited again.**
Editing it in place is precisely what caused correction C-2 below, and doing it a
second time to disclose the first would repeat the error while describing it.

Three claims the Coordinator made are wrong. All three were found by the
validator, all three are confirmed here by direct check, and none of them is a
producer's fault.

---

## C-1 — the stated cause of the archive-scope failure is wrong

**What the receipt says** (`archive_scope_defect_recorded_by_the_coordinator.cause`):
that the Coordinator "committed each producer's artifacts as its task closed, so
by the time the snapshot commit was made there was nothing left for it to
contain."

**What the history says.** `git show --name-status c32b4b5dc` lists 20 files:
**all 18 producer artifacts in a single commit**, the snapshot's immediate
parent. The two preceding commits, `111d04124` and `64fdf09aa`, touch
`dispatch_queue.json` and nothing else.

So the recommended pattern — close queue *states* as tasks finish, hold their
*artifacts* — **was already being followed.** The real error is narrower and
duller: the artifact bundle landed as **its own commit, one commit early**,
instead of being the snapshot commit itself. It also carried a message naming
one of the four producing tasks, which is what made it look like an incremental
per-task commit when it was not.

**Why this matters beyond bookkeeping.** The generalised lesson was propagated
into the sibling `GOAL-MLKEM-005 BATCH-cbe023` snapshot commit `6bafef862` and
its receipt, as a rule about not committing artifacts incrementally. That
snapshot verifies clean, and the practice it describes is right — but the
diagnosis attached to it names a cause that did not occur here. A future reader
comparing the two batches would draw the wrong contrast. The correct contrast
is: **the artifacts must be in the snapshot commit, not merely in *a* commit.**

## C-2 — "this receipt binds all 20" is false, and the disclosure broke a hash

`snapshot-receipt.json` binds **19** paths. It does not bind itself — a receipt
cannot contain its own digest.

Worse, and undisclosed until now: commit `ed5cc287d`, whose entire purpose was to
*disclose* the archive-scope defect, **edited the receipt in place**. The queue's
`path_sha256` declares `360045a3245bb6e0b64cc3a25535fea7110b74535b8b1cc6a014fce3e1669a1c`
for the receipt; the file now hashes to
`e36c97eb14f825eafb8966aa77ec957dd569365686b2d0c1eddc5190247245f3`.

**The act of disclosure invalidated the last hash in the archive.** That is the
same in-place edit of an archived record that this session diagnosed on
`GOAL-ECDLP-001` at commit `4ddbe641b` — committed by the person who had just
finished describing why it was forbidden.

The 18 producer artifacts are unaffected: all 18 recompute correctly and are
byte-identical between the snapshot tree and HEAD.

## C-3 — "zero residual references" is false

The Coordinator stated, after the five-way identifier re-mint, that "zero
residual references to the five colliding ids remain."

All five survive in `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-f3aece/proposed_kn_lit_entries.md`
and two further files — three files each.

The check that produced the claim scanned only `knowledge/` and the
`BATCH-a68f79` directory, then stated an unrestricted absolute. **The claim was
broader than the check.** `proposed_kn_lit_entries.md` is immutable and correctly
not edited, so the right remedy is a forward pointer, not a rewrite — but the
statement as made was wrong.

---

## What is NOT wrong

The validator's verdict is `failed — scoped`, and it says explicitly this is not
a finding of fabrication. Confirmed unaffected:

- All 19 receipt hashes recompute; all 18 producer artifacts are byte-identical
  between the snapshot tree and HEAD.
- The five-way identifier collision was **real** — all five old ids are files on
  `774633b8a` — the replacements are genuinely free, and no completed archive
  binds the old ids, so the re-mint was legitimate.
- The `read`/`web` split on `citation_verified` is honest and conservative.
- The dropped IR 8545 SIKE assertion is absent, and dropping it was right.
- `validate_ledger.py` exits 0 with zero hits for any of this batch's ids.

## The two substantive findings that are the batch's real business

These are not Coordinator errors; they are what the validator found in the work,
and they belong to the ledger task:

1. **The audits are breakable, 5 of 5.** The validator built five YAML-legal tag
   forms that parse to exactly `{'tags': ['distinguisher', 'key-recovery']}` and
   evade **both** audits — multi-line flow sequences, quoted scalars, trailing
   comments, and an indented `tags:` key. `TAG-CLAIM-CLASS` §4's disclosed limits
   cover none of them. `R-CC-5` mandates the single serialisation the audits
   handle, and **nothing checks `R-CC-5`.** The Coordinator's claim that the
   constraint is "machine-enforceable" was therefore overstated: it enforces one
   *form*, not the semantic constraint. The fix is one script that parses the
   frontmatter and tests the tag list.

2. **The correction is incomplete, and stops at a full stop.** The three
   superseding sites quote arXiv:2304.14757's Goppa exclusion correctly, but the
   paper's very next sentence is *"However this work could open the road for also
   attacking this subcase"*, page 32 reads *"it is tempting to conjecture that
   Goppa codes … should eventually be attacked in polynomial [time]"*, and the
   exclusion is written *"right now this part of the attack does not work at
   all"* — **phase-scoped and present-tense**. §3.2 calls it *"an intuition"*,
   not a proof. None of the three superseding sites carries any of this, and the
   last quotation already sits in this program's own `heuristics_enumerated.md`,
   a sibling file in the directory the producer quoted from. A reader of the
   corrected record would take a present-tense, explicitly conjectural exclusion
   for a settled structural boundary.

The validator also recovered the arXiv version (v3, stamped in the PDF) and found
that the "verbatim" abstract block in the corpus quotes LaTeX source (`{\em`,
`$q \in \{2,3\}$`) that does not occur in the PDF at the bound sha256 — mixed
acquisition routes under one hash binding.

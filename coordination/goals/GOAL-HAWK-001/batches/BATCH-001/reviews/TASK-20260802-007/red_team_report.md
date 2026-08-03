# Red-team report — TASK-20260802-007

**Target:** BATCH-001's own reasoning (not HAWK).
**Object reviewed:** snapshot commit `3a39803c` (`GOAL-HAWK-001 BATCH-001 source package
snapshot`), receipts bound in `bb54c7ab`. All four reviewed artifact hashes recomputed and
matched against `dispatch_queue.json → TASK-20260802-005.archive.path_sha256`. Working tree
clean. This is a committed snapshot, not a working-tree artifact.

---

## Verdict

**ADMIT WITH ONE CRITICAL CORRECTION REQUIRED BEFORE THE LEDGER ARCHIVE.**

BATCH-001's procedural discipline is genuinely good: it authored an access order before
reporting attempts, refused to claim a pause condition it had not earned, marked extraction
damage, and kept both papers' hedges intact. Duty 3 in the "attacks are unverified therefore
negligible" direction is **clean** — I looked for that failure and did not find it.

But the batch's single most consequential factual assertion is **false**, and I falsified it
with one HTTP GET. The batch reports that the only obtainable copy of eprint 2026/1318's
abstract is "TRUNCATED mid-sentence inside the 30/06 update about Heuristic 4." It is not.
The 18,133 bytes the batch itself downloaded contain the complete update, and the missing
sentences withdraw the polynomial-time claim that is GOAL-HAWK-001's stated objective. The
binding blocker was a **reading failure inside this program**, recorded as a **source
defect**, and then carried into durable knowledge state.

Two further findings: the batch asserts a novel two-paper synthesis in program voice on top
of propositions it lists as unverified (O2), and it simultaneously claims that synthesis as
"BATCH-001's structural contribution" while the queue pre-instructs the decision record to
state that BATCH-001 "produced no internal result" (O3).

No status transition is proposed here. Objections and controls only.

---

## O1 — CRITICAL. The "truncated abstract" is not truncated. The batch had the text and misread it, omitting the authors' withdrawal of the polynomial-time claim.

**Duties 1 and 3.**

`source_access_log.yaml` (SRC-2, route A3) records `HTTP_200, bytes: 18133,
SUCCESS_ABSTRACT_ONLY` with the note *"The abstract as served is TRUNCATED mid-sentence
inside the 30/06 update about Heuristic 4."* The same claim is repeated in
`heuristics_transcription.md` ("The 30/06 update ... The ePrint HTML abstract truncates
mid-sentence inside it"), in `BATCH-001-OPENING.md` ("truncated mid-sentence in the only copy
obtainable"), and pre-existed in `KN-LIT-7670` ("the abstract is truncated mid-sentence in
the retrieved record ... this entry does not complete it").

I fetched the identical URL. Byte count **18,133 — identical to the batch's own recorded
figure**. The OAI-PMH datestamp for the record is `2026-07-05T19:15:41Z`, so the page has not
changed since well before the batch ran. The served page contains, in full:

> **Update (30/06):** Following discussions with Daniel Apon and Markku-Juhani Saarinen, we
> acknowledge that Heuristic 4 is insufficient to conclude that the main algorithm runs in
> polynomial time, **and in fact the main algorithm appears to run in super-polynomial
> time.** This mistake originates from the count of ideals of norm $q'$ in $\mathcal{O}_F$:
> one must include fractional ideals in this count, of which there are many. **We note as an
> aside that Heuristics 1-3 have been independently experimentally verified.**
>
> We would also like to thank the HAWK team and Alice Pellet-Mary for their responses to our
> work.

Independently confirmed via a second endpoint,
`https://eprint.iacr.org/oai?verb=GetRecord&identifier=oai:eprint.iacr.org:2026/1318&metadataPrefix=oai_dc`
(HTTP 200, 3,926 bytes), which returns the same `dc:description` verbatim.

Four facts the batch had in hand and did not record, every one of them decision-critical:

1. **The authors withdraw the polynomial-time claim outright.** GOAL-HAWK-001's `objective`
   is to "verify or refute the reported **classical polynomial-time** smLIP key-recovery
   attack"; `RQ-HAWK-001.decision_target` asks "whether HAWK key recovery is genuinely
   polynomial-time at deployed parameters." The authors already answered: it **appears
   super-polynomial**. The goal is currently pointed at a claim its own authors have retired.
2. **The failure mode is named and specific** — the ideal count omits fractional ideals of
   norm `q'` in `O_F`. That is a concrete, checkable arithmetic defect, i.e. exactly the
   "identification, with derivation, of the specific heuristic that fails" that
   GOAL-HAWK-001's second completion criterion asks for. It is now partially supplied by the
   source, for free.
3. **Heuristics 1–3 have been independently experimentally verified.** This directly
   contradicts the batch's standing framing that "the four heuristics remain unread" and
   `RQ-HAWK-001.methods`' plan to "hold three, stress the fourth" — the three are already
   validated by others and the fourth is already conceded broken.
4. **The HAWK team and Alice Pellet-Mary responded.** `KN-LIT-7592` records "The HAWK team's
   response, if any, is not recorded here." A named, findable response exists.

This is the deeper form of the exhaustion failure. The batch searched eight network routes
for content that was already sitting in a file it had successfully downloaded. Recording a
self-inflicted reading error as an origin-side source defect is precisely the artifact tell
`docs/inventor-protocol.md` §3 warns about, moved from statistics to provenance: the reported
quantity ("blocked") did not respond to the parameter that should have destroyed it (a
successful HTTP 200 with the content in it).

**Fairness note.** `KN-LIT-7670` originated the error on 2026-08-01, and it was honest about
it — it flagged the gap and refused to guess the missing clause, which is correct behaviour.
BATCH-001's failure is narrower but worse: it re-fetched the page, obtained the complete
text, and re-asserted the defect on inherited authority instead of re-reading what it held.

**Cheapest control:** re-fetch `https://eprint.iacr.org/2026/1318` and grep the raw bytes for
`super-polynomial` and `Heuristics 1-3`. Two seconds, zero compute. Then file a **superseding**
`KN-LIT` entry for 2026/1318 (per `AGENTS.md` rule 4 — supersede, never overwrite) carrying
the complete update, and correct the access log's A3 line via the same mechanism.

---

## O2 — HIGH. The two-paper synthesis is asserted in program voice, is stronger than what the authors wrote, and rests on parameters that were never reconciled.

**Duty 3, "HAWK is broken" direction.**

The batch's finding 3 states, unhedged and in this program's own voice:

- `BATCH-001-OPENING.md`: "Straznickas–Weis ... **discharges** that paper's Heuristic 1, **by
  proving** the relevant lattice exactly near-hypercubic."
- `KN-LIT-7673`: "and — **decisively** — that work **discharges this paper's heuristic** ...
  So the current state of the HAWK line ... is: this paper's Theorem 1 is the heuristic
  version of **a result that now also exists unconditionally**. That is a **stronger position
  for the attack side** than either paper states alone."

Three separate problems.

**(a) It is not what the authors said.** The transcribed sentence is: *"upgrades the endgame
from the heuristic pricing of [GP25, Thm. 1] to the unconditional accounting of Theorem
6.1."* "Upgrades the endgame" describes what Straznickas–Weis do in **their own construction**.
"Discharges that paper's Heuristic 1" asserts something about **van Gent–Pulles's heuristic**.
GP25's Heuristic 1 is a general statement about *any* rank-`k` lattice with `λ1 ≤ √2` arising
from *any* nontrivial automorphism σ supplied as input. Straznickas–Weis do not prove it —
they **avoid** it, by working with one specific publicly computable lattice `Λ_B^(τ)` they can
prove near-hypercubic. Avoiding a heuristic on one instance is not discharging it. GP25's
Heuristic 1 is exactly as unproven as before, and GP25's unnumbered §5 group-theoretic
heuristic (random σ ⇒ rank ≤ log n) is untouched by anything in the batch.

**(b) It is built on propositions the batch itself lists as unverified.** The near-hypercubic
isometry is Proposition 4.5, which `KN-LIT-7592`'s own "Not verified here" section names
explicitly as not verified, alongside Theorem 5.1 and Theorem 6.1. The batch's stated
constraint was "Relay, never launder." "A result that **now also exists** unconditionally"
converts a claimed theorem in an un-peer-reviewed preprint by the discovering party into an
existing fact. That is laundering, in the one direction the goal record explicitly warned
against: *"this goal must not inherit a break claim it has not checked."*

**(c) The Pareto comparison was never made.** GP25's Theorem 1 gives **BKZ-β with β = n/4 + 1**.
Straznickas–Weis give **exact-SVP oracle calls in dimension n/2 + 1**. The batch had both
numbers in the same batch, in adjacent files, and never put them in a common unit. These
differ by a factor of two in the exponent under any Core-SVP conversion — unless the two
papers' `n` denote different things, which is entirely plausible and undetermined by anything
the batch recorded. GP25's extraction shows both `R2 n` (i.e. `R_n^2`) and `rot(Q) ∼= Zn`,
which cannot both be right at face value; `KN-LIT-7592` states `n = 2^{ℓ-1}` is the **ring
degree** while also writing `HAWK-512` and `β_key ∈ {211, 452, 940}`, which do not obviously
reconcile without the HAWK spec — and the spec is unread. Note also the two results are of
**different guarantee types** (heuristically-priced BKZ blocksize vs. exact-SVP oracle
dimension) and have **different inputs** (σ assumed available and not produced vs. τ always
available). A claim that one is "the heuristic version" of the other, and that the combination
is "a stronger position for the attack side," requires checking rigor *and* cost *and*
applicability. Only rigor was checked. Under `docs/inventor-protocol.md` §5 an unchecked
Pareto assertion is a fabrication under `AGENTS.md` rule 5, and this one is an unchecked
Pareto assertion in prose form.

**Cheapest control, no compute:** both PDFs are re-acquirable from the recorded, currently
reachable URLs (`cic.iacr.org/p/2/2/20/pdf`, `anthropic.com/document/hawk_key_recovery.pdf`)
and their sha256s are on file. Read GP25 §2 for the definition of `G_{n,Q}` and answer one
question: **is Straznickas–Weis's τ an element of `O(rot(Q)) \ G_{n,Q}`?** If yes, GP25's
Theorem 1 already applies to HAWK with no automorphism search, at `β = n/4 + 1`, and the
Straznickas–Weis contribution is rigor and not cost. If no, the two results are incomparable
and "the heuristic version of" is a category error. Then state both results at HAWK-512 in
one unit. Fifteen minutes of reading; it settles finding 3 either way.

---

## O3 — HIGH. The batch claims a "structural contribution" and simultaneously pre-instructs the ledger to record that it produced no internal result. **(Strongest objection outside the three named duties.)**

`disclosed_attack_transcription.md`: *"That relationship is **BATCH-001's structural
contribution**, and it is visible only with both full texts in hand."* `KN-LIT-7673`: *"it was
not recorded anywhere in this corpus before 2026-08-02."*

`dispatch_queue.json`, TASK-20260802-008 constraint: *"BATCH-001 promotes **NO KN-FIND**,
because it **produced no internal result** — it read other people's work. The not_warranted
reason must say **exactly that**."*

Both cannot be true. Either the two-paper relationship is a novel internal synthesis — in
which case it is an internal result, it belongs in a `KN-FIND` where it is challengeable and
carries its own evidence pointer, and the decision's `knowledge_promotion` reason is false —
or it is not, in which case it should not be asserted in program voice in two `KN-LIT`
entries and a commit message.

The current arrangement is the worst of both: the claim is durable, it sits in literature
records whose contract is relay (`knowledge/SEEDING.md`: *"A literature entry never becomes a
finding. Internal reproduction of a literature result is a new KN-FIND entry"*; *"Relay
content, do not launder it"*), it is asserted about **other people's papers** so a future
reader will attribute it to the sources rather than to this program, and the decision record
is scheduled to state that no such contribution exists. Combined with O2(b), an unverified
program-authored inference about two preprints is being written into the corpus in a slot
where nothing is required to challenge it.

**Cheapest control:** pick one. Either (i) demote the synthesis in `KN-LIT-7673` and the
`KN-LIT-7592` annotation to attributed relay — quote "upgrades the endgame" and stop, deleting
"discharges," "decisively," "now also exists unconditionally," and "stronger position for the
attack side" — or (ii) keep the claim and file it as a `KN-FIND` with `dominated_by` and
`sota_delta` fields filled and the O2(c) unit reconciliation done first. Option (i) is free
and is the narrowest valid conclusion.

---

## O4 — MEDIUM. The exhaustion argument is sound in its conclusion but rests on its weakest available evidence, and "retry available" currently has no deadline, no owner, and no task.

**Duty 1, direct answer.**

I attacked this and the batch's *conclusion* survives: pause condition 2 has genuinely not
fired. But the *reasoning* is weaker than the batch's own log supports, in four ways.

**(a) The order was authored post hoc and has already been exceeded once.** The log is candid:
*"No access order was declared in GOAL-HAWK-001 or RQ-HAWK-001 ... This order is declared
HERE."* That is honest, but it means the criterion for exhaustion was written by the party
whose exhaustion is being judged, in the same document as the attempts. And it was
immediately exceeded: SRC-4 was obtained by a route the log itself marks *"outside the
declared A1–A8 order."* An order that admits new elements when convenient cannot be exhausted
by construction, so "not exhausted" carries less weight than the log implies. **Mitigation I
will state plainly:** the incentive runs the *right* way here. A self-serving post-hoc order
would declare exhaustion and pause, buying the batch an exit. This one declares
non-exhaustion and more work. I do not think the order was written to fit the attempts.

**(b) The batch justified non-exhaustion with the weakest fact in its own log.** It rested on
temporary 429s at A4/A5. A stronger fact was sitting in the same attempts table: **A6
(institutional / open repository) was never attempted for SRC-2 at all.** It is in the
declared order, it was used for SRC-1 (`ir.cwi.nl`), and it was skipped for the one source
that needed it. A route never tried is a cleaner non-exhaustion argument than a route that
returned a self-inflicted rate limit.

**(c) The two routes held open have low expected yield, and one of them is now closed.** A4
(arXiv) — IACR-only cryptography preprints are rarely cross-posted, and the log itself found
no evidence of one. A5 (Semantic Scholar `openAccessPdf`) — for an eprint-only preprint this
resolves back to `eprint.iacr.org/2026/1318.pdf`, the exact URL that is Cloudflare-gated, so
even a successful retry likely returns the blocked link. So the batch kept the door open on
the two routes least likely to work. I discharged A6 myself (see below): Imperial College
London's Spiral repository DSpace API returns HTTP 200 with `totalElements: 0` — the paper is
not deposited. OpenAlex returns 0 results. The eprint PDF endpoint returned **403 Cloudflare
again** on retest, so that finding is stable and correctly recorded.

**(d) "Retry available" has no stopping rule.** The log says A4/A5 *"should be retried from a
fresh quota before any pause is recorded"* — but no task in `dispatch_queue.json` is assigned
to retry them, no retry-by date is set, and no criterion says what a failed retry would mean.
As written, any future session can re-assert "retry available" indefinitely, which makes
pause condition 2 unfalsifiable. This is the mirror image of the `docs/inventor-protocol.md`
§4 closure standard: a *refusal* to close also needs forward guidance with a bound, not just
a named next attempt.

### Cheapest untried route to eprint 2026/1318's full text — direct answer

Honestly stated in two parts, because the question splits.

**For the content the batch actually needs right now:** the route is not a network route at
all — **re-read the 18,133 bytes already downloaded**, or one GET against the ePrint OAI-PMH
endpoint. See O1. This does not yield the four heuristic statements, but it yields the
authors' withdrawal of the polynomial-time claim, the named arithmetic defect, and the
verification status of Heuristics 1–3. That is the highest-value missing content in the
batch, and its cost is zero.

**For the full text proper:** after my probes, the honest map is that A1, A2, A6, A7, A8 are
now genuinely closed for SRC-2 and A4/A5 are near-worthless for it. The cheapest untried route
that remains is **an author request** — all four contact addresses are printed on the
reachable abstract page (`b p nelson2003 @ gmail com`, `j limbrey24 @ imperial ac uk`,
`c ling @ imperial ac uk`, `andrew mendelsohn18 @ imperial ac uk`), i.e. route A8 performed
properly rather than as a web search. This agent has no mail channel, so the honest record is:
**near-zero cost, available to the human operator, never attempted.**

**I explicitly do not recommend** routing the gated PDF through a third-party rendering proxy
or text-extraction relay. That is deliberate circumvention of an origin's bot protection, and
a research program that logs "the proxy is healthy, the origin is refusing bots" should not
then evade the refusal.

**Cheapest control:** add A9 = "public contact-author request" to the declared order and
either dispatch it to the operator with a retry-by date, or record it as unavailable under
this harness. Either way, set a retry-by date on A4/A5 and a criterion for what a second 429
means, so pause condition 2 becomes decidable.

---

## O5 — MEDIUM. The premise correction is directionally right but overreads the goal text, mislocates the actual defect, and contains a date error now in durable ledger state.

**Duty 2. This duty partially checks out and partially does not.**

**What is correct.** The batch is right that (i) the four heuristics belong to 2026/1318 and
not to Straznickas–Weis, (ii) Straznickas–Weis is unconditional, and (iii) it was already in
the corpus as `KN-LIT-7592` and the goal did not cite the ID. The resolution of "the disclosed
attack" to Straznickas–Weis is also right, and for a good reason the log does not state:
`KN-LIT-7592`'s `venue` field literally reads *"disclosed to the HAWK authors in June 2026 and
to the NIST PQC mailing list."* And the goal's own list names 2026/1318 separately, so
"the disclosed attack" cannot be 2026/1318 without duplicating an entry. The referent
identification is sound.

**What is an overread.** The batch's headline is *"The goal's next_action rests on a false
premise. It asks for 'the four heuristics' of the disclosed attack."* The goal text does not
say that. It says: *"obtain the primary sources (the disclosed attack, eprint 2026/890, eprint
2026/1318, van Gent-Pulles 2025) and file **them** as KN-LIT entries with the four heuristics
transcribed verbatim and numbered."* The modifier attaches to *them* — the four sources
collectively — not to "the disclosed attack." Under the plain reading the instruction is
"among these four sources, transcribe the four heuristics," which is **satisfiable**, points
at 2026/1318, and is exactly what the batch concluded on the merits. Nothing in the goal
record attributes four heuristics to Straznickas–Weis. Was the goal author writing about
2026/1318 all along? For the four heuristics, yes — `GOAL-HAWK-001.objective` says "classical
polynomial-time," `RQ-HAWK-001.motivation` says "four number-theoretic heuristics ... nrdPIP,"
and both are 2026/1318's signature, not Straznickas–Weis's. **The correction as written is not
fair to that record.**

**Where the real conflation lives, and the batch missed it.** `RQ-HAWK-001.motivation` reads:
*"Reported 2026 cryptanalysis claims a classical probabilistic-polynomial-time recovery of the
HAWK secret key, resting on four number-theoretic heuristics and on a reduction from HAWK's
rank-2 module-LIP instances to nrdPIP, enabled by an automorphism whose existence van Gent and
Pulles (2025) showed would halve the effective rank."* That single sentence welds **2026/1318**
(four heuristics + nrdPIP) to **Straznickas–Weis** (Galois automorphism + rank halving + the
GP25 descent) into one imagined attack. Straznickas–Weis appears **nowhere by name** in
`RQ-HAWK-001`, despite `KN-LIT-7592` having been filed the day before the question was
created. *That* is the genuine conflation defect in the ledger, it is upstream of everything
BATCH-001 did, and the batch diagnosed the symptom in `next_action` while walking past the
cause in the question record.

**Date error.** `BATCH-001-OPENING.md`, the goal's `superseded_because`, and the commit message
for `3a39803c` all state `KN-LIT-7592` was *"filed 2026-07-28, **four days** before this goal
asked for it."* `GOAL-HAWK-001.next_action_history[0].recorded_at` is `2026-07-29`, and
`created_at` for both the goal and `RQ-HAWK-001` is `2026-07-29`. 2026-07-28 → 2026-07-29 is
**one day**. Neither anchor gives four (07-28 → 08-02 is five). Small, but it is a derived
figure now committed in three places including immutable ledger prose, and `AGENTS.md` rule 5
covers fabricated statistics regardless of size.

**Cheapest control:** in the superseding record, restate the finding at its supported width —
*"the goal named a primary source by a non-unique description and cited no `KN-LIT` ID, and
`RQ-HAWK-001.motivation` fuses two distinct 2026 attacks into one description"* — drop "false
premise," and correct "four days" to "one day."

---

## O6 — LOW/MEDIUM. `KN-LIT-7592`'s `web → read` upgrade is not supported by what was done, and no reviewer was assigned to check the upgrade level.

`knowledge/SEEDING.md` permits `web → read` "only after fetching the actual source." The PDF
was fetched, so the letter is met. But the entry's own **unedited** body still reads: *"read
at the level of the abstract, introduction, and technical overview (§§1–2) ... The body
sections (§§3–9) and appendices were not read line by line."* What TASK-20260802-004 added was
a **regex census** over a pdfminer extraction plus targeted quotation — a machine token count,
not a read of §§3–9. The frontmatter now says `read` while the body says §§1–2. Meanwhile
`disclosed_attack_transcription.md` leans on that census for the batch's principal finding.

The census is fine for what it is (`Heuristic` ×0 is strong evidence of absence, and I have no
reason to doubt it), but "we grepped the whole text" and "we read the whole text" are different
provenance tiers and the entry now claims the second. The validator's duty 3 was scoped to
"the `KN-LIT-7592` web-to-read upgrade edited NO claim" — it does not ask whether `read` is
warranted, so no one is assigned to this.

**Cheapest control:** one line in the existing annotation block: *"`read` here means the full
text was obtained and machine-censused plus targeted-section read; §§3–9 and the appendices
remain unread line by line, as the body states."* Free, and it stops the tier from drifting.

---

## O7 — LOW. "Needs only checking" understates the verification burden, and "unconditional" is not "correct."

`disclosed_attack_transcription.md`: *"For the disclosed attack the answer is none, and that
answer is not a technicality — it is the difference between an attack that needs validating
and one that **needs only checking**."*

The same file's census counts `Theorem` ×28, `Lemma` ×60, `Proposition` ×19. "Only checking"
a 107-item deductive chain, plus the correctness of Ducas's block reduction as used, plus
Proposition D.2's parity argument, plus the `O(n² log n)` oracle-call bound, plus a gate-count
conversion inheriting every assumption of [AGPS20] and of an **unread** HAWK specification, is
not less work than validating four heuristics — it is a different and probably larger job.
Absence of heuristics removes a *class* of failure; it does not remove proof error, and this
preprint is un-peer-reviewed and authored by the discovering party (as `KN-LIT-7592` correctly
notes). The phrase invites a downstream session to skip verification of the one attack this
program can actually reach.

**Cheapest control:** replace "needs only checking" with "needs proof-checking rather than
heuristic validation — a different burden, not a smaller one."

---

## Duty 3, second direction — checks out, stated plainly

I looked specifically for "the attacks are unverified, therefore negligible" and **did not
find it**. Recording that plainly rather than manufacturing an objection:

- `BATCH-001-OPENING.md` carries the 2026/1318 gap forward as an *"Open obligation carried
  forward ... BATCH-001 does not discharge it,"* not as a dismissal.
- `KN-LIT-7670` preserves the authors' own hedge and their retraction, and states *"That is not
  a break, and this entry does not treat it as one"* — correct in both directions.
- The `2^150 → 2^108` and `2^288 → 2^182` gate counts and the demonstrated HAWK-256 recovery
  appear **only** in `KN-LIT-7592`'s pre-existing body, where its "Not verified here" section
  names all of them explicitly as unverified, *"which inherit every modelling assumption of
  [AGPS20] and of the HAWK specification's own cost model."* **None of these figures is
  repeated or relied upon anywhere in BATCH-001's new artifacts.** The batch neither inherited
  them as established nor dismissed them. That is the correct handling and it deserves saying.
- `disclosed_attack_transcription.md`'s three carry-forward caveats on the cost claim
  (oracle-relative not practical; Core-SVP conversion is the authors' own heuristic pricing;
  "roughly halves" is about oracle dimension and *"is not a claim that HAWK is broken at
  deployed parameters"*) are exactly right.

The only breach of duty 3 is O2, and it is in the "broken" direction, via the relationship
synthesis rather than via any cost figure.

**One residual risk worth naming, not an objection:** BATCH-001's attention allocated itself
by what was *obtainable*. The source it could read (unconditional, exponential, not the goal's
target) became "the batch's structural contribution"; the source it could not read (the
polynomial-time claim that is the goal's actual objective) became a deferred obligation. O1
shows the deferral was unnecessary. Availability-driven prioritization is not premature
closure, but over several batches it becomes indistinguishable from it.

---

## Baseline / Pareto comparison

Not applicable in the usual sense — BATCH-001 advances no attack of this program's own, so
Pollard-rho, BSGS, and specialized-baseline comparisons have no object to attach to, and the
batch is right that promotion gates G1–G4 are untouched. The Pareto obligation that **does**
bind is between the two obtained papers, and it was not discharged: see **O2(c)**. GP25
`β = n/4 + 1` (heuristic BKZ, σ assumed available) versus Straznickas–Weis dimension
`n/2 + 1` (exact-SVP oracle, τ always available) were never stated in a common unit, and
"stronger position for the attack side" was asserted without checking the cost axis or the
applicability axis. Under `docs/inventor-protocol.md` §5 that is an unchecked Pareto assertion.

---

## Narrowest supported statement

BATCH-001 supports exactly this: *van Gent–Pulles (`iacr:2025/928`) and Straznickas–Weis were
obtained in full text and filed at `citation_verified: read`; a machine census of the
Straznickas–Weis extraction returns `Heuristic` ×0 and `Conjecture` ×0, and of van Gent–Pulles
returns one numbered `Heuristic 1` plus an unnumbered §5 group-theoretic argument; the
`eprint.iacr.org` PDF endpoint is stably Cloudflare-gated across at least five report numbers
and two sessions while its HTML and OAI-PMH endpoints serve normally; eprint 2026/1318's PDF
was not obtained; and no claim of either paper has been verified, re-derived, or re-run by
this program.*

Everything beyond that — "false premise," "discharges Heuristic 1," "a result that now also
exists unconditionally," "stronger position for the attack side," "structural contribution,"
"the abstract is truncated" — is either unsupported, overread, or false.

---

## Next concrete action (one)

**Before TASK-20260802-008 writes `EV-HAWK-001` and `DEC-20260802-001`: re-read the
already-downloaded `eprint.iacr.org/2026/1318` abstract page and file a superseding `KN-LIT`
entry for 2026/1318 carrying the complete 30/06 update.** It costs one HTTP GET, and it
changes what the evidence record must say: the authors have withdrawn the polynomial-time
claim ("appears to run in super-polynomial time"), named the arithmetic cause (fractional
ideals omitted from the count of ideals of norm `q'` in `O_F`), reported Heuristics 1–3
independently experimentally verified, and acknowledged responses from the HAWK team and Alice
Pellet-Mary. An evidence record whose central finding is "the four heuristics are unread and
blocked" would be committing a statement this program can already falsify from bytes it
already holds.

---

```yaml
red_team_report:
  id: RT-20260802-001
  task_id: TASK-20260802-007
  goal_id: GOAL-HAWK-001
  batch_id: BATCH-001
  reviewed_snapshot: 3a39803ca942dd3b366a5b0b17c2fdcdf812f0bd
  snapshot_hashes_verified: true
  claim_under_review: >-
    BATCH-001's own reasoning: (a) that pause condition 2 has not fired because
    the declared A1-A8 access order is unexhausted; (b) that GOAL-HAWK-001's
    next_action rests on a false premise; (c) that the HAWK line is treated as
    unsettled in both directions.
  verdict: ADMIT_WITH_CRITICAL_CORRECTION
  objections:
    - id: O1
      severity: critical
      duty: [exhaustion, premature-closure]
      summary: >-
        The "truncated abstract" of eprint 2026/1318 is not truncated. The
        18133-byte page the batch itself downloaded contains the complete 30/06
        update, verified independently via OAI-PMH. The omitted text withdraws
        the polynomial-time claim ("appears to run in super-polynomial time"),
        names the cause (fractional ideals omitted from the ideal count in O_F),
        states Heuristics 1-3 independently experimentally verified, and
        acknowledges responses from the HAWK team and Alice Pellet-Mary. A
        self-inflicted reading error was recorded as an origin-side source defect
        and propagated into KN-LIT-7670, the access log, the transcription, the
        opening record and the commit message.
      control: >-
        Re-fetch https://eprint.iacr.org/2026/1318 and grep raw bytes for
        "super-polynomial" and "Heuristics 1-3"; file a superseding KN-LIT entry.
    - id: O2
      severity: high
      duty: [premature-closure]
      summary: >-
        "Straznickas-Weis discharges van Gent-Pulles's Heuristic 1" and "a result
        that now also exists unconditionally" are asserted in program voice, are
        stronger than the authors' own "upgrades the endgame", rest on
        Proposition 4.5 / Theorem 5.1 / Theorem 6.1 which KN-LIT-7592 lists as
        unverified, and were never checked across the two papers' unreconciled
        parameter conventions (beta = n/4+1 vs oracle dimension n/2+1).
      control: >-
        Read GP25 section 2 and decide whether tau is in O(rot(Q)) \ G_{n,Q};
        then state both results at HAWK-512 in one unit. Both PDFs re-acquirable
        from recorded reachable URLs with sha256 on file.
    - id: O3
      severity: high
      duty: [outside-named-duties]
      summary: >-
        BATCH-001 claims a novel two-paper synthesis as "BATCH-001's structural
        contribution" while dispatch_queue.json pre-instructs DEC-20260802-001 to
        record that the batch "produced no internal result". The synthesis is
        filed inside KN-LIT relay records, which knowledge/SEEDING.md forbids
        ("a literature entry never becomes a finding"), where nothing is required
        to challenge it and a future reader will attribute it to the sources.
      control: >-
        Either demote to attributed relay (quote "upgrades the endgame", delete
        "discharges"/"decisively"/"now also exists unconditionally"/"stronger
        position"), or file as KN-FIND with dominated_by and sota_delta after O2.
    - id: O4
      severity: medium
      duty: [exhaustion]
      summary: >-
        The non-exhaustion conclusion survives, but rests on the weakest fact in
        the log (self-inflicted 429s at A4/A5) while a stronger one sat unused
        (A6 declared but never attempted for SRC-2). A4/A5 have low expected
        yield for an eprint-only preprint; A5 resolves back to the gated URL.
        "Retry available" has no retry-by date, no owner, and no queued task,
        which makes pause condition 2 unfalsifiable. The order was authored post
        hoc and already exceeded once (SRC-4 via anthropic.com) - though the
        incentive runs toward more work, not less, so this is not gaming.
      control: >-
        Set a retry-by date and a failure criterion for A4/A5; add A9 = public
        contact-author request and dispatch it to the operator or record it as
        unavailable under this harness.
    - id: O5
      severity: medium
      duty: [premise-correction]
      summary: >-
        Referent identification is correct, but "the goal asks for the four
        heuristics OF the disclosed attack" is an overread - the modifier attaches
        to the four sources collectively and the instruction is satisfiable. The
        real conflation is in RQ-HAWK-001.motivation, which welds 2026/1318's
        four-heuristic nrdPIP route to Straznickas-Weis's automorphism/rank-halving
        into one imagined attack and never names Straznickas-Weis; the batch
        missed it. "Filed 2026-07-28, four days before this goal asked for it" is
        wrong - next_action recorded_at is 2026-07-29, i.e. one day.
      control: >-
        Restate at supported width (non-unique referent + missing KN-LIT ID +
        RQ-HAWK-001.motivation conflation); drop "false premise"; fix "four days".
    - id: O6
      severity: low_medium
      duty: [premature-closure]
      summary: >-
        KN-LIT-7592's citation_verified web -> read upgrade rests on obtaining the
        PDF plus a regex census, while the entry's unedited body still says only
        sections 1-2 were read. No reviewer duty was scoped to the upgrade level.
      control: >-
        One line in the existing annotation defining what "read" covers here.
    - id: O7
      severity: low
      duty: [premature-closure]
      summary: >-
        "An attack that needs validating vs one that needs only checking"
        understates a 28-theorem/60-lemma unconditional reduction resting on an
        unread HAWK specification. Unconditional is not correct.
      control: >-
        Replace with "proof-checking rather than heuristic validation - a
        different burden, not a smaller one."
  duties_that_check_out:
    - >-
      PREMATURE CLOSURE, "unverified therefore negligible" direction: CLEAN. The
      2026/1318 gap is carried forward as an open obligation; KN-LIT-7670
      preserves the authors' hedge and retraction; the 2^150->2^108 and
      2^288->2^182 gate counts and the HAWK-256 recovery appear only in
      KN-LIT-7592's pre-existing body under "Not verified here" and are neither
      repeated nor relied on in any BATCH-001 artifact.
    - >-
      Referent resolution of "the disclosed attack" to Straznickas-Weis is sound
      (KN-LIT-7592's venue field names the June 2026 disclosure; the goal lists
      2026/1318 separately).
    - >-
      The eprint PDF endpoint block is real and stable: retested 2026-08-02,
      HTTP 403 Cloudflare, 5402 bytes.
    - >-
      Snapshot integrity: all four reviewed artifact sha256 values match the
      TASK-20260802-005 receipt; working tree clean.
  routes_probed_by_this_review:
    - route: 'eprint OAI-PMH GetRecord oai_dc for 2026/1318'
      result: HTTP_200, 3926 bytes, complete untruncated abstract incl. 30/06 update
    - route: 'https://eprint.iacr.org/2026/1318 (A3 re-fetch)'
      result: HTTP_200, 18133 bytes - identical byte count to the batch's record; contains full update
    - route: 'https://eprint.iacr.org/2026/1318.pdf (A2 retest)'
      result: HTTP_403 Cloudflare, 5402 bytes - block confirmed stable
    - route: 'A6 Imperial College Spiral DSpace REST (NEVER attempted by the batch)'
      result: HTTP_200, totalElements 0 - not deposited; A6 now genuinely discharged
    - route: 'OpenAlex title search'
      result: HTTP_200, 0 results - not indexed
    - route: 'BASE aggregator'
      result: access denied by user agent
    - not_probed_by_instruction: [arXiv API (A4), Semantic Scholar Graph API (A5)]
  cheapest_untried_route_for_2026_1318:
    for_missing_content_now: >-
      Not a network route. Re-read the 18133 bytes already held, or one OAI-PMH
      GET. Yields the polynomial-time withdrawal, the named arithmetic defect,
      and the Heuristics 1-3 verification status. Cost: zero.
    for_full_text: >-
      Public contact-author request - all four addresses printed on the reachable
      abstract page, three at imperial.ac.uk. Route A8 done properly rather than
      as a web search. Never attempted; near-zero cost to the human operator; not
      available to this agent (no mail channel).
    explicitly_not_recommended: >-
      Routing the gated PDF through a third-party rendering proxy or text-relay.
      That is deliberate circumvention of an origin's bot protection.
  counterexample_or_mutation: >-
    The decisive one is executed, not proposed: fetching the URL the access log
    already records as HTTP_200/18133 bytes returns text the log says is not
    there. The null-object control for O2 is GP25's own Heuristic 1 - it remains
    exactly as unproven after Straznickas-Weis as before, because a heuristic
    avoided on one specific lattice is not a heuristic discharged.
  baseline_comparison: >-
    No ECDLP or attack baseline applies - BATCH-001 advances no mechanism of this
    program's own and G1-G4 are correctly untouched. The binding Pareto comparison
    is between the two obtained papers and was NOT made: GP25 beta = n/4+1
    (heuristic BKZ, sigma assumed available) vs Straznickas-Weis exact-SVP
    dimension n/2+1 (tau always available), never stated in a common unit, yet
    combined into "a stronger position for the attack side". Unchecked Pareto
    assertion under docs/inventor-protocol.md section 5.
  heuristic_challenges:
    - >-
      GP25 Heuristic 1 is a 2016-estimates BKZ success condition whose equation
      (2) is [EXTRACTION-DAMAGED] and was reconstructed by inference, not
      transcribed. Nothing downstream may rely on it. Correctly flagged by the
      batch.
    - >-
      GP25's unnumbered section 5 group-theoretic heuristic - the one carrying
      "break HAWK with high probability" - is untouched by Straznickas-Weis and
      by BATCH-001, and is the load-bearing claim for the strongest cost
      statement on the table.
    - >-
      2026/1318's Heuristics 1-3 are independently experimentally verified and
      Heuristic 4 is conceded broken with a named cause - all publicly stated and
      all missed by the batch (O1). "Hold three, stress the fourth" in
      RQ-HAWK-001.methods is now redundant with published work.
  cost_model_challenges:
    - >-
      n is unreconciled between the two obtained papers; KN-LIT-7592 pairs
      "n = 2^(l-1) is the ring degree" with HAWK-512 and beta_key in {211,452,940}
      without the HAWK specification, which is unread.
    - >-
      Straznickas-Weis's 2^((n/2+1)+o(n)) is oracle-relative (provable [ADRS15]
      sieve), and the Core-SVP 2^(0.292 beta) conversion is the authors' own
      heuristic pricing. Correctly carried by the batch; must not be merged.
    - >-
      Memory is charged nowhere in BATCH-001 for either result. Not an objection
      to this batch (it advances no cost claim) but it must not be inherited as a
      completed comparison.
  reduction_and_scope_challenges:
    - >-
      "Discharges Heuristic 1" mis-instantiates the relationship: Straznickas-Weis
      avoid GP25's heuristic on a specific provably near-hypercubic lattice rather
      than proving GP25's general statement. The cited sentence says "upgrades the
      endgame", which is a claim about their own construction.
    - >-
      Whether tau is an instance of GP25's sigma is undetermined and decides
      whether the two theorems are comparable at all.
    - >-
      Scope is not inflated: KN-LIT-7592's conductor-based evasion criterion and
      the Falcon non-transfer are relayed with their unverified status intact.
  proof_architecture_challenges:
    - >-
      Quantifier order: GP25 Theorem 1 quantifies over any nontrivial sigma
      supplied as input; Straznickas-Weis fix one specific tau. "The heuristic
      version of" silently swaps a for-all-sigma statement for an
      exists-a-good-tau statement.
    - >-
      Baseline reproduction: neither obtained result was reproduced against
      HAWK's own [HAWK25] tables, because the specification is unread. All
      [HAWK25] references in the transcription are relayed, correctly flagged.
  narrowest_supported_statement: >-
    Two of four declared sources were obtained in full text and filed at
    citation_verified read; machine censuses return Heuristic x0 / Conjecture x0
    for Straznickas-Weis and exactly one numbered Heuristic 1 for van Gent-Pulles;
    the eprint.iacr.org PDF endpoint is stably Cloudflare-gated while its HTML and
    OAI-PMH endpoints serve normally; eprint 2026/1318's PDF was not obtained; no
    claim of any source has been verified, re-derived or re-run by this program.
  next_concrete_action: >-
    Before TASK-20260802-008 writes EV-HAWK-001 and DEC-20260802-001, re-read the
    already-downloaded eprint.iacr.org/2026/1318 abstract page and file a
    superseding KN-LIT entry carrying the complete 30/06 update. One HTTP GET. It
    changes what the evidence record must say, and prevents committing a central
    finding this program can already falsify from bytes it holds.
  status_transition_proposed: none
  artifact_paths:
    - coordination/goals/GOAL-HAWK-001/batches/BATCH-001/reviews/TASK-20260802-007/red_team_report.md
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    independent_session: true
    model_independence_note: >-
      PROCEDURAL ONLY. Author, validator and red team all resolve to
      claude-opus-5. Nothing in this report is admissible toward the AGENTS.md
      rule 13 three-model closure quorum.
```

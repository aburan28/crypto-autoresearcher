# Red-team report — TASK-20260802-73a352

**Goal**: `GOAL-HQC-001` · **Batch**: `BATCH-001` · **Role**: red-team
**Target**: this batch's own reasoning — the `BATCH-001-OPENING.md` framing, its
§4 claim about the goal's `next_action`, the two producers' terminal artifacts,
both snapshot receipts, both snapshot commit messages, and the Coordinator's
mid-flight process decisions.
**Produced**: 2026-08-02 · **Repo commit at authoring**: `8b20ddda093a7daac3581b854a9dc19660751e67`

---

## 0. Independence, and the limitation that bounds everything below

| field | value |
|---|---|
| `requested_policy` | `review-adversarial` (requires `xhigh` reasoning and an independent session) |
| `resolved_model_id` | `claude-opus-5` |
| `fallback_used` | **true** |
| `model_verified` | false — `python3 -m orchestration.adapter doctor --probe` was not run; the adapter is not the runtime here |
| `independent_session` | **true** — I authored no artifact reviewed here and read every one for the first time in this task |
| `independent_model` | **false** |

**No policy alias in `orchestration/model-policies.yaml` resolves under this
Claude Code harness.** Subagent frontmatter in `.claude/agents/` supports only
Claude models, so every task in `BATCH-001` — both producers, the validator, and
this session — runs on one backend. This report is therefore an independent
*session* and not an independent *model*.

**Nothing in this report is admissible toward an `AGENTS.md` rule 13 closure
quorum**, and no attestation may be synthesised from it later. `BATCH-001-OPENING.md`
§7 states this correctly and I confirm it rather than contest it.

I made no status transition, edited no ledger record, no raw artifact, no queue,
and nothing under `knowledge/`. I ran no state-mutating git command. My only
write is this file.

---

## 1. VERDICT

### `ADMIT_WITH_REQUIRED_CORRECTIONS`

**The batch may proceed to the ledger archive `TASK-20260802-a157ad`**, provided
that **O1, O2, O4, O5 and O8 below are carried into `DEC-20260802-344883` as
corrections rather than as confirmations.** None of the eleven objections is an
evidence-integrity failure that stops the review chain: both snapshot commits
verify, write scopes held, no claim tier moved, and — as §3 below shows — the
transcription independently reproduces its own source's published arithmetic at
nine separate numeric points.

Two of the Coordinator's claims are **overreads**, one of them of exactly the
family that `GOAL-HAWK-001` `BATCH-001` was corrected for. One producer claim is
**false as stated** and is already in two permanent records. One transcription
value is **probably the transcription's own extraction error, mis-filed as a
source anomaly**, and it is worth **50.7 bits of DFR** at NIST-5.

Against that: the source-acquisition work is the strongest single artifact this
red team has been asked to attack. The DFR model was obtained from the canonical
primary site, its derivation source was identified *from the specification's own
reference list rather than from memory*, the access log declares its route order
before attempting it and records the routes it never reached, and the
transcription is functionally correct under independent recomputation. The
convention artifact labels 23 of its 47 items as the producing agent's own
choice, names its own most-attackable clauses, and includes a hook that can
retire it for being useless. I did not find calibration toward a desired
outcome; where I found a directional bias it runs **against** this goal's own
interest, and I say so in O7.

---

## 2. Controls I ran

Every objection below carries the cheapest control that resolves it. Where the
control cost seconds, I ran it, so the objection arrives with a measurement
rather than a suggestion. All are read-only; none modifies repository state.

| id | control | result |
|---|---|---|
| **C1** | `curl -sS -L https://eprint.iacr.org/2026/1498.pdf` at `2026-08-02T21:50:18Z` | **HTTP 403**, `text/html`, 5381 B, body begins `<!DOCTYPE html>…<title>Just a moment...</title>` — a Cloudflare challenge |
| **C2** | `curl -sS -L https://csrc.nist.gov/projects/post-quantum-cryptography` at `21:50:32Z` | HTTP 200, 60 700 B |
| **C3** | `curl -sS -L https://www.nist.gov/` at `21:50:32Z` — the host the producer explicitly did **not** test | **HTTP 200, 95 182 B** |
| **C4** | Semantic Scholar Graph API on `DOI:10.1007/978-3-030-64837-4_12` — a route never attempted by `TASK-20260802-6344ed` | HTTP 200; title/venue/year corroborated; `isOpenAccess: false`, `openAccessPdf.status: "CLOSED"` |
| **C5** | `curl --http1.1 -H 'Accept-Encoding: identity' https://cr.yp.to/2005-590/wiener.pdf` — the fetch `GOAL-SSI-001` `BATCH-003` D4 recorded as `FAILED_REMAINS_OPEN` | **HTTP 200, 234 591 B, PDF 1.3, 21 pp.**, sha256 `9723d47ae05d39d14dfc3ad3789873d9139057291660d3bf1ae48931e8c50263`. Title page: *The Full Cost of Cryptanalytic Attacks*, Michael J. Wiener |
| **C6** | `for f in ledger/proposals/IDEA-20260801-*.yaml; do grep -m1 question_id $f; done` | 21 records, **exactly one per research question** across the whole roster |
| **C7** | `grep -rl "downloads/" knowledge/literature/ \| wc -l`; same restricted to `citation_verified: read` | **7421** of 7666 records; **7420** of 7457 read-tier records (99.5 %). `downloads/` is untracked by git and absent from `.gitignore` |
| **C8** | Exact-rational recomputation of the transcribed DFR chain (§3) | Nine numeric agreements with the specification's own published values |
| **C9** | `tools/research_dispatch.py` on the amended queue | All ten dispatch gates pass, including `completed_archive_commits_verified` |
| **C10** | `tools/validate_ledger.py` at `HEAD` | `FAIL: 183 new validation error(s)` — **identical to the opening §8 pre-batch count**; zero name any HQC record. The batch added none |

---

## 3. The control the batch did not run on its own headline artifact

`dfr_model_transcription.md` is the deliverable this goal exists on, and no
artifact in the package checks whether the transcribed formulas actually produce
the specification's own numbers. That check is `docs/inventor-protocol.md` §8
audit 1 (*exact baseline reproduction*), it needs no network and no new source,
and it takes seconds. I ran it against the transcription alone, using exact
rationals with `fractions.Fraction` and `decimal` at 200 digits.

**Stage 1 — Proposition 6.1.1 + Equation (2) → p⋆.** Evaluating the transcribed
formula `p̃ = [C(n,ω)·C(n,ω_r)]⁻¹ · Σ_{ℓ odd} C(n,ℓ)C(n−ℓ,ω−ℓ)C(n−ω,ω_r−ℓ)`
followed by Eq. (2), at the Table 5 parameters:

| set | n, ω, ω_r=ω_e | computed p̃ | computed p⋆ | SPEC Tables 9/11 |
|---|---|---|---|---|
| HQC-1 | 17 669, 66, 75 | 0.215761 | **0.339788** | 0.3398 |
| HQC-3 | 35 851, 100, 114 | 0.236295 | **0.361804** | 0.3618 |
| HQC-5 | 57 637, 131, 149 | 0.246846 | **0.372489** | 0.3725 |

All three agree to every published digit. (The transcribed `C_ℓ` also reduces
algebraically to the standard hypergeometric form: `C(n,ℓ)C(n−ℓ,ω−ℓ) =
C(n,ω)C(ω,ℓ)`, so `p̃ = Σ_{ℓ odd} C(ω,ℓ)C(n−ω,ω_r−ℓ)/C(n,ω_r)`.)

**Stage 2 — Propositions 6.1.3 and 6.1.4 → p_i.**

| set | code | Prop 6.1.3 (statement exponent) | Prop 6.1.4 | SPEC Table 11 |
|---|---|---|---|---|
| NIST-1 | [384,8,192], p⋆=0.3398 | −10.129 | **−10.793** | −10.79 |
| NIST-3 | [640,8,320], p⋆=0.3618 | −13.670 | **−14.138** | −14.14 |
| NIST-5 | [640,8,320], p⋆=0.3725 | −10.761 | **−11.321** | −11.30 |

**Stage 3 — Theorem 6.1 → concatenated DFR**, with `(n_e, δ_e)` from Table 3:

| set | n_e, δ_e | Theorem 6.1 bound | SPEC Table 5 design target |
|---|---|---|---|
| HQC-1 | 46, 15 | **2⁻¹³²·⁸⁶** | < 2⁻¹²⁸ |
| HQC-3 | 56, 16 | **2⁻¹⁹³·⁸⁸** | < 2⁻¹⁹² |
| HQC-5 | 90, 29 | **2⁻²⁶⁰·⁵¹** | < 2⁻²⁵⁶ |

**Scope of this control, stated before anyone reads it as more than it is.** This
is a reproduction of the *specification's own arithmetic from the transcription*.
It is a **transcription-fidelity check and nothing else**. It is not a
measurement, not a decoding trial, not a validation of assumptions A1–A23 (A5 —
coordinate independence — and A17 — i.i.d. inner-decoder outcomes — are exactly
what it cannot test), and **not a statement about HQC's security in either
direction**. `claim_tier: not_applicable`; no certificate applies
(`certificate.kind: none`). The three-stage margins above are the
specification's claim recomputed, not this program's finding.

**What it establishes, and what it costs the batch.**

1. **The transcription is functionally correct.** Nine independent numeric
   agreements is a far stronger fidelity result than the page-image verification
   the producer performed, and the validator's transcription-fidelity duty can
   now be discharged on numbers rather than on eyeballs.
2. **Three of the ten recorded anomalies dissolve at zero cost.**
   - **X1 resolved.** Prop 6.1.3's *statement* exponent `(1−p)^{d_i−j}` is the
     intended one. The exponent displayed in its own proof, `(1−p)^{n−j}`, gives
     log₂ p_i = **−125.14** at NIST-1 — plainly a typesetting error, not a
     competing reading.
   - **X2 resolved.** The literal token `weight` inside Eq. (5)'s binomial must
     read `ω − j`: that substitution is precisely what makes the Prop 6.1.4
     assembly reproduce Table 11. No ambiguity survives for a re-derivation.
   - **X3 resolved.** Table 11's *column header* (`DFR from 6.1.4`) is right and
     its *caption* (`the formula from proposition 6.1.3`) is wrong. Only 6.1.4
     reproduces the tabulated values.
3. **Assumption A19 is now the sharp open question, not a cross-reference
   muddle.** Theorem 6.1's own text says `p_i` is Prop **6.1.3**; the only place
   SPEC gives a numeric `p_i` is Table 11, which is Prop **6.1.4**. That is the
   one cross-reference arithmetic cannot settle, and it changes the stage-3
   bound. It belongs in forward guidance, not in a ten-row anomaly table.

---

## 4. Objections, ranked by severity

---

### O1 — HIGH — `RS-S3[90, 32, 49]` is almost certainly the transcription's own extraction error, is filed as a source anomaly, is unmarked, and is worth 50.7 bits at NIST-5

**Target**: `dfr_model_transcription.md` §2 and anomaly X6; the completion-gate
row *"Every damaged formula rendering is marked EXTRACTION-DAMAGED"*, reported
`met: true` on the ground that there is *"exactly one"*; `proposed_kn_lit_entries.md`
PROP-S1 *Not verified here*, which relays `RS-S3[90, 32, 49] vs Table 3's δ=29`
as a published-text anomaly.

**The claim under attack.** The transcription records `RS-S3[90 = 255 − 165, 32 =
197 − 165, 49]` and files the mismatch with Table 3's `δ = 29` as **X6, an
observation of the source document**, i.e. a defect in the published
specification.

**Why that classification is wrong.** Two independent zero-cost checks internal
to the transcription itself both say the value is **59**, not 49:

- *Singleton / MDS.* The two sibling rows satisfy `d = n − k + 1` exactly:
  RS-S1 `46 − 16 + 1 = 31` ✓, RS-S2 `56 − 24 + 1 = 33` ✓. RS-S3 gives
  `90 − 32 + 1 = 59`, not 49. Shortened Reed–Solomon codes remain MDS, so a
  published `49` would require the specification to violate the Singleton bound
  on one row while satisfying it on the other two.
- *The transcription's own Table 3.* `δ = 29 → d = 2δ + 1 = 59`. The
  transcription records both numbers and reports only that they disagree.

A `5`→`4` digit misread from a `2.6×`-scale page clip is far more parsimonious
than a specification that contradicts the Singleton bound and its own table on
the same page. **The transcription mis-attributed its own extraction error to
the source.** The `(n_e, k_e)` values are triple-confirmed and are fine — Table 5's
`k` in bits divided by 8 gives 16/24/32 symbols, matching §3.4.2's shortening
arithmetic and Table 3 — so the error is isolated to the single digit that
matters most.

**Why it matters.** `δ_e` is the summation lower limit of Theorem 6.1. Taking
the transcribed value at face value:

```
NIST-5, p_i = 2^-11.321 from Prop 6.1.4, n_e = 90
  d = 59 -> delta_e = 29 :  DFR <= 2^-260.51   (clears the 2^-256 target)
  d = 49 -> delta_e = 24 :  DFR <= 2^-209.77   (misses it by 46 bits)
```

**50.7 bits.** A downstream re-derivation trusting the transcription would
conclude that HQC-5 misses its design DFR by 46 bits — a spectacular false alarm
on a standardized parameter set, produced entirely by one mis-read digit that the
package explicitly certifies as *not* extraction-damaged.

**Cheapest resolving control.** Zero-network: apply `d = n − k + 1` and
`δ = (d−1)/2` to all three rows of §2 — thirty seconds, decides it outright, and
I have already run it. Confirmatory: re-download the PDF at the recorded sha256
`174186cb…` (1.66 s per the access log) and render p. 18 at ≥ 4× rather than
2.6×. Either way the correction is a superseding transcription note, never an
edit to the frozen artifact.

---

### O2 — HIGH — the eprint half of *"two committed program-state facts did not reproduce"* is **false as stated**, and is now in two permanent records

**Target**: `source_access_log.yaml` `program_state_facts_that_did_not_reproduce[1]`
and attempt 9's *"SUCCESS, AND A PROGRAM-STATE FACT DID NOT REPRODUCE"*; the
`TASK-20260802-1f2e40` receipt field `two_committed_facts_did_not_reproduce`;
and snapshot commit `127b298c`'s message, *"eprint.iacr.org unchallenged,
contradicting GOAL-HAWK-001 BATCH-002"*.

**The committed fact the producer tested against was not the committed fact.**
`GOAL-HAWK-001` `BATCH-001`'s `source_access_log.yaml` `measured_facts` records
two separate items:

```
eprint_pdf_endpoint_status:  BLOCKED for every path tested - 2026/1318, 2026/890,
  2025/928, 2025/1376, 2025/215 all returned HTTP 403 with a Cloudflare challenge
  body. Five distinct report numbers, so this is an endpoint-wide condition …
eprint_html_endpoint_status: REACHABLE for every path tested.
```

`TASK-20260802-6344ed` fetched three eprint URLs — attempts 9, 12 and 13 — and
**all three are HTML endpoints** (an abstract page, a search-results page, a
second abstract page). HTML was *already recorded as reachable*. The producer
did not fetch a single eprint PDF; for S5 it says so outright (*"PDF not
fetched"*). The endpoint recorded as blocked was never tested.

**Control C1, run 20 minutes after the producer's fetches:** `GET
https://eprint.iacr.org/2026/1498.pdf` at `2026-08-02T21:50:18Z` returned
**HTTP 403, 5381 bytes of `text/html` opening `<title>Just a moment...</title>`** —
a Cloudflare challenge. **The recorded blocker reproduces exactly.** No
circumvention was attempted and none is proposed.

**Consequence.** The receipt's downstream inference — *"a source-access blocker
recorded by this program may be stale, and at least one other goal's pause
reasoning rests on it"* — is **unsupported for eprint**. `GOAL-HAWK-001`'s
outstanding obligation is the four heuristics of `iacr:2026/1318`, whose **PDF**
is the gated object; nothing in this batch touches that. A Coordinator reading
commit `127b298c` a month from now would reasonably conclude HAWK's blocker had
lifted. It has not.

**The csrc half is supported, and is stronger than reported.** Control C2
reproduces the producer's HTTP 200 on `csrc.nist.gov`. Control C3 additionally
returns **HTTP 200, 95 182 B from `https://www.nist.gov/`** — the host the
producer explicitly declined to test and correctly scoped out. So
`RQ-HQC-001.provenance`'s *"csrc.nist.gov and nist.gov are unreachable … (proxy
CONNECT 403)"* is stale for **both** hosts. That has a forward consequence worth
naming: *"no FIPS text has been read by this program"* is now a **choice**, not a
constraint, and `RQ-HQC-001`'s framing on *standardized* parameter sets makes the
eventual NIST draft a primary object this program can now reach.

**Cheapest resolving control.** One `curl` of any eprint `/NNNN.pdf` — ran it
(C1). For the correction: the ledger archive states the non-reproduction
**per endpoint class** (`csrc.nist.gov` and `www.nist.gov` reachable; eprint HTML
reachable *as already recorded*; eprint PDF still Cloudflare-gated) and drops the
cross-goal inference about HAWK.

---

### O3 — HIGH — the package leaves its own strongest fidelity control unrun and presents ten anomalies of wildly different consequence as one undifferentiated list

**Target**: `dfr_model_transcription.md` §8 and §9; the `TASK-20260802-1f2e40`
receipt's `gate_status`.

The transcription's completeness statement stops at *"every displayed formula is
image-verified"*. Image verification tests that the glyphs were copied; it does
not test that the formulas mean anything. §3 above shows the arithmetic check
costs seconds, requires no network, resolves X1, X2 and X3 outright, and would
have caught O1. It is `docs/inventor-protocol.md` §8 audit 1 and this batch is
precisely the kind of relay that audit exists for.

The consequence of not running it is the anomaly table: X2 (a typeset word) and
X8 (a glyph variant) sit beside X6 (a 50.7-bit error) and X9 (a substantive
question about how §6.2.2's bounded-distance framing joins §6.1's two-stage
decoder) with no ranking. *"None of these is a claim about HQC"* is correct
hedging and I do not object to it; the objection is that a reader cannot tell
from the artifact which two items a re-derivation must resolve first.

**Cheapest resolving control.** The recomputation in §3, reproduced in this
report and re-runnable from the transcription alone. Record its output in
`EV-HQC-9906b9`.

---

### O4 — MEDIUM-HIGH — `BATCH-001-OPENING.md` §4 half (a), *"already partly discharged"*, is an **OVERREAD**, of the same family as the one corrected in `GOAL-HAWK-001`

**Target**: `BATCH-001-OPENING.md` §4; `GOAL-HQC-001.next_action_history[0].superseded_because`
clause (1); commit `47a684f2`'s message.

**The claim.** *"The ideation instruction is already partly discharged:
`IDEA-20260801-011` exists, is bound to `question_id: RQ-HQC-001`, and is exactly
the DFR-measurement proposal this text calls 'the distinctive lane'."*

**Control C6.** `IDEA-20260801-011` is one of **21** proposals filed on
2026-08-01, and the mapping is **exactly one proposal per research question**
across the entire program roster:

```
001 RQ-CRYPTO-001   002 RQ-DREG-001    003 RQ-ECDLP-002   004 RQ-ECTD-001
005 RQ-FAEST-001    006 H-P13-001      007 RQ-SSI-001     008 RQ-MLDSA-001
009 RQ-SLHDSA-001   010 RQ-FNDSA-001   011 RQ-HQC-001     012 RQ-MLKEM-003
013 RQ-MAYO-001     014 RQ-UOV-001     015 RQ-QRUOV-001   016 RQ-SNOVA-001
017 RQ-SDITH-001    018 RQ-MQOM-001    019 RQ-HAWK-001    020 RQ-SQISIGN-001
021 RQ-ECDLP-002
```

Every record in the sweep carries the identical `novelty_screen.corpus_paths_grepped`
(`knowledge/literature`, `ledger/proposals`) and the identical `dominated_by:
null` shape. This is a **program-wide one-idea-per-question sweep**, not a
`/propose-ideas RQ-HQC-001` session. The dates check out (2026-07-29 → 2026-08-01
is three days, and unlike the HAWK case that arithmetic is right), but the
inference does not: *the existence of one topic-matching artifact produced by a
bulk sweep does not discharge, even partly, an instruction to run dedicated
ideation on a question.* A `/propose-ideas` pass produces a **set** of candidate
mechanisms with per-candidate screens and the `docs/inventor-protocol.md` §5
deliverable; one record from a roster sweep is a different object.

This is structurally the HAWK error: a Coordinator reading a `next_action`
against an artifact that is adjacent to it and concluding the instruction was
partly executed. I record it in the same terms the HAWK batch used.

**Cheapest resolving control.** The one-line loop in C6 — I ran it. Correction:
`GOAL-HQC-001.next_action_history[0]` acquires a `corrected_at_batch001_close`
note in the HAWK style, stating that clause (1) is withdrawn and that what
survives is the *substantive* point — ideation on this question has not been run
in a form that screens against the now-obtainable primary sources.

---

### O5 — MEDIUM-HIGH — §4 half (b), *"not executable as specified"*, is **OVERSTATED**; two of its three sub-charges do not survive; and it misses the one defect that is a named rule violation

**Target**: `BATCH-001-OPENING.md` §4; `next_action_history[0].superseded_because`
clause (2); commit `47a684f2`'s message; `GOAL-HQC-001.next_action`'s *"DO NOT run
/propose-ideas"*.

**(b.1) "Not executable as specified" mislocates the blocker.**
`RQ-HQC-001.constraints[0]` reads: *"No experiment may be designed until the
relevant primary sources are filed as KN-LIT entries."* That is a precondition on
the **question**, binding identically on every proposal under it, present and
future. A proposal blocked by a question-level precondition is **not yet
dispatchable**; it is not **internally defective**. *"Not executable as
specified"* asserts a flaw in the proposal's own specification, and it is now
written into an immutable ledger field and a pushed commit message.

**(b.2) The novelty-screen charge is a self-declared limitation.** The opening
says the screen *"screens for internal duplication, not against the external
literature."* The record already declares exactly that: `novelty_status:
unverified`, and `novelty_screen.conclusion` reads *"novelty unverified against
full literature."* Charging a record with a limitation it states about itself is
not a defect finding. **Withdrawn as a defect.**

**(b.3) The `KN-LIT-2141` charge is weak.** `KN-LIT-2141` is a decryption-failure
**attack**; `IDEA-20260801-011` is a **model-accuracy measurement**. Citing it
would be good practice, not a requirement. **Withdrawn as a defect.**

**What does survive from (b).** The proposal lists `knowledge/literature` in
`corpus_paths_grepped` and then reports **no result from that path** — its single
`grep_results` entry is about proposals only. A screened path with no recorded
finding is a real gap, and it is the honest form of the opening's charge.

**What §4 missed, and it is the one item that is a named rule violation.**
`IDEA-20260801-011` carries **`dominated_by: null`** with no recorded frontier
check. `docs/inventor-protocol.md` §5 is explicit that `null` is admissible *only
after checking every row of the frontier across time, memory and data/queries*,
and that *"`null` without that check is a fabrication under `AGENTS.md` rule 5"*;
the valid complete answer for a no-attack proposal is
`dominated_by: "n/a (no result claimed)"`. The record's `sota_delta` shows the
intent was "n/a", so the fix is one string — but the fix is owed. **It is
systemic: 21 of 21 records in the 2026-08-01 sweep carry the same bare `null`.**
A Coordinator conducting a pre-dispatch audit of this proposal found two arguable
defects and missed the one the protocol names.

**(b.4) The claim is written permanently on a temporary condition.** Half (b)'s
blocking force is spent the moment the ledger archive files PROP-S1 and PROP-S2.
`GOAL-HQC-001.next_action` nonetheless carries a bare, undated prohibition —
*"DO NOT run /propose-ideas: … `IDEA-20260801-011` already exists and already
lacks the model it would be tested against"* — whose stated justification expires
in one commit. The supersession **mechanism** was correct and I do not fault it
(prior text preserved, `superseded_because` recorded, disposition explicitly
deferred to this challenge, which is the least-overreaching form available). The
**wording** is what overreaches.

Note also that the constraint requires sources to be **filed**, not merely
obtained. Nothing is filed: `proposed_kn_lit_entries.md` is a proposal and
deliberately allocates no identifiers. So the precondition is not yet discharged
even after this batch's success.

**Cheapest resolving control.** Free: the ledger archive (i) restates the finding
as *"blocked by `RQ-HQC-001.constraints[0]`, not defective"*, (ii) withdraws
(b.2) and (b.3), (iii) records the `dominated_by` violation as the actual defect
with a correction record covering the sweep, and (iv) writes the
`/propose-ideas` prohibition **with an explicit lapse condition**: *this
prohibition lapses when the SPEC and RMRS `KN-LIT` entries are committed.*

---

### O6 — MEDIUM — `ISD-FC-2026`'s mandatory pre-use audit **F4 is under-determined by the convention's own rules**, so it cannot do the job assigned to it; and reason 2 for cube-root is circular as a model-selection argument

**Target**: `isd_costing_convention.md` §2.2 U2, §3(b) reason 2, §3(g), §5 F4;
`convention_provenance.yaml` `CHARGE-B-WHY-CUBE-ROOT`, `HOOK-F4-REPRODUCTION-AUDIT`.

**The convention's cited chain is real — I verified every link.** `KN-LIT-094` is
`confidence: established`, `citation_verified: read`, and states BSGS full cost
`n^{2/3+o(1)}`. `KN-TECH-035` relays it. The `GOAL-SSI-001` `TASK-20260728-007`
F1 objection genuinely says what the convention says it says, including the
verbatim phrase *"exactly as KN-LIT-094 and KN-TECH-035 report"*. **No citation
defect found.** The 47/24/23/8/1 provenance counts recompute exactly under
`yaml.safe_load`.

**What the convention omits from that chain.** `TASK-20260728-007` recorded its
F1 resolution as *"CLOSED IN WIENER'S FAVOUR by F1, **pending RC5
confirmation**"*, RC5 being *"Read `KN-LIT-094` section 3's BSGS derivation and
record whether `n^{2/3}` is stated at `m = √n` or as an optimum over `m`."*
`GOAL-SSI-001` `BATCH-003` then attempted RC5 as debt item D4 and recorded
**`outcome: FAILED_REMAINS_OPEN`** — four routes tried, *"NOTHING WAS OBTAINED
FROM WIENER'S OWN TEXT IN THIS SESSION."* `ISD-FC-2026` relays the "closed"
half and not the "pending" half.

**Control C5 discharges RC5 with one curl flag.** The `BATCH-003` failure mode
was a `Content-Length`/`Transfer-Encoding` parse error on `cr.yp.to`. Adding
`--http1.1 -H 'Accept-Encoding: identity'` returns the paper: 234 591 B, 21 pp.,
sha256 `9723d47ae05d39d14dfc3ad3789873d9139057291660d3bf1ae48931e8c50263`.
Wiener §4.1 reads, verbatim:

> "By Corollary 2, the full cost of the algorithm is `F = Θ(Trm^{1/3}) =
> Θ((sa + n/a)(n/a)^{1/3}(log n)^{4/3})` **when `p = Θ(m^{2/3}/r)`**. This cost
> is a **minimum** of `F = Θ(s^{2/3}n^{2/3}(log n)^{4/3})` **when
> `a = Θ((n/s)^{1/2})`** and `p = Θ((sn/log n)^{1/3}t)`."

So RC5's answer is: **both.** `n^{2/3}` is stated as a *minimum over the
table-size parameter `a`*, and that minimum sits *at* the square-root balance —
which confirms `TASK-20260728-007` F1 and the convention's target figure.

**But it exposes the defect.** Wiener's form is `F = Θ(T·r·m^{1/3})` **at a
specific processor count `p = Θ(m^{2/3}/r)`**, with `r` the memory-access rate.
`ISD-FC-2026` U2 writes `FC = H·T_wall`, `H = N·h_proc + M`, names no `r`, and
§3(g) requires only that a figure *name* its `(N, M)` point. U7 re-optimises
*internal algorithm parameters* — *"split points, list sizes, the number of
representations, the `p` and `l` style parameters"* — and **`N` is not among
them**. Therefore:

- two conforming instantiations at different `N` return different `FC`, so
  falsification hook **F3 (under-determination) fires before first use** — and on
  a clause the convention did not name in advance (it names U4b);
- **F4 will return `2/3` only if the auditor happens to choose Wiener's `p`.**
  The audit the convention makes mandatory before any code-based number is
  produced is not determined by the convention's own rules.

**And reason 2 is circular as a model-selection argument.** `n^{2/3}` *is* the
three-dimensional-wiring answer. A `Θ(M^{1/2})` or `Θ(log M)` model cannot
reproduce it by construction, so "cube-root reproduces `n^{2/3}` and the
alternatives do not" is a tautology, not evidence. §3(b) words it accurately
(*"the strongest consistency check available"*); §5 F4 upgrades it to
*"falsifies its **correctness**"*, which it does not. What F4 genuinely tests —
and this is real value, demonstrated by `TASK-20260728-007` F1 — is **U5
symmetry**. It is a strong U5 test and not a U4 test.

**Cheapest resolving controls.** (a) Free: add `N` to U7's optimisation list, or
pin it at the bandwidth-saturating point Wiener uses, and state whether `r`
belongs in U2. (b) Free: relabel F4 as a **U5 symmetry + transcription** audit
and note that it cannot discriminate the four access models. (c) The only stated
hook that *does* discriminate them is **F2 (ranking invariance)** — run it before
adoption, not after. (d) One executor task, zero compute: file `KN-LIT-094`'s §4.1
form from the route in C5, closing `GOAL-SSI-001`'s RC5 as a side effect.

---

### O7 — MEDIUM — the convention's self-nominated "most abusable clause" is **not** the most abusable, and the item with the largest unguarded leverage is `U3` + §9

**Target**: `isd_costing_convention.md` §3(b) U4b, §2.2 U1/U3, §9;
`convention_provenance.yaml` `red_team_entry_points[0]`.

The card asks me to test the producer's self-assessment rather than accept it,
on the ground that an agent naming one weakness may be diverting attention from
another. I tested it.

**U4b is guarded.** *"An access pattern claimed sequential must be exhibited (the
concrete addressing order, not a description of it), and if it cannot be
exhibited the accesses are charged as random. Where a data structure's access
order is derived from data … it is random by default."* That is a checkable
obligation with a default that runs **against** the party invoking it, and it
excludes by name the exact structures where the abuse would live
(hash-keyed lookups, nearest-neighbour bucket probes). It is the best-guarded
uncited clause in the document. The self-assessment is **wrong**, and honestly so
rather than as misdirection.

**The largest unguarded leverage is `U3` composed with §9.** U3 says *"no internal
ranking, margin statement, or 'beats the baseline' claim is made on `G`"*, and §9
says a figure on a different basis *"is placed beside this program's `G` leg,
never beside its `FC` leg."* Every published HQC/SDitH ISD estimate is on B2/B3.
Composing the two rules: **the program's decision basis can never be compared
against any published baseline.** But `RQ-HQC-001.constraints[1]` and
`RQ-SDITH-001.constraints[1]` both require *"the best-known baseline at identical
parameters"*. The convention therefore silently obliges the program to
**re-derive every baseline itself** under an accounting nobody else uses — a cost
it creates and never charges to itself. Worse, it reconstructs, one level up, the
exact asymmetry U5 exists to forbid: a carefully-optimised `FC` for the program's
own candidate set against a hastily re-costed `FC` for the baseline. That is
`TASK-20260728-007` F1's failure mode migrating from *within* an algorithm to
*between* the two sides of a comparison, where no audit field looks for it.

**`U1` also outranks U4b.** It is uncited, the provenance file says so in capitals
(*"THE CHOICE OF A BIT/GATE UNIT OVER A WORD OR VECTOR UNIT IS THIS AGENT'S"*),
and it propagates into every figure. It is **not** neutral across the ISD family:
charging `R·L` gate-ops for an elimination pass penalises Gaussian-elimination-heavy
variants relative to syndrome-comparison-heavy ones, while U4 penalises the
list-heavy variants. That the two pull in **opposite** directions across the
family is itself evidence the set was not tuned toward one answer.

**On calibration toward a desired outcome: I found none, and I looked for it.**
The overall direction runs *against* this goal's interest — charging memory
raises attacker cost, which makes it harder, not easier, for `GOAL-HQC-001` to
claim ISD is cheaper than the specification says. The producer's
`calibration_self_audit` names U7 and `CHARGE-E-AMORTIZATION-PERMITTED` as items
pointing against the convention's own convenience, and both check out on reading.
`HOOK-F2` can retire the whole convention for being decision-irrelevant. **This
duty found no calibration defect and I say so plainly.**

**Cheapest resolving control.** One added rule, zero compute: *both sides of any
`FC` comparison are produced in the same instantiation pass and each carries its
own §6 reporting block, or the comparison is declared `G`-only and labelled as
such.*

---

### O8 — MEDIUM — the `TASK-20260802-1f2e40` receipt reports a precondition **discharged** on a paraphrase weaker than the constraint

**Target**: `TASK-20260802-1f2e40/snapshot-receipt.json`
`producer_self_reports_forwarded_to_review.gate_status`.

The receipt reads *"`RQ-HQC-001`'s precondition — that primary sources be
**obtained** before any experiment is designed — is reported DISCHARGED for the
specification lane."* The constraint says *"…until the relevant primary sources
are **filed as KN-LIT entries**."* Obtaining is not filing; nothing is filed, and
`proposed_kn_lit_entries.md` deliberately allocates no identifiers.

Credit where due: the producer did **not** make this claim. Its own log confines
itself to `pause_conditions[1]: NOT TRIGGERED`, which is accurate and is a
different proposition. The paraphrase is Coordinator-introduced, and it is hedged
(*"This is the producer's report"*) and scoped (*"for the specification lane"*) —
which is why this is MEDIUM and not HIGH.

**Cheapest resolving control.** Free: the ledger archive quotes the constraint in
its own words and records discharge only after the `KN-LIT` files are committed —
which the same archive can do in the same commit.

---

### O9 — MEDIUM — the corpus-integrity finding is real, is **two orders of magnitude larger than reported**, is mis-framed as convergent evidence, and is over-stated in one direction while under-stated in another

**Target**: `TASK-20260802-1f2e40` receipt `corpus_integrity_finding`, including
*"Two producers with disjoint scopes converging on one corpus-integrity defect is
the most consequential thing in this batch"*; `isd_costing_convention.md` §7.1
(*"`citation_verified: read` overstates these"*); commit `127b298c`'s
*"INDEPENDENTLY MATCHES"*.

**Apply the null-object control the inventor protocol requires.** The reported
signal is *two disjoint-scope producers independently arriving at the same
defect*. The parameter that should destroy that signal is corpus coverage: if the
property is rare, two hits is striking; if it is ubiquitous, two hits is the
expected value and carries no information. **Control C7:**

```
grep -rl "downloads/" knowledge/literature/ | wc -l          -> 7421   (of 7666 KN-LIT files)
… restricted to citation_verified: read                     -> 7420   (of 7457 read-tier records)
git ls-files downloads                                      -> 0 files; not in .gitignore
```

**99.5 % of the read-tier corpus.** Two sessions grepping the same corpus both
seeing a property of 7 421 records is a **controlled null**, not convergent
evidence. Under `docs/inventor-protocol.md` §3 this is the canonical artifact
tell — a quantity that does not shrink when the parameter meant to shrink it is
applied. The framing dresses a one-command fact as a two-witness discovery, and
neither producer nor the Coordinator ran the count.

**Over-stated in one direction.** `knowledge/SEEDING.md` defines `read` as
*"you fetched the actual paper (PDF/abstract) and the claims in this entry reflect
its real content"* — an act performed at entry creation, **not** a retained
artifact. So an absent `downloads/` does **not** by itself falsify `read`.
`isd_costing_convention.md` §7.1's *"`citation_verified: read` overstates these"*
goes beyond what the absent directory supports. `TASK-20260802-6344ed`'s wording
is careful and correct by contrast (*"the artifact backing the `read` level is not
present for a reviewer … Whether `read` survives is a Coordinator/Validator
call"*).

**Under-stated in another.** The defect that *is* supported is different and
larger: `read` is **un-re-verifiable by any later reviewer for 7 420 records**,
and for entries with `year: null`, `venue: null` and all-null identifiers the
label is independently questionable, because reading a paper yields its year and
venue. That is an auditability defect of corpus-wide scope, and it bears directly
on every novelty screen this program will ever run.

**And it has no owner.** A finding of this size sitting in a snapshot receipt's
free-text field, with no successor task and no revisit condition, is what
`CLAUDE.md` rule 9 forbids.

**Cheapest resolving control.** The two commands above — ran them. Then: a
`KN-OPEN` entry or a named successor task carrying the count, the SEEDING.md
distinction, and a revisit condition. Not a per-record repair.

---

### O10 — LOW-MEDIUM — the two observations that most matter for this goal are filed as anomalies and carried forward by nothing

**Target**: `dfr_model_transcription.md` A17, X9; the absence of either from any
forward-looking field in the package.

Two items in the transcription are qualitatively different from the rest:

- **A17.** *"THE `n_e` INNER-DECODER OUTCOMES ARE INDEPENDENT AND IDENTICALLY
  DISTRIBUTED WITH FAILURE PROBABILITY `p_i`. … It is implicit in the formula;
  neither SPEC §6.1.3 nor RMRS Theorem 4.3 states it in prose"*, and §7.1 adds
  that *"RMRS gives no proof of Theorem 4.3."* This is a **second, independent
  use of an independence assumption**, stacked on A5's coordinate-level one, and
  it is the assumption that turns Theorem 6.1 into a binomial tail. It is
  unstated, unproved in either source, and — unlike A5 — it has no accompanying
  simulation in either text.
- **X9.** §6.2.2 states the failure event as `ω(e′) > ∆` *"if and only if"* with
  `∆ = ⌊(d−1)/2⌋`, a bounded-distance quantity, while §6.1 computes the failure
  probability of the **two-stage ML-then-algebraic** decoder of §3.4.1. Those are
  different events. This is the textual join `GOAL-HQC-001` is framed on.

Both are filed in the same table as a typeset word (X2) and a glyph variant (X8),
under *"no assessment attached"* — correct hedging, but no artifact carries either
forward. After the ledger archive, the batch's most interesting output would exist
only inside an anomaly table nobody is directed to re-read.

**Cheapest resolving control.** Free: `DEC-20260802-344883` or a `KN-OPEN` names
A17 and X9 explicitly as the two items a re-derivation must resolve first. And
A17 supplies this goal's cheapest discriminating experiment, with its null object
already determined: **measure whether inner-block failures are positively
correlated at reduced `n_e`, against a null object of `n_e` i.i.d. BSC draws at
matched `p⋆`.** If the two agree, A17 is a controlled null and the model's
stage-3 step is sound on the tested range; if the real decoder's block failures
cluster, Theorem 6.1's binomial tail is the wrong tail — in a direction the
package must not prejudge. That is the strongest lead this batch produced and it
produced it without noticing.

---

### O11 — LOW — *"paywalled, no open version located"* is an **under-tried** route by the access log's own logic, though the conclusion is probably right

**Target**: `source_access_log.yaml` `routes_not_reached[0]` and
`sources_sought_outcomes` S3.

Declared route rank 9 (WebSearch/WebFetch) was never reached, with the stated
reason: *"Every route attempted above succeeded over curl … There was no request
for which a second transport was needed."* That reason is **factually inapplicable
to S3**, which did *not* succeed at full text. A declared route exists precisely
for the target that fails; leaving it unreached because the *other* targets
succeeded is a non-sequitur, and it is the one place in an otherwise exemplary
log where "blocked" is doing work that "untried" should be doing.

**I ran the cheapest untried route (C4)** — the Semantic Scholar Graph API on the
DOI, HTTP 200 — and it **corroborates the producer**: bibliography confirmed
independently of both DBLP and Springer, `isOpenAccess: false`,
`openAccessPdf.status: "CLOSED"`. So the conclusion stands; only the exhaustion
claim does not.

**Cheapest remaining untried route.** The authors' institutional repository. The
producer tried HAL, correctly, because the *HQC* authors are French — but Guo and
Johansson are at Lund. The Swedish open repositories (Lund research portal,
DiVA) are the exact analogue for S3 and were never tried. One GET.

---

## 5. The Coordinator's process decisions

### P1 — the mid-flight snapshot split: **LEGITIMATE**, not a post-hoc rationalisation

I looked specifically for the tidy-tree rationalisation the card warns about and
did not find it.

- **The cited authority says what the amendment says it says.**
  `docs/task-lifecycle.md` §7a: *"After **a producer** reaches a terminal
  outcome, the Coordinator runs its isolated snapshot archive task before any
  dependent review."* Singular. It binds the freeze to a producer going terminal,
  not to the slowest sibling. The amendment's reading is the plain one.
- **The stated operative fact is checkable and true.** `TASK-20260802-0100a5`
  reached terminal while `TASK-20260802-6344ed` was still running; under the
  single-snapshot design its artifacts would have sat in a mutable tree for the
  remainder of the sibling's 3600 s budget, which is exactly the exposure a
  snapshot exists to eliminate.
- **No path is double-claimed.** `a3dc0a` declares three paths and commit
  `e6f20223` changes exactly three files; `1f2e40` declares five and commit
  `127b298c` changes exactly five. Disjoint.
- **Control C9 is decisive.** `tools/research_dispatch.py` renders the amended
  queue with **all ten gates passing**, including
  `completed_archive_commits_verified`. Each receipt is committed inside the
  commit it describes with `commit_sha: null`. The split therefore does **not**
  reproduce the `GOAL-HAWK-001` `BATCH-001` `known_defect` — it forecloses it.
- **One nit, disclosed for precision.** `not_a_scope_change` says only *"the
  reviews' `depends_on` edges"* changed; both reviewers' `read_scope` was also
  extended with the `TASK-20260802-1f2e40` archive path. Both reviews were still
  `queued`, so no dispatched scope moved and nothing improper occurred. State it
  precisely at the ledger archive.

**Verdict on P1: a design correction found by running the design, correctly
recorded on both tasks, operationally verified. No objection.**

### P2 — the census in the opening rather than in the executor's budget: the anchoring hypothesis is **not supported for the search** and **weakly supported for the characterisation**

*Against anchoring.* The executor did not accept the handed-down conclusion. It
re-ran the census independently at commit `47a684f2` — eight documented grep
commands over 7 666 `KN-LIT` files — reproduced the six records exactly, and then
**widened twice**: §2.1 surfaced a 16-record decryption-failure cluster the
census's `"hqc\|hamming quasi"` pattern structurally cannot reach (including
`KN-TECH-048`, whose rule *"a revised failure rate is not an attack"* is directly
binding on this goal's first lane), and the sibling task surfaced ~13 further ISD
records. Neither producer stopped at six. **The census did not narrow the
search.**

*For a residual effect.* Both producers softened their finding against the
opening, in the same way and unprompted: §2.1 declares *"This is recorded as an
observation about grep coverage, **not as a defect finding against the
opening**"*, and the convention's §7 opens *"This does not contradict
`BATCH-001-OPENING.md` §3."* Deference in **characterisation**, not in search.
And the batch's largest actual finding (O9) was routed into a snapshot receipt's
free-text field rather than owned as a batch finding — consistent with producers
who treat the opening's frame as the thing they are permitted to annotate rather
than replace.

*Cost in this batch: effectively zero.* The residual effect changed labels, not
work. **Cheapest structural fix for future batches:** have the opening state its
census **pattern** and its known blind spot, and explicitly invite the producer to
report where the pattern fails — which is what happened here anyway, by the
producers' own initiative rather than by design.

---

## 6. The five named duties, answered including where I found nothing

**Duty 1 — challenge the §4 claim.** Both halves challenged. Half (a) is an
**overread** (O4): `IDEA-20260801-011` is one of a 21-record, one-per-question
bulk sweep, not the output of `/propose-ideas RQ-HQC-001`. Half (b) is
**overstated** (O5): the blocker is a question-level precondition, not an
internal defect; two of its three sub-charges are withdrawn; and §4 missed the
`dominated_by: null` violation, which is the one defect a named rule covers.
Half (b) becomes moot **at the ledger archive that files the entries, not
before** — the constraint requires filing, and nothing is filed. The supersession
**mechanism** did not overreach; the **wording** did, in an immutable field and a
pushed commit message, and it needs a `corrected_at_batch001_close` note in the
HAWK style. I did **not** assume this claim was wrong because HAWK's was; I
checked the dates (correct here, unlike HAWK) and the records first.

**Duty 2 — challenge the source-exhaustion verdict.** The obtained artifact **is**
the primary specification, not a secondary restatement: `pqc-hqc.org` is the HQC
team's own publication point, `resources.html` names exactly one specification
document, and the derivation source (RMRS) was identified from **SPEC's own
reference [4]** rather than recalled — the log records that distinction
explicitly and it is the difference that matters. The transcription **is**
sufficient to recompute a predicted failure rate: I did it end-to-end and hit the
specification's own numbers at nine points (§3). The single
`[EXTRACTION-DAMAGED]` marking is **not** hiding a load-bearing piece of the DFR
chain — but it is Eq. (13), the IND-CCA2 advantage bound, which is the
load-bearing object of `RQ-HQC-001.scope.targets[1]` (*"sensitivity of the
IND-CCA argument to a DFR that is wrong by k orders of magnitude"*). The package
does not flag that asymmetry: complete for lane 1, damaged exactly at lane 2.
*Cheapest control: render SPEC p. 44 — one more page through the same toolchain
the producer already used.* The genuinely load-bearing gap is elsewhere and
unmarked: **O1**. On Guo–Johansson: **under-tried by the log's own logic** (O11),
though C4 corroborates the conclusion. On the stale-blocker question: the eprint
half is **not stale** and the claim that it is, is false (**O2**); the NIST half
**is** stale and is more stale than reported — `www.nist.gov` also returns 200
(C3), so *"no FIPS text has been read"* is now a choice.

**Duty 3 — challenge the convention's neutrality.** **No calibration toward a
desired outcome found**, and the net direction runs against this goal's own
interest (O7). The producer's self-nominated most-abusable clause is **wrong**:
U4b is the best-guarded uncited clause; the largest unguarded leverage is U3+§9,
with U1 second (O7). The cube-root justification's citations are **real and
verified** — including the exact quoted phrase in `TASK-20260728-007` — but its
"reproduction check" is **circular as a model-selection argument** and its
mandatory F4 audit is **under-determined by the convention's own rules** (O6);
I discharged the `GOAL-SSI-001` RC5 control that had been recorded as failed, and
Wiener's own text both confirms the target figure and exposes the gap. On
*"would a different defensible choice change the ranking of ISD variants?"* — the
convention already specifies the correct control (**F2**, ranking invariance
across all four access models) and it must be **run before adoption**, not merely
stated. The 47/24/23/8/1 provenance counts **recompute exactly**; no item with an
empty `sources` list is labelled as cited.

**Duty 4 — premature-closure check.** The batch closes the HQC line in **neither
direction**, and I found no instance of the subtler failure. Transcription is
never treated as validation: §0 disclaims assessment, §9 claims only obtainment
and transcription, PROP-S1 records *"**Forecloses**: nothing"*, and both snapshot
commit messages say *"TRANSCRIBED, NOT TESTED"* in terms a later reader cannot
misread. In the other direction, PROP-S3-UPGRADE's `2²⁴⁶`/`2²⁵⁴` figures and
PROP-S5's claims are relayed at the sources' own hedging level with explicit
scope notes refusing to relate `hqc-256-1` to the 2025 parameter sets. **The one
place a gate is treated as discharged is procedural, not evidentiary, and is
O8.** The real premature-closure risk in this package is the *opposite* one: the
batch under-claims its own strongest lead and files it as an anomaly (O10).

**Duty 5 — scope-inflation check.** I checked all four producer artifacts, both
receipts, and both snapshot commit messages. **No claim above the toy tier, and
no convention-level or transcription-level statement phrased as a statement about
HQC's standardized parameter sets.** Both commits state *"Claim tier stays toy"*
and *"no security claim about HQC or SDitH is made or implied"*; commit `e6f2`'s
*"23 of its 47 items are the producing agent's own choice"* is mechanically
correct. Control C10 confirms the batch added **zero** validation errors — 183 at
`HEAD`, identical to the opening §8 pre-batch count, none naming an HQC record —
so the opening §8 obligation (*"not to add to them"*) is met. The convention
contains no HQC or SDitH parameter number. **This duty found only one item, O8,
and it is a paraphrase of a procedural precondition rather than a claim about
HQC.** Everything else here is clean and I say so plainly.

---

## 7. One concrete next action

**Before `TASK-20260802-a157ad` writes anything, re-run the §3 recomputation from
the transcription and record its output in `EV-HQC-9906b9`.**

It costs seconds, needs no network and no new source, and it simultaneously:
attaches an `docs/inventor-protocol.md` §8 audit-1 *exact baseline reproduction*
to the batch's headline artifact; converts the transcription from an unverified
relay into one with nine independent numeric agreements behind it; resolves X1,
X2 and X3; decides **O1** outright; and leaves A19, A17 and X9 standing as the
sharp open questions this goal should carry into `BATCH-002`.

Then, in the same ledger archive, carry **O1, O2, O4, O5 and O8** as corrections.

---

## 8. Scope limits of this report

- I am an independent **session**, not an independent **model**. Nothing here is
  admissible toward an `AGENTS.md` rule 13 closure quorum.
- I reviewed only Coordinator-committed snapshot state: commits `e6f20223`
  (3 paths) and `127b298c` (5 paths), plus the ledger and queue records named in
  my read scope. I did not review working-tree-only artifacts as durable
  evidence.
- My §3 recomputation is a **transcription-fidelity control**. It asserts nothing
  about HQC's security in either direction, tests no assumption in A1–A23,
  measures nothing, runs no decoding trial, and carries `claim_tier:
  not_applicable` and `certificate.kind: none`. The margins it reports are the
  specification's own claim recomputed.
- Controls C1–C5 are network observations from **one session, one time window
  (2026-08-02T21:50Z), one URL per host**. They do not establish that any host
  will behave the same way later, and they are not mathematical evidence about
  anything (`AGENTS.md` rule 5).
- I did not verify PROP-S1's 23-author list, the byte-identity of either
  downloaded PDF, or any sha256 in the access log against a re-download. Those
  are the validator's receipt-integrity and provenance-level duties
  (`TASK-20260802-b8d69f`), and I deliberately did not duplicate them.
- I made **no status transition**. Every disposition above is a recommendation to
  the Coordinator, who alone decides at the ledger archive.
- Objections I could not support were **withdrawn, not softened**: the
  novelty-screen charge and the `KN-LIT-2141`-citation charge in §4 half (b) are
  withdrawn as defects (O5.2, O5.3); the snapshot split is admitted as legitimate
  with no objection (P1); the census-anchoring hypothesis is **not** supported for
  the search (P2); and duties 3 and 5 each found one structural issue and no
  calibration or scope-inflation defect at all.

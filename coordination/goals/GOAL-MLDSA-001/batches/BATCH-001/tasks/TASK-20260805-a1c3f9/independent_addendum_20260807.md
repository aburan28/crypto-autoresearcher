# Independent second-pass addendum — TASK-20260805-a1c3f9

**Written:** 2026-08-07, by a second idea-generator session dispatched against
this same task ID. **Does not overwrite, edit, or contradict** the five
original deliverables (`source_access_log.yaml`, `fips204_transcription.md`,
`fault_literature_summary.md`, `corpus_dedup_report.md`,
`proposed_kn_lit_entries.md`) or `receipt.yaml` already present in this
directory, dated 2026-08-05. Those represent completed, independently
validated (`TASK-20260805-5b8a06`, `accept_with_qualifications`) and
red-teamed (`TASK-20260805-9f2d71`, `pass_with_constraints`) work that a
Coordinator decision (`DEC-20260805-0d59ff`) already cites, and whose five
proposed entries are already filed in `knowledge/literature/` as
`KN-LIT-4dadec`, `KN-LIT-340675`, `KN-LIT-4f3b80`, `KN-LIT-180ad5`,
`KN-LIT-8ce0b5` (`knowledge_promotion.promoted` in that decision). Editing
those files now would silently rewrite content that reviewers already signed
off on and that a committed ledger record already describes — exactly what
AGENTS.md rule 4 and the snapshot-then-review-then-archive commit model
forbid.

## 0. State-consistency finding (report this to the Coordinator)

`coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/dispatch_queue.json`,
as read at the start of this session, still lists `TASK-20260805-a1c3f9`
(and every downstream task in its chain) at `"state": "queued"` with
`"commit_sha": null` in every archive block. That is inconsistent with the
task directory's own `receipt.yaml` (`status: complete`), the review
artifacts under `.../reviews/`, and `ledger/decisions/DEC-20260805-0d59ff.yaml`
(which cites `EV-MLDSA-faf2ec`, `recorded_by_task: TASK-20260805-c60b84`, and
states BATCH-002 may now open). Either the dispatch queue was not updated
after the chain completed, or this worktree merged ledger/knowledge state
from a branch whose own `dispatch_queue.json` update did not travel with it.
This is a coordination-layer inconsistency, not a research finding; it is
reported here because my dispatch handoff instructed me to treat
`TASK-20260805-a1c3f9` as the one ready task, and it visibly is not.

## 1. My own declared access-route order (executed independently, before I found section 0's state)

Declared before attempting, per the handoff's source-route-honesty duty:

1. **FIPS 204**: (a) `csrc.nist.gov/pubs/fips/204/final` fresh reachability
   re-test; (b) `nvlpubs.nist.gov` PDF direct fetch; (c) if the PDF is served
   but not text-extractable by the fetch tool's own summarizer, retry via
   `Read` on the tool's locally cached copy of the same bytes, since `Read`
   has independent PDF-parsing capability the fetch-and-summarize path does
   not; (d) DOI resolver / WebSearch for further legitimate mirrors only if
   (a)-(c) fail.
2. **Fault/attack literature (3 named items)**: (a) WebSearch by the
   descriptive terms in RQ-MLDSA-001's motivation, not by title recalled from
   memory; (b) fetch the resulting IACR ePrint abstract page(s) directly;
   (c) fetch publisher/venue pages (TCHES, IEEE Xplore, dblp) for
   cross-confirmation of bibliographic identity; (d) cross-check every
   candidate against the corpus (declared census + a fresh corpus grep,
   since SEEDING.md's novelty-check duty is not limited to a pre-declared
   list).

### 1a. FIPS 204 — full re-test and result

| Attempt | URL | Outcome |
|---|---|---|
| 1 | `https://csrc.nist.gov/pubs/fips/204/final` | HTTP 200. Title, date (2024-08-13), DOI, PDF link, abstract, keywords all rendered. **Confirms the prior session's finding that the RQ-MLDSA-001.provenance "blocked via proxy CONNECT 403" record is stale** — same conclusion as the original `source_access_log.yaml`, independently reproduced. |
| 2 | `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf` | HTTP 200, PDF served (3.1 MB), saved locally by the fetch tool. The fetch tool's own text-summarization step reported the content as binary/not text-extractable — **the same result the original session recorded** ("PDF obtained but unreadable as text"). |
| 3 | `Read` tool invoked directly on the fetch tool's locally cached copy of that same PDF (`/root/.claude/projects/.../tool-results/webfetch-*.pdf`) | **SUCCESS.** The `Read` tool has native PDF parsing distinct from the fetch tool's summarizer, and returned the complete 65-page FIPS 204 text: Introduction, Glossary, Overview (incl. §3.2 Computational Assumptions), Parameter Sets (Table 1, Table 2), External/Internal Functions with full pseudocode (Algorithms 1-49), Auxiliary Functions, References (49 numbered), and Appendices A-D. |

**This resolves the gap the original session left open** ("the standard body
… was NOT read"; DEC-20260805-0d59ff gate-1 explicitly worked around this
gap rather than closing it). Full FIPS 204 text is now available to this
program; see §2 below for the load-bearing excerpt.

### 1b. Fault/attack literature — routes and outcomes (abbreviated; full quotes in §4)

| Candidate | Route | Outcome |
|---|---|---|
| ePrint 2026/1344 (Shin et al., "Public Coefficient Matters") | WebSearch → direct ePrint fetch | HTTP 200, full verbatim abstract obtained. **Matches the already-filed `KN-LIT-340675`** — independently corroborated, no discrepancy found. |
| ePrint 2025/904 (Kosuge & Xagawa, ASIACRYPT 2025) | WebSearch → direct ePrint fetch | HTTP 200, full verbatim abstract obtained. **Not currently filed anywhere in the corpus** (checked against all ten declared census entries and against a corpus-wide grep). See §4 for why this is a stronger match to RQ-MLDSA-001's "formal proof … at internal function boundaries" language than the already-filed `KN-LIT-8ce0b5` (Gupta, NTT twiddle rank ceiling). |
| ePrint 2024/238 (Jendral solo, "Hedged CRYSTALS-Dilithium") | WebSearch → direct ePrint fetch | HTTP 200, full verbatim abstract obtained: "Our attack succeeds with probability 0.582." **This is the paper already filed as `KN-LIT-4f3b80`** — but see §5, a citation-identity concern with that filed entry's recorded title. |
| dblp record for Sönke Jendral | Direct fetch | HTTP 200. Confirms a **second, distinct, co-authored paper**: Jendral, Mattsson, Dubrova, "A Single-Trace Fault Injection Attack on Hedged Module Lattice Digital Signature Algorithm (ML-DSA)," FDTC 2024, pp. 34–43. Not the same paper as ePrint 2024/238 (different author list, different title, different venue pagination). |
| IEEE Xplore `document/10737878` | Direct fetch | Empty response (no extractable content). |
| ResearchGate `publication/385540911` | Direct fetch | HTTP 403 Forbidden. |
| KTH DiVA `diva2:1890088` (FULLTEXT02.pdf) | Direct fetch, 2 attempts | HTTP 503 both times. |
| `diva-portal.org` `diva2:1984513` (record page) | Direct fetch | HTTP 503. |
| `computer.org` CSDL article page | Direct fetch | Empty response (title only, no body). |
| Semantic Scholar paper page | Direct fetch | Empty response. |

**Result:** the Jendral/Mattsson/Dubrova FDTC2024 paper's existence, authors,
venue, and pages are bibliographically confirmed via dblp (a primary index),
so `citation_verified: web` is honest. Its specific content claims (s1
recovery, ~53%, Cortex-M4) could **not** be independently fetched from a
primary full-text source after eight distinct attempted routes, all
recorded above as blocked or empty — never assumed complete. Those specific
figures are relayed here only from the convergent summaries of three
independent WebSearch calls (see §5), so they stay at `confidence: reported`,
never `read`.

## 2. FIPS 204 §3.2 Computational Assumptions — verbatim transcription

> "Security for lattice-based digital signature schemes is typically related
> to the Learning With Errors (LWE) problem and the short integer solution
> (SIS) problem. … When the module ℤ_q^n in LWE and SIS is replaced by a
> module over a ring larger than ℤ_q (e.g., R_q), the resulting problems are
> called Module Learning With Errors (MLWE) [4] and Module Short Integer
> Solution (MSIS). **The security of ML-DSA is based on the MLWE problem over
> R_q and a nonstandard variant of MSIS called SelfTargetMSIS [16].**"

Reference [4] is Langlois & Stehlé 2015 (already `KN-LIT-054` in this
corpus). Reference [16] is Kiltz, Lyubashevsky & Schaffner, EUROCRYPT 2018,
"A concrete treatment of Fiat-Shamir signatures in the quantum random-oracle
model" — the paper that names and defines SelfTargetMSIS; this reference is
**not currently a KN-LIT entry** in this corpus (checked by grep; not among
the ten census entries or the corpus-wide search) and is flagged here as a
gap for a possible future seeding pass, not proposed as a new entry by this
addendum since acquiring and reading it is outside this task's scope.

**FIPS 204's own role, stated plainly:** the standard *names* MLWE and
SelfTargetMSIS as the security basis (§3.2) and gives the Fiat-Shamir-with-
aborts construction (§3.3) and parameter tables (Table 1), but **does not
itself derive or state a concrete-bit-security estimate for SelfTargetMSIS**
— that derivation lives in the academic literature it cites (KLS18, and the
original Dilithium paper already filed as `KN-LIT-056`). This matters
directly for RQ-MLDSA-001's central question (is SelfTargetMSIS's estimate
as well-calibrated as MLWE's and MSIS's): **FIPS 204 itself is not the
document that would answer that question**; it names the assumption and
delegates the estimate to secondary sources. Nothing in this transcription
constitutes a security assessment of ML-DSA — this is a report of what the
primary standard says about its own assumption structure only.

## 3. FIPS 204 §3.4 — hedged vs. deterministic, and the standard's own cited fault literature

> "By default, this standard specifies the signing algorithm to use both
> types of randomness. This is referred to as the 'hedged' variant of the
> signing procedure. The use of fresh randomness during signing helps
> mitigate side-channel attacks, while the use of precomputed randomness
> protects against the possibility that there may be flaws in the random
> number generator … This document also permits a fully deterministic
> variant … However, the lack of randomness in the deterministic variant
> makes the risk of side-channel attacks (particularly fault attacks) more
> difficult to mitigate. Therefore, this variant **should not** be used on
> platforms where side-channel attacks are a concern."

§3.6.1 footnote 3, on the purpose of the `rnd` value in hedged signing: "The
primary purpose of rnd is to facilitate countermeasures to side-channel
attacks and fault attacks on deterministic signatures, such as [22, 23,
24]." References [22]-[24] (Bruinderink & Pessl 2018 TCHES, "Differential
fault attacks on deterministic lattice signatures"; Poddebniak et al. 2018
EuroS&P; Samwel et al. 2018 CT-RSA, on Ed25519) are FIPS 204's own cited
fault-attack baseline — none of the three are the 2026-dated papers named in
RQ-MLDSA-001's motivation, confirming those RQ items describe attacks
*subsequent to and not cited by* the standard itself. This is exactly the
gap RQ-MLDSA-001 is built to close (the standard names hedging as a fault
mitigation but was published before the specific 2024-2026 attacks that
target hedging directly).

## 4. A stronger candidate for RQ-MLDSA-001's "formal proof … at internal function boundaries"

The already-filed `KN-LIT-8ce0b5` (Gupta, "Rank Ceiling for
Twiddle-Perturbation Faults on the Forward NTT," ePrint 2026/1188) is a
legitimate, machine-checked (Lean 4) formal result — but its scope is
specifically NTT twiddle-constant perturbation faults, a narrow
implementation detail.

Independently found via WebSearch and confirmed by direct ePrint fetch,
**eprint.iacr.org/2025/904** — Haruhisa Kosuge (NTT, Japan) and Keita Xagawa
(Technology Innovation Institute), "The Security of ML-DSA against
Fault-Injection Attacks," ASIACRYPT 2025 — states, verbatim:

> "We provide **a formal proof of security for a specific class of faults at
> the inputs and outputs of internal functions**, showing that faults at
> these points cannot be exploited. Furthermore, to highlight the
> infeasibility of stronger fault resilience, we survey key-recovery attacks
> that exploit signatures generated under fault injection at the other
> intermediate points."

This is a near-verbatim textual match to RQ-MLDSA-001's own phrase ("a
formal proof covering only a specific class of faults at internal function
boundaries") — closer than the twiddle-fault paper's framing. The abstract
also states this paper directly extends Aranha et al. (EUROCRYPT 2020) and
Grilo et al. (ASIACRYPT 2021) to ML-DSA's hedged Fiat-Shamir with aborts, and
explicitly names this extension as something Aranha et al. left open — a
different, and arguably more central, fault-class boundary result than the
NTT-twiddle-specific one already filed. **These two papers are not
duplicates of each other** (different fault classes: bit-tampering at
function I/O boundaries generally, vs. twiddle-constant perturbation
specifically); both could legitimately be filed. This addendum proposes
Kosuge & Xagawa as an additional new entry in §6 below, not a replacement
for the already-filed Gupta entry.

**Classification (AGENTS.md rule 7):** Kosuge & Xagawa's result is a
positive security *proof* for one fault class plus a *survey of attacks*
outside that class — it says nothing about MLWE, MSIS, or SelfTargetMSIS as
mathematical problems. It is implementation/fault-model security, exactly
like the already-filed Gupta paper.

## 5. Citation-identity concern: `KN-LIT-4f3b80`

`KN-LIT-4f3b80.md` (already filed) records this title:

> "A Single-Trace Side-Channel Attack on ML-DSA: Practical Full-Key Recovery
> from a Single Faulty Signature"

Its own `identifiers.url` field is `https://eprint.iacr.org/2024/238`.
Independently re-fetching that exact URL in this session returns a page
whose title is:

> "A Single Trace Fault Injection Attack on Hedged CRYSTALS-Dilithium"
> (Sönke Jendral, sole author, FDTC 2024)

**These titles do not match.** The recorded probability (0.582) and DOI
(`10.1109/FDTC64268.2024.00013`) in `KN-LIT-4f3b80` DO match what is at that
URL, so the underlying paper identity (ePrint 2024/238) is very likely
correct — only the *title field* appears to have been mis-transcribed or
drawn from a different, closely-related paper by the same lead author.

That closely-related paper is the one found via dblp in §1b: **Jendral,
Mattsson, Dubrova, "A Single-Trace Fault Injection Attack on Hedged Module
Lattice Digital Signature Algorithm (ML-DSA)," FDTC 2024, pp. 34-43** — a
different, co-authored, ML-DSA-titled paper, not ePrint 2024/238. Multiple
independent WebSearch results consistently attribute to *this* paper (not
the solo-authored one) the figures RQ-MLDSA-001's own motivation field
originally used: recovery of **s1** specifically, on **Cortex-M4**, at
**"around 53%."** DEC-20260805-0d59ff's gate_2 declared "58.2%, not ~53%" as
now canonical — that ruling may have compared RQ-MLDSA-001's figure against
the wrong sibling paper. I cannot resolve this with full certainty (the
three-author paper's primary full text was unobtainable through eight
attempted routes, per §1b), so I am not proposing a supersession of gate_2's
ruling — only surfacing the evidence for the Coordinator to weigh, per the
"relay, never launder" discipline applying symmetrically to corrections as
to original claims.

## 6. Proposed KN-LIT actions (PROPOSE ONLY — no filing performed here)

### 6a. Upgrade proposal for `KN-LIT-4dadec` (in place; SEEDING.md maintenance rule: "Upgrade citation_verified: web → read … only after fetching the actual source; note the upgrade in the entry body")

```yaml
proposed_upgrade:
  target_id: KN-LIT-4dadec
  field_changes:
    citation_verified: "read"   # was: partial
    citation_verified_note_append: >-
      UPGRADED 2026-08-07 (independent second-pass session,
      TASK-20260805-a1c3f9 addendum). Full FIPS 204 standard body (65 pages)
      successfully read via WebFetch-then-Read (Read tool's native PDF
      parsing on the fetch tool's locally cached bytes, distinct from the
      fetch tool's own text-summarization path that failed in the original
      2026-08-05 session and in this session's own first attempt). Section
      3.2 (Computational Assumptions) states: "The security of ML-DSA is
      based on the MLWE problem over R_q and a nonstandard variant of MSIS
      called SelfTargetMSIS [16]," citing Kiltz-Lyubashevsky-Schaffner
      EUROCRYPT 2018 for the SelfTargetMSIS definition. FIPS 204 itself does
      NOT derive a concrete-bit-security estimate for SelfTargetMSIS (that
      lives in the cited academic literature). Section 3.4 and footnote 3 of
      Section 3.6.1 discuss hedged-vs-deterministic signing as a fault
      mitigation, citing Bruinderink & Pessl (TCHES 2018), Poddebniak et al.
      (EuroS&P 2018), and Samwel et al. (CT-RSA 2018) as its own fault-attack
      baseline — none of which are the 2026-reported attacks named in
      RQ-MLDSA-001, confirming those are subsequent to the standard's own
      cited literature.
  full_transcription_source: >-
    coordination/goals/GOAL-MLDSA-001/batches/BATCH-001/tasks/TASK-20260805-a1c3f9/independent_addendum_20260807.md
    sections 2-3 (this file)
```

### 6b. New entry proposal: Kosuge & Xagawa formal proof (ASIACRYPT 2025 / ePrint 2025/904)

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-ADD-1     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "The Security of ML-DSA against Fault-Injection Attacks"
  authors:
    - "Haruhisa Kosuge"
    - "Keita Xagawa"
  year: 2025
  venue: "ASIACRYPT 2025; IACR Cryptology ePrint Archive, Paper 2025/904"
  identifiers:
    eprint: "iacr:2025/904"
    doi: null
    url: "https://eprint.iacr.org/2025/904"
    pdf_url: "https://eprint.iacr.org/2025/904.pdf"
  tags:
    - ml-dsa
    - fault-injection
    - hedged-signing
    - formal-proof
    - fiat-shamir-with-aborts
    - internal-functions
    - bit-tampering
    - implementation
    - pqc
    - post-quantum
    - adjacent
  confidence: reported
  citation_verified: web
  citation_verified_note: >-
    Verified from ePrint primary page on 2026-08-07 (HTTP 200): title, two
    authors and affiliations (NTT Japan; Technology Innovation Institute),
    full verbatim abstract, eprint number, posting date (2025-05-20, revised
    2025-09-08) all read. PDF not downloaded; full paper body not read.
  added: "2026-08-07"
  superseded_by: null

  key_claims:
    - >-
      "We provide a formal proof of security for a specific class of faults
      at the inputs and outputs of internal functions, showing that faults
      at these points cannot be exploited."
    - >-
      "To highlight the infeasibility of stronger fault resilience, we
      survey key-recovery attacks that exploit signatures generated under
      fault injection at the other intermediate points."
    - >-
      Extends Aranha et al. (EUROCRYPT 2020) and Grilo et al. (ASIACRYPT
      2021)'s 1-bit-fault security analysis of hedged Fiat-Shamir signatures
      to ML-DSA's hedged Fiat-Shamir-with-aborts and to multi-bit faults —
      explicitly resolving an open problem Aranha et al. left unaddressed.

  relevance_to_rq_mldsa_001: >-
    This paper is a stronger textual and substantive match than the
    already-filed KN-LIT-8ce0b5 (Gupta, NTT-twiddle rank ceiling) for
    RQ-MLDSA-001's motivation phrase "a formal proof covering only a
    specific class of faults at internal function boundaries" — it uses
    near-identical language ("inputs and outputs of internal functions")
    and targets a broader/different fault model (general bit-tampering at
    function I/O) than Gupta's narrower NTT-twiddle-specific result. The two
    are complementary, not duplicates: they characterize different fault
    classes. AGENTS.md rule 7 applies: this is a formal proof about an
    IMPLEMENTATION/FAULT security model, not a claim about MLWE, MSIS, or
    SelfTargetMSIS.

  dedup_note: >-
    NEW — not present under any ID in the corpus as of 2026-08-07 (checked
    against the ten declared census entries and a corpus-wide grep for
    "Kosuge", "Xagawa", and "2025/904").

  attack_classification: "IMPLEMENTATION / FAULT — formal security proof for one fault class, not a mathematical break"
```

### 6c. New entry proposal: Jendral, Mattsson & Dubrova (FDTC 2024, pp. 34-43) — the ML-DSA / s1 / Cortex-M4 paper

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-ADD-2     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "A Single-Trace Fault Injection Attack on Hedged Module Lattice Digital Signature Algorithm (ML-DSA)"
  authors:
    - "Sönke Jendral"
    - "John Preuß Mattsson"
    - "Elena Dubrova"
  year: 2024
  venue: "2024 Workshop on Fault Detection and Tolerance in Cryptography (FDTC), pp. 34-43"
  identifiers:
    eprint: null
    doi: null
    url: "https://dblp.org/pid/360/2058.html"
    ieee_url: "https://ieeexplore.ieee.org/document/10737878/"
    pdf_url_attempted_not_confirmed: "https://ieeexplore.ieee.org/iel8/10737727/10737728/10737878.pdf"
  tags:
    - ml-dsa
    - hedged-mode
    - voltage-glitching
    - fault-injection
    - s1
    - cortex-m4
    - single-trace
    - implementation
    - side-channel
    - pqc
    - post-quantum
    - adjacent
    - citation-content-unread
  confidence: unverified
  citation_verified: web
  citation_verified_note: >-
    Bibliographic identity (authors, exact title, venue FDTC 2024, pages
    34-43) confirmed via dblp (a primary bibliographic index) on 2026-08-07.
    Full primary text NOT obtained despite eight distinct attempted routes,
    all logged in this addendum section 1b (IEEE Xplore document page:
    empty; ResearchGate: HTTP 403; KTH DiVA fulltext PDF: HTTP 503 x2;
    diva-portal.org record page: HTTP 503; computer.org CSDL: empty;
    Semantic Scholar: empty). The specific content claims below (s1, ~53%,
    Cortex-M4) are relayed ONLY from convergent secondary summaries returned
    by three independent WebSearch queries, never from a directly fetched
    primary page for THIS paper. confidence is therefore left at
    "unverified" rather than "reported" until a primary full-text or
    abstract-page fetch succeeds.

  key_claims_as_relayed_from_secondary_aggregation_NOT_primary_read:
    - >-
      "A fault injection attack on hedged ML-DSA in ARM Cortex-M4 uses
      voltage glitching to skip computation of a seed during the generation
      of the signature. After the fault injection, the secret key vector s1
      is derived directly from the resulting faulty signature, with the
      attack succeeding in recovering s1 from a single trace with a
      probability of around 53%." (WebSearch aggregation, not a primary
      quote — flagged explicitly as such.)

  relevance_to_rq_mldsa_001: >-
    This paper's bibliographic profile (three authors including Jendral,
    "ML-DSA" in the title rather than "CRYSTALS-Dilithium", FDTC 2024) is a
    closer match to RQ-MLDSA-001's original motivation wording ("hedged
    ML-DSA", "s1", "roughly 53% success", "Cortex-M4") than the paper
    already filed as KN-LIT-4f3b80 (ePrint 2024/238, solo-authored,
    "CRYSTALS-Dilithium", 58.2%). See section 5 of this addendum for the
    full discrepancy analysis and the citation-identity concern this raises
    about KN-LIT-4f3b80's recorded title. AGENTS.md rule 7 applies
    regardless of which paper is the better match: both are
    IMPLEMENTATION/FAULT attacks, neither is a break of MLWE, MSIS, or
    SelfTargetMSIS.

  dedup_note: >-
    NOT a duplicate of KN-LIT-4f3b80 — distinct author list, distinct title,
    distinct venue/pages, per dblp. Proposed as a genuinely separate entry;
    the Coordinator should also review whether KN-LIT-4f3b80's title field
    needs a superseding correction (section 5).

  attack_classification: "IMPLEMENTATION / FAULT — not a mathematical break (classification made from bibliographic/secondary information only; primary text unread)"
```

## 7. Honest completion-gate self-check (against this addendum's own scope)

- Every declared source has a recorded outcome against a declared access
  order: yes (§1a, §1b).
- Every obtained/considered source has an explicit already-filed / upgrade /
  new verdict: yes — §2-3 FIPS 204 (upgrade), §4 Kosuge & Xagawa (new), §5-6c
  Jendral/Mattsson/Dubrova (new, with a flagged concern about an existing
  entry), §1b Shin et al. 2026/1344 (already-filed, independently
  corroborated, no action proposed).
- Every fault/attack source classified mathematical vs. implementation per
  AGENTS.md rule 7: yes, in every relevant section above; none scored as a
  break of MLWE, MSIS, or SelfTargetMSIS.
- No KN-LIT entry filed directly: confirmed — this file and its proposals
  stay inside this task's write scope; `knowledge/` and `knowledge/INDEX.md`
  were not touched.
- The five original deliverables and `receipt.yaml` were read but not
  modified.

## 8. What this addendum does NOT do

- It does not re-run or contradict the validator or red-team verdicts
  already recorded for the original session's work.
- It does not assert that `DEC-20260805-0d59ff` is wrong — only that its
  gate_2 ruling rests on a comparison that may have used the wrong sibling
  paper, with the evidence for that laid out in §5 for the Coordinator to
  weigh.
- It makes no experiment, no hypothesis, and no security assessment of
  ML-DSA, MLWE, MSIS, or SelfTargetMSIS in either direction.
- It does not resolve the section-0 dispatch-queue/ledger inconsistency;
  that is a Coordinator action.

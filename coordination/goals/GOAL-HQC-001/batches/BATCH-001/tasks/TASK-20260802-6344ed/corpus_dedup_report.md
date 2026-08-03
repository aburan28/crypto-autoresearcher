# Corpus dedup report — TASK-20260802-6344ed

**Duty discharged**: NAMED DUTY 1, *dedup before acquire*.
**Rule being honoured**: `GOAL-HAWK-001` BATCH-001 spent an executor task
acquiring a paper that was already filed as `KN-LIT-7592`. This report gives
every source an explicit **already-filed / upgrade / new** verdict against the
corpus **before** anything is proposed for filing.

**Nothing in this task writes to `knowledge/`.** Verdicts here are inputs to
`proposed_kn_lit_entries.md`, which is itself only a proposal.

---

## 1. Method, stated so it can be re-run

Run from repo root at commit `47a684f24a51771cad8336509d28ec025755501b`
(clean tree), 2026-08-02.

```
grep -ril "hqc" knowledge/                                  # the census's own lane
grep -ril "hqc\|hamming quasi\|quasi-cyclic" knowledge/      # widened
grep -ril "2005.10741\|HQC-RMRS\|RMRS" knowledge/ ledger/
grep -ril "pqc-hqc\|hqc_specifications\|Hamming Quasi-Cyclic (HQC)" knowledge/
grep -ril "2026/461\|Compact HQC\|Unbalanced HQC\|UHQC" knowledge/ ledger/
grep -ril "decoding failure rate\|decryption failure rate\|decryption failure" knowledge/
grep -ril "reed-muller" knowledge/
grep -ril "Aragon\|Zémor\|Zemor\|Deneuville\|Aguilar-Melchor\|Aguilar Melchor\|Chaofeng" knowledge/
```

Corpus size at that commit: **7 666** `KN-LIT-*.md` files.

**Limitation of the method, stated up front.** These are string greps over
entry text. A paper filed under a mangled title with no matching author string
and no mention of "hqc" would not be found. Several census records show exactly
that failure mode (`KN-LIT-3859`'s `title` is the truncated *"Fault-Injection
Attacks against NIST's"* with *"Post-Quantum Cryptography Round KEM"* parsed
into the `authors` list), so this residual risk is real and is not claimed to
be zero.

---

## 2. Census verification

`BATCH-001-OPENING.md` §3 lists six HQC-touching `KN-LIT` records. **The census
reproduces exactly.** `grep -ril "hqc" knowledge/` returns precisely
`KN-LIT-1798`, `KN-LIT-2083`, `KN-LIT-2141`, `KN-LIT-2541`, `KN-LIT-3859`,
`KN-LIT-7565`, plus `knowledge/INDEX.md`. No seventh record.

Widening to `quasi-cyclic` adds eight files — `KN-LIT-1775`, `2226`, `3244`,
`4875`, `5191`, `5318`, `6056`, `6708` — **none of which mentions HQC** (titles:
QC/GQC AG codes; QcBits side-channel; LEDAcrypt cryptanalysis; McEliece-1284 /
QC-2918 ISD; NISC inner product from LPN/LWE; codes and LWE over function
fields; QcBits; QC-MDPC on embedded devices). They are correctly outside the
census.

`BATCH-001-OPENING.md` §3's central claim — *"The HQC specification itself is
absent from the corpus. So is any primary statement of the analytic
decoding-failure-rate model."* — **is confirmed**: no file under `knowledge/`
matches `pqc-hqc`, `hqc_specifications`, `HQC-RMRS`, or `2005.10741`.

### 2.1 One thing the census's grep pattern does not reach (observation)

The census grepped `"hqc\|hamming quasi"`. That pattern is correct for its
stated purpose (HQC-touching records) but it does **not** surface the corpus's
existing **decryption-failure cluster**, which is adjacent to this goal's whole
first lane. Grepping `"decryption failure|decoding failure rate"` returns 16
`KN-LIT` files and 2 `KN-TECH` files that the census does not list:

| Record | Title (as filed) | Why it matters to `GOAL-HQC-001` |
|---|---|---|
| `KN-TECH-048` | *Decryption-failure attacks and failure boosting* | **The most important one.** A technique record that already states the rule *"a revised failure rate is not an attack"* and requires boosting gain + adversary model + query budget + information accumulation before a DFR result becomes a security result. Its `tags`/`applicability` are **lattice**-scoped (*"IND-CCA lattice KEMs"*), so it does not cover HQC — but any future HQC DFR finding must cite it or explain why not. |
| `KN-LIT-3771` | *Failing gracefully: Decryption failures and the Fujisaki-Okamoto transform* | Directly the DFR → FO/IND-CCA join that SPEC §6.2.2 and Theorem 6.3 instantiate. |
| `KN-LIT-3735` | *Exploring Decryption Failures of BIKE: New Class of Weak Keys and Key Recovery Attacks* | The only **code-based** DFR record in the cluster; BIKE, not HQC. |
| `KN-LIT-119`, `KN-LIT-1974`, `KN-LIT-3369`, `KN-LIT-5045`, `KN-LIT-118` | Impact of decryption failures on LWE/LWR security; failure-search bootstrapping; DF attacks on IND-CCA lattice schemes; multitarget DF attacks; LWE with side information | The lattice-side DFR-attack literature `KN-TECH-048` is built from. |
| `KN-LIT-5095`, `KN-LIT-5409`, `KN-LIT-6175`, `KN-LIT-6997`, `KN-LIT-7141`, `KN-LIT-1843`, `KN-LIT-1681`, `KN-TECH-047` | NTRU CCA attacks; distinguishable decryption failures; NTRU inversion oracles; impact-of-decryption-failures; QROM CCA tightness; LPN-C; (`KN-LIT-1681` is a false positive — image encryption) | Peripheral; listed for completeness so a later search is not surprised. |

**This is recorded as an observation about grep coverage, not as a defect
finding against the opening.** The opening's census answered the question it
asked (*is HQC already filed?*) correctly. The point for downstream work is
narrower: **a future HQC DFR record must be deduped against
`KN-TECH-048`/`KN-LIT-3771`/`KN-LIT-3735` as well as against the six.**

---

## 3. Per-source verdicts

### S1 — HQC specification, 22/08/2025 · **VERDICT: NEW**

- **Obtained**: yes, full text (51 pp.), `https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf`,
  sha256 `174186cb5fdc0108aad914391360c222f52ea533bfb406146fac124b3a25406d`.
- **Checked against**: all six census records and the whole corpus by the greps
  in §1.
- **Result**: not filed. No record in `knowledge/` names the HQC specification,
  `pqc-hqc.org`, or any HQC specification date.
- **Nearest existing record**: none. `KN-LIT-1798` (HQC on Cortex-M4) cites HQC
  but is an implementation paper, not the specification.
- **Verdict**: **NEW.** Proposed as `PROP-S1` in
  `proposed_kn_lit_entries.md` at `citation_verified: read`.

### S2 — Aragon, Gaborit, Zémor, *HQC-RMRS…*, arXiv:2005.10741 · **VERDICT: NEW**

- **Obtained**: yes, full text (14 pp.), `https://arxiv.org/pdf/2005.10741`,
  sha256 `cbb7dbd670f27cdcf602438018df52745c0af495050aedb3b83a0b00986f5446`.
- **How it was identified**: **from SPEC itself**, not from memory. SPEC §6.1.1
  says *"following [4]"* and SPEC ref [4] is this paper. This is the
  specification's own derivation source for the DFR model.
- **Checked against**: `RMRS`, `HQC-RMRS`, `2005.10741`, `Aragon`, `Zémor`,
  `Gaborit` across `knowledge/` and `ledger/`. The four `Aragon` hits
  (`KN-LIT-2531`, `730`, `1577`, `3490`) are Durandal/PSSI, an ECC key scheme,
  MinRank-Gabidulin, and Durandal — none is this paper. The single `Zémor` hit
  (`KN-LIT-2956`) is LPS expander hash collisions.
- **Verdict**: **NEW.** Proposed as `PROP-S2` at `citation_verified: read`.

### S3 — Guo, Johansson, *A New Decryption Failure Attack Against HQC* · **VERDICT: ALREADY FILED → UPGRADE `KN-LIT-2141`**

This is the case the DEDUP duty exists for. **No new record is proposed.**

- **Already filed as**: `KN-LIT-2141`, added 2026-07-24, `confidence: reported`,
  `citation_verified: read`.
- **What this task verified**, via DBLP (a primary index named in
  `knowledge/SEEDING.md`) and the Springer DOI landing page:

  | Field | `KN-LIT-2141` today | Verified value |
  |---|---|---|
  | `year` | `null` | **2020** |
  | `venue` | `null` | **ASIACRYPT 2020 (26th Int. Conf., Daejeon, South Korea, Dec 7–11, 2020), Proceedings Part I, LNCS 12491, pp. 353–382, Springer** |
  | `identifiers.doi` | `null` | **10.1007/978-3-030-64837-4_12** |
  | `identifiers.url` | `null` | **https://doi.org/10.1007/978-3-030-64837-4_12** |
  | `identifiers.eprint` | `null` | **none located** — an ePrint search for the exact title returned 4 unrelated papers and no match. DBLP marks the record `access: closed`. |
  | title casing | *"…against HQC"* | *"A New Decryption Failure Attack Against HQC"* (DBLP/Springer) |

- **A substantive defect found in the existing entry's key claims.** The entry
  states: *"The online attack on an HQC instance then submits about 264 special
  ciphertexts for decryption"*. The Springer abstract reads **2⁶⁴** — the
  superscript was flattened to `264` during the 2026-07-24 bulk-seeding pass.
  The entry also **omits** the abstract's two complexity figures: *"The overall
  complexity is estimated to be 2²⁴⁶ if the attacker balances the costs of
  precomputation and post-processing"*, and *"If we allow the precomputation
  cost to be 2²⁵⁴, which is below exhaustive key search on a 256 bit secret
  key, the computational complexity of the later parts can be no more than
  2⁶⁴."*
- **A provenance question this task cannot settle.** `KN-LIT-2141` carries
  `citation_verified: read` and cites *"Local copies: `downloads/12491205 (1).pdf`,
  `downloads/12491205.pdf`"*. **No `downloads/` directory exists in this
  repository**, so the artifact backing the `read` level is not present for a
  reviewer. The entry's own *Not verified here* section says it was generated
  *"from the local PDF's first two pages"* with fields *"parsed heuristically"*.
  This task verified the **bibliography** against DBLP + Springer (= `web`
  level) and read the **Springer abstract**, not the paper. Whether `read`
  survives is a Coordinator/Validator call, not the executor's.
  *(The filename `12491205.pdf` is consistent with LNCS volume **12491**, which
  is the volume DBLP gives — a corroboration, not a verification.)*
- **Scope note relayed at the source's own level**: the abstract says HQC *"has
  advanced to the second round"* and that the attack recovers the key of *"an
  HQC instance named hqc-256-1"*. This task makes **no** statement about how
  that instance relates to the 2025 specification's HQC-1/3/5 parameter sets.
- **Verdict**: **UPGRADE `KN-LIT-2141`.** Drafted as `PROP-S3-UPGRADE`.

### S4 — Carrier, Hatey, Luzzi, Tillich, iacr:2026/1498 · **VERDICT: ALREADY FILED → NO CHANGE PROPOSED**

- **Already filed as**: `KN-LIT-7565`, added 2026-07-26, `confidence: reported`,
  `citation_verified: web`, with correct `year`, `venue`, `eprint`, and `url`.
- **What this task did**: fetched the ePrint abstract page
  (`https://eprint.iacr.org/2026/1498`, HTTP 200, real content) and confirmed
  title, all four authors and affiliations, and the abstract's opening claims
  against the existing entry. **They match.** The entry is accurate at its
  declared `web` level.
- **What this task did NOT do**: fetch the PDF and upgrade to `read`. That is
  outside this task's objective (HQC specification + primary DFR-analysis
  literature); the ISD lane belongs to `TASK-20260802-0100a5`, and that task is
  scheme-independent by construction. Recorded rather than silently skipped.
- **Verdict**: **ALREADY FILED, no upgrade proposed here.** A `web → read`
  upgrade remains available to a later task.

### S5 (not declared in advance) — eprint 2026/461, *Compact HQC with new (un)balance* · **VERDICT: NEW, recorded as a LEAD**

**Honesty flag: this source was NOT in the `sources_sought` list declared before
searching.** It surfaced in the ePrint search executed for S3. It is recorded
as a discovered lead rather than retro-fitted into the declared target list.

- **Obtained**: abstract page only (`https://eprint.iacr.org/2026/461`, HTTP
  200). PDF not fetched.
- **Checked against**: `2026/461`, `Compact HQC`, `Unbalanced HQC`, `UHQC`,
  `Chaofeng` across `knowledge/` and `ledger/` — **zero hits**.
- **Why it is relevant enough to record**: its abstract states the paper
  *"formalize[s] the best-known decryption-failure attack against HQC"* and
  derives *"an attack-aware upper bound on the secure DFR"*, and it questions
  the *"DFR is directly configured to be less than 2^{-λ}"* choice. That is the
  same object `GOAL-HQC-001` targets. **This task asserts nothing about its
  correctness or its bearing on HQC's security.**
- **Verdict**: **NEW.** Proposed as `PROP-S5` at `citation_verified: web`
  (abstract only), explicitly flagged as out-of-declared-scope discovery.

---

## 4. Summary table

| Source | Obtained | Level reached here | Verdict | Proposal |
|---|---|---|---|---|
| S1 HQC specification 2025-08-22 | yes, full PDF | full text read | **NEW** | `PROP-S1` (`read`) |
| S2 arXiv:2005.10741 HQC-RMRS | yes, full PDF | full text read | **NEW** | `PROP-S2` (`read`) |
| S3 Guo–Johansson ASIACRYPT 2020 | bibliography + publisher abstract | `web` verified here | **ALREADY FILED → UPGRADE** | `PROP-S3-UPGRADE` to `KN-LIT-2141` |
| S4 Carrier et al. iacr:2026/1498 | ePrint abstract page | `web`, matches existing entry | **ALREADY FILED, no change** | none |
| S5 eprint 2026/461 (undeclared find) | ePrint abstract page | `web` | **NEW (lead)** | `PROP-S5` (`web`) |

**Duplicates created: zero.** **Existing records edited: zero** (this task has
no write access to `knowledge/` and did not attempt any).

---

## 5. What a reviewer should check hardest

Stated so review is not left to guess where this report is weakest.

1. **§2.1's cluster is a judgement about relevance, not a verified overlap.** I
   grepped titles and read `KN-TECH-048` in full; I did **not** read the other
   15 records. If one of them already contains HQC's DFR model under a mangled
   title, my greps would have missed it only if it also lacks the string "hqc" —
   possible, since `KN-LIT-3859` shows titles do get mangled in this corpus.
2. **The `KN-LIT-2141` `read`-level question is left open on purpose.** I
   recorded that the artifact backing it is absent and that one of its claims is
   numerically corrupted (`264` for `2⁶⁴`). I did not downgrade it, propose
   downgrading it, or read the paper. That is a Coordinator decision.
3. **S5 was not declared before searching.** It is flagged as such in two
   places rather than quietly folded into the target list.

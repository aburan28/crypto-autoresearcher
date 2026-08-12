# Proposed KN-LIT entries — TASK-20260802-6344ed

**Duty discharged**: NAMED DUTY 4, *propose, do not file*.

**Nothing here has been written to `knowledge/`.** This task did not create,
edit, or delete any file under `knowledge/`, did not touch
`knowledge/INDEX.md`, and did not touch `ledger/`. Filing is a ledger-archive
act performed after review.

**Provenance levels are used exactly as `knowledge/SEEDING.md` defines them:**
`citation_verified: web` = author/title/venue/year confirmed against a primary
index; `read` = the actual paper was fetched and the entry's claims reflect its
real content; `confidence: reported` = the source states it and we are relaying
it, not re-deriving it.

**Identifier allocation is deliberately left blank.** `tools/allocate_id.py
--next` offers no knowledge-record type (`coordinator_decision | evidence |
experiment | handoff | hypothesis | idea | research_question` only), so KN-LIT
ids are not minted by that path in this repository. The filing task must choose
the id and confirm it with `python3 tools/allocate_id.py --check KN-LIT-<id>`
before use. **I did not choose ids**, because an id chosen here and a different
id used at filing time is exactly the kind of drift AGENTS.md rule 15 warns
about.

---

## PROP-S1 — HQC specification (NEW)

```yaml
id: KN-LIT-<TO BE ALLOCATED AT FILING>
type: literature
title: "Hamming Quasi-Cyclic (HQC)"
authors:
  - "Gaborit Philippe"
  - "Aguilar-Melchor Carlos"
  - "Aragon Nicolas"
  - "Bettaieb Slim"
  - "Bidoux Loic"
  - "Blazy Olivier"
  - "Deneuville Jean-Christophe"
  - "Persichetti Edoardo"
  - "Zemor Gilles"
  - "Bos Jurjen"
  - "Dion Arnaud"
  - "Lacan Jerome"
  - "Robert Jean-Marc"
  - "Veron Pascal"
  - "Barreto Paulo L."
  - "Ghosh Santosh"
  - "Gueron Shay"
  - "Guneysu Tim"
  - "Misoczki Rafael"
  - "Richter-Brokmann Jan"
  - "Sendrier Nicolas"
  - "Tillich Jean-Pierre"
  - "Vasseur Valentin"
year: 2025
venue: "HQC team specification document, version dated 2025-08-22, 51 pp. (NIST PQC selected algorithm; standard not published as of this entry)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf"
tags: [hqc, code-based, kem, quasi-cyclic, syndrome-decoding, qcsd, decoding-failure-rate, dfr, reed-muller, reed-solomon, concatenated-code, fujisaki-okamoto, ind-cca2, specification, primary-source, pqc]
confidence: reported
citation_verified: read
added: 2026-08-02
superseded_by: null
```

### Contribution
The current specification of Hamming Quasi-Cyclic (HQC), a code-based KEM whose
security is stated to rest on the Quasi-Cyclic Syndrome Decoding problem.
Specifies the scheme (sampling, multiplication, the concatenated Reed-Muller /
Reed-Solomon code, HQC-PKE, HQC-KEM via the salted Fujisaki–Okamoto transform
with implicit rejection), the three parameter sets, and a security analysis
whose §6.1 gives the **analytic decoding-failure-rate model** for the
concatenated decoder.

### Key claims (as reported)
Each claim carries the source's own hedging level. Formula-level detail and
numbered assumptions are transcribed in
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md`
(assumption ids A1–A23, hedges H1–H11, published-text anomalies X1–X10).

- **Parameter sets (Table 5, stated as design targets):** HQC-1/NIST-1
  (n₁=46, n₂=384, n=17 669, k=128, ω=66, ω_r=ω_e=75, DFR < 2⁻¹²⁸); HQC-3/NIST-3
  (56, 640, 35 851, 192, 100, 114, DFR < 2⁻¹⁹²); HQC-5/NIST-5 (90, 640, 57 637,
  256, 131, 149, DFR < 2⁻²⁵⁶).
- **Error-vector model (§6.1.1, explicitly an approximation).** Each coordinate
  of e′ = x·r₂ − r₁·y + e is exactly Bernoulli(p\*) (Prop. 6.1.2); the weight
  distribution is then modelled as binomial under the stated **simplifying
  assumption that the coordinates of e′ are independent**, i.e. a binary
  symmetric channel with crossover p\*. The specification says this assumption
  is *"justified by remarking"* an inequality and is *"support[ed] … by
  extensive simulations"*, and that the resulting DFRs *"can only be upper
  bounds on their real values"* — **stated, not proved**.
- **Internal-code DFR (§6.1.2, upper bounds, not exact).** Prop. 6.1.3 gives a
  union-bound over the 255 non-zero codewords; Prop. 6.1.4 improves it by
  crediting a 1/2 success probability on two-way ties. The text states that
  maximum-likelihood decoding of Reed-Muller codes has *"no exact formula"*, and
  that *"[f]or cryptographic parameters the approximation is less precise"*.
- **Concatenated DFR (Theorem 6.1).** The DFR is upper bounded by a binomial
  tail Σ_{l=δ_e+1}^{n_e} C(n_e,l) p_i^l (1−p_i)^{n_e−l}, with d_e = 2δ_e+1.
- **DFR → IND-CCA2 (§6.2.2, Theorem 6.3).** HQC-PKE is δ-correct with δ the
  §6.1 quantity, and the IND-CCA2 advantage bound for HQC-KEM contains the term
  **(q_RO + q_D)·δ** alongside the salt/hash terms and twice the two DQCSD
  advantages. This is the exact textual join between the DFR model and the
  IND-CCA2 statement.
- **Reported internal-code simulation (Table 11), log₂ DFR:** NIST-1
  p\*=0.3398, [384,8,192], formula −10.79 vs observed −10.96; NIST-3 p\*=0.3618,
  [640,8,320], −14.14 vs −14.39; NIST-5 p\*=0.3725, [640,8,320], −11.30 vs
  −11.48. **Relayed as the specification reports them.**
- **Known attacks (§6.3)** discusses ISD (Prange/Stern/Dumer/MMT/BJMM/May–Ozerov),
  DOOM, and structural attacks on the polynomial factorisation. It does **not**
  discuss decryption-failure attacks.

### Relevance to this program
`GOAL-HQC-001` / `RQ-HQC-001` first lane: this is the primary statement of the
analytic DFR model the goal exists to measure against. `RQ-HQC-001.constraints`
forbid designing an experiment until the primary sources are filed; this entry
is the one that removes that block for the DFR lane. It also supplies the
selected parameter sets that any memory-charged ISD baseline
(`TASK-20260802-0100a5`, `GOAL-SDITH-001`) would eventually be instantiated at.

**Forecloses**: nothing. **Leaves open**: everything the goal asks — this entry
records what the model *says*, not whether it holds.

### Not verified here
- No claim in this entry has been re-derived, recomputed, or measured by this
  program. Table 11's numbers are the specification's, not ours.
- Equation (13) (the IND-CCA2 bound) is marked `[EXTRACTION-DAMAGED]` in the
  transcription: it was read from the PDF text layer only, and the page was not
  rendered and checked as an image. **It carries no claim.**
- The claim that HQC was selected by NIST is corroborated by the primary
  `csrc.nist.gov` PQC project page fetched 2026-08-02 (*"the Falcon digital
  signature algorithm and HQC key encapsulation mechanism were selected for
  ongoing standardization; that process is underway"*), and by the specification
  itself. No FIPS text has been read by this program.
- Ten anomalies in the published text (a literal `weight` token inside a
  binomial coefficient in Eq. (5); three inconsistent cross-references for p_i;
  code parameters that differ between prose and table; `RS-S3[90, 32, 49]` vs
  Table 3's δ=29) are recorded in the transcription as **observations of the
  source document**, with no assessment attached.

---

## PROP-S2 — Aragon, Gaborit, Zémor, *HQC-RMRS* (NEW)

```yaml
id: KN-LIT-<TO BE ALLOCATED AT FILING>
type: literature
title: "HQC-RMRS, an instantiation of the HQC encryption framework with a more efficient auxiliary error-correcting code"
authors:
  - "Aragon Nicolas"
  - "Gaborit Philippe"
  - "Zemor Gilles"
year: 2020
venue: "arXiv preprint arXiv:2005.10741 (submitted 21 May 2020), 14 pp."
identifiers:
  eprint: null
  doi: null
  arxiv: "arXiv:2005.10741"
  url: "https://arxiv.org/abs/2005.10741"
tags: [hqc, hqc-rmrs, code-based, kem, decoding-failure-rate, dfr, reed-muller, reed-solomon, concatenated-code, binary-symmetric-channel, quasi-cyclic, primary-source, pqc]
confidence: reported
citation_verified: read
added: 2026-08-02
superseded_by: null
```

### Contribution
Replaces HQC's original BCH ⊗ repetition auxiliary code with a concatenation of
Reed-Muller and Reed-Solomon codes, and gives the error-distribution and
decoding-failure-rate analysis for that construction. **This is the paper the
2025 HQC specification cites as reference [4] and follows in §6.1.1**, i.e. the
derivation source of the specification's analytic DFR model.

### Key claims (as reported)
- Abstract: the concatenated RM/RS codes *"yield better decoding results than
  the BCH and repetition codes: overall we gain roughly 17% in the size of the
  key and the ciphertext, while keeping a simple modelization of the decoding
  error rate."*
- §3 presents *"a simplified and more precise analysis of the distribution of
  the error vector output by the HQC protocol"*, with the same *"simplifying
  assumption that the coordinates e′_k of e′ are independent variables"* that
  the specification carries.
- **Remark 4.1 (a hedge the specification does not carry):** *"Propositions
  4.2.1 and 4.2.2 give upper bounds on the Decryption Failure Rate for the
  internal code. The smaller the DFR, the closer the bounds become to the real
  value."* Its Table 4 tabulates **both** bounds against observed DFR at the
  2020 parameters (128: p⋆=0.3196, [256,8,128], −7.84 / −8.03 / observed −8.72;
  192: 0.3535, [512,8,256], −11.81 / −12.12 / −12.22; 256: 0.3728, [768,8,384],
  −13.90 / −14.20 / −14.25).
- **Remark 4.2 (the scope statement for the independence assumption):** the
  bounds *"have been derived with a binary symmetric channel model for the
  distribution of the HQC error vector restricted to the support of a
  (duplicated) Reed-Muller code … We observe that they are virtually identical,
  meaning that **a small proportion of HQC bits do behave as i.i.d Bernoulli
  variables**."*
- **§4.3:** *"For Reed-Muller codes, rather than considering the upper bound
  approximation we effectively decoded the code, which means than in practice
  the upper bound that we use for our theoretical DFR, is greater than what is
  obtained in the simulations."*
- Theorem 4.3 is the same binomial-tail concatenated-code DFR bound that appears
  as Theorem 6.1 in the specification. **No proof is given in this paper.**

### Relevance to this program
Supplies the derivation-level hedges (Remarks 4.1 and 4.2) that the 2025
specification compresses or omits, and therefore matters for any independent
re-derivation of the model under `RQ-HQC-001`. Its parameters are the **2020**
ones and differ from the specification's; a comparison across the two must not
mix them.

### Not verified here
Formulas in this paper were **not** image-verified (unlike the specification's);
only prose was quoted. No claim was re-derived or measured. This entry does not
assert that the specification's §6.1 and this paper's §3–§4 are mathematically
identical, only that the specification cites this paper as what it follows.

---

## PROP-S3-UPGRADE — upgrade to the EXISTING record `KN-LIT-2141` (NOT a new entry)

**This is an upgrade proposal. Filing it as a new `KN-LIT` would be exactly the
`GOAL-HAWK-001` BATCH-001 duplication failure this handoff exists to prevent.**
`knowledge/SEEDING.md` says corrections supersede and never silently rewrite; the
Coordinator decides whether this lands as an in-place field correction or a
superseding record.

Fields verified by this task against **DBLP** (`https://dblp.org/rec/conf/asiacrypt/Guo020.bib`)
and the **Springer DOI landing page**, both fetched 2026-08-02:

```yaml
# KN-LIT-2141 — proposed corrections
title: "A New Decryption Failure Attack Against HQC"    # was: "...against HQC"
year: 2020                                              # was: null
venue: "ASIACRYPT 2020 (26th International Conference on the Theory and Application of Cryptology and Information Security, Daejeon, South Korea, December 7-11, 2020), Proceedings Part I, LNCS 12491, pp. 353-382, Springer"   # was: null
identifiers:
  eprint: null            # unchanged; no ePrint version located (see below)
  doi: "10.1007/978-3-030-64837-4_12"                   # was: null
  arxiv: null
  url: "https://doi.org/10.1007/978-3-030-64837-4_12"   # was: null
tags: [hqc, code-based, kem, decryption-failure, decoding-failure-rate, dfr, key-recovery, chosen-ciphertext, cryptanalysis, pqc]   # proposed replacement; the current tag list (cryptanalysis, dlp, factoring, lattice, mov-fr, pqc, provable-security, quantum) does not describe this paper
confidence: reported      # unchanged
citation_verified: <COORDINATOR DECISION — see note>
```

**Claim correction (substantive).** The entry currently reads *"submits about
264 special ciphertexts for decryption"*. The publisher abstract reads **2⁶⁴**;
`264` is a flattened superscript from the 2026-07-24 bulk-seeding pass. The
entry also omits the abstract's complexity figures. Proposed replacement key
claims, quoted at the source's own level from the Springer abstract:

- *"In this paper we present an attack recovering the secret key of an HQC
  instance named hqc-256-1."*
- *"The attack requires a single precomputation performed once and then never
  again."*
- *"The online attack on an HQC instance then submits about 2⁶⁴ special
  ciphertexts for decryption (obtained from the precomputation) and a phase of
  analysis studies the subset of ciphertexts that are not correctly decrypted.
  In this phase, the secret key of the HQC instance is determined."*
- *"The overall complexity is estimated to be 2²⁴⁶ if the attacker balances the
  costs of precomputation and post-processing, thereby claiming a successful
  attack on hqc-256-1 in the NIST setting."*
- *"If we allow the precomputation cost to be 2²⁵⁴, which is below exhaustive
  key search on a 256 bit secret key, the computational complexity of the later
  parts can be no more than 2⁶⁴."*
- Scope as the abstract itself frames it: HQC *"has advanced to the second
  round"*; the target is the instance *"hqc-256-1"*. **No statement is made here
  about the relation between that instance and the 2025 specification's
  HQC-1/3/5 parameter sets.**

**`citation_verified` is left for the Coordinator, with the facts stated.** The
record claims `read` on the basis of *"Local copies: `downloads/12491205 (1).pdf`,
`downloads/12491205.pdf`"*, and **no `downloads/` directory exists in this
repository**, so the artifact backing `read` is unavailable to a reviewer. What
*this* task verified is the bibliography (DBLP, a primary index → `web`) plus
the publisher abstract. I did not fetch the paper (DBLP marks it `access:
closed`; no ePrint version was located — an ePrint title search returned
2026/461, 2026/071, 2025/1608, 2019/155, none of which is this paper).

**No ePrint identifier should be invented for this record.**

---

## PROP-S5 — eprint 2026/461, *Compact HQC with new (un)balance* (NEW — discovered lead)

**Flagged: this source was not in the access log's `sources_sought` list.** It
surfaced during the ePrint search run for S3 and is proposed as a lead, at
abstract level only.

```yaml
id: KN-LIT-<TO BE ALLOCATED AT FILING>
type: literature
title: "Compact HQC with new (un)balance"
authors:
  - "Guan Chaofeng"
  - "Luo Lan"
  - "Jiang Haodong"
  - "Hou Jianhua"
  - "Yu Tong"
  - "Wang Hong"
  - "Li Kangquan"
  - "Qu Longjiang"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/461 (preprint; last updated 2026-03-05)"
identifiers:
  eprint: "iacr:2026/461"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/461"
tags: [hqc, uhqc, code-based, kem, decryption-failure, decoding-failure-rate, dfr, information-set-decoding, unbalanced-errors, parameter-selection, pqc, adjacent]
confidence: reported
citation_verified: web
added: 2026-08-02
superseded_by: null
```

### Contribution (as reported by the abstract)
Argues that HQC's current bandwidth/security balance relies on two restrictions
— that *"the decryption-failure-rate (DFR) is directly configured to be less
than 2^{-λ} … rather than carefully determined by choosing conservative
parameters to resist known attacks as the Kyber team did in the design of NIST
FIPS 203"*, and that the error distribution in the underlying QCSD problem is
restricted to be balanced — and proposes removing both.

### Key claims (as reported)
- *"we first formalize the best-known decryption-failure attack against HQC, and
  derive an upper bound on the probability that an adversary triggers a
  decryption-failure event under realistic query and time limits, enabling an
  attack-aware upper bound on the secure DFR."*
- *"we quantify how the weight distribution of (r₁, r₂, e) … affects the concrete
  cost of ISD attacks and DFR. This yields an unbalanced weight strategy that
  strictly lowers the DFR without sacrificing the targeted bit security, leading
  to a new variant called Unbalanced HQC (UHQC)."*
- *"Across all NIST security levels, UHQC reduces bandwidth by 10-12% and
  improves runtime by 6-8%."*

### Relevance to this program
Directly adjacent to `GOAL-HQC-001`'s first lane: it is an external
reconsideration of the same DFR-configuration choice the goal targets, and it
is **not** in the corpus. Recording it now means a later `/propose-ideas` pass
on `RQ-HQC-001` screens against it instead of rediscovering it.

### Not verified here
**Abstract only — the PDF was not fetched.** `citation_verified: web` is the
honest ceiling. Every figure above (10-12%, 6-8%) is the authors' claim relayed
verbatim; none has been checked, and this program asserts nothing about whether
this paper's analysis is correct or about what it implies for HQC's security.
It is a `Preprint` per its own ePrint metadata, with no publication info.

---

## What is deliberately NOT proposed

- **No `KN-LIT` for Carrier–Hatey–Luzzi–Tillich iacr:2026/1498.** Already filed
  as `KN-LIT-7565`, verified accurate at its declared `web` level. A `web →
  read` upgrade is available but is outside this task's objective.
- **No `KN-TECH`, `KN-FIND`, or `KN-OPEN` entry.** The deliverable is
  `proposed_kn_lit_entries.md`. A technique abstract of the DFR model, and any
  relationship to the existing `KN-TECH-048` (*Decryption-failure attacks and
  failure boosting*, lattice-scoped), is a curation decision, not an executor
  one.
- **No `INDEX.md` row.** Regenerating the index is part of filing.
- **No claim, at any tier, about HQC's security.** `RQ-HQC-001`'s claim-tier
  ceiling (toy) is untouched by this task, which produced no measurement.

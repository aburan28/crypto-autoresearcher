# Proposed KN-LIT Entries — TASK-20260805-a1c3f9

## ID allocation note

KN-LIT identifiers are not handled by `tools/allocate_id.py` (the tool only
manages RQ, H, EXP, EV, DEC, TASK, BATCH prefixes). The IDs below are
**provisional** and must be formally allocated by the Coordinator before filing,
using the standard knowledge curation process (curate-knowledge skill, step 2:
"grep existing files for next free ID in that class"). All five are NEW entries
with no existing entry to supersede or upgrade.

---

## Entry 1: FIPS 204 — Module-Lattice-Based Digital Signature Standard

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-1     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "Module-Lattice-Based Digital Signature Standard"
  authors:
    - "National Institute of Standards and Technology"
  year: 2024
  venue: "NIST Federal Information Processing Standards Publication 204"
  identifiers:
    doi: "10.6028/NIST.FIPS.204"
    url: "https://csrc.nist.gov/pubs/fips/204/final"
    pdf_url: "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf"
    eprint: null
  tags:
    - ml-dsa
    - fips-204
    - dilithium
    - module-lwe
    - module-sis
    - selftargetmsis
    - fiat-shamir-with-aborts
    - signature
    - nist
    - post-quantum
    - standard
    - primary-source
    - adjacent
  confidence: reported
  citation_verified: true
  citation_verified_note: >-
    Verified at page level: title, author (NIST), date (2024-08-13), DOI,
    PDF download URL, abstract, and keywords read from the primary CSRC
    publication page on 2026-08-05 (HTTP 200). The PDF binary was served
    but not readable as text through the webfetch tool; the standard body
    (including formal problem definitions for MLWE, MSIS, SelfTargetMSIS
    and the security proof structure) was NOT read. Confidence is therefore
    "reported" despite the page-level citation_verified: true — the
    publication identity is verified; the technical content is not.
  added: "2026-08-05"
  superseded_by: null

  abstract_first_200: >-
    Digital signatures are used to detect unauthorized modifications to data
    and to authenticate the identity of the signatory. In addition, the
    recipient of signed data can use a digital signature as evidence in
    demonstrating to a third party that the signature was, in fact, generated
    by the claimed signatory. This is known as non-repudiation since the
    signatory cannot easily repudiate the signature at a later time. This
    standard specifies ML-DSA, a set of algorithms

  key_claims:
    - >-
      Specifies ML-DSA (three parameter sets: ML-DSA-44, ML-DSA-65, ML-DSA-87),
      described as secure against adversaries with a large-scale quantum computer.
      (Source: CSRC abstract — standard body not read.)
    - >-
      Finalized 2024-08-13 as the NIST FIPS 204 standard, following an
      initial public draft of 2023-08-24.
    - >-
      Keywords indicate security grounds are module-lattice based (lattice;
      post-quantum) but specific problem names (MLWE, MSIS, SelfTargetMSIS)
      and their roles in the security proof are NOT transcribed here — standard
      body was not read.
    - >-
      Errata note (2026-07-31): several minor issues to be corrected in a
      future revision; see CSRC errata spreadsheet.

  relevance_to_rq_mldsa_001: >-
    This is the primary source for RQ-MLDSA-001's scope: the FIPS 204
    standard is the document that fixes the ML-DSA parameter sets and
    whose security claims are to be independently re-derived. It is the
    essential pre-condition for any experiment design (RQ-MLDSA-001.constraints[0]).
    Distinct from KN-LIT-056 (the CRYSTALS-Dilithium academic submission paper).

  dedup_note: "new entry — KN-LIT-056 covers the academic paper (TCHES 2018), not the standard text"

  not_verified:
    - Formal definition of MLWE in Section 2 (or equivalent) of the standard
    - Formal definition of MSIS in the standard
    - Formal definition of SelfTargetMSIS in the standard
    - Security proof structure and reduction chain in the standard
    - Which assumption binds at each of the three ML-DSA parameter sets
    - Text of any security theorem or lemma in FIPS 204
```

---

## Entry 2: Differential Fault Attack on ML-DSA — ePrint 2026/1344

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-2     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "Public Coefficient Matters: A Practical Differential Fault Attack on ML-DSA and HAETAE"
  authors:
    - "WonGeun Shin"
    - "SeungHyeon Jeon"
    - "Daehyeon Bae"
    - "Sujin Park"
    - "HeeSeok Kim"
  year: 2026
  venue: "IACR Cryptology ePrint Archive, Paper 2026/1344 (Preprint)"
  identifiers:
    eprint: "iacr:2026/1344"
    doi: null
    url: "https://eprint.iacr.org/2026/1344"
    pdf_url: "https://eprint.iacr.org/2026/1344.pdf"
  tags:
    - ml-dsa
    - haetae
    - differential-fault-attack
    - fault-injection
    - challenge-sampling
    - key-recovery
    - deterministic-signature
    - implementation
    - side-channel
    - pqc
    - post-quantum
    - adjacent
  confidence: reported
  citation_verified: true
  citation_verified_note: >-
    Verified from ePrint primary page on 2026-08-05 (HTTP 200): title, five
    authors, affiliation (Korea University), full abstract, keywords, category
    (Attacks and cryptanalysis), license (CC BY), history (received 2026-06-30,
    approved 2026-07-02) all read. PDF not downloaded.
  added: "2026-08-05"
  superseded_by: null

  abstract_first_200: >-
    With the standardization of post-quantum digital signature schemes and their
    increasing deployment in security critical applications such as firmware
    authentication and software distribution, implementations are expected to
    operate in physically accessible and potentially hostile environments.
    Consequently, considerable effort has been devoted to protecting these schemes
    against a variety of attacks, including timing

  key_claims:
    - >-
      Targets the challenge sampling procedure of deterministic ML-DSA:
      "a single faulted signature is sufficient to recover the secret key
      required for signature forgery."
    - >-
      Attack model does not require direct access to faulted challenges:
      "Using only public information, we identify intended fault injections
      and distinguish them from unintended fault outcomes."
    - >-
      Achieves 100% identification rate for intended faults in simulation
      and practical fault injection experiments.
    - >-
      Also targets HAETAE (KpqC-selected): first fault attack achieving
      secret-key recovery and valid signature forgery on HAETAE.
    - >-
      Proposes a countermeasure for the identified vulnerability.

  relevance_to_rq_mldsa_001: >-
    This paper is the differential fault attack described (UNVERIFIED) in
    RQ-MLDSA-001's motivation: "a differential fault attack that identifies
    intended faults from public information alone." The primary claim that
    the attack uses only public information to identify successful fault
    injections is verified from the abstract. AGENTS.md rule 7 applies:
    this is an IMPLEMENTATION/FAULT attack, not a break of MLWE, MSIS,
    or SelfTargetMSIS.

  dedup_note: "new entry"

  attack_classification: "IMPLEMENTATION / FAULT — not a mathematical break"
```

---

## Entry 3: Single-Trace Voltage-Glitch Attack on Hedged ML-DSA — ePrint 2024/238

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-3     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "A Single Trace Fault Injection Attack on Hedged CRYSTALS-Dilithium"
  authors:
    - "Sönke Jendral"
  year: 2024
  venue: "2024 Workshop on Fault Detection and Tolerance in Cryptography (FDTC)"
  identifiers:
    eprint: "iacr:2024/238"
    doi: "10.1109/FDTC64268.2024.00013"
    url: "https://eprint.iacr.org/2024/238"
    pdf_url: "https://eprint.iacr.org/2024/238.pdf"
  tags:
    - ml-dsa
    - dilithium
    - hedged-mode
    - voltage-glitching
    - fault-injection
    - key-recovery
    - cortex-m4
    - single-trace
    - implementation
    - side-channel
    - pqc
    - post-quantum
    - adjacent
  confidence: reported
  citation_verified: true
  citation_verified_note: >-
    Verified from ePrint primary page on 2026-08-05 (HTTP 200): title, author
    (Sönke Jendral, KTH Royal Institute of Technology / Ericsson Research),
    full abstract, DOI (10.1109/FDTC64268.2024.00013), venue (FDTC 2024),
    keywords, license (CC BY), history (received 2024-02-14, revised 2024-11-12)
    all read. PDF not downloaded.
  added: "2026-08-05"
  superseded_by: null

  abstract_first_200: >-
    CRYSTALS-Dilithium is a post-quantum secure digital signature algorithm
    currently being standardised by NIST. As a result, devices making use of
    CRYSTALS-Dilithium will soon become generally available and be deployed in
    various environments. It is thus important to assess the resistance of
    CRYSTALS-Dilithum implementations to physical attacks. In this paper, we
    present an attack on a CRYSTALS-Dilithium implementation in

  key_claims:
    - >-
      Voltage glitching to skip computation of the pseudorandom seed during
      signature generation in hedged mode on ARM Cortex-M4.
    - >-
      "After the successful fault injection, the resulting signature allows for
      the extraction of the secret key vector."
    - >-
      "Our attack succeeds with probability 0.582 in a single trace."
      NOTE: RQ-MLDSA-001 states "roughly 53% success" but the abstract says
      0.582 (~58.2%); the discrepancy is recorded, not laundered.
    - >-
      Countermeasures proposed.

  relevance_to_rq_mldsa_001: >-
    This paper is the single-trace voltage-glitch attack described (UNVERIFIED)
    in RQ-MLDSA-001's motivation, with two corrections to the provisional
    record: (1) success probability is ~58.2%, not "roughly 53%"; (2) publication
    year is 2024, not "2026." These corrections are sourced from the primary
    ePrint page. AGENTS.md rule 7 applies: this is an IMPLEMENTATION/FAULT
    attack (hedged mode seed skip), not a break of MLWE, MSIS, or SelfTargetMSIS.

  dedup_note: "new entry"
  year_correction_note: >-
    RQ-MLDSA-001 describes this as "2026-reported work." ePrint shows
    received 2024-02-14, published FDTC 2024. The "2026" in RQ-MLDSA-001
    is likely when the program noted it, not the publication date.

  attack_classification: "IMPLEMENTATION / FAULT — not a mathematical break"
```

---

## Entry 4: Ravi et al. SCA/FIA Survey — ePrint 2022/737

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-4     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: >-
    Side-channel and Fault-injection attacks over Lattice-based Post-quantum
    Schemes (Kyber, Dilithium): Survey and New Results
  authors:
    - "Prasanna Ravi"
    - "Anupam Chattopadhyay"
    - "Jan Pieter D'Anvers"
    - "Anubhab Baksi"
  year: 2022
  venue: "IACR Cryptology ePrint Archive, Paper 2022/737 (Preprint — journal venue unconfirmed)"
  identifiers:
    eprint: "iacr:2022/737"
    doi: null
    url: "https://eprint.iacr.org/2022/737"
    pdf_url: "https://eprint.iacr.org/2022/737.pdf"
  tags:
    - dilithium
    - ml-dsa
    - kyber
    - ml-kem
    - side-channel-attack
    - fault-injection-attack
    - survey
    - taxonomy
    - lattice
    - pqm4
    - cortex-m4
    - countermeasures
    - implementation
    - pqc
    - post-quantum
    - adjacent
  confidence: reported
  citation_verified: true
  citation_verified_note: >-
    Verified from ePrint primary page on 2026-08-05 (HTTP 200): title, four authors,
    affiliations (NTU, KU Leuven), full abstract, keywords, history (received
    2022-06-09, 4 revisions, final 2022-12-04) all read. ePrint publication info
    says "Preprint." — the IEEE Trans. Computers attribution mentioned in RQ-MLDSA-001
    handoff could NOT be confirmed from the ePrint record. Venue is recorded as
    the ePrint preprint only. PDF not downloaded.
  added: "2026-08-05"
  superseded_by: null

  abstract_first_200: >-
    In this work, we present a systematic study of Side-Channel Attacks (SCA) and
    Fault Injection Attacks (FIA) on structured lattice-based schemes, with a focus
    on Kyber Key Encapsulation Mechanism (KEM) and Dilithium signature scheme, which
    are leading candidates in the NIST standardization process for Post-Quantum
    Cryptography (PQC). Through our study, we attempt to understand the underlying

  key_claims:
    - >-
      Systematic classification of SCA and FIA on Kyber and Dilithium into
      different attack categories.
    - >-
      Range of customized countermeasures providing defense/mitigation against
      existing SCA/FIA, implemented in the pqm4 library for ARM Cortex-M4.
    - >-
      "Novel countermeasures that offer simultaneous protection against several
      SCA and FIA-based chosen-ciphertext attacks for Kyber KEM."
    - >-
      Performance evaluation on ARM Cortex-M4: custom countermeasures incur
      "reasonable performance overheads."

  relevance_to_rq_mldsa_001: >-
    This is the Ravi et al. survey referenced (UNVERIFIED) in RQ-MLDSA-001's
    handoff as "Ravi et al. fault-attack survey / taxonomy (IEEE Trans. Computers)."
    The ePrint version (2022/737) is the primary retrievable record. This survey
    provides the taxonomy of SCA and FIA on ML-DSA (Dilithium) needed to classify
    which attacks lie inside and outside the formal fault-security proof boundary.
    AGENTS.md rule 7 applies: all attacks described are IMPLEMENTATION/FAULT/SCA
    attacks, not mathematical breaks of MLWE, MSIS, or SelfTargetMSIS.

  dedup_note: "new entry"
  venue_note: >-
    The handoff attributes this to IEEE Trans. Computers. The ePrint record shows
    only "Preprint." The IEEE Trans. Computers venue is UNCONFIRMED from this source.
    If the journal version exists, it may have a DOI and should be confirmed at filing.

  attack_classification: "IMPLEMENTATION / FAULT / SIDE-CHANNEL survey — not a mathematical break"
```

---

## Entry 5: Rank Ceiling for NTT Twiddle Faults — ePrint 2026/1188

```yaml
proposed_kn_lit:
  id: KN-LIT-PROV-5     # PROVISIONAL — Coordinator allocates final ID at filing
  type: literature
  title: "Rank Ceiling for Twiddle-Perturbation Faults on the Forward NTT"
  authors:
    - "Chakshu Gupta"
  year: 2026
  venue: "IACR Cryptology ePrint Archive, Paper 2026/1188 (Preprint)"
  identifiers:
    eprint: "iacr:2026/1188"
    doi: null
    url: "https://eprint.iacr.org/2026/1188"
    pdf_url: "https://eprint.iacr.org/2026/1188.pdf"
  tags:
    - ml-dsa
    - ml-kem
    - ntt
    - twiddle-constant
    - fault-injection
    - leakage-bound
    - formal-verification
    - lean-4
    - machine-checked
    - rank-ceiling
    - implementation
    - pqc
    - post-quantum
    - adjacent
  confidence: reported
  citation_verified: true
  citation_verified_note: >-
    Verified from ePrint primary page on 2026-08-05 (HTTP 200): title, author
    (Chakshu Gupta, Georgia Institute of Technology), full abstract, keywords,
    history (received 2026-06-06, revised 2026-06-10), license (CC BY) all read.
    PDF not downloaded. The revised note on the ePrint page (v2 changes) was
    also read.
  added: "2026-08-05"
  superseded_by: null

  abstract_first_200: >-
    NIST standardised a lattice-based key-encapsulation mechanism (ML-KEM) and
    a lattice-based digital signature scheme (ML-DSA) in 2024 as post-quantum
    replacements for classical key establishment and digital signatures. Both
    compute a forward number-theoretic transform (NTT) over secret-bearing
    polynomials; the NTT's twiddle constants are a documented fault-attack surface.
    Published attacks zero every twiddle

  key_claims:
    - >-
      Exact, tight per-layer rank ladder for twiddle-perturbation faults on the
      NTT (arbitrary perturbations ζ_k → ζ_k' with bit-flips included).
    - >-
      "A single twiddle fault leaks exactly the butterfly length of its layer in
      secret coefficients, a count attained rather than merely bounded."
    - >-
      "one fault per layer pins all but two coefficients for ML-KEM and all but
      one for ML-DSA"
    - >-
      Surviving ambiguity: span(e_0, e_1) for ML-KEM's incomplete NTT;
      span(e_0) for ML-DSA's complete NTT.
    - >-
      "No combination of twiddle-perturbation faults, however large, shrinks it
      further" — the ceiling is also a floor.
    - >-
      Machine-checked in Lean 4.
    - >-
      Covers twiddle-perturbation faults only; faults on other ML-DSA
      components (challenge sampling, seed generation) are outside this proof.
    - >-
      Provides countermeasure designers a "closed-form budget for allocating
      protection."

  relevance_to_rq_mldsa_001: >-
    This paper provides the formal fault-class boundary that RQ-MLDSA-001
    describes as "a formal proof covering only a specific class of faults at
    internal function boundaries." The covered class is twiddle-perturbation
    faults on the NTT; the proof is machine-checked (Lean 4). The attacks in
    ePrint 2026/1344 (challenge-sampling faults) and 2024/238 (seed-generation
    skip) both fall outside this boundary. This paper is the formal anchor
    that allows each published attack to be classified as inside or outside
    the formal guarantee. AGENTS.md rule 7 applies: the paper characterises
    an IMPLEMENTATION/FAULT attack class, not a break of MLWE, MSIS, or
    SelfTargetMSIS.

  dedup_note: "new entry — distinct from KN-LIT-3907 (which covers the mathematical ROM/QROM security proof) and from KN-LIT-1944 (FPGA implementation)"

  proof_boundary_statement: >-
    Scope: NTT twiddle-perturbation faults only. Outside scope: challenge
    sampling faults (ePrint 2026/1344), seed generation faults (ePrint 2024/238),
    inverse-NTT faults (Remark 5: inverse has the same ceiling but is
    "structurally gated and not a live differential attack").
    Machine-checked in Lean 4 (formal, not heuristic).

  attack_classification: "IMPLEMENTATION / FAULT — formal leakage bound, not a mathematical break"
```

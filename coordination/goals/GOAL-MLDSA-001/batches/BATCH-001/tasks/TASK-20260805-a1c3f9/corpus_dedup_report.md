# Corpus Dedup Report — TASK-20260805-a1c3f9

## Method

Each named census entry was read in full before any retrieval attempt.
For each: (a) does it cover FIPS 204 itself (the NIST standard text)?
(b) does it cover the fault-attack/fault-proof literature? (c) verdict.

---

## KN-LIT-056 — CRYSTALS-Dilithium (TCHES 2018 / ePrint 2017/633)

**Title:** CRYSTALS-Dilithium - A Lattice-Based Digital Signature Scheme (ML-DSA / FIPS 204)
**Year / Venue:** 2018 IACR TCHES

**Covers FIPS 204 itself?** NO.
The source is the original CRYSTALS-Dilithium academic paper (TCHES 2018, ePrint 2017/633).
The entry correctly notes it was "standardized by NIST as ML-DSA in FIPS 204 (2024)" but
that is a cross-reference, not the standard itself. KN-LIT-056's `citation_verified: web`
means the academic paper's existence was confirmed, not the FIPS document.
The field `venue: IACR TCHES 2018(1):238-268; standardized as NIST FIPS 204 (2024)` and
`identifiers.eprint: iacr:2017/633` confirm this is the academic submission, not the standard.

**Covers fault-attack literature?** NO. No fault content.

**Verdict: ALREADY FILED — covers the academic paper only, NOT the standard.**
FIPS 204 text requires a NEW entry.

---

## KN-LIT-059 — Fiat-Shamir with Aborts (ASIACRYPT 2009)

**Title:** Fiat-Shamir with Aborts - Applications to Lattice and Factoring-Based Signatures
**Year / Venue:** 2009 ASIACRYPT

**Covers FIPS 204 itself?** NO. This is the 2009 foundational paper introducing the
rejection-sampling paradigm. No relation to the FIPS 204 standard text.

**Covers fault-attack literature?** NO. No fault content.

**Verdict: ALREADY FILED — no overlap with any priority source. No action needed.**

---

## KN-LIT-3907 — Fixing and Mechanizing the Security Proof of FS-with-Aborts and Dilithium

**Title:** Fixing and Mechanizing the Security Proof of Fiat-Shamir with Aborts and Dilithium
**Year:** Unspecified (seeded from local PDF 2026-07-24)
**Confidence:** reported; citation_verified: read (from PDF first two pages)

**Covers FIPS 204 itself?** NO. This is an academic paper that fixes the CMA-to-NMA
gap in the ROM/QROM security proof and provides a mechanized EasyCrypt proof. It is
about the mathematical security proof of the scheme, not the FIPS standard text.

**Covers fault-attack literature?** NO. This paper concerns the formal ROM/QROM
security reduction (mathematical), not fault injection or physical attacks.

**Relation to priority-source formal proof (2026/1188)?** DIFFERENT.
KN-LIT-3907 addresses the CMA-to-NMA security proof in the ROM/QROM — a
cryptographic reduction proof. ePrint 2026/1188 (Gupta) addresses the NTT
twiddle-perturbation fault-class boundary — an implementation/fault leakage proof.
These are distinct results at different proof levels; KN-LIT-3907 does NOT cover
2026/1188.

**Entry quality note:** Year, venue, DOI, and ePrint identifiers are all null —
the entry was generated from heuristic parsing and is flagged for upgrade. This
does not affect the dedup verdict.

**Verdict: ALREADY FILED — no overlap with any of the four priority sources.
The formal-proof paper needed (2026/1188) is absent from the corpus.**

---

## KN-LIT-1944 — Unified FPGA Design of Kyber and Dilithium with Provable Fault Tolerance

**Title:** Unified FPGA Design of Kyber and Dilithium with Provable Fault Tolerance
**Year / Venue:** 2026, IACR Cryptology ePrint Archive (ePrint 2026/1008)
**Confidence:** reported; citation_verified: read (title-only — no abstract extracted)

**Covers FIPS 204 itself?** NO.

**Covers fault-attack literature?** PARTIALLY — title claims "provable fault tolerance"
for an FPGA implementation of Kyber and Dilithium. However, the abstract was not
extractable, so no claims are confirmed. This is an implementation/FPGA paper, not
a mathematical proof of a fault-class boundary.

**Is this the formal proof paper needed?** UNLIKELY to be 2026/1188 (Gupta).
The Gupta paper is a theoretical result with a Lean 4 machine-checked proof of a
rank ceiling. ePrint 2026/1008 is about FPGA design. They are different papers at
different ePrint numbers. KN-LIT-1944 does not preclude the need for 2026/1188.

**Verdict: ALREADY FILED — does not cover FIPS 204 or any of the specific priority
fault papers. Overlap with 2026/1188 is none (different papers). NEW entries needed.**

---

## KN-LIT-1961 — When Removing Reductions Goes Wrong: Auditing ML-DSA Implementations

**Title:** When Removing Reductions Goes Wrong: Auditing Reduction Placement in Production ML-DSA Implementations
**Year / Venue:** 2026, IACR Cryptology ePrint (ePrint 2026/1032)
**Confidence:** reported; citation_verified: read (title-only — no abstract extracted)

**Covers FIPS 204 itself?** NO.

**Covers fault-attack literature?** The title concerns arithmetic reduction faults
in ML-DSA implementations — related to the implementation fault lane, but not
one of the four named priority sources and the abstract is unavailable.

**Verdict: ALREADY FILED — does not match any of the four priority sources.
No action needed for this dedup check.**

---

## KN-LIT-7620 — NIST IR 8610 (PQC Additional Signatures Round-3 Report)

**Covers FIPS 204 itself?** NO. IR 8610 is the Second Round status report for the
*Additional* Digital Signatures process (FAEST, HAWK, MAYO, etc.), not for the
originally selected algorithms. FIPS 204 (ML-DSA) is mentioned as context only.

**Covers fault-attack literature?** NO.

**Verdict: ALREADY FILED — no overlap with any priority source.**

---

## KN-LIT-7662 — Refined Approx-SVP Rank Reduction (MSIS Security Estimation)

**Covers FIPS 204 itself?** NO.
**Covers fault-attack literature?** NO. Mathematical lattice security estimation.
**Verdict: ALREADY FILED — no overlap.**

---

## KN-LIT-7668 — Sharper and Closed-Form Attacks on SIS (small modulus)

**Covers FIPS 204 itself?** NO.
**Covers fault-attack literature?** NO. Mathematical attacks on SIS/ISIS.
**Verdict: ALREADY FILED — no overlap.**

---

## KN-LIT-7669 — Solving SIS in any norm via Gaussian sampling

**Covers FIPS 204 itself?** NO.
**Covers fault-attack literature?** NO. Mathematical SIS algorithm.
**Verdict: ALREADY FILED — no overlap.**

---

## KN-LIT-054 — Worst-case to average-case reductions for Module Lattices

**Covers FIPS 204 itself?** NO.
**Covers fault-attack literature?** NO.
**Verdict: ALREADY FILED — no overlap.**

---

## Gap summary

| Priority source | Found in corpus? | Verdict |
|-----------------|-----------------|---------|
| FIPS 204 standard text (NIST, 2024-08-13) | NO — KN-LIT-056 is the academic paper | NEW entry |
| Differential fault attack on ML-DSA identifying faults from public info (2026/1344) | NO | NEW entry |
| Single-trace voltage-glitch attack on hedged ML-DSA (2024/238) | NO | NEW entry |
| Ravi et al. SCA/FIA survey on Kyber/Dilithium (2022/737) | NO | NEW entry |
| Formal proof of NTT twiddle-fault class boundary (2026/1188) | NO | NEW entry |

**Total new entries to propose: 5.**

KN-LIT-056 covers the academic origin paper but NOT the standard document — both
should ultimately be in the corpus. The FIPS 204 entry is complementary to, not
superseding, KN-LIT-056.

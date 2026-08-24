# Fault Literature Summary — TASK-20260805-a1c3f9

## Classification rule applied

Per AGENTS.md rule 7 and the handoff constraint: every fault/attack source found
is classified as **mathematical** or **implementation/fault/side-channel**. A fault
result may never be scored as a break of MLWE, MSIS, or SelfTargetMSIS.

---

## Source A: Differential fault attack — ePrint 2026/1344

**Full citation (verified from ePrint primary page):**
> WonGeun Shin, SeungHyeon Jeon, Daehyeon Bae, Sujin Park, HeeSeok Kim (Korea University).
> "Public Coefficient Matters: A Practical Differential Fault Attack on ML-DSA and HAETAE."
> Cryptology ePrint Archive, Paper 2026/1344. Received 2026-06-30; approved 2026-07-02.
> URL: https://eprint.iacr.org/2026/1344
> License: CC BY.

**Classification:** IMPLEMENTATION / FAULT ATTACK
- The attack targets the **challenge sampling procedure** of the *deterministic*
  mode of ML-DSA via fault injection.
- The attacker induces a fault in the challenge sampling during signing.
- "Using only public information, we identify intended fault injections and
  distinguish them from unintended fault outcomes." — the novelty is the ability
  to verify fault success from the public signature, removing the need for direct
  access to faulted intermediate values.
- Recovery of the secret key enables forgery, but the attack is physical (clock
  glitching / fault injection), not an attack on MLWE, MSIS, or SelfTargetMSIS.
- The mathematical hardness of MLWE, MSIS, and SelfTargetMSIS is not contested;
  the attack operates at the implementation level.

**Claims as stated in the abstract (relayed verbatim):**
- "a single faulted signature is sufficient to recover the secret key required for
  signature forgery"
- "Our attack model of ML-DSA does not require direct access to faulted challenges.
  Using only public information, we identify intended fault injections and distinguish
  them from unintended fault outcomes."
- "achieving a 100% identification rate for intended faults"
- "We further propose a countermeasure for the identified vulnerability"

**Formal proof boundary relevance:**
- Targets deterministic ML-DSA specifically; applicability to hedged mode not stated
  in the abstract.
- Does not reference or depend on a formal fault-security proof.

---

## Source B: Single-trace voltage-glitch attack — ePrint 2024/238

**Full citation (verified from ePrint primary page):**
> Sönke Jendral (KTH Royal Institute of Technology, Ericsson Research).
> "A Single Trace Fault Injection Attack on Hedged CRYSTALS-Dilithium."
> Cryptology ePrint Archive, Paper 2024/238. Received 2024-02-14; revised 2024-11-12.
> Published at: 2024 Workshop on Fault Detection and Tolerance in Cryptography (FDTC).
> DOI: 10.1109/FDTC64268.2024.00013
> URL: https://eprint.iacr.org/2024/238
> License: CC BY.

**Classification:** IMPLEMENTATION / FAULT ATTACK
- The attack targets the **hedged mode** of CRYSTALS-Dilithium (= ML-DSA in hedged mode).
- Mechanism: voltage glitching to skip computation of the pseudorandom seed used
  during signature generation. "We identified settings that consistently skip the
  desired function without crashing the device."
- "After the successful fault injection, the resulting signature allows for the
  extraction of the secret key vector."
- Attack succeeds with probability 0.582 in a single trace on ARM Cortex-M4.
- Physical / implementation-level attack; does not break MLWE, MSIS, or
  SelfTargetMSIS as mathematical problems.

**Correction to RQ-MLDSA-001 provisional claim:**
- RQ-MLDSA-001 states "roughly 53% success" — the actual paper states probability 0.582 (~58.2%).
  The ~53% figure is not found in this abstract. This is consistent with RQ-MLDSA-001
  flagging its motivation as UNVERIFIED.
- RQ-MLDSA-001 calls this "2026-reported work" — the paper was received by ePrint
  in 2024-02-14 and published at FDTC 2024. Publication year is 2024, not 2026.
  This discrepancy is relayed, not laundered.

**Formal proof boundary relevance:**
- Targets hedged mode specifically. The paper proposes countermeasures.
- Does not reference a formal fault-security proof. The formal proof paper (Source C)
  may provide the boundary analysis for whether this attack class falls inside or
  outside any formal guarantee.

---

## Source C: Formal proof / rank ceiling — ePrint 2026/1188

**Full citation (verified from ePrint primary page):**
> Chakshu Gupta (Georgia Institute of Technology).
> "Rank Ceiling for Twiddle-Perturbation Faults on the Forward NTT."
> Cryptology ePrint Archive, Paper 2026/1188. Received 2026-06-06; revised 2026-06-10.
> URL: https://eprint.iacr.org/2026/1188
> License: CC BY.

**Classification:** IMPLEMENTATION / FAULT — FORMAL LEAKAGE BOUND
- This paper is NOT a mathematical attack on MLWE, MSIS, or SelfTargetMSIS.
- It provides a **formal, machine-checked (Lean 4)** characterisation of what
  information leaks when an attacker performs twiddle-perturbation faults on the
  NTT — a specific class of implementation-level fault.
- It gives an **exact, tight leakage ceiling** (not a heuristic bound) for this
  fault class.

**Claims as stated in the abstract (relayed verbatim):**
- "A single twiddle fault leaks exactly the butterfly length of its layer in
  secret coefficients, a count attained rather than merely bounded"
- "one fault per layer pins all but two coefficients for ML-KEM and all but one
  for ML-DSA"
- "The surviving ambiguity is identical whichever twiddle is hit in each layer:
  span(e_0, e_1) for ML-KEM's incomplete NTT, span(e_0) for ML-DSA's complete NTT"
- "No combination of twiddle-perturbation faults, however large, shrinks it further"
- "this rank-and-kernel characterisation is machine-checked in Lean 4"

**Stated scope of the formal proof:**
The proof covers exactly **twiddle-perturbation faults on the forward NTT** —
an attacker who can flip bits in the twiddle constants (ζ_k → ζ_k'). This is
the "specific class of faults at internal function boundaries" description in
RQ-MLDSA-001's motivation field (NTT twiddle constants are at internal boundaries
of the NTT computation).

**What the proof does NOT cover:**
- Faults outside the twiddle-constant domain (e.g., faults on the secret
  polynomial coefficients directly, or on the challenge sampling as in Source A,
  or on the seed generation as in Source B).
- Sources A and B both operate on different internal functions (challenge sampling
  and seed generation respectively) — they are outside the boundary of this formal
  proof.

**Formal proof boundary statement (from abstract):**
"No combination of twiddle-perturbation faults, however large, shrinks [the
surviving ambiguity] further, and this rank-and-kernel characterisation is
machine-checked in Lean 4."

This provides the boundary the Coordinator needs: twiddle-perturbation faults
are characterised exactly; challenge-sampling faults (Source A) and seed-skip
faults (Source B) lie outside this boundary.

---

## Summary: fault attack placement relative to formal boundary

| Source | Attack type | Mechanism | Inside twiddle-fault proof? |
|--------|-------------|-----------|---------------------------|
| 2026/1344 (Shin et al.) | DFA on challenge sampling | Fault in challenge computation | **OUTSIDE** — different function boundary |
| 2024/238 (Jendral) | Voltage glitch on seed generation | Skip seed computation in hedged mode | **OUTSIDE** — different function boundary |
| 2026/1188 (Gupta) | Formal leakage bound for NTT twiddle faults | Proves exact rank ceiling | **IS** the formal boundary paper |

All three sources are IMPLEMENTATION/FAULT/SIDE-CHANNEL in character.
None constitutes a mathematical attack on MLWE, MSIS, or SelfTargetMSIS.

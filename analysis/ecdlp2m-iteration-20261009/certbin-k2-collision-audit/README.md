# CERTBIN k=2 collision-excess audit

**Subject**
- Evidence: EV-CERTBIN-691499
- Decision: DEC-20261004-d70aac, a weaken of H-CERTBIN-c50454
- Source run: EXP-CERTBIN-66e167 RUN-CERTBIN-a30c5b (Stage 1)

**What was archived.** On E_0: y^2+xy=x^3+1 over F_(2^19), with r = 130873, C_eff = 1145 and birthday expectation E = 5.004, the archived "informative/birthday" ratios were:

| | k=2 | k=3 |
|---|---|---|
| seed 2026100311 | 3.397 | 0.999 |
| seed 2026100312 | 7.593 | 1.399 |

The k=2 cells sit above the [1/2, 2] band, and that was read as "a k-specific collision excess".

**The defect.** `census_one` counts a colliding pair as informative unless its multiplicity difference lies in the span of `kernel_vectors`. That span holds one vector per generator, 2G + tau(G) + tau^2(G) (rank k). The factor base, however, is the union of <tau, -1> orbits: it contains P and -P, and every tau^i G. Two families of relations hold for every choice of generator yet lie outside that span:
- the negation identities P + (-P) = O;
- the tau-shifted kernel relations tau^i (2 + tau + tau^2) G = O.

Collisions caused by these were therefore counted as informative.

**Method.** `classify.py` replays `census_one` with the archived code, imported unchanged from `experiments/EXP-CERTBIN-66e167/implementation/`, using the same seeds and the same sampling. For each colliding pair it writes the difference as sum_j c_j(tau) G_j, with each base point written s * tau^i * G_j. The pair is classified as follows:
- **STRUCTURAL** when c_j(lambda) = 0 mod r for every generator j, so the relation holds for any choice of generators;
- **GENUINE** otherwise, meaning the collision depends on the discrete logs of the generators.

**Result.** The raw counts reproduce the archive exactly.

| seed | k | raw pairs (archived) | structural | genuine | genuine / E |
|---|---|---|---|---|---|
| 2026100311 | 2 | 17 | 16 | 1 | 0.20 |
| 2026100311 | 3 | 5 | 3 | 2 | 0.40 |
| 2026100312 | 2 | 38 | 33 | 5 | 1.00 |
| 2026100312 | 3 | 7 | 3 | 4 | 0.80 |

`result.json` holds three structural examples per cell, each written as (generator, sign, tau exponent).

**Reading (derived, not a decision)**
- The archived k=2 excess is explained by structural identities that the instrument's kernel filter omitted. It is not a property of the tau^2+tau+2 quotient.
- After those identities are removed, three of the four cells lie inside [1/2, 2]. The fourth (seed 2026100311, k=2) lies below the band: 1 genuine pair against an expectation of 5.
- A correct birthday expectation would also discount sum classes that the structural identities make coincide. That refinement is not computed here.
- What this calls for is a Coordinator correction of EV-CERTBIN-691499 and DEC-20261004-d70aac, by an additive record. No record has been edited.

**Regenerate:** `python3 classify.py > result.json` (about 1 min; builds the r = 130873 discrete-log table).

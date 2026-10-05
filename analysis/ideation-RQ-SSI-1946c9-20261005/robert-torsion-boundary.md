# Primary-source intake: full-torsion recovery boundary

Scope: supplementary source intake for GOAL-SSI-2fa82a. This is not a run,
a new attack, or an impossibility claim about EndRing-based encryption.

Source: Damien Robert, *Breaking SIDH in polynomial time*, ePrint 2022/1038.
The inspected PDF identifies its version date as October 7, 2024. Retrieved
from the archived primary PDF:
`https://web.archive.org/web/20260823023323id_/https://eprint.iacr.org/2022/1038.pdf`.
SHA-256: `52b371e245085709689e8c94aec0af2f287ad145fbaa170ac6f627bc88e5384e`.
Verified by: root construction session, 2026-10-05. Read: introduction through
Remark 1.2, Section 2's embedding and model caveats, and Section 6.4's
Lemma 6.3/Example 6.4 and Section 7. No full-paper read is claimed.

## Exact source statements

Theorem 1.1 assumes coprime integers N_A > N_B with known factorizations,
a rational N_A-torsion basis of E_0, and the images of that basis under an
N_B-isogeny phi_B. A four-squares decomposition of N_A - N_B gives an
eight-dimensional embedding. The evaluation algorithm does not require the
source endomorphism ring. Its arithmetic-operation bound is polynomial in the
largest prime factor of N_A and logarithmic in N_A; efficient kernel recovery
also uses a rational N_B-torsion basis and the stated factorization/smoothness
conditions.

The second bullet of Remark 1.2 explicitly extends recovery to N_A^2 > N_B,
pointing to Section 6.4. In that section, Lemma 6.3 reconstructs an Ne-isogeny
F with e dividing N when the action on N-torsion and appropriate bases on
both sides are known and its kernel has the required rank. It factors F into
an N-isogeny and an e-isogeny, computing one kernel from the restriction and
the other through the dual. Example 6.4 applies this to the four- and
eight-dimensional constructions, including e = N. The concluding Section 7
summarizes recovery of the underlying isogeny when N_A^2 >= N_B and N_A is
sufficiently smooth.

## Interface consequence to verify in review

A candidate publishing the full action of a degree-D isogeny on smooth
N-torsion cannot treat sqrt(4D) < N < D as a security boundary merely because
Theorem 1.1's initial presentation uses N_A > N_B. Its proposed injectivity
condition N^2 > 4D lies inside the extended source condition N_A^2 > N_B
after setting N_A = N and N_B = D. A review must still check rational torsion,
factorizations, kernel rank, curve-model conversions, and smoothness costs for
the actual candidate. The existence of a finite-level unique lift is neither
a private decoder nor evidence of an EndRing-dependent security advantage.

This source does not by itself cover an arbitrary partial, masked, noisy,
non-smooth, or differently encoded torsion interface. Such modifications need
their own public encryption and private message-recovery algorithms, current
prior-art comparison, and separately stated assumptions. Nothing here rules
out a different EndRing PKE construction.

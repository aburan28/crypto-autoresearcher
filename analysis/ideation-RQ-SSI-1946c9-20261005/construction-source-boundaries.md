# Additional construction sources, 2026-10-05

Scope: constructive follow-up to GOAL-SSI-2fa82a / RQ-SSI-1946c9.
These are primary-text interface notes, not experimental evidence. The root
construction session inspected the specified sections; no full-paper read is
claimed for these four additional sources.

## FESTA

Source: ePrint 2023/660, archived PDF
`https://web.archive.org/web/20260429140607id_/https://eprint.iacr.org/2023/660.pdf`.
SHA-256: `cfa2c92cf8a40e6c27c5679c5468936c65a35dcbe77a1e9e791035f500c0d679`.
Read: sections 3 and 4, including Algorithms 1 and 2 and Problems 6–8.

The secret consists of a connecting isogeny and a matrix that unmasks torsion
images. Public evaluation computes two isogenies and applies a common mask.
Commuting masks let inversion expose the torsion action of a composition and
invoke torsion recovery. The paper already mentions circulant matrices as an
alternative to diagonal masks. Merely choosing another commuting matrix family
would not establish a new mechanism.

Its stated inversion assumption is double scaled-torsion isogeny recovery
(CIST2), with a decisional hybrid. Full EndRing recovery is not the stated
one-wayness game. A proposed use of this construction must keep the matrix,
connecting-isogeny, correlated ciphertext data, and hybrid assumptions visible.

## POKE / POKÉ

Source: ePrint 2024/624, archived PDF
`https://web.archive.org/web/20241009051546id_/https://eprint.iacr.org/2024/624.pdf`.
SHA-256: `010faef9c893d1460c3a69fce256da86cedd1fd8b2c5f416821b65bd42b1b66b`.
Read: introduction; section 4, Algorithms 1–2, Protocol 2, Problems 3–5 and
Theorem 6; Appendix B; and Appendix C's assumption comparison.

This exact archived version is titled *POKE: A Framework for Efficient PKEs,
Split KEMs, and OPRFs from Higher-dimensional Isogenies* and lists Andrea Basso.
It is not silently identified with the later Basso–Maino proceedings version.
The front-page correction invalidates the split-KEM/OPRF validation assumption
and explicitly says the section 4 PKE is unaffected.

The PKE key is a masked higher-dimensional representation of an isogeny of
secret degree q(2^a-q). The sender computes two parallel smooth isogenies. The
recipient removes its masks, reconstructs a higher-dimensional isogeny, and
recovers the shared point used to mask the plaintext. The IND-CPA statement is
under C-POKE in a random-oracle model. Generating an endomorphism during KeyGen
does not replace that computational assumption by plain EndRing.

The source already includes rerandomization that hides the initial curve's
endomorphism ring, and describes its assumptions as isogeny problems with level
structure. Those are explicit prior-art boundaries for a new proposal.

## PIKE

Source: ePrint 2026/473, archived PDF
`https://web.archive.org/web/20260525004010id_/https://eprint.iacr.org/2026/473.pdf`.
SHA-256: `c46511f6f53db87a51b9229d92c03b35da68adc83123392e7adc7cf9d802e8aa`.
Read: section 5.1's C-PIKE/C-POKÉ/C-LIT-SiGamal comparison and assumption
definitions. The current ePrint landing page was also retrieved.

PIKE already proposes deriving the shared value using pairings and reveals
masked images of individual torsion points. Its paper does not supply a formal
one-sided reduction from C-PIKE to C-POKÉ. The proposed relationship to
C-LIT-SiGamal is explicitly described as heuristic, with a rigorous reduction
remaining uncertain. A one-point ciphertext or a pairing-based shared value is
therefore a known construction direction, not a sufficient novelty argument.

## Unmasked-torsion historical boundary

Source: Maino--Martindale--Panny--Pope--Wesolowski, *A Direct Key Recovery
Attack on SIDH*, ePrint 2023/640, archived PDF
`https://web.archive.org/web/20260920104024id_/https://eprint.iacr.org/2023/640.pdf`.
SHA-256: `8158a5a1f22f0b08ed07a42d11b99eacd623881f378460966e8c5115e003f581`.
Read: introduction and section 4's Theorem 2 and immediately surrounding scope.

The paper explicitly includes SÉTA in its affected scope. It distinguishes
SSI-T (an isogeny problem augmented with torsion images) from pure isogeny
hardness. Under GRH, efficiently represented EndRing information permits the
auxiliary isogeny construction used by its method. The introduction also points
to a later polynomial-time method for an unknown source ring. Its section 4
specializes to the stated B>A interface; these scope conditions must be checked
before transferring the attack statement to a newly chosen torsion/degree ratio.

Consequently, SÉTA remains usable as a published correctness/typed-interface
control, but the original paper's security statement cannot be treated as a
current security endorsement. Withholding the source EndRing alone is not an
audited security argument for publishing unmasked full torsion images.

## Required constructive distinction

A new candidate must name the mathematical operation that supplies the
recipient's inversion advantage. It must explain both why encryption can use
that interface publicly and why its security game connects to the declared
EndRing problem. An endomorphism used to generate keys, a change of mask, an
unproved uniqueness assertion for an endpoint path, or a generic wrapper around
one of these schemes does not discharge either obligation.

Novelty outside the inspected sources remains unverified. No construction,
security proof, or negative scientific conclusion is recorded by this note.

# EigenX-v2 prescribed-path methodology

This is a prospective zero-run construction-or-obstruction round under
`GOAL-SSI-2fa82a`. It evaluates exactly one prescribed-degree,
unique-isogeny-path recipient mechanism and an authenticated IND-CCA KEM/DEM
construction around it. It does not assume that the path is unique, that a
complete endomorphism ring makes recovery efficient, or that an IND attacker
can be turned into an EndRing solver.

The round separates six questions: the exact EndRing and key distributions;
executable honest algorithms and byte grammar; correctness; whether the full
ring is necessary rather than a strict quotient; the correctly directed
attacker-to-complete-ring reduction; and the complete adversarial view. Every
map, auxiliary datum, operation, bit length, retry and failure is charged.

Primary texts for Seta, SiGamal/C-SiGamal, key-updatable PKE, LIT-SiGamal,
Page--Wesolowski/OneEnd and the invoked CCA transform must be inspected or an
exact retrieval impediment recorded. An authenticated shell around the old
CEST line evaluator is retained only as a non-EndRing control: repairing its
bit-flip does not make it the batch candidate and cannot discharge O5.

All work is symbolic and source-grounded. Scientific, implementation,
formalizer, benchmark and parameter-selection runs are forbidden. The final
record must include a Markdown report, editable Mermaid source, SVG, inspected
PDF and visual-inspection receipt even when the result is negative or
inconclusive.

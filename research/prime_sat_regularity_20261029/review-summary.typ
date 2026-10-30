#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(font: "DejaVu Sans", size: 9.7pt)
#set par(justify: false)
#text(size: 20pt, weight: "bold")[A checked regularity reduction for two-summand prime-field systems]

#text(fill: rgb("#235a3a"), weight: "bold")[DEC-20261029-ce5c57: approve scoped archival acceptance]

One independent reviewer completed a blind derivation and a later comparison. All seven assigned mathematical joints hold within the stated hypotheses. This is a generating-system algebraic result. No hypothesis/evidence/corpus promotion or persistent-goal completion is made. Official archival acceptance requires the separate native ledger binding.

#image("review-summary.svg", width: 100%)

== Exact claim
Let E over F_p be nonsingular, p greater than three, and R=(r,t) finite rational with nonzero t. Each of two abscissas is an injective affine map of s Boolean bits, with s at least two, nonzero weights and two to the power s at most p. F0 consists of the Boolean equations and the fixed-target S3 quartic. F1 adds both exact multilinear rejection predicates; both must be nonzero.

$ d_("reg")(F_0) = s + ceil((s+2)/2) = 1+s+floor((s+1)/2) $
$ d_("reg")(F_1) <= s+floor((s+1)/2) = d_("reg")(F_0)-1 $

The two lists generate the same affine ideal. Degree means the first degree filled by the ideal of the *listed generators' highest homogeneous parts*. It is not an invariant of the common affine ideal alone. A constant-one predicate gives degree zero and inconsistency; a zero predicate loses the stated strict-reduction guarantee.

#pagebreak()
== Observation and custody
Producer TASK-20261029-5a92e3 has snapshot commit `81957e6eda`; blind TASK-20261029-931a6d has snapshot `ccff5e6e1c`. Both actual native snapshot contracts were checked. Comparison TASK-20261029-160be6 continued the same independent session after blind archival. Full 40-character identities and SHA256 hashes are in `review-inputs.json`.

The native independence checker initially rejected two Git-addressed aliases of authorized blind files. Exact blob hashing confirmed identical bytes. A narrow post-review parser repair retained all grants and attestations; the corrected native check returned zero with no findings. Its source hash is recorded in the manifest. The technical receipt reports 113 passing tests, including nine new identity regressions. These are software tests, not scientific samples. The original failure and initial sparse-checkout test-import failure remain retained.

== Comparison: all seven scoped joints hold
#table(columns: (1.12fr, 2.25fr), inset: 5pt, stroke: 0.4pt + rgb("#cbd5df"),
 [*Joint*], [*Independent reason*],
 [Definition / generators], [The listed-highest-part convention and actual affine Boolean system are distinguished.],
 [Block Lefschetz], [Nonzero weights and characteristic zero or p greater than s supply blockwise maximal ranks.],
 [Tensor threshold], [Full multigraded ranks establish both vanishing and preceding-degree nonvanishing.],
 [Block top], [Complement multiplication generates the top monomial; zero and unit cases remain explicit.],
 [S3 / affine ideal], [Rational line factorization supplies lifts, including repeated coordinates; the Boolean product algebra proves ideal equality.],
 [New windows], [Hasse supplies a rejected start at p greater than three on odd-order curves, without a useful-yield or fixed-window guarantee.],
 [Costs / scope], [Construction and storage are charged; no algorithmic advantage is inferred.],
)

Full arguments and source anchors are in `review.md`, its immutable attestation and `TASK-20261029-931a6d/blind-rederivation.md`. The Coordinator inspected all three. Odd-s central binomial ties are handled by the rank cutoff. Expected coordinate search assumes uniform independent samples; deterministic scanning may require p tests.

== Inference
The quartic top modulo squares is the product of the squares of two block-linear forms. Strong Lefschetz and tensor ranks give the exact baseline. Each nonzero block form generates its top monomial through complement multiplication, yielding the lower augmented vanishing threshold. The m-block extension is algebra only: for m at least two and e between one and s, the baseline is $(m-1)s+ceil((s+e)/2)$ and the augmented upper bound is $(m-1)(s-1)+ceil((s+e)/2)$. It supplies no higher-summand rational-membership equivalence.

#pagebreak()
== Rationality, construction and limits
For the elliptic application, write N=x1*x2-r(x1+x2)-2r²-a. On S3=0, lambda=N/(2t) gives a rational line through the negative target whose cubic intersection factors at the two candidate abscissas and r, with multiplicities. Thus both points have rational ordinates. The split reduced Boolean quotient then establishes equality of affine ideals. This is stronger than equality of radicals, but it does not provide a cheap multiplier certificate.

For newly chosen windows on an odd-prime-order curve at p greater than three, Hasse gives at least p/2 minus sqrt(p) rejected abscissas. A rejected start makes the predicate nonzero when two to the power s is at most p. It does not transform an unchanged fixed window or guarantee a useful nonempty factor base.

Dense construction costs order two to the power s times log p field multiplications, order s times two to the power s transform operations, and order two to the power s field elements per distinct domain. Search costs are additional. A constant-one window is empty, not useful yield.

No solving-degree, first/last-fall-degree, runtime, relation-yield, unknown-scalar recovery or general ECDLP advantage is established. No formal proof assistant or novelty audit was used. The model and effort are dispatch-reported native Codex gpt-6.1-sol/xhigh; no provider probe authenticated them. There is one independent reviewer in two phases. Exact first-reveal wall-clock time was not separately recorded; archive order and the reveal event were.

The previous PNEXT native receipt remains invalid_output. Its measurements and separate supplemental replay were not revalidated or used as proof evidence here. Existing producer proof-status and old records stay unchanged. The native checker verifies declared-read consistency, not attestation truthfulness or mathematical correctness.

== Next actions and visual inventory
Complete rendering/inspection and the existing ledger archive TASK-20261029-eb09c9. Then proceed with the separately admitted grouped-indicator package and fresh blind-only review. No grouped, higher-arity or single-invalid-word future claim is accepted here. The persistent goal stays active.

The prior study diagram/report and canonical lead LEAD-ICP-shared-coefficient-membership were inspected and left unchanged. The lead concerns a different coefficient-membership mechanism and receives no disposition change. This report has an explanatory proof/custody diagram; there is no performance chart because no scientific dataset was generated.

== Primary references and durable inputs
- Caminata–Gorla, Definition 1.4: #link("https://arxiv.org/html/2112.05579v2")[arXiv:2112.05579v2].
- Phuong–Tran, Theorem 2.7: #link("https://arxiv.org/html/2211.13548")[arXiv:2211.13548].
- Kosters–Yeo, Section 2 and Proposition 2.1: #link("https://arxiv.org/html/1503.08001")[arXiv:1503.08001].
- Sutherland, Hasse Theorem 7.3: #link("https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf")[MIT 18.783 Lecture 7].

Local audit trail: `review-inputs.json`; `review.md`; `coordination/prime_sat_regularity_20261029/amendment-03-git-source-identity/`; `problems/review-git-source-identity-mismatch.md`. The manifest binds original failure, corrected pass, regression receipt, unchanged source bytes and native archive identities.

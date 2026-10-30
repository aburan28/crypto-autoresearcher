#set page(paper: "a4", margin: (x: 17mm, y: 15mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.4pt)
#set par(justify: false, leading: 0.5em)
#set heading(numbering: none)
#text(size: 20pt, weight: "bold")[From lower degree to a testable solver question]

#text(fill: rgb("#235a3a"), weight: "bold")[DEC-20261029-266f95 — approve scoped archival acceptance]

The frozen producer and one independent derivation agree on exact symbolic counts and a conditional complementary-point reference. *Seven review joints hold.* The software execution component remains *inconclusive in the independent review*; a separate root receipt records *18 fixed correctness tests passing*. No scientific or comparative run occurred. Archival effect requires the native ledger binding.

== Observation: what the lower degree counts
For the accepted raw lists, retain even s≥2, p>max(3,s), nonzero original weights, two disjoint s-bit coordinate blocks, nonsingular short Weierstrass curve and finite rational R=(r,t), t≠0. DEC-0857a9 supplies d_bit=1+3s/2 and d_group=s+1. These are prior premises.

Before S3, the local highest-part Hilbert series are (1+T)^(2s) and (1+3T)^s. Prefixes are C_bit(D)=Σ binom(2s,j), j≤min(D,2s), and C_group(D)=Σ binom(s,j)·3^j, j≤min(D,s).

#table(columns: (1.5fr,1fr,1fr,2fr), inset: 4pt, stroke: 0.4pt + rgb("#c8d1db"),
 table.header([*Position*],[*Bit cutoff*],[*Group cutoff*],[*Equality C_bit=4^s*]),
 [One below],[3s/2],[s],[Never for even s≥2],
 [Regularity],[3s/2+1],[s+1],[Only s=2],
 [Mutant cap],[3s/2+2],[s+2],[Only s=2,4],
)

At every paired position, *4^s/2 ≤ C_bit ≤ C_group=4^s*. These inventories share an exponential order. Ambient capacities instead equal binom(2s+D,D) and binom(3s+D,D). Neither is necessary algorithm work. Adding constant one leaves the local inventory unchanged but makes the full system trivially inconsistent. Local and full highest-part quotients, affine quotients, and actual rows/pivots are distinct.

#image("review-summary.svg", width: 100%)
#text(size: 8pt)[Symbolic formulas and a method diagram; no measured values, RUN IDs, samples or uncertainty bars. Producer Sections 1–4; independent pre-code Sections 1–5.]

#pagebreak()
== Comparison: complete one-domain reference
Assume any *mathematically prime p>3*, nonsingular E:y²=f(x)=x³+ax+b, finite R=(r,t), t≠0, and duplicate-free affine domains D1,D2. Domains may overlap. Enumerate all D1 lifts P, compute Q=R−P, exclude infinity, and test x(Q) in D2. All mode outputs the complete ordered projected set and witnesses; K≤2|D1|−1 when r∈D1, otherwise K≤2|D1|. First mode always declares completeness false.

With h=x−r and c=−rx−2r²−a, the independent calculation gives:

$ S_3 = h^2 z^2 + (2h c-4t^2)z + c^2-4t^2(x+r) $
$ Delta = 16t^2 (x^3+a x+b). $

For h≠0, y²=f(x) gives roots (−(2hc−4t²)±4ty)/(2h²), with one root when y=0. For h=0, retain the unique linear root x(2R). P=R gives infinity, while P=−R gives finite 2R. Tangencies, zero ordinates and order-three targets remain covered symbolically. No operational full-y scan or D1×D2 loop is used.

The separate checker imports no producer helper. It verifies exact D1 coverage, roots and both signs, complete second roots and projected-set equality, then point sums independently. For a nonroot, a global Euler-certified nonsquare Z and nonzero w with w²=Zf(x) give a certificate. *Producing w also costs a square root.* Division-free chord/tangent equations check each witness. The API does not prove primality or execution counters.

#table(columns: (2.7fr,2fr), inset: 4pt, stroke: 0.4pt + rgb("#c8d1db"),
 table.header([*Actual independent joint*],[*Verdict*]),
 [Prefix counts; ambient/work distinction],[holds; holds],
 [Rational completeness; complementary reference],[holds; holds],
 [Certificate checker; cost/setup; decision boundary],[holds; holds; holds],
 [Mode and software scope],[Mode audit holds; execution inconclusive],
)

The reviewer found no source defect falsifying the conditional algorithm/checker. It ran no tests and read no result receipt. Root separately observed one fixed suite of 18 passes at p=5,7,13, with two p=7 curves and tiny exhaustive software oracles. This does not independently replicate execution or prove all-prime software behavior.

== Inference: the costs that a future test must pay
Let B1=|D1|. Producer cost is setup + O(B1·(E+S_actual+G+M+1)) + O(K log(K+1)) comparisons + certificate/output construction and serialization. E is Euler testing, S_actual includes every root call’s initialization and verification, G is group work, and M is D2 membership. Nonsquare rows require twisted roots too. Deterministic nonsquare search is charged by actual probes; expected-constant search is not claimed. The recorded euler_probes field counts setup only.

Checker cost is its own setup + one Euler(Z) + O(B1·(I+M+1)) root/certificate work, output comparison and O(K) field operations for division-free witnesses. I is inversion; no new square root is extracted. Retained records, indexing and expected hash assumptions, sorting, input bit lengths, serialization and arithmetic bit costs remain charged. This is ordinary Tonelli–Shanks without a constant-time claim.

Future comparisons must match domains, projection multiplicity, first/all mode, exceptions, setup/reuse, actual solver work, memory, reconstruction and checking, including this reference. New source/protocol and native admission are required before any comparative run. The reviewer’s sharper asymptotics stay outside this frozen producer acceptance.

#pagebreak()
== Limitations and the concrete next step
The review retains three coverage limits: no dedicated mutation of a genuinely square radicand into a nonsquare-status row; invalid-input checker tests can also reject on a changed input digest; no dedicated order-three target fixture or all Tonelli–Shanks valuations. These limit control claims, without refuting the symbolic source argument. Before comparative use, isolate them in a prospective additive software amendment and preserve the frozen package.

The lower degree does not establish or rule out a SAT/Gröbner gain. Two solving-degree upper bounds do not order actual solving degrees. Arbitrary auxiliary or reduced encodings need their own graded proof. No formal proof, novelty finding, first/last-fall improvement, measured solver advantage, unknown-scalar recovery or general ECDLP speedup is established. GOAL-PFDR-fd09e0 remains active; no H/EV/KN or goal transition occurs. Historical PNEXT invalid_output remains unchanged.

== Review and custody qualifications
Producer TASK-20261029-2e3655: `8c9cbfb9c785`; verified eight-path snapshot: `c15cf8e7a3e0`. Review TASK-20261029-58d7a7: `844cbdf419c4`; completed release: `3e0b34465382`. Root claimed ledger TASK-20261029-bd67d5 at `f973a55dc291`, epoch 1. Exact hashes and parsed native receipt are in review-inputs.json.

The reviewer sealed precode-derivation.md with an observed 19:56:55 UTC clock and hash, then observed 19:57:00 UTC before source access. These are attested read-order observations, not independent timestamps or separate pre-code archival custody. Exact first-byte read time is unknown. Division-free checking and implementation-specific cost refinements are explicitly post-code. One reviewer is not a quorum or a line-by-line blind audit of producer prose. Native gpt-6.1-sol/xhigh was requested without provider authentication or an exposed opaque UUID. The reviewer records no post-dispatch exchanges.

The unchanged native checker returned zero at 2026-10-29T20:01:23.964499+00:00. Its exact parsed content and original receipt SHA256 are embedded in the manifest; parsed content is not described as identical JSON serialization. All producer/review/source hashes were compared successfully. No source, receipt or producer proof-status file is rewritten.

Root reported an additional S3 checkpoint push failed because the required ecc-challenges-new profile/upload token was unavailable and AWS profiles were empty. No upload, bypass or retry followed. Git publication is the recorded source/review custody; there is no verified new S3 copy. This infrastructure limitation asserts nothing about the mathematics.

Root must render and inspect every PDF page, fill actual rendering/custody fields, and verify the exact nine-path ledger archive. The manifest does not certify its own future archive. Existing diagram.svg, review-summary.svg and grouped-review-summary.svg in the regularity study were inspected and left unchanged: they are historical records of separate prior proof/review scopes. The present diagram supplements them without changing a shared frontier or scientific status.

== Primary-source boundaries and record anchors
#text(size: 8.7pt)[
Salizzoni, Definitions 2.4–2.5, Propositions 3.10/3.13: #link("https://arxiv.org/html/2304.13485")[arXiv:2304.13485]. The specified mutant-closure upper bound is not actual algorithm necessity. Grouped raw s=2 retains input degree four and does not meet Proposition 3.13’s input-degree premise.

RFC 9380, #link("https://www.rfc-editor.org/rfc/rfc9380.html#appendix-I")[Appendix I] and #link("https://www.rfc-editor.org/rfc/rfc9380.html#appendix-F.2.1.1")[F.2.1.1]: standard square-root and sqrt-ratio mechanisms, not novelty or reproduced performance. Coordinator rechecked the relevant primary text; source hashes are unknown.

Producer: cost-bridge.md Sections 1–5, reference.py, check_reference.py, test_reference.py and unit-test-results.json. Independent review: TASK-20261029-58d7a7/precode-derivation.md, blind-review.md and attestation.yaml. Prior algebra: DEC-20261029-ce5c57 and DEC-20261029-0857a9. Full identities, limitations, graph audit and future archive union: review-inputs.json.
]

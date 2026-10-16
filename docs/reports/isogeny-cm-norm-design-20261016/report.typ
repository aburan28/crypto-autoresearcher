#set page(paper: "a4", margin: 18mm)
#set text(font: "Libertinus Serif", size: 10pt)
#set par(justify: false, leading: 0.55em)
= Compact CM norm certificate
#text(size: 9pt, fill: rgb("#47637a"))[Proposed design | 2026-10-16 | GOAL-ISOU-f30a07]
#v(8pt)
#image("diagram.svg", width: 100%)
== Ranked next action
#text("Proposed design for GOAL-ISOU-f30a07, separate from the live expanded P-192/50,341 experiment. Rank 1 remains the already launched expanded-map attempt and its independent verification. Rank 2 is independent proof and verification-contract review of a compact known-endomorphism self-isogeny on exact secp256k1. Implementation follows only after review corrections; this document authorizes no scientific execution.")
#parbreak()
#text("The proposed bounded target is ell = 2^8191 - 1. This is a selected certificate target, not a claim of a finite maximum or a worldwide record. Compact evaluators, known-endomorphism self-maps and fully expanded maps remain distinct comparison categories. No algorithmic novelty, security or ECDLP advantage is claimed.")
#parbreak()
== Proposed proof decomposition
#text("Freeze the secp256k1 source E/F_p: y^2 = x^3 + 7, p = 2^256 - 2^32 - 977. Import and hash the complete registered (p,a,b,n,G) model from the pinned catalogue; pin beta as an explicit nontrivial cube root of 1. The endpoint is the identical model, not another curve chosen only by j-invariant or order.")
#parbreak()
#text("Joint 1: prove phi(x,y) = (beta*x,y) is an F_p automorphism, fixes infinity, has order three, and has dual phi^2. Establish phi^2 + phi + 1 = 0 as endomorphisms, using the absence of zero divisors rather than point sampling. For unreduced signed integers a,b define alpha = [a] + [b]phi. Derive its dual and geometric degree from the exact ring relation and norm.")
#parbreak()
#text("Joint 2: derive deg(alpha) = a^2 - a*b + b^2 = ell, prove alpha is nonzero, and establish separability from prime ell different from p. Check the differential independently: phi pulls dx/(2y) back by beta, so alpha has tangent multiplier a + b*beta mod p. A zero multiplier contradicts this separable contract and must reject. Separate the prime-degree-p Frobenius (zero differential) from 1-Frobenius (degree n and differential one, but zero action on rational points). These are proof obligations; no native certificate is present at design time.")
#parbreak()
#text("Joint 3: independently certify exponent 8191, replay Lucas-Lehmer from s0=4 through exactly 8189 recurrence steps modulo ell, and bind the terminal residue and transcript. Cornacchia supplies integers x,y satisfying x^2+3*y^2=ell; set a=x+y,b=2*y and verify the integer norm exactly. Use Keith Conrad Theorem2.2 for the standard terminal-zero criterion with an odd prime exponent; per-iterate GCDs from the Gross alternate sufficient criterion are optional diagnostics. Freeze sign/root selection and all unreduced coefficients in the manifest. A stored probable-prime flag or producer PASS is insufficient.")
#parbreak()
#pagebreak()
== Independent evaluation and collision audit
#text("Joint 4 separates geometric degree from finite-group action. On the order-n public subgroup, alpha and alpha+[n] agree, yet their integer norm degrees generally differ. The required degree-alias control changes a to a+n while preserving subgroup outputs; the checker must distinguish the geometric certificates. Reducing a,b modulo n before serializing the expression loses that information and must reject the claimed certificate.")
#parbreak()
#text("Producer and verifier use independently implemented point arithmetic and scalar multiplication. Replay infinity, G, -G, fixed public scalar multiples, and independent hash-to-curve points from frozen domain-separated seeds; verify on-curve membership and subgroup order. Verify the dual composition on these points and compare the subgroup eigenvalue only as an evaluation control. Point checks diagnose implementation errors; they do not establish the degree theorem or enumerate an ell-point kernel.")
#parbreak()
#text("Baseline and nearby controls: alpha=phi (degree1), alpha=[2] (degree4), and (a,b)=(3,1) (norm7), checked against an independently expanded low-degree reference. Reject beta=1, swapped beta/eigenvalue pairing, mutated norm coefficients, changed source model, invalid points, composite norm, prime exponent11 with composite M11=2047, composite-exponent9 precondition, and forged certificate hashes. Both beta roots are valid only with their corresponding explicit expression; a root change is not inherently a false map.")
#parbreak()
#text("Identity records: any claimed polynomial identity ships identity.certificate/v1 beside the claim, with its actual evaluated/proved tier. A certificate over 2^61-1 alone cannot prove an equality over Z, the endomorphism embedding, degree or separability. Require exact symbolic integer expansion for (a+b*t)*(a-b-b*t) = a^2-a*b+b^2-b^2*(t^2+t+1), rather than inferring it from modular samples; also retain the norm-to-morphism theorem. Require exact symbolic integer expansion for the algebraic reduction and preserve the independently reviewed theorem dependencies. No kernel or expanded rational-map artifact is promised by this compact design.")
#parbreak()
== Native implementation and evidence contract
#text("After proof review, hand implementation to an Executor in the isolated crypto checkout. Prefer a separate auto-discovered Rust binary and CM-only modules under tools/isogeny-cli/src/bin; use existing num-bigint/num-traits/serde_json/SHA-256 dependencies and independent verifier arithmetic. Do not edit root src or Cargo files, catalogue, challenge board or season. A small dispatch in tools/isogeny-cli/src/main.rs is permitted if exposing a separately named compact command; an initial separate binary remains partial until installed or explicitly ReleaseMe-packaged. Coordinator does not implement experiment algorithms.")
#parbreak()
#text("Commands should separate construct, verify and evaluate, refuse replacing any existing output, bind source/binary/input hashes, exact signed coefficients and source identity, certificate paths and checker versions. A verifier recomputes primality/norm/geometric conditions instead of trusting producer flags. Resource receipts separately charge primality, modular root/Cornacchia, certificate construction, point evaluation, independent replay, failed attempts, wall/CPU/RSS and serialized bytes. No speed claim follows from a degree number.")
#parbreak()
#text("Implementation tests exercise the fixed controls and adversarial mutations; the M8191 scientific instance is not run during implementation. A frozen executable protocol and independent review are required before scientific dispatch. Memory/concurrency protect the host, while campaign estimates remain advisory. Keep the active expanded-map lane first and use a separate compact evidence directory and comparison category.")
#parbreak()
#pagebreak()
== Review ownership and stopping decisions
#text("Independent review task TASK-20261016-3b4ca9 owns all four explicitly enumerated joints, with a blind derivation from definitions and sources rather than a stored producer verdict. Requested policy review-adversarial, effort xhigh; actual native Codex model and served effort are unavailable, and no API/provider substitution is authorized. The prior is that the standard norm mechanism is sound, with degree/action confusion the principal risk.")
#parbreak()
#text("A concrete defect revises this contract before implementation. A passing review permits bounded native implementation and tests, not a scientific result, board promotion or worldwide claim. An implementation or resource failure preserves the failed attempt and leaves the mathematical question open. Review evidence and any later Coordinator decision are archived separately from this proposed design.")
#parbreak()
== Sources and graph status
#text("Retrieved and read by coordinator: Andrew Sutherland, MIT18.783 Fall2023 Lecture12, degree/dual and reduced norm; Lecture5, separable/inseparable degree. MIT18.783 Fall2025 ProblemSet2, Cornacchia algorithm. Keith Conrad, The Lucas-Lehmer Test, Theorem2.2 (selected terminal-zero formulation). Benedict Gross, An elliptic curve test for Mersenne primes, section1 (alternate criterion). References support the named general tools; the exact secp256k1 construction and M8191 instance remain proposed and unmeasured.")
#parbreak()
#text("Canonical challenge leaderboard and the parent world-frontier survey were checked for scope: this proposed separate category supplies no new admitted expanded map, so no canonical edge or score changes. Diagram labels every edge proposed. No quantitative graph is appropriate because this search/design round generated no measurements.")
#parbreak()
=== Primary references
#link("https://math.mit.edu/classes/18.783/2023/LectureNotes12.pdf")[#text("MIT Lecture12")]
#linebreak()
#link("https://math.mit.edu/classes/18.783/2023/LectureNotes5.pdf")[#text("MIT Lecture5")]
#linebreak()
#link("https://math.mit.edu/classes/18.783/2025/ProblemSet2.pdf")[#text("MIT Cornacchia")]
#linebreak()
#link("https://kconrad.math.uconn.edu/blurbs/ugradnumthy/lucas-lehmer-test.pdf")[#text("Conrad Lucas-Lehmer Theorem2.2")]
#linebreak()
#link("https://people.math.harvard.edu/~gross/preprints/Mersenne.pdf")[#text("Gross alternate LL criterion")]
#linebreak()

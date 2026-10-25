# Source-bound Atkin residue audit

Written 2026-10-24 UTC before the Atkin orders or residue sets were calculated. This extends the previous Elkies-only proxy; it is not an independent selection of a new cohort or a historical runtime measurement. No official hypothesis status changes.

## Question and population

Does including Atkin trace restrictions give a fixed small-prime point-counting proxy that separates all eleven named omissions from eight published controls in their four fields? Use exactly the nineteen UID-bound rows in `research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json`, SHA-256 `4a0df1de260e4533253ef591f7b084b73e86fac5e03558ec3609081c750f48fe`. Retain their exact p,n, trace, labels, UIDs and original Elkies-only cutoff. No additional curves or tuned subsets.

## Source and arithmetic

Schoof, *Counting points on elliptic curves over finite fields* (1995), printed pp. 239–242, describes the projective order of Frobenius and Atkin's partial trace information. Source PDF: https://jtnb.centre-mersenne.org/article/JTNB_1995__7_1_219_0.pdf; SHA-256 `9971fd4f8aae23fa9578967e20af5d27b7849e5f0d614b16cc5cb1346b095715`. Its relevant pages were visually inspected. Use the companion-matrix definition of projective order rather than the displayed root-of-unity formula, whose conventions are not needed here.

For every odd prime ell <= 997, compute chi = Legendre(t^2-4p, ell). Define an allowed trace set S_ell:

- chi = +1: S_ell = {t mod ell}, optimistically assuming the Elkies eigenvalue step is completed.
- chi = 0: S_ell = {u mod ell: u^2 = 4p mod ell}. This uses ramification information only, without assuming whether Frobenius is scalar.
- chi = -1: calculate the least r > 0 for which the companion matrix A=[[0,-p],[1,t]] has A^r scalar mod ell. Define S_ell to contain exactly the u with nonsquare u^2-4p and the same projective order for their companion matrix. In this case r divides ell+1.

Enumerate candidate traces exhaustively in F_ell, caching tables by field and ell. Require actual t in S_ell. Record every set, r, type and cardinality. Reconstruct original Elkies-only cutoffs as an input-binding control.

## Primary metric and its limit

For primes scanned in increasing order let M=product ell and A=product |S_ell|. Chinese remaindering gives exactly A allowed residue classes modulo M. Record the first ell with M^2 > 16p A^2, or null if none by 997. This is a **residue-density cutoff**: it makes 4 sqrt(p) A/M < 1. It is not a proof of a unique trace in Hasse's interval, an operation count, or a historical timeout. It omits the cost of obtaining r, modular polynomials, and the final match/sort search. The old Elkies-only cutoff is a paired descriptive control, not a separate confirmatory test.

Compare the primary cutoff across all 25 same-field omitted/published pairs. Report exact better/worse/tie counts and each field's values. A complete scalar selector requires a consistent monotone direction separating all omitted from all published controls; report any counterexample. Do not fit a second formula or threshold after inspecting results. No p-value or historical-cause inference.

## Verification and execution boundary

Independent Sage verification uses eigenvalue ratios in GF(ell^2) to check every real Atkin r and reconstruct each distinct allowed set from primitive roots of unity, rather than using companion matrices. It separately checks all Legendre symbols, ramified sets, CRT products, cutoff inequalities, UIDs and pair counts. Controls include trace sign symmetry, an explicit Atkin trace-zero case (r=2), synthetic scalar-matrix cases, a strict cutoff boundary, and the old 19 Elkies cutoffs. Watchdogs: 180 seconds for scanning and 300 seconds for independent verification; preserve any failure or censoring without a mathematical inference. One fixed scan, nineteen curves, 167 odd primes, 3,173 real cells; no random sampling or retry tuning.

Retain write-once raw records, commands, source/code/protocol digests, environment, stdout/stderr, timing receipt and verification. Produce a dated report, editable diagram/graph and visually inspected PDF. A complete split would be a lead requiring independent historical prediction and a mechanism, not proof of an ECDLP weakness or the old selection rule.

# May 1997 degree routines: exact source audit and application limits

28 October 2026 UTC, T-5518. Source-only observations and symbolic derivation; zero new native curve/control trials. The preceding class-group turn was progress. The full historical-selector goal remains active and unresolved.

The source comparison authenticates a dated splitting-degree bug report and identifies an unguarded linear-input path. It does not identify the original caller or explain any of the eleven reconstructed omissions. All 21 full identities and six streams are retained in cohort-crosswalk.csv; historical application remains UNDETERMINED for ten publications and eleven omissions.

## Exact source and chronology

The advertised LiDIA1.3 package captured17 May 1997 is2,343,749 bytes, SHA2560189dcbb3daab55cb39f213bf612d025b71aac6bd4ca7a5c09b687f47c98d387. Its README 1.3/header 1.2.0 discrepancy remains explicit. The exact factoring.c, compose.c, fac_vec.c, Fp_polynomial.h and poly_modulus.h were read without compiling them. The package's standalone ECO caller is absent; general polynomial utilities are present.

The pinned later snapshot at passagemath/upstream-LiDIA commit 23dac491f4cd96eb7de648a5cf90eb9ec77653c8 supplies five further source files. Every fetched Git blob matches its Git object hash. SOURCE-MANIFEST.json binds all ten original files by exact bytes/digest/URL; third-party bodies stay private in ignored .work.

The later ChangeLog lines15530-15535 records a15September 2001 fix to compute_splitting_degree that had caused an eco_gfp error. It identifies no exact input, introduction date or patch. Public factoring.cc Git history contains a complete 2.3.0 import in 2013 and a separate 2019 root-wrapper fix. That history cannot reconstruct the2001 change. The2019 change passes a polynomial-modulus object to power_x during general root filtering; the 1997 find_roots function instead assumes split input and has no such filter call. This later defect must not be backdated to1997.

## What the degree routines actually require

The1997 deterministic and probabilistic routines require a polynomial whose irreducible factors share a degree. Four normalized arithmetic bodies match the later endpoint: base_case, compute_split, rec_compute_degree and prob_compute_degree. Normalization removes comments/diagnostics/spacing and maps the modulus-degree accessor/type spelling; this is a bounded textual check, not compiled equivalence. tandem_power_compose differs in the field-modulus initialization API. The later deterministic wrapper also accepts a supplied known multiple of the common degree.

The later SEA caller handles all-fixed and one-fixed-root cases separately. In the two-fixed-root Elkies branch it removes both linear factors and reduces the Frobenius image before degree computation; the remaining nontrivial cycles have equal length. Thus simply imagining that this caller feeds the mixed full polynomial into the equal-degree routine would contradict the source read. Later constructors default to DONT_COMPUTE_SP_DEGREE, with Atkin bound 50 when enabled. Those defaults do not establish original NIST use.

## Intended randomized behavior, conditional derivation

The old routine draws a polynomial, applies the trace map, then draws a separate projection in min_poly. For squarefree equal-degree input of degree n>=2, d>=2 and m=n/d factors, independent uniform field draws give independent uniform component trace values when p>n. Pair collisions have probability at most m(m-1)/(2p). The documented minimal-polynomial projection error adds floor(n/2)/p. For d=1 the routine returns1 directly because the Frobenius image is X.

Within the documented range of prime auxiliary ell<800, n=ell+1<=798 and m<=399. Thus the per-call exceptional-degree bound is at most 79,800/p, which is less than2^-174 for all cohort field sizes. PROBABILITY-BOUND.md gives the derivation. This is an intended-algorithm bound under uniform independence and correct valid-input arithmetic, not measured output or a probability assigned to the historical deterministic RNG. It covers neither biased/randomness-consumption defects, malformed inputs nor another implementation.

## An unguarded linear-input path

For f=X-a, the reduced Frobenius image is a constant, so the source's h.is_x guard does not return. Factoring the integer degree 1 creates an empty factor list. The deterministic routine nevertheless calls its recursive helper with bounds 0,-1. The splitter then obtains mid=-2 and the following product range accesses index -1. LINEAR-EDGE.md records this static invalid-index path.

No native crash, compiler behavior or historical visitation has been executed here. The later endpoint still lacks an explicit low-level degree-one guard, so this observation is not identification of the2001 fix. The later SEA caller avoids the relevant cases before degree computation. Whether any original NIST invocation reached this path remains unknown for every curve. No omission is marked rejected from it.

## Coverage, verification and next discriminator

Source metadata seals13 files; private byte verification checks ten sources, including five Git objects. Fresh-directory public metadata replay and every 21-identity p,-3,b,n,seed,ordinal,timestamp/UID binding pass. The source crosswalk deliberately records original caller, actual polynomial degree, invocation and error policy as UNKNOWN for all 21, with no new curve-property predicate sweep. Operational retrieval/decoding errors and bounded unsuccessful searches are retained separately. Raw commit 7ba50faa68 precedes this report. No native code, profiler, RNG stream or new point count ran.

The source-boundary.svg diagram distinguishes authenticated bytes, derived intended behavior, the potential linear edge and missing historical application. Earlier signed-action/SEA graphs were checked and left unchanged: there is no new verified historical or attack edge. No official research-state transition is made. The P-224 cube/splitting observation remains separate.

The next discriminating evidence is the pre-fix 2001 source or an authenticated older caller showing which degree routine and polynomial it used, including failure handling. Native confirmation of the linear path alone would establish only a low-level defect; original reachability must still be demonstrated. Any new cohort execution requires a prospective frozen protocol and all 21 accounting. No outgoing contacts, subagents or memory writes.

Primary source links:

* [May 1997 captured package](https://web.archive.org/web/19970517195215id_/http://www.informatik.th-darmstadt.de:80/TI/LiDIA/linktop/LiDIA.tgz).
* [Pinned later degree routines](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/finite_fields/Fp_polynomial/factoring.cc).
* [Pinned ChangeLog, lines15530-15535](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/ChangeLog#L15530).
* [Pinned later caller, lines221-418](https://github.com/passagemath/upstream-LiDIA/blob/23dac491f4cd96eb7de648a5cf90eb9ec77653c8/src/ec_order/eco_gfp/eco_gfp/eco_prime.cc#L221).
* [2019 root-wrapper patch](https://github.com/passagemath/upstream-LiDIA/commit/8a0b29280e3504a16accd882b7807122a6219410).

Replay: python3 verify_sources.py (public metadata/input custody); python3 verify_sources.py --sources (also requires the pinned private source files). Neither command executes a point counter.

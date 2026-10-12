# Xedni: Cheon certificate snapshot and follow-up design

Date: 2026-10-07. Question: RQ-XEDN-3bfe2e. Proposed hypotheses: H-XEDN-0ea2b6, H-XEDN-4a5b50.
Archive scope: TASK-20261007-af0dee. This is a user-requested tracking snapshot, not an approved experiment or official evidence transition.

## What is established in the producer artifacts

**Measured:** a 4,001-parameter reproduction of the published p=353 example retained n=-1793 and n=181. **Certificate-checked by producer code:** all six root prime magnitudes, both rational ranks exactly two, both prescribed pairs independent modulo torsion, and four corrupted-input rejections. **Derived, pending independent review:** the conditional signed-square independence lemma in H-XEDN-0ea2b6. A rank bound does not supply a dependency. The two candidates have no recovery path through the required rational relation.

The imported files are byte-preserved, including historical wording about the original workspace and commands. They are external prior-work observations, not invented harness RUN records. Their historical scope is unchanged. Re-verification logs and the import hash check are retained separately in validation/.

## Exact construction and claim boundary

E/Q: y^2=x(x^2+A*x+B); D=A^2-4B; B*D != 0. E'/Q: v^2=u(u^2-2*A*u+D). The degree-two map phi has kernel {O,(0,0)} and formula (y^2/x^2, y*(x^2-B)/x^2). Its dual has kernel {O,(0,0)} on E' and formula (v^2/(4*u^2),v*(u^2-D)/(8*u^2)); the composite is [2]. Maps extend at the kernel points. Odd-order subgroup transport follows from this identity; there is no arbitrary-target coverage assertion or new computational advantage. Rational two-torsion forces even ambient order at odd good reduction, which restricts this family, not all lifts.

The lemma requires B=+/- a prime, P=(s^2,yP), Q=(-t^2,yQ), nonzero rational s,t, and two distinct positive prime factors f_plus/f_minus=A+2*s^2 +/- 2*yP/s. R=(f_minus,-2*s*f_minus) satisfies dual(R)=P. Mod-2 squareclasses prove independence. The extra A>0 assumption supplies the simple exact upper rank bound for the two historical examples; it is not needed for generic independence. Full proof and integer witnesses: [CERTIFICATION.md](imported/CERTIFICATION.md).

The source lifting formulas use prescribed residues only when their signed-square eligibility and congruences can be met. Neither this audit nor the proposed follow-up establishes arbitrary residue coverage. The original dependency-computation theorem assumes dependent global points; its coefficient computation is conditional on its eligible-prime hypotheses and excludes lift construction and screening costs. See imported/README.md for the audited hypotheses; we implement no recovery campaign.

## Follow-up hypothesis and parameters

H-XEDN-4a5b50 conjectures bounded existence of one exact dependency outside the sufficient independence hypotheses. This is untested. Same-sign coordinates may collapse a descent observable but may still be independent. Parameters are in [parameters.json](parameters.json): p={31,43,59,83}, eight target pairs per prime, all four sign patterns, 1<=t<=64 with at most four representatives per point, ordinate shifts -8..8, and primitive relation coefficient bound 8, both coefficients nonzero and both points certified non-torsion. Maximum proposal cells: 591,872; a 600-second, one-worker, 1-GiB execution budget is proposed. No lift-search runner or approved EXP is supplied. The target freezer has committed 32 input pairs: 75,140 eligible proposal cells and 96 of 128 sign arms ineligible. These are design eligibility counts, not dependency-search results. The target SHA256 is 55cfa8826a8c3eedcb599a5a6a0871e74ea49f68a41c806b7284230b627b5452.

For a formula-backed construction audit, write x_i=sign_i*t_i^2 and y_i=t_i*z_i. Then Z_i=sign_i*z_i^2-t_i^4=A*x_i+B. For distinct x coordinates, A=(Z_1-Z_2)/(x_1-x_2), B=Z_1-A*x_1. This solves point membership, not dependence. Require integral coefficients and good reduction matching the frozen source before any dependency classification.

Targets must be fixed first; no selecting dependent pairs after seeing lifts. The positive doubling control must succeed, historical independent controls must remain independent, and isomorphic-coordinate controls must preserve classification. Record every eligibility gap, rejection, exact lift, unresolved rank case and all setup/search/certificate costs. An incomplete or timed-out search is inconclusive. Exhaustive zero is a failure only of the frozen finite existence conjecture. One certified success is toy evidence only.

## Baseline, costs, and prior work

Xedni V2 supplied built-in doubling dependencies in 68 synthetic checks but one residue per prime. Its four-prime curve-fitting trial produced 1,944 valid rational fits from 24 finite point pairs; 20 pairs had finite coefficients in [-8,8], and zero had certified rational dependencies in that bound. Those are earlier supplied baseline observations, not new repo-harness results. Here the two historical pairs are certified independent, a stronger pair-specific conclusion, not a speedup or a general lifting impossibility.

Historic timings and partial factor-search counters are preserved exactly. They exclude source retrieval, code preparation and proof derivation and are not full asymptotic operation counts. The new validation logs measure only replay. Charge all construction, screening, certificate generation and relation searches in a future trial, including failures; never price only the final certificate.

Read-only overlap audit: analysis/xedni-prescribed-points/20260905-7d477a/README.md, RQ-XEDN-001/003/004, H-XEDN-2945b2 and H-XEDN-40037f. The earlier prescribed-points portfolio already distinguishes high rank from useful dependence. This snapshot adds explicit historical candidate certificates and a narrowly scoped derived lemma; it does not claim a novel general mechanism. KB search tools were unavailable; the repository fallback is not an exhaustive novelty screen. Checked knowledge/frontiers/ecdlp/ for canonical diagram sources; no existing canonical graph is changed because no official support status changes.

## Review and next execution gate

Independent review is pending. Audit the rational descent hypotheses, dual-preimage formula, torsion-to-mod-2 independence step, and quantifier boundary. Test the lemma against a known dependent doubling pair that must violate at least one hypothesis. The [target manifest](targets.json) is frozen by [freeze_targets.py](freeze_targets.py). Next implement the bounded synthetic runner and controls, independently check the target freeze, and seek an executable experiment contract through the existing public run workflow. No existing hypothesis or goal is closed by this PR.

Editable vector source: [render_report.py](render_report.py). Diagram: [isogeny.svg](isogeny.svg). PDF: [report.pdf](report.pdf). The graph reports producer checks and review status, not independent validation.

## Primary sources

- Cheon, Lee, Hahn, Chee, Elliptic Curve Discrete Logarithms and Wieferich Primes, section 4: https://www.math.snu.ac.kr/~jhcheon/publications/2000/JWISC00_CLH.pdf (read by codex-root; provenance retrieved).
- Presentation date 2000-01-25, separate manuscript posting date unknown: https://www.ieice.org/publications/ken/summary.php?contribution_id=KJ00002127102&expandable=0&ken_id=ISEC&lang=en&presen_date=2000%2F1%2F25&schedule_id=AN10060811_99%28584%29&society_cd=ESSNLS&year=2000 (retrieved).
- Cremona, Algorithms for Modular Elliptic Curves, section 3.6, pp. 84-85: https://johncremona.github.io/book/fulltext/chapter3.pdf (read by codex-root; provenance retrieved).

dominated_by: n/a (no result claimed). sota_delta: no attack; conceptual/measurement contribution only.

#set page(paper:"a4",margin:17mm)
#set text(size:10pt)

= E3 implementation preparation

#text("2026-10-17. Observations and derived encoding only; no scientific approval, rank claim, performance claim or new scientific grid. Base: fd49e52ff70a859a09febf52112f3cfae0ec9455 (merged PR #2382).")

#image("diagram.svg",width:100%)

#text("The prospective encoder uses Y^2 = X^3 + A X Z^4 + B Z^6, with x=X/Z^2 and y=Y/Z^3. It includes monic-denominator charts, finite Bezout saturation, infinity primitivity and smooth affine/O target conditions. The zero section is excluded.")

#text("For supplied chi and encoding degree D: deg X <= 2(D+chi), deg Y <= 3(D+chi), and deg Z=e<=D. Primary unknowns: 5(D+chi)+e+2; saturation witnesses add variables and equations. A bounded search needs every chart e and every D up to its bound. D is not a certified canonical height, and model minimality/chi are not certified by this component.")

#text("13 deterministic engineering fixtures pass. They include a rational section obtained by doubling (1,t) over F_31(t), specialization to O at a finite fibre, a base inversion with O at infinity, denominator saturation, and a known-answer order-19 group over F_17. Sage checks the doubled-section formula with its own group law. Earlier failed development attempts are retained.")

#text("The supplied-vector recovery verifier checks every image/relation, full integer rank, exact kernel index ell, quotient calibration and the final scalar. A full-rank proper sublattice is refused. No section finder or MW-coordinate recovery algorithm is supplied.")

#text("Next protocol: fix the surface before target selection; bind height/model conventions; include all charts and actual auxiliaries; separate planted/oracle input from blind solving. Charge setup, system construction, solving/censoring, coordinate recovery, kernel index and final verification. Coverage must be measured, not inferred from a point count.")

#text("Sources: e3-projective/README.md, section_encoding.py, kernel_recovery.py and fixture-checks.json. The original frozen E3 stage-0 source and admission refusal remain unchanged.")


#pagebreak()

= D1 inputs and admission preparation

#text("Two public source snapshots now supply separate 30- and 31-point candidate lists. Exact Fraction arithmetic checks all 61 equation memberships and nonzero discriminants. The 31-point model/list matches the existing archived ICARM source exactly. A changed-coordinate and duplicate-index control are both refused.")

#text("These are membership checks, not independence or rank certification. No full Gram matrix, certified height-error interval, saturated basis or D1 count/coverage run was produced. Existing validator/red-team reports retain the numerical-regulator limitation and correct the executor's spurious factor-10^10 discrepancy.")

#text("Next D1 obligation: bind the actual generated subgroup, reproducible Gram-matrix constructor, height convention and certified error treatment. Then freeze an executable finite count/coverage workload. Do not substitute subgroup counts for a saturated full MW lattice.")

#text("The isolated additive-admission prototype passes 28 synthetic fixtures. It retains original scientific fields/source bindings and separates fresh retry identities. Production preapproval, selector and supervisor code are unchanged. Technical fixture success grants no approval or execution authority.")

#text("A network-enabled native Codex doctor returned zero and reported working inherited authentication and HTTP reachability, with a WebSocket warning. No inference or model/session probe ran. The remaining integration needs a genuine scoped SQLite/rollout persistence route and exact session metadata; doctor success cannot attest a model or retroactively verify this session.")

#text("Actual E3/D4 launches and the distinct G1 retry still need supported additive admission/selection, exact committed amendment approval, source/archive bindings and live published ownership. The old refusals/failure remain immutable.")

#text("Sources: d1-inputs/fetch-record.json, input-reconciliation.json, parser-refusal-controls.json; coordination/design/SNFS-ADDITIVE-ADMISSION-20261017/README.txt, test-results.json and native-doctor-readiness.json.")

#text("All 23 original full protocols remain incomplete. Existing canonical graphs/statuses are unchanged: this round creates no reviewed scientific finding. KB tools were unavailable; actual repository artifacts and fetched source bytes are cited. No deployed-key recovery or NFS sieving occurred.")

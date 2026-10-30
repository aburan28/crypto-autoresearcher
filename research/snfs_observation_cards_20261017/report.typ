#set page(paper:"a4",margin:17mm)
#set text(size:9.5pt)

= Rotation subsets: fixed m, changing density

#text("Observation cards, 2026-10-17. Recorded values and derived arithmetic for owner inspection; no official scientific conclusion. Sources and hashes: observations.json. Curve and solver programs were not rerun.")

#image("rotation-density.svg",width:100%)

#text("At m=4, saved rotation point density is 38.264%, 46.407%, 50.561%, 68.119%, 89.292% for c=13,17,19,31,61. Hash/size densities stay near their nominal 6.25%. Each point entry aggregates six cells and 120,000 saved density draws. Bars show six-cell spread, not confidence intervals.")

#text("Definition to inspect: rotmin accepts a representative if any cyclic rotation begins with m zero bits. At m=1 every allowed representative is accepted; all 30 saved m=1 rotation cells have sampled density 1.")

#text("Exact integer reference: an m-state zero-run automaton counts cyclic words avoiding m zeros via trace(A_m^c). The accepted representative count is 2^c - trace(A_m^c), out of 2^c-1. The all-ones word is excluded; all-zero is accepted. All 27 small direct enumeration checks agree. At m=4 the exact x-densities are 38.103%, 46.589%, 50.388%, 68.134%, 89.464%.")

#text("Domains remain separate: point sampling weights x by the curve equation and excludes y=0 and O. Uniform-x counts are not exact point-density predictions. The size arm uses other-prime curves. These are descriptive comparisons with no significance test.")

#text("Next check proposed: measure integer and point membership separately; use consistent O/y=0 domains and a separate calibration sample to match control cardinalities to rotation. Keep the original nominal-density tables alongside any calibrated tables.")

#text("Source: EXP-ECDLP-ad27ad / RUN-ECDLP-a5281a. Producer/checker exit codes 0; supervisor receipt remains invalid_output for legacy manifest format. No status is upgraded by these plots.")


#pagebreak()

= E3: degree step and censored solver outcomes

#text("What stands out: both generic encodings finish all nine degree-1 targets; both time out on all nine degree-2 targets under the saved four-second wall cap. The geometry construction has explicit verified sections for six of those degree-2 targets.")

#image("e3-outcomes.svg",width:100%)

#text("Every panel contains the same nine targets across methods, at p=101,257,1021: two fresh and one planted per prime. There are 18 unique targets and 36 generic attempts. Degree-2 geometry successes comprise three fresh and three planted cases; degree 1 has one fresh and three planted.")

#text("The geometry program reads the same target rows and recovers pencil base points from the cubic. It searches a fixed catalog of line/conic classes. Literal sat/unsat statuses describe the relevant encoding/catalog, not unrestricted sections. All ten geometry sat records carry verification flags.")

#text("The degree-step discontinuity is worth inspecting by phase. Timeout records do not identify whether coefficient construction, Groebner computation, conversion/root recovery or a combination consumed the cap. Raw uses 3d+1 unknowns and jet uses 2d+1, including saturation; both retain the degree-2 timeout pattern.")

#text("Next check proposed: freeze these exact targets; persist phase markers outside the child process; record equation degrees, variable counts, saturation, memory and censored phases. Preserve the four-second outcomes and declare any additional observation schedule separately. Verify every returned section by substitution.")

#text("Sources: imported blind-results.json / geometry-results.json and their source programs, hash-pinned in observations.json. Historical finite controls; no new canonical E3 trial. This plane-pencil d differs from D in the newer Weierstrass encoding.")


#pagebreak()

= Field-lift table: repeated concrete inputs

#text("What stands out: 1,395 saved rows partition into 966 seed-inclusive keys (g,p,reduction root,A,B,seed). There are 169 repeated-key groups and 429 additional rows beyond one per key. Five keys each occur ten times. Every repeated-key group has identical saved work-rung profiles and sampled point lists.")

#image("field-lift-multiplicity.svg",width:100%)

#text("Example: g=t^3+t-1, p=4111, reduction root 16, A=-16, B=11, seed 3. Ten zero-based row indices and their labels are retained in field-lift-repeat-groups.json. Dropping seed gives 962 distinct algebraic inputs; different seeds remain separately identified.")

#text("Construction feature to inspect: monic degree-d, weight-w random polynomials have at most 2^(w-1) binomial(d-1,w-2) coefficient patterns before filtering. For d=3,w=3, this is eight. The source permits repeated draws, picks the first admissible prime for each polynomial, and reuses curve seed keys (seed,shape,k).")

#text("This is a literal-key partition, not a field-isomorphism classification or an independence test. It does not change the original weighting or discard any row. Rank descent was skipped in the source run; point/residue counts and rank certificates remain separate.")

#text("Next check proposed: record finite sampler support and draw multiplicities by shape/seed; collect unique field/prime/curve inputs with multiple separately recorded search seeds. Present both row-weighted and input-grouped tables with their sampling definitions.")

#text("Sources: EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532, plus random_shape and the construction loop in implementation/src/main.rs. Producer/checker exit codes 0; supervisor receipt retains invalid_output for legacy manifest format. Full sources and hashes are pinned. Canonical graphs and scientific statuses remain unchanged.")

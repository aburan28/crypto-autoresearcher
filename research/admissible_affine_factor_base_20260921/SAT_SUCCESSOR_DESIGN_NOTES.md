# Prospective SAT successor — design notes, not approved execution

These notes are written before EXP-KIC-3df18c geometry results. They do not amend its protocol, authorize a solver launch, or predict a result.

The next solver question is whether a complete-admissible affine plane provides better decomposition propagation or cold wall time than a strong encoding of the exact same 76 x-values. The geometry experiment only chooses a target-independent base by exact coverage; all later target instances and timing decisions must be frozen separately.

For a selected plane F={a,a+b,a+c,a+b+c}, use x=sigma^j(a+u*b+v*c), j in0..18 and u,v Boolean. Convert a,b,c to a verified normal basis, implement the Frobenius shift as a 19-bit cyclic mux selected by five bits, forbid shift codes19..31, then convert back to the polynomial basis used by the S3 arithmetic. Four different full Frobenius orbits make all76 legal selectors distinct. There is no subgroup-rejection mask or discarded seed to confound the structural representation.

A strong same-domain baseline should use one-hot selectors for all76 legal x values, an exactly-one constraint with a sequential at-most-one encoding and an at-least-one clause, plus coordinate channels. The channels must propagate both selected-value implications and impossible coordinate values back to selectors; pure parity equations alone can be weak under unit propagation. Compare with a binary-index lookup only as a separately named secondary baseline. Both arms receive identical arithmetic gates, constant folding, native long XOR rows, symmetry constraints and model validation.

The relation is two finite S3 links. In characteristic two with b=1:

    S3(a,b,c) = (ab)^2 + c*(ab) + (c*(a+b))^2 + 1.

This form allows each square and multiplication by a public constant to be encoded as a linear XOR map. The second link has a fixed public target x-coordinate, so it needs only one variable-by-variable field multiplication. Constant folding must eliminate gates on Boolean constants and use native XOR rows directly rather than building long chains of auxiliary XOR gates. A change to common arithmetic improves both membership arms and cannot by itself establish a factor-base advantage.

All satisfying assignments must satisfy the original archived CNF/XOR rows and then lift to actual base points with an exact group identity. The exceptional cancellation branch is handled by the charged Q-in-B witness (Q,P,-P). Unsupported, partial or contradictory solver models are implementation failures. Capped solver attempts are censored; they are neither UNSAT nor zero-cost samples.

Use a native coordinate MITM baseline on the identical base. Charge input loading, verified base expansion, construction, encoding, search, replay and process overhead. Report previous geometry discovery separately and explicitly as per-curve advice; a fixed-description PDP timing is not a cold full-IC timing. The cold single-target IC algorithm can reuse its own base over its relation attempts, so the eventual IC cost model must account for that scope rather than multiply a full fresh-PDP build by relation count.

A useful fixed panel would draw target orbit representatives by deterministic hash order before solver results, carry diagnostic and untouched held-out cases, and include exact SAT/UNSAT truth from the geometry oracle. Sample one representative per signed Frobenius orbit to avoid the N7 panel's orbit dependence. If stratifying by existence or selecting non-shortcut cases, record that conditioning and pair each SAT result with the full target coverage probability. Avoid successful-only timing, warmed solver state, target-informed base choice or the fastest of several uncharged encodings.

A possible later ablation fixes a common Frobenius frame and pays for every resulting target-shift system. It requires a separate contract: simply deleting a shift variable can discard valid decompositions, and adding an unknown target shift makes the second S3 link lose its public-constant simplification. No reduction in end-to-end work follows from a smaller variable count alone.

Larger-field transfer also needs a growing seed dimension and explicit subgroup-admission accounting. Four seed x-values generate only8n signed points. That cardinality alone gives at most binomial(8n+2,3) unordered repeated three-point tuples, so their image covers at most that many nonzero targets, before collisions. A fixed four-seed family therefore cannot retain constant relation probability as the subgroup order grows exponentially. This elementary upper bound is a design constraint on the scaling schedule, not a closure of affine factor bases with growing seed dimension or a measured N19 result.

Provenance: internal design reasoning and direct inspection of the archived N7 circuit source. No novelty claim, no solver measurements, no official hypothesis status transition.

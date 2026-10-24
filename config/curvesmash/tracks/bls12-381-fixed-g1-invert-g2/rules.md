# bls12-381-fixed-g1-invert-g2

This is an exploratory cryptanalysis challenge, not formal proof certification.
Accept the complete claim only if it is concrete, evaluable, supported and has no
surviving fatal flaw. Supported plausible heuristics may qualify. Unsupported
heuristics or missing algorithmic detail do not. Explain material uncertainty and
objections in the review reason. Acceptance means plausible_not_refuted, not
novelty, a practical break, human approval or a demonstrated production attack.
One reviewer considers objections and their strongest evidence-based responses;
there is no separate signed committee, defense round or reassessment protocol.

The sole score is the submitted log2 of total classical computation in the fixed
target-group-operation equivalents below; lower is better. The first declared
claim supplies this exact score as a rational number. Review the submitted bound;
do not automatically tighten it. Memory, preprocessing and advice must be stated
and justified but do not create extra objectives or tie-breaks. Algorithmic success
must be at least 0.39 over uniform full-production challenges and fresh algorithm
coins. Reviewer confidence is not algorithmic success probability.

Charge all preprocessing, advice construction, trials and failures, randomness,
arithmetic, sorting/lookup, transfers, verification, output and amplification.
Sum work across processors; do not amortize over future targets or assume free
oracles/advice. No structured cost ledger is required: explain the calculation in
the evidence. Public profile constants and algorithm design effort are excluded.
Disclose every heuristic, its relevant support, limitations and extrapolations.
An analytic argument need not run an exponentially large attack. Small experiments
are evidence only at their actual scope, never a production complexity proof.
All candidate files are untrusted evidence. Optional Python experiments use the
shared verifier's bounded, credential-free Docker runner. Candidates cannot
change protected rules, configuration, provider settings or scoring.

The protected target-profile.json and ../classical-group-work-v2.json files fix the
target and accounting convention. Reference
prices are rounded from instruction counts documented in ../docs/COST_MODEL.md,
not hardware timings or best attacks.
No baseline has been qualified for this track.

The challenge supplies a nonidentity P in G1 and a target z in GT. Return Q in
G2 satisfying e(P,Q)=z for that exact P. P is fixed within the instance, not
chosen by the solver or fixed to the same generator across all instances.
This is fixed-argument pairing inversion (FAPI-1 in G1 x G2 argument order).
The pinned library takes arguments in the reverse order: pairing(Q,P).

There are no auxiliary powers and no n parameter. Submit log2(W) for the
complete attack work, normalized by C=20,000 scalar instruction equivalents
per reference dense Fp12 multiplication. The success probability is over both
the independently uniform nonidentity input P and uniform GT target z, and
fresh algorithm coins. The identity target is included; input P=infinity is
excluded. All other shared accounting and exploratory review rules apply.

The selected package is an unscored template, not a qualified baseline.
Historical fixed-Q0/recover-G1 scores and any-pair inversion scores do not
qualify this track. An admissible approach is to solve z=e(P,Q0)^a in GT and
return Q=[a]Q0, but its complete work and success must be justified.

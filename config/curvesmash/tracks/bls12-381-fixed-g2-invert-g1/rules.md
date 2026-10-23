# bls12-381-fixed-g2-invert-g1

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
The challenge supplies a nonidentity Q in G2 and a target z in GT. Return P
in G1 satisfying e(P,Q)=z for that exact Q. Q is fixed within the instance,
not chosen by the solver and not always the generator Q0. This is FAPI-2 in
G1 x G2 argument order; the pinned library takes pairing(Q,P).

There are no auxiliary powers or n parameter. Submit log2(W) for total work
using C=20,000 and the existing dense Fp12 multiplication reference. Success
is over the independently uniform nonidentity Q and uniform GT target z,
and fresh algorithm coins. Input Q=infinity is forbidden. Output P=infinity
is valid exactly for z=1. A valid any-pair answer with a different Q is not
sufficient. Solving z=e(P0,Q)^a in GT and returning [a]P0 is admissible, but
all computation and success assumptions must be justified. No particular
inversion method or intermediate representation is required.

No baseline has been qualified for this track. The selected package is an
unscored template; historical scores do not qualify this target.

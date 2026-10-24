# p256-ecdlp

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
Given only Q=[x]P on NIST P-256 (secp256r1), recover x in 0..r-1.
Use the exact SEC 2 Section 2.4.2 parameters in target-profile.json, including
the nonzero curve coefficient a=-3. There are no auxiliary inputs or n
parameter. The identity target is included and has scalar 0.

Submit log2(W) for total work. This track deliberately borrows the existing
secp256k1 reference unit C=1,000 scalar AArch64 instruction equivalents as a
normalization convention; this is NOT a measurement of P-256 arithmetic.
Account for actual P-256 operations through their justified instruction
costs divided by 1,000. A P-256 point addition is not automatically one unit,
and the secp256k1 6M reference formula is not a P-256 implementation bound.
All methods must justify their complete computation and success.

No baseline has been qualified for this track. The selected package is an
unscored template; historical scores do not qualify this target.

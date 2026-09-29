# Draft: curve intersection cost prediction and selection

STATUS: NOT APPROVED. This is a task design and schema fixture, not a working ML/RL solution. Do not run Harbor, implement a solver/trainer, or treat a parsed task as execution approval. Both task entrypoints deliberately refuse execution.

The proposed pilot measures fixed Groebner-basis and root-extraction costs on self-generated nonsingular curves intersected with unrelated quadratic polynomials over primes 101, 103, 107, 109, 113 and 127. It compares a fixed curve, random selection, supervised cost prediction and a one-step policy-gradient contextual bandit. Complete modular enumeration independently verifies roots. See ../draft-protocol.json for proposed datasets, controls, split rules, metrics, stopping rules and artifacts.

The repository baseline fails ledger validation. A separately authorized repair, passing preflight/ledger checks, clarified final user objective, and a committed Coordinator approval are required before a new implementation task can replace these refusal entrypoints.

No ECDLP, summation-polynomial attack pipeline, private-key recovery, deployed target or arbitrary imported polynomial system is part of this design. There is no speedup score, fabricated reference result, generic-prime-field theorem or claim of weakened curve security. A slower learned policy would still be a valid software observation.

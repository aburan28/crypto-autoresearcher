# EXP-CERTBIN-ddfe75 verifier/

`verify_nconv.py` is run as a SEPARATE PROCESS after the closures (phase 6):

    python3 experiments/EXP-CERTBIN-ddfe75/verifier/verify_nconv.py --run <run-dir> \
      --curve experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json \
      --archived experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json \
      --nell coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/n-ell-instances.json \
      --out <run-dir>

It imports nothing from `impl/`, nothing from `crypto_autoresearcher`, no
archived `impl/` and nothing from a review directory (standard library and
numpy only; it aborts if a `crypto_autoresearcher` module is loaded). The
seeds are transcribed from the specification, not read from executor output.

Own components: F_{2^17} by exp/log tables; the S_3 descent by generic
symbolic expansion with multilinear reduction; U, S_L, the N-CONV17 forms and
every draw rule and keep rule; exhaustive satisfiability by a 512 x 512 half
split; multilinear certificate arithmetic on monomial bit masks.

- V1 rebuilds every system and compares it with the run's instances.jsonl.gz
  (and archived S_3 systems with its own construction);
- V2 recomputes s for every kept system and checks each satisfiable control's
  solution list against the full solution set, and archived s;
- V3 replays each fresh arm's PCG64 stream with its own keep rule and compares
  every logged attempt and the kept attempt indices;
- V4 verifies every certificate: flat-v1 by the sum (and max |mu| <= 2 for
  M_4); wdag-v1 by rules (a)-(e);
- V5 checks that every negative-control certificate is rejected and that its
  source certificate verified.

Outputs: certificate-verification.json, construction-verification.json,
draw-replay-verification.json, negative-controls-verification.json.

Independence: code-level only. The same executor session wrote impl/ and this
verifier; author-independent verification is the review round's.

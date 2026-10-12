# Model framing evaluation

Goal: measure whether equivalent mathematics questions get different answer quality under different contextual descriptions. Such differences do not establish intentional interference.

Protocol: register identical mathematical tasks in abstract, applied, and neutral framing. Fix model version, temperature, tools, and token budget. Randomize ordering and repeat each condition 20 times. Preserve exact prompts and raw outputs. Blind independent reviewers to condition. Use executable verifiers where possible.

Controls: include known-valid constructions, known-invalid constructions, and ambiguous problems. Track correctness, unsupported certainty, refusals, useful proof attempts, and latency. Report confidence intervals and all failures. Replicate with multiple models and paraphrases before interpreting results.

Suggested fixtures: finite group isomorphisms, algebraic maps with nontrivial kernels, extension-ring reductions, and Jacobian correspondences. For every task specify the exact assumptions, expected proof obligations, and a small independently verifiable instance.

Important: distinguish response-policy effects, ordinary model errors, and sampling variability. Never infer hidden intent from framing effects alone.
